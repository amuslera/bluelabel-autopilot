"""Agent model interfaces for type consistency across the system.

This module re-exports the core agent models for easy importing.
"""

from agents.base_agent import (
    AgentInput,
    AgentOutput,
    AgentCapability,
    BaseAgent
)

__all__ = [
    "AgentInput",
    "AgentOutput", 
    "AgentCapability",
    "BaseAgent"
]

"""Shared models for agent interfaces.

This module defines the common data structures used across all agents
in the Bluelabel Autopilot system.
"""

from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """Standardized input for all agents."""
    task_id: str = Field(..., description="Unique task identifier")
    task_type: Literal["url", "pdf"] = Field(..., description="Type of content to process")
    source: str = Field(..., description="Source identifier (e.g., 'whatsapp', 'web', 'cli')")
    content: Dict[str, Any] = Field(..., description="Main content payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentOutput(BaseModel):
    """Standardized output from all agents."""
    task_id: str = Field(..., description="Matching task_id from input")
    status: Literal["success", "error", "pending"] = Field(..., description="Processing status")
    result: Dict[str, Any] = Field(..., description="Processing results")
    error: Optional[str] = Field(None, description="Error message if status is 'error'")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = Field(None, description="Processing duration in milliseconds")


class AgentCapability(BaseModel):
    """Describes a capability or tool available to an agent."""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="What this capability does")
    parameters: Dict[str, Any] = Field(..., description="Expected parameters")


class ContentMetadata(BaseModel):
    """Common metadata for processed content."""
    content_id: str = Field(..., description="Unique content identifier")
    content_type: Literal["url", "pdf"] = Field(..., description="Type of content")
    source: str = Field(..., description="Content source")
    title: Optional[str] = Field(None, description="Content title")
    author: Optional[str] = Field(None, description="Content author")
    created_at: datetime = Field(..., description="When content was created")
    processed_at: datetime = Field(..., description="When content was processed")
    content_length: int = Field(..., description="Length of content in characters")
    additional_metadata: Dict[str, Any] = Field(default_factory=dict, description="Type-specific metadata")