"""
Agent Registry - Dynamic agent registration and discovery system.

This module provides a dependency injection system for agents, replacing
hardcoded agent dictionaries with a flexible, extensible registry.
"""

import threading
import logging
from typing import Dict, Type, Optional, List, Any, Callable
from datetime import datetime
from enum import Enum
import inspect

from agents.base_agent import BaseAgent
from interfaces.agent_models import AgentCapabilities


logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Status of registered agents."""
    REGISTERED = "registered"
    INITIALIZED = "initialized"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DISABLED = "disabled"


class AgentMetadata:
    """Metadata for a registered agent."""
    
    def __init__(
        self,
        agent_id: str,
        agent_class: Type[BaseAgent],
        version: str = "1.0.0",
        capabilities: Optional[AgentCapabilities] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ):
        self.agent_id = agent_id
        self.agent_class = agent_class
        self.version = version
        self.capabilities = capabilities or AgentCapabilities()
        self.description = description or ""
        self.tags = tags or []
        self.status = AgentStatus.REGISTERED
        self.registered_at = datetime.utcnow()
        self.last_health_check = None
        self.health_check_errors = []
        self.instance: Optional[BaseAgent] = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'agent_id': self.agent_id,
            'agent_class': f"{self.agent_class.__module__}.{self.agent_class.__name__}",
            'version': self.version,
            'capabilities': self.capabilities.model_dump() if hasattr(self.capabilities, 'model_dump') else {},
            'description': self.description,
            'tags': self.tags,
            'status': self.status.value,
            'registered_at': self.registered_at.isoformat(),
            'last_health_check': self.last_health_check.isoformat() if self.last_health_check else None
        }


class AgentRegistry:
    """
    Thread-safe registry for agent discovery and management.
    
    Implements singleton pattern to ensure single registry instance.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry (only runs once due to singleton)."""
        if self._initialized:
            return
            
        self._agents: Dict[str, AgentMetadata] = {}
        self._observers: List[Callable] = []
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._initialized = True
        
        logger.info("AgentRegistry initialized")
    
    def register(
        self,
        agent_id: str,
        agent_class: Type[BaseAgent],
        version: str = "1.0.0",
        capabilities: Optional[AgentCapabilities] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        replace: bool = False
    ) -> None:
        """
        Register an agent with the registry.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_class: Class type that extends BaseAgent
            version: Agent version string
            capabilities: Agent capabilities specification
            description: Human-readable description
            tags: List of tags for categorization
            replace: Whether to replace existing registration
            
        Raises:
            ValueError: If agent_id already registered and replace=False
            TypeError: If agent_class doesn't extend BaseAgent
        """
        # Validate agent class
        if not inspect.isclass(agent_class) or not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{agent_class} must be a subclass of BaseAgent")
        
        with self._lock:
            if agent_id in self._agents and not replace:
                raise ValueError(f"Agent '{agent_id}' already registered. Use replace=True to override.")
            
            # Create metadata
            metadata = AgentMetadata(
                agent_id=agent_id,
                agent_class=agent_class,
                version=version,
                capabilities=capabilities,
                description=description,
                tags=tags
            )
            
            # Store in registry
            self._agents[agent_id] = metadata
            
            logger.info(f"Registered agent '{agent_id}' version {version}")
            
            # Notify observers
            self._notify_observers('register', agent_id, metadata)
    
    def discover(
        self,
        tags: Optional[List[str]] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        status: Optional[AgentStatus] = None
    ) -> List[str]:
        """
        Discover agents matching criteria.
        
        Args:
            tags: Filter by tags (matches any)
            capabilities: Filter by capabilities
            status: Filter by status
            
        Returns:
            List of matching agent IDs
        """
        with self._lock:
            matches = []
            
            for agent_id, metadata in self._agents.items():
                # Check status filter
                if status and metadata.status != status:
                    continue
                
                # Check tag filter
                if tags and not any(tag in metadata.tags for tag in tags):
                    continue
                
                # Check capabilities filter
                if capabilities:
                    # Simple capability matching - could be enhanced
                    agent_caps = metadata.capabilities.model_dump() if hasattr(metadata.capabilities, 'model_dump') else {}
                    if not all(agent_caps.get(k) == v for k, v in capabilities.items()):
                        continue
                
                matches.append(agent_id)
            
            return matches
    
    def get(self, agent_id: str, initialize: bool = True) -> Optional[BaseAgent]:
        """
        Get an agent instance by ID.
        
        Args:
            agent_id: Agent identifier
            initialize: Whether to initialize the agent if not already done
            
        Returns:
            Agent instance or None if not found
        """
        with self._lock:
            metadata = self._agents.get(agent_id)
            if not metadata:
                logger.warning(f"Agent '{agent_id}' not found in registry")
                return None
            
            # Create instance if needed
            if metadata.instance is None and initialize:
                try:
                    metadata.instance = metadata.agent_class()
                    metadata.status = AgentStatus.INITIALIZED
                    logger.info(f"Initialized agent '{agent_id}'")
                    
                    # Notify observers
                    self._notify_observers('initialize', agent_id, metadata)
                    
                except Exception as e:
                    logger.error(f"Failed to initialize agent '{agent_id}': {e}")
                    metadata.status = AgentStatus.UNHEALTHY
                    metadata.health_check_errors.append(str(e))
                    return None
            
            return metadata.instance
    
    def get_metadata(self, agent_id: str) -> Optional[AgentMetadata]:
        """Get metadata for an agent."""
        with self._lock:
            return self._agents.get(agent_id)
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """List all registered agents with their metadata."""
        with self._lock:
            return {
                agent_id: metadata.to_dict()
                for agent_id, metadata in self._agents.items()
            }
    
    async def health_check(self, agent_id: str) -> bool:
        """
        Perform health check on an agent.
        
        Args:
            agent_id: Agent to check
            
        Returns:
            True if healthy, False otherwise
        """
        with self._lock:
            metadata = self._agents.get(agent_id)
            if not metadata:
                return False
            
            metadata.last_health_check = datetime.utcnow()
            
            # Get or create instance
            agent = self.get(agent_id)
            if not agent:
                metadata.status = AgentStatus.UNHEALTHY
                return False
            
            try:
                # Check if agent has health check method
                if hasattr(agent, 'health_check'):
                    is_healthy = await agent.health_check()
                else:
                    # Basic check - can we call process?
                    is_healthy = callable(getattr(agent, 'process', None))
                
                metadata.status = AgentStatus.HEALTHY if is_healthy else AgentStatus.UNHEALTHY
                
                if not is_healthy:
                    metadata.health_check_errors.append(f"Health check failed at {metadata.last_health_check}")
                else:
                    # Clear errors on successful check
                    metadata.health_check_errors = []
                
                # Notify observers
                self._notify_observers('health_check', agent_id, metadata)
                
                return is_healthy
                
            except Exception as e:
                logger.error(f"Health check failed for agent '{agent_id}': {e}")
                metadata.status = AgentStatus.UNHEALTHY
                metadata.health_check_errors.append(str(e))
                return False
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Perform health checks on all agents."""
        results = {}
        for agent_id in list(self._agents.keys()):
            results[agent_id] = await self.health_check(agent_id)
        return results
    
    def add_observer(self, callback: Callable) -> None:
        """
        Add an observer for registry events.
        
        Callback signature: callback(event: str, agent_id: str, metadata: AgentMetadata)
        """
        with self._lock:
            self._observers.append(callback)
    
    def remove_observer(self, callback: Callable) -> None:
        """Remove an observer."""
        with self._lock:
            if callback in self._observers:
                self._observers.remove(callback)
    
    def _notify_observers(self, event: str, agent_id: str, metadata: AgentMetadata) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            try:
                observer(event, agent_id, metadata)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
    
    def clear(self) -> None:
        """Clear all registrations (useful for testing)."""
        with self._lock:
            self._agents.clear()
            logger.info("AgentRegistry cleared")
    
    def disable(self, agent_id: str) -> None:
        """Disable an agent."""
        with self._lock:
            metadata = self._agents.get(agent_id)
            if metadata:
                metadata.status = AgentStatus.DISABLED
                logger.info(f"Disabled agent '{agent_id}'")
                self._notify_observers('disable', agent_id, metadata)
    
    def enable(self, agent_id: str) -> None:
        """Enable a disabled agent."""
        with self._lock:
            metadata = self._agents.get(agent_id)
            if metadata and metadata.status == AgentStatus.DISABLED:
                metadata.status = AgentStatus.REGISTERED
                logger.info(f"Enabled agent '{agent_id}'")
                self._notify_observers('enable', agent_id, metadata)


# Global registry instance
registry = AgentRegistry()


# Convenience functions
def register_agent(agent_id: str, agent_class: Type[BaseAgent], **kwargs) -> None:
    """Register an agent with the global registry."""
    registry.register(agent_id, agent_class, **kwargs)


def get_agent(agent_id: str) -> Optional[BaseAgent]:
    """Get an agent from the global registry."""
    return registry.get(agent_id)


def discover_agents(**kwargs) -> List[str]:
    """Discover agents from the global registry."""
    return registry.discover(**kwargs)