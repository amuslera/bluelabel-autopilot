"""Base agent classes with self-registration support.

This is an enhanced version of BaseAgent that supports automatic
registration with the AgentRegistry when agents are instantiated.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

# Import standardized models from the single source of truth
from interfaces.agent_models import AgentInput, AgentOutput, AgentCapability, AgentCapabilities


logger = logging.getLogger(__name__)


class BaseAgentV2(ABC):
    """Enhanced base class with self-registration support.
    
    This class extends the original BaseAgent with:
    - Automatic registration with AgentRegistry
    - Enhanced capability reporting
    - Better initialization patterns
    """
    
    # Class-level registration flag
    _auto_register = True
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        agent_id: Optional[str] = None,
        version: str = "1.0.0",
        tags: Optional[List[str]] = None,
        auto_register: bool = True
    ):
        """Initialize the base agent with self-registration.
        
        Args:
            name: Human-readable agent name
            description: What this agent does
            agent_id: Unique identifier (auto-generated if not provided)
            version: Agent version string
            tags: Tags for categorization
            auto_register: Whether to auto-register with registry
        """
        self.name = name
        self.description = description
        self.agent_id = agent_id or f"{name.lower().replace(' ', '_')}"
        self.version = version
        self.tags = tags or []
        self.capabilities: List[AgentCapability] = []
        self._initialized = False
        
        # Storage paths (can be set by engine)
        self.storage_path = None
        self.temp_path = None
        
        # Self-register if enabled
        if auto_register and self._auto_register:
            self._register_self()
    
    def _register_self(self):
        """Register this agent with the global registry."""
        try:
            from core.agent_registry import registry
            
            # Build capabilities object
            capabilities = self._build_capabilities()
            
            # Register with the registry
            registry.register(
                agent_id=self.agent_id,
                agent_class=self.__class__,
                version=self.version,
                capabilities=capabilities,
                description=self.description,
                tags=self.tags,
                replace=True  # Allow re-registration for development
            )
            
            logger.info(f"Agent '{self.agent_id}' auto-registered successfully")
            
        except Exception as e:
            logger.warning(f"Failed to auto-register agent '{self.agent_id}': {e}")
    
    def _build_capabilities(self) -> AgentCapabilities:
        """Build capabilities object from agent metadata."""
        # Default implementation - override in subclasses
        return AgentCapabilities(
            can_process_files=hasattr(self, 'process_file'),
            can_process_urls=hasattr(self, 'process_url'),
            can_generate_summaries=hasattr(self, 'generate_summary'),
            supported_formats=getattr(self, 'supported_formats', [])
        )
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent with any necessary setup.
        
        This method is called once before the agent processes any tasks.
        Use it to set up connections, load models, etc.
        """
        pass
        
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process an input and return structured output.
        
        This is the main method that all agents must implement.
        It should handle the core logic of the agent.
        
        Args:
            input_data: Standardized input following MCP schema
            
        Returns:
            AgentOutput with results or error information
        """
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """Return the list of capabilities this agent supports.
        
        Returns:
            List of capability definitions
        """
        pass
        
    async def shutdown(self) -> None:
        """Clean shutdown of the agent.
        
        Override this method to implement cleanup logic like closing
        connections, saving state, etc.
        """
        pass
        
    async def validate_input(self, input_data: AgentInput) -> tuple[bool, Optional[str]]:
        """Validate input before processing.
        
        Override this method to add custom validation logic.
        
        Args:
            input_data: Input to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Basic validation
        if not input_data.task_id:
            return False, "task_id is required"
        if not input_data.content:
            return False, "content is required"
        return True, None
        
    def create_output(
        self, 
        task_id: str,
        status: str = "success",
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentOutput:
        """Helper method to create standardized output.
        
        Args:
            task_id: Task identifier from input
            status: Status of the operation
            result: Result data if successful
            error: Error message if failed
            metadata: Additional metadata
            
        Returns:
            Standardized AgentOutput
        """
        return AgentOutput(
            task_id=task_id,
            agent_id=self.agent_id,
            status=status,
            result=result or {},
            error=error,
            metadata=metadata or {},
            timestamp=datetime.utcnow().isoformat()
        )
    
    async def health_check(self) -> bool:
        """Perform a health check on the agent.
        
        Override this method to implement custom health checks.
        
        Returns:
            True if healthy, False otherwise
        """
        # Basic health check - agent is initialized
        return self._initialized
    
    @classmethod
    def disable_auto_registration(cls):
        """Disable automatic registration for this class."""
        cls._auto_register = False
    
    @classmethod
    def enable_auto_registration(cls):
        """Enable automatic registration for this class."""
        cls._auto_register = True