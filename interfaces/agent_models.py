"""
Agent model interfaces for type consistency across the system.

This module is the SINGLE SOURCE OF TRUTH for all agent-related data models.
All agents must import these models from this location to ensure consistency.

MCP Compliance: These models follow the Model Context Protocol standards
for agent communication and data exchange.
"""

from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class AgentInput(BaseModel):
    """Standardized input for all agents following MCP patterns."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique task identifier")
    task_type: Optional[Literal["url", "pdf"]] = Field(None, description="Type of content to process")
    source: str = Field(..., description="Source identifier (e.g., 'whatsapp', 'web', 'cli')")
    content: Dict[str, Any] = Field(default_factory=dict, description="Main content payload")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentOutput(BaseModel):
    """Standardized output from all agents following MCP patterns."""
    task_id: str = Field(..., description="Matching task_id from input")
    status: Literal["success", "error", "pending"] = Field(..., description="Processing status")
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


class AgentCapabilities(BaseModel):
    """Collection of agent capabilities."""
    can_process_files: bool = Field(False, description="Can process files")
    can_process_urls: bool = Field(False, description="Can process URLs")
    can_generate_summaries: bool = Field(False, description="Can generate summaries")
    supported_formats: List[str] = Field(default_factory=list, description="Supported file formats")


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


__all__ = [
    "AgentInput",
    "AgentOutput", 
    "AgentCapability",
    "ContentMetadata"
]