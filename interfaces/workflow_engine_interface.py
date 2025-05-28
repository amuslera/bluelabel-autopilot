"""
Workflow Engine Interface - Common interface for workflow execution engines.

This module defines the interface that all workflow engines must implement,
enabling the UnifiedWorkflowEngine to delegate to different implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from datetime import datetime

from interfaces.run_models import WorkflowRunResult


class IWorkflowEngine(ABC):
    """Interface for workflow execution engines."""
    
    @abstractmethod
    async def execute_workflow(
        self,
        workflow_path: Path,
        persist: bool = True,
        initial_input: Optional[Dict[str, Any]] = None,
        on_complete: Optional[Callable] = None,
        **kwargs
    ) -> WorkflowRunResult:
        """
        Execute a workflow from a YAML file.
        
        Args:
            workflow_path: Path to workflow YAML file
            persist: Whether to persist outputs to disk
            initial_input: Optional initial input data for the first step
            on_complete: Optional async callback function to call after successful completion
            **kwargs: Additional engine-specific parameters
            
        Returns:
            WorkflowRunResult with execution details
            
        Raises:
            ValueError: If workflow execution fails
        """
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """
        Get current execution status.
        
        Returns:
            Dictionary containing current status information
        """
        pass
    
    @property
    @abstractmethod
    def supports_resume(self) -> bool:
        """Whether this engine supports resuming from failure."""
        pass
    
    @property
    @abstractmethod
    def supports_parallel_execution(self) -> bool:
        """Whether this engine supports parallel step execution."""
        pass