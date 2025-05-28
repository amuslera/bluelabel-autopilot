"""
Agent Registry - Dynamic agent registration and dependency injection

This module provides a centralized registry for agent discovery and instantiation,
enabling flexible agent configuration and dependency injection throughout the system.
"""

import logging
from typing import Dict, Type, Optional, Any, List, Callable
from pathlib import Path
import inspect

from agents.base_agent import BaseAgent
from interfaces.agent_models import AgentCapabilities

logger = logging.getLogger(__name__)


class AgentRegistry:
    """
    Singleton registry for dynamic agent registration and discovery.
    
    Provides dependency injection capabilities for agents with
    configuration management and capability-based discovery.
    """
    
    _instance = None
    _agents: Dict[str, Type[BaseAgent]] = {}
    _agent_configs: Dict[str, Dict[str, Any]] = {}
    _agent_instances: Dict[str, BaseAgent] = {}
    _agent_capabilities: Dict[str, AgentCapabilities] = {}
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def register(cls, 
                 agent_type: str, 
                 agent_class: Type[BaseAgent],
                 config: Optional[Dict[str, Any]] = None,
                 capabilities: Optional[AgentCapabilities] = None):
        """
        Register an agent class with the registry.
        
        Args:
            agent_type: Unique identifier for the agent type
            agent_class: The agent class to register
            config: Default configuration for the agent
            capabilities: Agent capabilities for discovery
        """
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"{agent_class} must be a subclass of BaseAgent")
        
        cls._agents[agent_type] = agent_class
        cls._agent_configs[agent_type] = config or {}
        
        if capabilities:
            cls._agent_capabilities[agent_type] = capabilities
        
        logger.info(f"Registered agent: {agent_type} -> {agent_class.__name__}")
    
    @classmethod
    def get_agent(cls, 
                  agent_type: str, 
                  config_override: Optional[Dict[str, Any]] = None,
                  force_new: bool = False) -> BaseAgent:
        """
        Get or create an agent instance.
        
        Args:
            agent_type: Type of agent to retrieve
            config_override: Configuration to override defaults
            force_new: Force creation of new instance
            
        Returns:
            Agent instance
        """
        if agent_type not in cls._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        # Check for existing instance if not forcing new
        if not force_new and agent_type in cls._agent_instances:
            return cls._agent_instances[agent_type]
        
        # Merge configurations
        config = cls._agent_configs.get(agent_type, {}).copy()
        if config_override:
            config.update(config_override)
        
        # Create agent instance
        agent_class = cls._agents[agent_type]
        
        # Inspect constructor to determine required parameters
        sig = inspect.signature(agent_class.__init__)
        params = sig.parameters
        
        # Build kwargs based on what the agent accepts
        kwargs = {}
        for param_name, param in params.items():
            if param_name == 'self':
                continue
            
            # Check config for parameter
            if param_name in config:
                kwargs[param_name] = config[param_name]
            elif param.default is not inspect.Parameter.empty:
                # Has default value, skip
                continue
            else:
                # Try common parameters
                if param_name == 'storage_path' and 'storage_path' not in kwargs:
                    kwargs['storage_path'] = Path("./data/knowledge")
                elif param_name == 'temp_path' and 'temp_path' not in kwargs:
                    kwargs['temp_path'] = Path("./data/temp")
        
        # Create instance
        agent = agent_class(**kwargs)
        
        # Cache instance if not forced new
        if not force_new:
            cls._agent_instances[agent_type] = agent
        
        logger.info(f"Created agent instance: {agent_type}")
        return agent
    
    @classmethod
    def discover(cls, 
                 capability: Optional[str] = None,
                 tags: Optional[List[str]] = None) -> List[str]:
        """
        Discover agents by capability or tags.
        
        Args:
            capability: Required capability
            tags: Required tags
            
        Returns:
            List of agent types matching criteria
        """
        matching_agents = []
        
        for agent_type, capabilities in cls._agent_capabilities.items():
            # Check capability match
            if capability and capability not in capabilities.capabilities:
                continue
            
            # Check tag match
            if tags:
                agent_tags = getattr(capabilities, 'tags', [])
                if not all(tag in agent_tags for tag in tags):
                    continue
            
            matching_agents.append(agent_type)
        
        return matching_agents
    
    @classmethod
    def list_agents(cls) -> Dict[str, Dict[str, Any]]:
        """List all registered agents with their info."""
        agents_info = {}
        
        for agent_type, agent_class in cls._agents.items():
            info = {
                "class": agent_class.__name__,
                "module": agent_class.__module__,
                "config": cls._agent_configs.get(agent_type, {}),
                "instantiated": agent_type in cls._agent_instances
            }
            
            if agent_type in cls._agent_capabilities:
                info["capabilities"] = cls._agent_capabilities[agent_type].dict()
            
            agents_info[agent_type] = info
        
        return agents_info
    
    @classmethod
    def clear(cls):
        """Clear all registrations (useful for testing)."""
        cls._agents.clear()
        cls._agent_configs.clear()
        cls._agent_instances.clear()
        cls._agent_capabilities.clear()
        logger.info("Agent registry cleared")
    
    @classmethod
    def update_config(cls, agent_type: str, config: Dict[str, Any]):
        """Update configuration for a registered agent."""
        if agent_type not in cls._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        cls._agent_configs[agent_type].update(config)
        
        # Invalidate cached instance
        if agent_type in cls._agent_instances:
            del cls._agent_instances[agent_type]
        
        logger.info(f"Updated config for agent: {agent_type}")
    
    @classmethod
    def health_check(cls, agent_type: str) -> Dict[str, Any]:
        """Perform health check on an agent."""
        try:
            agent = cls.get_agent(agent_type)
            
            # Basic health check
            health = {
                "status": "healthy",
                "agent_type": agent_type,
                "class": agent.__class__.__name__,
                "instance_id": id(agent)
            }
            
            # Check if agent has custom health check
            if hasattr(agent, 'health_check'):
                custom_health = agent.health_check()
                health.update(custom_health)
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "agent_type": agent_type,
                "error": str(e)
            }


# Convenience functions for module-level access
def register_agent(agent_type: str, 
                   agent_class: Type[BaseAgent],
                   config: Optional[Dict[str, Any]] = None,
                   capabilities: Optional[AgentCapabilities] = None):
    """Register an agent with the global registry."""
    AgentRegistry.register(agent_type, agent_class, config, capabilities)


def get_agent(agent_type: str, 
              config_override: Optional[Dict[str, Any]] = None,
              force_new: bool = False) -> BaseAgent:
    """Get an agent from the global registry."""
    return AgentRegistry.get_agent(agent_type, config_override, force_new)


def discover_agents(capability: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> List[str]:
    """Discover agents by capability or tags."""
    return AgentRegistry.discover(capability, tags)


# Auto-register built-in agents when module is imported
def _auto_register_agents():
    """Auto-register built-in agents."""
    try:
        from agents.ingestion_agent import IngestionAgent
        from agents.digest_agent import DigestAgent
        
        # Register ingestion agent
        register_agent(
            "ingestion",
            IngestionAgent,
            config={
                "storage_path": Path("./data/knowledge"),
                "temp_path": Path("./data/temp")
            },
            capabilities=AgentCapabilities(
                agent_id="ingestion",
                name="Ingestion Agent",
                description="Processes URLs and PDFs to extract content",
                version="1.0.0",
                capabilities=["url_processing", "pdf_extraction", "content_storage"],
                input_schema={
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "pdf_path": {"type": "string"},
                        "text": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "metadata": {"type": "object"},
                        "output_path": {"type": "string"}
                    }
                }
            )
        )
        
        # Register digest agent
        register_agent(
            "digest",
            DigestAgent,
            config={
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1024
            },
            capabilities=AgentCapabilities(
                agent_id="digest",
                name="Digest Agent",
                description="Creates summaries and digests from content",
                version="1.0.0",
                capabilities=["summarization", "digest_creation", "content_analysis"],
                input_schema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "content_type": {"type": "string"},
                        "digest_type": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "key_points": {"type": "array"},
                        "output_path": {"type": "string"}
                    }
                }
            )
        )
        
        logger.info("Auto-registered built-in agents")
        
    except ImportError as e:
        logger.warning(f"Could not auto-register agents: {e}")


# Perform auto-registration on import
_auto_register_agents()