"""
Workflow Engine V2 - Core execution service with dependency injection.

This is an updated version of WorkflowEngine that uses AgentRegistry
for dynamic agent discovery instead of hardcoded agents.
"""

import asyncio
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import yaml

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import models and registry
from interfaces.agent_models import AgentInput, AgentOutput
from interfaces.run_models import WorkflowRunResult, StepResult, WorkflowStatus
from core.agent_registry import registry, get_agent
from runner.workflow_loader import WorkflowLoader, WorkflowStep
from runner.workflow_storage import WorkflowStorage
from services.validation import validate_workflow_file, WorkflowValidationError


class WorkflowEngineV2:
    """Core workflow execution engine with dependency injection."""
    
    def __init__(self, storage_path: Optional[Path] = None, temp_path: Optional[Path] = None,
                 agent_registry=None):
        """Initialize the workflow engine.
        
        Args:
            storage_path: Path to content storage directory
            temp_path: Path to temporary files directory
            agent_registry: Optional agent registry instance (uses global if None)
        """
        self.storage_path = storage_path or Path("./data/knowledge")
        self.temp_path = temp_path or Path("./data/temp")
        self.workflow_storage = WorkflowStorage()
        
        # Use provided registry or global instance
        self.agent_registry = agent_registry or registry
        
        # Setup logging
        self.logger = logging.getLogger('workflow_engine_v2')
        
        # Store initial input if provided
        self.initial_input: Optional[Dict[str, Any]] = None
        
        # Initialize agent configuration
        self._agent_config = {
            'storage_path': self.storage_path,
            'temp_path': self.temp_path
        }
        
    def _get_agent(self, agent_id: str):
        """Get an agent from the registry with proper configuration.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Configured agent instance
            
        Raises:
            ValueError: If agent not found in registry
        """
        agent = self.agent_registry.get(agent_id)
        if not agent:
            raise ValueError(f"Agent '{agent_id}' not found in registry")
        
        # Apply configuration if agent supports it
        if hasattr(agent, 'storage_path') and not agent.storage_path:
            agent.storage_path = self._agent_config['storage_path']
        if hasattr(agent, 'temp_path') and not agent.temp_path:
            agent.temp_path = self._agent_config['temp_path']
            
        return agent
        
    def _load_step_input(self, step: WorkflowStep, step_outputs: Dict[str, StepResult]) -> Dict[str, Any]:
        """Load input data for a workflow step.
        
        Args:
            step: Step definition
            step_outputs: Results from previous steps
            
        Returns:
            Input data dictionary
            
        Raises:
            ValueError: If input data is invalid
        """
        # Check for input file
        if step.input_file:
            input_file = Path(step.input_file)
            if not input_file.exists():
                raise ValueError(f"Input file not found: {input_file}")
            
            with open(input_file) as f:
                input_data = json.load(f)
                
            # Special handling for PDF inputs
            if step.agent == 'ingestion_agent' and input_data.get('task_type') == 'pdf':
                pdf_path = input_data.get('content', {}).get('file_path')
                if pdf_path and Path(pdf_path).exists():
                    # Check file size before loading
                    file_size = Path(pdf_path).stat().st_size
                    max_size = 100 * 1024 * 1024  # 100MB limit
                    
                    if file_size > max_size:
                        raise ValueError(f"PDF file too large: {file_size} bytes (max: {max_size})")
                    
                    # For now, still load the whole file but with size limit
                    # TODO: Implement streaming for ingestion agent
                    with open(pdf_path, 'rb') as pdf_file:
                        input_data['content']['pdf_data'] = pdf_file.read()
                        input_data['content']['filename'] = Path(pdf_path).name
                        input_data['content']['file_size'] = file_size
                        
            return input_data
        
        # Check for input from previous step
        elif step.input_from:
            source_step = step.input_from
            if source_step not in step_outputs:
                raise ValueError(f"Source step output not found: {source_step}")
            
            # Create input from previous step's output
            source_output = step_outputs[source_step]
            if source_output.status != "success":
                raise ValueError(f"Source step failed: {source_step}")
                
            input_data = {
                'task_id': f"workflow-{step.id}",
                'source': 'workflow',
                'content': source_output.result or {},
                'metadata': source_output.metadata
            }
            
            # Add any additional configuration
            if step.config:
                input_data['content'].update(step.config)
            
            return input_data
        
        # Check for initial input (for first step without input_file or input_from)
        elif self.initial_input and len(step_outputs) == 0:
            return self.initial_input
        
        else:
            raise ValueError("Step must specify either input_file or input_from, or be the first step with initial_input")
    
    async def _execute_step(self, step: WorkflowStep, step_outputs: Dict[str, StepResult]) -> StepResult:
        """Execute a single workflow step.
        
        Args:
            step: Step definition
            step_outputs: Results from previous steps
            
        Returns:
            Step execution result
            
        Raises:
            ValueError: If step execution fails
        """
        start_time = datetime.utcnow()
        
        try:
            # Load input data
            input_data = self._load_step_input(step, step_outputs)
            
            # Get agent from registry
            agent = self._get_agent(step.agent)
            
            # Create agent input
            agent_input = AgentInput.model_validate(input_data)
            
            # Initialize agent if needed
            if hasattr(agent, 'initialize') and not getattr(agent, '_initialized', False):
                await agent.initialize()
            
            # Execute step
            self.logger.info(f"Executing step: {step.name} ({step.id}) with agent {step.agent}")
            agent_output = await agent.process(agent_input)
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Create step result
            step_result = StepResult(
                step_id=step.id,
                step_name=step.name,
                status=agent_output.status,
                duration_ms=duration_ms,
                result=agent_output.result,
                error=agent_output.error,
                metadata=agent_output.metadata,
                timestamp=start_time
            )
            
            # Log result
            if agent_output.status == "success":
                self.logger.info(f"Step completed successfully: {step.name}")
            else:
                self.logger.error(f"Step failed: {step.name} - {agent_output.error}")
            
            return step_result
            
        except Exception as e:
            self.logger.error(f"Error executing step {step.id}: {e}")
            
            # Calculate duration
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Return error result
            return StepResult(
                step_id=step.id,
                step_name=step.name,
                status="error",
                duration_ms=duration_ms,
                error=str(e),
                timestamp=start_time
            )
    
    async def execute_workflow(self, workflow_path: Path, persist: bool = True, 
                             initial_input: Optional[Dict[str, Any]] = None,
                             on_complete: Optional[callable] = None) -> WorkflowRunResult:
        """Execute a workflow from a YAML file.
        
        Args:
            workflow_path: Path to workflow YAML file
            persist: Whether to persist outputs to disk
            initial_input: Optional initial input data for the first step
            on_complete: Optional async callback function to call after successful completion
            
        Returns:
            WorkflowRunResult with execution details
            
        Raises:
            ValueError: If workflow execution fails
        """
        # Store initial input
        self.initial_input = initial_input
        # Start execution
        start_time = datetime.utcnow()
        run_id = str(uuid.uuid4())
        
        try:
            # Validate workflow file for security
            is_valid, error_msg = validate_workflow_file(workflow_path)
            if not is_valid:
                raise WorkflowValidationError(f"Workflow validation failed: {error_msg}")
            
            # Load and validate workflow
            loader = WorkflowLoader(workflow_path)
            workflow_data = loader.load()
            steps = loader.parse_steps()
            
            # Get workflow info
            workflow_info = workflow_data['workflow']
            workflow_name = workflow_info['name']
            workflow_version = workflow_info['version']
            
            self.logger.info(f"Starting workflow: {workflow_name} (v{workflow_version})")
            self.logger.info(f"Run ID: {run_id}")
            
            # Initialize result
            result = WorkflowRunResult(
                run_id=run_id,
                workflow_name=workflow_name,
                workflow_version=workflow_version,
                status=WorkflowStatus.RUNNING,
                started_at=start_time,
                workflow_file=str(workflow_path)
            )
            
            # Create output directory if persisting
            if persist:
                workflow_id = workflow_name.lower().replace(' ', '_')
                run_dir = self.workflow_storage.create_run_directory(workflow_id, use_uuid=True)
                result.output_directory = str(run_dir)
                
                # Save workflow definition
                import yaml
                workflow_yaml = yaml.dump(workflow_data)
                self.workflow_storage.save_workflow_definition(
                    run_dir, workflow_yaml
                )
                
                # Save initial metadata
                self.workflow_storage.save_run_metadata(
                    run_dir, {
                        'workflow_name': workflow_name,
                        'version': workflow_version,
                        'timestamp': start_time.isoformat(),
                        'status': 'running',
                        'run_id': run_id
                    }
                )
            
            # Get execution order
            execution_order = loader.get_execution_order()
            result.execution_order = execution_order
            
            # Execute steps in order
            step_outputs = {}
            for step_id in execution_order:
                step = loader.step_map[step_id]
                
                # Execute step
                step_result = await self._execute_step(step, step_outputs)
                step_outputs[step_id] = step_result
                result.step_outputs[step_id] = step_result
                
                # Save step output if persisting
                if persist:
                    self.workflow_storage.save_step_output(
                        run_dir, step_id, {
                            'step_id': step_id,
                            'status': step_result.status,
                            'timestamp': step_result.timestamp.isoformat(),
                            'result': step_result.result,
                            'error': step_result.error,
                            'duration_ms': step_result.duration_ms
                        }
                    )
                
                # Check for failure
                if step_result.status == "error":
                    result.status = WorkflowStatus.FAILED
                    result.failed_step = step_id
                    result.errors.append(f"Step {step_id} failed: {step_result.error}")
                    break
            
            # Set completion status
            if result.status == WorkflowStatus.RUNNING:
                result.status = WorkflowStatus.SUCCESS
            
            # Set completion time and duration
            end_time = datetime.utcnow()
            result.completed_at = end_time
            result.duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Save final metadata if persisting
            if persist:
                metadata = {
                    'workflow_name': workflow_name,
                    'version': workflow_version,
                    'timestamp': start_time.isoformat(),
                    'completed_at': end_time.isoformat(),
                    'status': result.status.value,
                    'duration_ms': result.duration_ms,
                    'steps_completed': len([s for s in result.step_outputs.values() if s.status == "success"]),
                    'steps_failed': len([s for s in result.step_outputs.values() if s.status == "error"]),
                    'run_id': run_id
                }
                
                # Save run metadata
                self.workflow_storage.save_run_metadata(run_dir, metadata)
                
                # Extract summary from last successful step
                summary = ""
                tags = []
                source = {}
                
                for step_id in reversed(result.execution_order or []):
                    step_result = result.step_outputs.get(step_id)
                    if step_result and step_result.status == "success" and step_result.result:
                        # Extract summary/digest
                        summary = step_result.result.get('digest', 
                                 step_result.result.get('summary', 
                                 step_result.result.get('content', '')[:200]))
                        # Extract tags
                        tags = step_result.result.get('tags', [])
                        # Extract source info
                        source = step_result.result.get('metadata', {}).get('source', {})
                        break
                
                # Add to archive
                archive_metadata = {
                    **metadata,
                    'summary': summary,
                    'tags': tags,
                    'source': source
                }
                self.workflow_storage.add_to_archive(workflow_id, run_id, archive_metadata)
            
            self.logger.info(f"Workflow completed with status: {result.status.value}")
            
            # Call post-execution hook if provided and workflow succeeded
            if on_complete and result.status == WorkflowStatus.SUCCESS:
                try:
                    await on_complete(result)
                    self.logger.info("Post-execution hook completed successfully")
                except Exception as e:
                    # Log error but don't fail the workflow
                    self.logger.error(f"Post-execution hook failed: {e}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            
            # Create error result
            end_time = datetime.utcnow()
            return WorkflowRunResult(
                run_id=run_id,
                workflow_name=workflow_info.get('name', 'Unknown') if 'workflow_info' in locals() else 'Unknown',
                workflow_version=workflow_info.get('version', '0.0.0') if 'workflow_info' in locals() else '0.0.0',
                status=WorkflowStatus.FAILED,
                started_at=start_time,
                completed_at=end_time,
                duration_ms=int((end_time - start_time).total_seconds() * 1000),
                workflow_file=str(workflow_path),
                errors=[str(e)]
            )


# Public API function with dependency injection
async def run_workflow_v2(path: str, persist: bool = True, storage_path: Optional[str] = None, 
                         temp_path: Optional[str] = None, initial_input: Optional[Dict[str, Any]] = None,
                         on_complete: Optional[callable] = None) -> WorkflowRunResult:
    """Execute a workflow from a YAML file using dependency injection.
    
    This is the updated public API that uses AgentRegistry.
    
    Args:
        path: Path to the workflow YAML file
        persist: Whether to persist outputs to disk (default: True)
        storage_path: Optional path to content storage directory
        temp_path: Optional path to temporary files directory
        initial_input: Optional initial input data for the first step
        on_complete: Optional async callback function to call after successful completion
        
    Returns:
        WorkflowRunResult containing execution details
        
    Example:
        >>> # First register agents
        >>> from core.agent_registry import register_agent
        >>> from agents.ingestion_agent import IngestionAgent
        >>> from agents.digest_agent import DigestAgent
        >>> 
        >>> register_agent('ingestion_agent', IngestionAgent)
        >>> register_agent('digest_agent', DigestAgent)
        >>> 
        >>> # Then run workflow
        >>> result = await run_workflow_v2('workflows/sample_ingestion_digest.yaml')
        >>> print(result.status)
        WorkflowStatus.SUCCESS
    """
    # Create engine
    engine = WorkflowEngineV2(
        storage_path=Path(storage_path) if storage_path else None,
        temp_path=Path(temp_path) if temp_path else None
    )
    
    # Execute workflow
    return await engine.execute_workflow(Path(path), persist=persist, initial_input=initial_input, on_complete=on_complete)