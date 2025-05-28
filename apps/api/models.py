"""
Data models for the FastAPI application.

Defines request/response models for the API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DAGRunResponse(BaseModel):
    """Response model for a DAG run."""
    id: str = Field(..., description="Unique run identifier")
    workflow_name: str = Field(..., description="Name of the workflow")
    workflow_version: str = Field(..., description="Version of the workflow")
    status: str = Field(..., description="Current status (running, success, failed)")
    started_at: str = Field(..., description="ISO timestamp when run started")
    completed_at: Optional[str] = Field(None, description="ISO timestamp when run completed")
    duration_ms: Optional[int] = Field(None, description="Total duration in milliseconds")
    step_count: int = Field(..., description="Number of steps in the workflow")
    steps: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed step information")
    failed_step: Optional[str] = Field(None, description="ID of the step that failed")
    errors: List[str] = Field(default_factory=list, description="List of error messages")
    execution_order: Optional[List[str]] = Field(None, description="Order of step execution")


class DAGRunListResponse(BaseModel):
    """Response model for listing DAG runs."""
    items: List[DAGRunResponse] = Field(..., description="List of DAG runs")
    total: int = Field(..., description="Total number of runs")
    limit: int = Field(..., description="Number of items per page")
    offset: int = Field(..., description="Offset for pagination")


class DAGRunCreateRequest(BaseModel):
    """Request model for creating a DAG run."""
    workflow_path: str = Field(..., description="Path to workflow YAML file")
    initial_input: Optional[Dict[str, Any]] = Field(None, description="Initial input data")
    persist: bool = Field(True, description="Whether to persist outputs to disk")
    engine_type: Optional[str] = Field(None, description="Engine type (sequential or stateful_dag)")
    storage_path: Optional[str] = Field(None, description="Path to content storage directory")
    force: bool = Field(False, description="Force start even if workflow is already running")


class DAGRunStatusUpdate(BaseModel):
    """Request model for updating DAG run status."""
    status: str = Field(..., description="New status (e.g., cancelled)")
    message: Optional[str] = Field(None, description="Optional message for the update")


class WebSocketMessage(BaseModel):
    """WebSocket message format."""
    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())