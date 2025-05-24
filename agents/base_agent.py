"""Base agent classes for the Bluelabel Autopilot system.

This module provides the foundational classes for all agents in the system,
following MCP (Model Context Protocol) compliance standards.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """Standardized input for all agents following MCP patterns."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str = Field(..., description="Source identifier (e.g., 'whatsapp', 'web', 'cli')")
    content: Dict[str, Any] = Field(default_factory=dict, description="Main content payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentOutput(BaseModel):
    """Standardized output from all agents following MCP patterns."""
    task_id: str = Field(..., description="Matching task_id from input")
    status: str = Field(..., description="Status: 'success', 'error', 'pending'")
    result: Dict[str, Any] = Field(default_factory=dict, description="Processing results")
    error: Optional[str] = Field(None, description="Error message if status is 'error'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = Field(None, description="Processing duration in milliseconds")


class AgentCapability(BaseModel):
    """Describes a capability or tool available to an agent."""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="What this capability does")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Expected parameters")
    
    
class BaseAgent(ABC):
    """Base class for all agents in the Bluelabel Autopilot system.
    
    This class provides the foundation for MCP-compliant agents that can:
    - Process standardized input/output
    - Report their capabilities
    - Handle initialization and shutdown
    - Support async processing
    """
    
    def __init__(
        self, 
        name: str, 
        description: str, 
        agent_id: Optional[str] = None,
        version: str = "1.0.0"
    ):
        """Initialize the base agent.
        
        Args:
            name: Human-readable agent name
            description: What this agent does
            agent_id: Unique identifier (auto-generated if not provided)
            version: Agent version string
        """
        self.name = name
        self.description = description
        self.agent_id = agent_id or f"{name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
        self.version = version
        self.capabilities: List[AgentCapability] = []
        self._initialized = False
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the agent with any necessary setup.
        
        This method should be called before the agent starts processing.
        Implementations should set self._initialized = True when complete.
        """
        pass
    
    @abstractmethod
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process the input and return an output.
        
        Args:
            input_data: Standardized agent input
            
        Returns:
            Standardized agent output
            
        Raises:
            Exception: If processing fails
        """
        pass
    
    async def shutdown(self) -> None:
        """Cleanup when the agent is shut down.
        
        Override this method if your agent needs cleanup.
        """
        self._initialized = False
    
    def add_capability(self, capability: AgentCapability) -> None:
        """Register a capability for this agent.
        
        Args:
            capability: The capability to add
        """
        self.capabilities.append(capability)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the agent's capabilities in MCP format.
        
        Returns:
            Dictionary containing agent metadata and capabilities
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "initialized": self._initialized,
            "capabilities": [
                {
                    "name": cap.name,
                    "description": cap.description,
                    "parameters": cap.parameters
                } for cap in self.capabilities
            ]
        }
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(id={self.agent_id}, name={self.name})"