"""
Abstract interface for DAG runners.

This module provides the base interface and contracts for DAG execution,
allowing different implementations while maintaining consistent behavior.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Callable

from .dag_run_tracker import DAGRun


class DAGRunnerInterface(ABC):
    """Abstract base class for DAG runners."""

    @property
    @abstractmethod
    def run_id(self) -> str:
        """Get the current run ID."""
        pass

    @property
    @abstractmethod
    def dag_id(self) -> str:
        """Get the DAG ID."""
        pass

    @abstractmethod
    def register_step(self, step_id: str, executor: Callable, max_retries: int = 3):
        """
        Register a step executor.
        
        Args:
            step_id: Unique step identifier
            executor: Async callable to execute the step
            max_retries: Maximum retry attempts
        """
        pass

    @abstractmethod
    async def execute(self, step_order: Optional[List[str]] = None) -> DAGRun:
        """
        Execute the DAG.
        
        Args:
            step_order: Optional execution order for steps

        Returns:
            DAGRun instance with execution results
        """
        pass

    @abstractmethod
    async def cancel(self):
        """Cancel the DAG execution."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        pass


class StepExecutor(ABC):
    """Abstract base class for step executors."""

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the step.
        
        Args:
            context: Execution context with inputs and configuration

        Returns:
            Step execution results
        """
        pass

    @abstractmethod
    def validate_inputs(self, context: Dict[str, Any]) -> bool:
        """
        Validate step inputs.
        
        Args:
            context: Execution context

        Returns:
            True if inputs are valid
        """
        pass


class DAGDefinition:
    """Represents a DAG definition with steps and dependencies."""

    def __init__(self, dag_id: str, name: str, description: str = ""):
        """
        Initialize DAG definition.
        
        Args:
            dag_id: Unique DAG identifier
            name: Human-readable DAG name
            description: DAG description
        """
        self.dag_id = dag_id
        self.name = name
        self.description = description
        self.steps: Dict[str, StepDefinition] = {}
        self.dependencies: Dict[str, List[str]] = {}

    def add_step(self, step: 'StepDefinition'):
        """Add a step to the DAG."""
        self.steps[step.step_id] = step

    def add_dependency(self, step_id: str, depends_on: List[str]):
        """Add step dependencies."""
        self.dependencies[step_id] = depends_on

    def get_execution_order(self) -> List[str]:
        """
        Get topologically sorted execution order.

        Returns:
            List of step IDs in execution order
        """
        # Simple topological sort (assumes no cycles)
        visited = set()
        order = []

        def visit(step_id: str):
            if step_id in visited:
                return
            visited.add(step_id)

            # Visit dependencies first
            for dep in self.dependencies.get(step_id, []):
                visit(dep)

            order.append(step_id)

        # Visit all steps
        for step_id in self.steps:
            visit(step_id)

        return order


class StepDefinition:
    """Represents a step definition within a DAG."""

    def __init__(self,
                 step_id: str,
                 name: str,
                 executor_class: str,
                 config: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 critical: bool = True):
        """
        Initialize step definition.
        
        Args:
            step_id: Unique step identifier
            name: Human-readable step name
            executor_class: Class name of the step executor
            config: Step configuration
            max_retries: Maximum retry attempts
            critical: Whether step failure should fail the entire DAG
        """
        self.step_id = step_id
        self.name = name
        self.executor_class = executor_class
        self.config = config or {}
        self.max_retries = max_retries
        self.critical = critical