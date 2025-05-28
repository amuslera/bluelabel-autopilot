"""
Unified Workflow Engine - Adapter for multiple workflow execution engines.

This module provides a unified interface that can delegate to either the
WorkflowEngine or StatefulDAGRunner based on configuration or feature flags.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, Callable, Union
from pathlib import Path
from datetime import datetime
from enum import Enum

from interfaces.workflow_engine_interface import IWorkflowEngine
from interfaces.run_models import WorkflowRunResult, StepResult, WorkflowStatus
from core.workflow_engine import WorkflowEngine
from services.workflow.dag_runner import StatefulDAGRunner, DAGRunnerFactory
from services.workflow.dag_run_tracker import DAGRunStatus, DAGStepStatus
from runner.workflow_loader import WorkflowLoader


logger = logging.getLogger(__name__)


class EngineType(Enum):
    """Available workflow engine implementations."""
    SEQUENTIAL = "sequential"  # Original WorkflowEngine
    STATEFUL_DAG = "stateful_dag"  # StatefulDAGRunner


class UnifiedWorkflowEngine(IWorkflowEngine):
    """
    Unified adapter for workflow execution engines.
    
    This adapter implements the strategy pattern to delegate workflow execution
    to different underlying engines based on configuration.
    """
    
    def __init__(
        self,
        engine_type: Optional[EngineType] = None,
        storage_path: Optional[Path] = None,
        temp_path: Optional[Path] = None,
        **engine_kwargs
    ):
        """
        Initialize the unified workflow engine.
        
        Args:
            engine_type: Type of engine to use (defaults to env var or SEQUENTIAL)
            storage_path: Path to content storage directory
            temp_path: Path to temporary files directory
            **engine_kwargs: Additional engine-specific configuration
        """
        # Determine engine type from env var if not specified
        if engine_type is None:
            env_engine = os.getenv('WORKFLOW_ENGINE_TYPE', 'sequential')
            try:
                engine_type = EngineType(env_engine)
            except ValueError:
                logger.warning(f"Invalid engine type '{env_engine}', using SEQUENTIAL")
                engine_type = EngineType.SEQUENTIAL
        
        self.engine_type = engine_type
        self.storage_path = storage_path or Path("./data/knowledge")
        self.temp_path = temp_path or Path("./data/temp")
        self.engine_kwargs = engine_kwargs
        
        # Track execution for performance monitoring
        self._execution_start_time: Optional[datetime] = None
        self._current_run_id: Optional[str] = None
        
        # Initialize the appropriate engine
        self._engine: Optional[Union[WorkflowEngine, StatefulDAGRunner]] = None
        self._initialize_engine()
        
        logger.info(f"UnifiedWorkflowEngine initialized with {self.engine_type.value} engine")
    
    def _initialize_engine(self):
        """Initialize the underlying workflow engine based on type."""
        if self.engine_type == EngineType.SEQUENTIAL:
            self._engine = WorkflowEngine(
                storage_path=self.storage_path,
                temp_path=self.temp_path
            )
        elif self.engine_type == EngineType.STATEFUL_DAG:
            # StatefulDAGRunner is initialized per workflow execution
            # So we don't create it here
            self._engine = None
        else:
            raise ValueError(f"Unsupported engine type: {self.engine_type}")
    
    async def execute_workflow(
        self,
        workflow_path: Path,
        persist: bool = True,
        initial_input: Optional[Dict[str, Any]] = None,
        on_complete: Optional[Callable] = None,
        **kwargs
    ) -> WorkflowRunResult:
        """
        Execute a workflow using the configured engine.
        
        Args:
            workflow_path: Path to workflow YAML file
            persist: Whether to persist outputs to disk
            initial_input: Optional initial input data for the first step
            on_complete: Optional async callback function to call after successful completion
            **kwargs: Additional engine-specific parameters
            
        Returns:
            WorkflowRunResult with execution details
        """
        self._execution_start_time = datetime.utcnow()
        
        # Log which engine is being used
        logger.info(f"Executing workflow '{workflow_path}' with {self.engine_type.value} engine")
        
        try:
            if self.engine_type == EngineType.SEQUENTIAL:
                # Use original WorkflowEngine
                result = await self._engine.execute_workflow(
                    workflow_path=workflow_path,
                    persist=persist,
                    initial_input=initial_input,
                    on_complete=on_complete
                )
                self._current_run_id = result.run_id
                
            elif self.engine_type == EngineType.STATEFUL_DAG:
                # Use StatefulDAGRunner with adapter
                result = await self._execute_with_stateful_dag(
                    workflow_path=workflow_path,
                    persist=persist,
                    initial_input=initial_input,
                    on_complete=on_complete,
                    **kwargs
                )
                self._current_run_id = result.run_id
            
            else:
                raise ValueError(f"Unsupported engine type: {self.engine_type}")
            
            # Calculate and log performance overhead
            execution_end_time = datetime.utcnow()
            overhead_ms = int((execution_end_time - self._execution_start_time).total_seconds() * 1000) - result.duration_ms
            logger.info(f"Workflow execution completed with {overhead_ms}ms adapter overhead")
            
            # Verify performance requirement (<100ms overhead)
            if overhead_ms > 100:
                logger.warning(f"Performance overhead {overhead_ms}ms exceeds 100ms target")
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise
    
    async def _execute_with_stateful_dag(
        self,
        workflow_path: Path,
        persist: bool = True,
        initial_input: Optional[Dict[str, Any]] = None,
        on_complete: Optional[Callable] = None,
        run_id: Optional[str] = None,
        **kwargs
    ) -> WorkflowRunResult:
        """
        Execute workflow using StatefulDAGRunner with adapter logic.
        
        This method adapts the StatefulDAGRunner to work with the WorkflowRunResult
        interface expected by the rest of the system.
        """
        # Load workflow definition
        loader = WorkflowLoader(workflow_path)
        workflow_data = loader.load()
        steps = loader.parse_steps()
        workflow_info = workflow_data['workflow']
        
        # Create DAG runner
        dag_id = workflow_info['name'].lower().replace(' ', '_')
        runner = DAGRunnerFactory.create_runner(
            dag_id=dag_id,
            run_id=run_id  # Support resuming if run_id provided
        )
        
        # Register step executors
        # We need to create executors that bridge to our agents
        from interfaces.agent_models import AgentInput
        from agents.digest_agent import DigestAgent
        from agents.ingestion_agent import IngestionAgent
        
        # Initialize agents
        agents = {
            'ingestion_agent': IngestionAgent(
                storage_path=self.storage_path,
                temp_path=self.temp_path
            ),
            'digest_agent': DigestAgent()
        }
        
        # Track step outputs for dependencies
        step_outputs = {}
        
        # Create executor for each step
        for step in steps:
            async def make_executor(step_def, stored_outputs, stored_initial_input):
                """Create a closure for step execution."""
                async def execute_step():
                    # Prepare input based on step configuration
                    if step_def.input_file:
                        # Load from file
                        import json
                        with open(step_def.input_file) as f:
                            input_data = json.load(f)
                    elif step_def.input_from:
                        # Get from previous step
                        if step_def.input_from not in stored_outputs:
                            raise ValueError(f"Dependency step {step_def.input_from} not found")
                        prev_result = stored_outputs[step_def.input_from]
                        input_data = {
                            'task_id': f"workflow-{step_def.id}",
                            'source': 'workflow',
                            'content': prev_result.result or {},
                            'metadata': prev_result.metadata
                        }
                        if step_def.config:
                            input_data['content'].update(step_def.config)
                    elif stored_initial_input and len(stored_outputs) == 0:
                        # Use initial input for first step
                        input_data = stored_initial_input
                    else:
                        raise ValueError("Step must specify input source")
                    
                    # Get agent
                    agent = agents.get(step_def.agent)
                    if not agent:
                        raise ValueError(f"Unknown agent: {step_def.agent}")
                    
                    # Create agent input and execute
                    agent_input = AgentInput.model_validate(input_data)
                    
                    # Initialize agent if needed
                    if hasattr(agent, 'initialize') and not getattr(agent, '_initialized', False):
                        await agent.initialize()
                    
                    agent_output = await agent.process(agent_input)
                    
                    # Store output for dependencies
                    stored_outputs[step_def.id] = StepResult(
                        step_id=step_def.id,
                        step_name=step_def.name,
                        status=agent_output.status,
                        result=agent_output.result,
                        error=agent_output.error,
                        metadata=agent_output.metadata,
                        timestamp=datetime.utcnow(),
                        duration_ms=0  # Will be calculated by runner
                    )
                    
                    if agent_output.status != "success":
                        raise RuntimeError(f"Step failed: {agent_output.error}")
                    
                    return agent_output.result
                
                return execute_step
            
            # Register the executor
            executor = await make_executor(step, step_outputs, initial_input)
            runner.register_step(
                step_id=step.id,
                executor=executor,
                max_retries=kwargs.get('max_retries', 3),
                retry_delay=kwargs.get('retry_delay', 1.0),
                critical=kwargs.get('critical', True)
            )
        
        # Execute the DAG
        execution_order = loader.get_execution_order()
        dag_run = await runner.execute(step_order=execution_order)
        
        # Convert DAGRun to WorkflowRunResult
        result = self._convert_dag_run_to_result(
            dag_run=dag_run,
            workflow_info=workflow_info,
            workflow_path=workflow_path,
            step_outputs=step_outputs
        )
        
        # Handle persistence if needed
        if persist:
            # The StatefulDAGRunner already persists its state
            # We just need to ensure compatibility with existing storage
            result.output_directory = f"./data/workflows/{dag_id}/{dag_run.run_id}"
        
        # Call completion callback if provided and successful
        if on_complete and result.status == WorkflowStatus.SUCCESS:
            try:
                await on_complete(result)
            except Exception as e:
                logger.error(f"Completion callback failed: {e}")
        
        return result
    
    def _convert_dag_run_to_result(
        self,
        dag_run,
        workflow_info: Dict[str, Any],
        workflow_path: Path,
        step_outputs: Dict[str, StepResult]
    ) -> WorkflowRunResult:
        """Convert DAGRun to WorkflowRunResult for compatibility."""
        # Map DAG status to workflow status
        status_map = {
            DAGRunStatus.SUCCESS: WorkflowStatus.SUCCESS,
            DAGRunStatus.FAILED: WorkflowStatus.FAILED,
            DAGRunStatus.RUNNING: WorkflowStatus.RUNNING,
            DAGRunStatus.CANCELLED: WorkflowStatus.FAILED,
            DAGRunStatus.PARTIAL_SUCCESS: WorkflowStatus.FAILED,
        }
        
        # Build step outputs with proper timing
        for step_id, step_state in dag_run.steps.items():
            if step_id in step_outputs:
                # Update with actual timing from DAG runner
                step_result = step_outputs[step_id]
                step_result.duration_ms = int(step_state.duration_seconds * 1000) if step_state.duration_seconds else 0
                step_result.timestamp = step_state.start_time or datetime.utcnow()
        
        # Find failed step if any
        failed_step = None
        errors = []
        for step_id, step_state in dag_run.steps.items():
            if step_state.status == DAGStepStatus.FAILED:
                failed_step = step_id
                if step_state.error:
                    errors.append(f"Step {step_id} failed: {step_state.error}")
        
        return WorkflowRunResult(
            run_id=dag_run.run_id,
            workflow_name=workflow_info['name'],
            workflow_version=workflow_info['version'],
            status=status_map.get(dag_run.status, WorkflowStatus.FAILED),
            started_at=dag_run.start_time or datetime.utcnow(),
            completed_at=dag_run.end_time,
            duration_ms=int(dag_run.duration_seconds * 1000) if dag_run.duration_seconds else 0,
            workflow_file=str(workflow_path),
            step_outputs=step_outputs,
            execution_order=list(step_outputs.keys()),
            failed_step=failed_step,
            errors=errors
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        status = {
            'engine_type': self.engine_type.value,
            'current_run_id': self._current_run_id,
            'supports_resume': self.supports_resume,
            'supports_parallel': self.supports_parallel_execution
        }
        
        if self.engine_type == EngineType.STATEFUL_DAG and hasattr(self._engine, 'get_status'):
            # Include DAG-specific status
            status['dag_status'] = self._engine.get_status()
        
        return status
    
    @property
    def supports_resume(self) -> bool:
        """Whether this engine supports resuming from failure."""
        return self.engine_type == EngineType.STATEFUL_DAG
    
    @property
    def supports_parallel_execution(self) -> bool:
        """Whether this engine supports parallel step execution."""
        # Currently neither engine truly supports parallel execution
        # This is a placeholder for future enhancement
        return False


# Factory function for creating unified engine
def create_unified_engine(
    engine_type: Optional[Union[str, EngineType]] = None,
    **kwargs
) -> UnifiedWorkflowEngine:
    """
    Create a unified workflow engine instance.
    
    Args:
        engine_type: Type of engine to use (string or EngineType enum)
        **kwargs: Additional engine configuration
        
    Returns:
        UnifiedWorkflowEngine instance
    """
    if isinstance(engine_type, str):
        engine_type = EngineType(engine_type)
    
    return UnifiedWorkflowEngine(engine_type=engine_type, **kwargs)