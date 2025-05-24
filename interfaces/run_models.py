"""
Run Models for Workflow Execution

This module defines the data models for workflow execution results
and related structures.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class WorkflowStatus(str, Enum):
    """Status of a workflow run."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepResult(BaseModel):
    """Result of a single workflow step execution."""
    step_id: str = Field(..., description="Unique identifier for the step")
    step_name: str = Field(..., description="Human-readable name of the step")
    status: str = Field(..., description="Execution status (success/error)")
    duration_ms: int = Field(..., description="Execution duration in milliseconds")
    result: Optional[Dict[str, Any]] = Field(None, description="Step output data")
    error: Optional[str] = Field(None, description="Error message if step failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Execution timestamp")


class WorkflowRunResult(BaseModel):
    """Result of a complete workflow execution."""
    run_id: str = Field(..., description="Unique identifier for the workflow run")
    workflow_name: str = Field(..., description="Name of the workflow")
    workflow_version: str = Field(..., description="Version of the workflow")
    status: WorkflowStatus = Field(..., description="Overall workflow status")
    
    # Execution details
    started_at: datetime = Field(..., description="When the workflow started")
    completed_at: Optional[datetime] = Field(None, description="When the workflow completed")
    duration_ms: Optional[int] = Field(None, description="Total execution duration")
    
    # Step results
    step_outputs: Dict[str, StepResult] = Field(
        default_factory=dict, 
        description="Results from each step, keyed by step ID"
    )
    execution_order: List[str] = Field(
        default_factory=list,
        description="Order in which steps were executed"
    )
    
    # Error handling
    errors: List[str] = Field(default_factory=list, description="List of errors encountered")
    failed_step: Optional[str] = Field(None, description="ID of the step that caused failure")
    
    # Storage and metadata
    output_directory: Optional[str] = Field(None, description="Directory where outputs are stored")
    workflow_file: str = Field(..., description="Path to the workflow YAML file")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def to_summary(self) -> Dict[str, Any]:
        """Generate a concise summary of the workflow run."""
        return {
            "run_id": self.run_id,
            "workflow": f"{self.workflow_name} v{self.workflow_version}",
            "status": self.status.value,
            "duration_ms": self.duration_ms,
            "steps_completed": len([s for s in self.step_outputs.values() if s.status == "success"]),
            "steps_failed": len([s for s in self.step_outputs.values() if s.status == "error"]),
            "errors": len(self.errors),
            "output_directory": self.output_directory
        }
    
    def get_successful_outputs(self) -> Dict[str, Any]:
        """Get outputs from all successful steps."""
        return {
            step_id: step.result
            for step_id, step in self.step_outputs.items()
            if step.status == "success" and step.result
        }
    
    def get_step_by_name(self, name: str) -> Optional[StepResult]:
        """Get a step result by its name."""
        for step in self.step_outputs.values():
            if step.step_name == name:
                return step
        return None