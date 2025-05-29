"""
Unified Workflow Adapter - Bridges WorkflowEngine and DAGRunner

This adapter provides a single interface for workflow execution that combines
the YAML-based WorkflowEngine with the stateful DAGRunner for persistent
execution tracking.
"""

import asyncio
import json
import uuid
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import hashlib

from core.workflow_engine import WorkflowEngine
from services.workflow.dag_runner import StatefulDAGRunner
from services.workflow.dag_run_tracker import DAGRun, DAGStepState, DAGStepStatus, DAGRunStatus
from services.workflow.dag_run_store import DAGRunStore
from runner.workflow_loader import WorkflowLoader, WorkflowStep
from interfaces.run_models import WorkflowRunResult, StepResult, WorkflowStatus
from interfaces.agent_models import AgentInput, AgentOutput
from core.agent_registry import get_agent
from core.performance_cache import workflow_cache, cached, performance_monitor

logger = logging.getLogger(__name__)


class UnifiedWorkflowAdapter:
    """Bridges WorkflowEngine and DAGRunner for unified execution."""
    
    def __init__(self, 
                 storage_path: Optional[Path] = None,
                 temp_path: Optional[Path] = None,
                 dag_store: Optional[DAGRunStore] = None):
        """
        Initialize the unified adapter.
        
        Args:
            storage_path: Path to content storage directory
            temp_path: Path to temporary files directory
            dag_store: DAGRunStore instance for persistence
        """
        self.storage_path = storage_path or Path("./data/knowledge")
        self.temp_path = temp_path or Path("./data/temp")
        self.dag_store = dag_store or DAGRunStore(storage_path="data/workflows")
        
        # Initialize workflow engine
        self.workflow_engine = WorkflowEngine(
            storage_path=self.storage_path,
            temp_path=self.temp_path
        )
        
        # Track active runners
        self._active_runners: Dict[str, StatefulDAGRunner] = {}
        
        logger.info("UnifiedWorkflowAdapter initialized")
    
    async def run_workflow(self, 
                          workflow_name: str, 
                          inputs: Dict[str, Any],
                          workflow_yaml: Optional[str] = None) -> str:
        """
        Execute a workflow using the unified system.
        
        Args:
            workflow_name: Name of the workflow to execute
            inputs: Input parameters for the workflow
            workflow_yaml: Optional YAML content (if not loading from file)
            
        Returns:
            run_id: Unique identifier for tracking this execution
        """
        run_id = str(uuid.uuid4())
        logger.info(f"Starting unified workflow execution: {workflow_name} (run_id: {run_id})")
        
        try:
            with performance_monitor.measure("workflow_run_total"):
                # Load workflow definition with caching
                with performance_monitor.measure("workflow_loading"):
                    if workflow_yaml:
                        # Hash the YAML for caching
                        yaml_hash = hashlib.md5(workflow_yaml.encode()).hexdigest()
                        cache_key = f"workflow_def_{yaml_hash}"
                        
                        workflow_def = workflow_cache.get(cache_key)
                        if workflow_def is None:
                            workflow_def = yaml.safe_load(workflow_yaml)
                            workflow_cache.set(cache_key, workflow_def)
                    else:
                        # Cache loaded workflows by name
                        cache_key = f"workflow_file_{workflow_name}"
                        workflow_def = workflow_cache.get(cache_key)
                        
                        if workflow_def is None:
                            loader = WorkflowLoader()
                            workflow_def = loader.load_workflow(workflow_name)
                            workflow_cache.set(cache_key, workflow_def)
            
            # Create DAGRun for tracking
            dag_run = DAGRun(
                run_id=run_id,
                dag_id=workflow_name,
                metadata={
                    "workflow_version": workflow_def.get("version", "1.0.0"),
                    "description": workflow_def.get("description", ""),
                    "inputs": inputs,
                    "workflow_def": workflow_def  # Store for later reference
                }
            )
            
            # Add steps to DAGRun
            for step in workflow_def.get("steps", []):
                dag_run.add_step(
                    step_id=step["name"],
                    max_retries=step.get("retry_count", 3)
                )
            
            # Store the DAGRun first
            self.dag_store.create(dag_run)
            
            # Create DAG runner with existing run_id
            runner = StatefulDAGRunner(
                dag_id=workflow_name,
                store=self.dag_store,
                run_id=run_id
            )
            
            # Store runner for status queries
            self._active_runners[run_id] = runner
            
            # Execute workflow asynchronously
            asyncio.create_task(self._execute_workflow(
                runner, workflow_def, inputs, run_id
            ))
            
            return run_id
            
        except Exception as e:
            logger.error(f"Failed to start workflow: {e}")
            raise
    
    async def _execute_workflow(self, 
                               runner: StatefulDAGRunner,
                               workflow_def: dict,
                               inputs: Dict[str, Any],
                               run_id: str):
        """Execute the workflow using the DAG runner."""
        try:
            # Set up shared context for all steps
            context = {"inputs": inputs, **inputs}
            
            # Extract step configurations from DAG
            step_configs = {}
            for step in workflow_def.get("steps", []):
                step_configs[step["name"]] = step
            
            # Register each step with the runner
            for step_name in runner.dag_run.steps:
                step_config = step_configs.get(step_name, {})
                
                # Create step executor closure
                async def make_step_executor(name: str, config: dict):
                    """Create a step executor for the given step."""
                    async def execute_step() -> Any:
                        """Execute a single workflow step using the appropriate agent."""
                        agent_type = config.get("agent", "")
                        step_input = config.get("input", {})
                        output_name = config.get("output", "")
                        
                        # Resolve input variables from context
                        resolved_input = self._resolve_variables(step_input, context)
                        
                        # Get agent from registry
                        try:
                            agent = get_agent(agent_type)
                        except ValueError:
                            # Try legacy agent names
                            agent_type_map = {
                                'ingestion_agent': 'ingestion',
                                'digest_agent': 'digest'
                            }
                            mapped_type = agent_type_map.get(agent_type)
                            if mapped_type:
                                agent = get_agent(mapped_type)
                            else:
                                raise ValueError(f"Unknown agent type: {agent_type}")
                        
                        # Create agent input
                        agent_input = AgentInput(
                            task_id=f"{run_id}_{name}",
                            source="workflow",
                            data=resolved_input
                        )
                        
                        # Execute agent
                        logger.info(f"Executing step {name} with agent {agent_type}")
                        
                        # Initialize agent if needed
                        if hasattr(agent, 'initialize') and not hasattr(agent, '_initialized'):
                            await agent.initialize()
                            agent._initialized = True
                        
                        # Process the input
                        result = await agent.process(agent_input)
                        
                        # Store output in context
                        if output_name:
                            context[output_name] = result.result
                        
                        return result.result
                    
                    return execute_step
                
                # Register the step with its executor
                executor = await make_step_executor(step_name, step_config)
                runner.register_step(
                    step_id=step_name,
                    executor=executor,
                    max_retries=step_config.get("retry_count", 3),
                    retry_delay=1.0,
                    critical=True
                )
            
            # Determine execution order based on dependencies
            step_order = self._topological_sort(workflow_def.get("steps", []))
            
            # Execute the DAG
            result = await runner.execute(step_order=step_order)
            
            logger.info(f"Workflow {run_id} completed with status: {result.status}")
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            # DAGRunner handles its own state persistence on failure
            # But we need to update the error if it's not already set
            if not runner.dag_run.error:
                runner.dag_run.error = str(e)
                self.dag_store.update(runner.dag_run)
            raise
        finally:
            # Clean up runner reference
            if run_id in self._active_runners:
                del self._active_runners[run_id]
    
    def _topological_sort(self, steps: List[dict]) -> List[str]:
        """Sort steps topologically based on dependencies."""
        # Build dependency graph
        graph = {}
        in_degree = {}
        
        for step in steps:
            step_name = step["name"]
            graph[step_name] = []
            in_degree[step_name] = 0
        
        # Add edges based on dependencies
        for step in steps:
            step_name = step["name"]
            
            # Check for explicit dependencies
            if "depends_on" in step:
                for dep in step["depends_on"]:
                    if dep in graph:
                        graph[dep].append(step_name)
                        in_degree[step_name] += 1
            
            # Check for implicit dependencies via variable references
            if "input" in step:
                input_str = str(step["input"])
                import re
                refs = re.findall(r'\{\{(\w+)\}\}', input_str)
                
                for ref in refs:
                    for other_step in steps:
                        if other_step.get("output") == ref:
                            dep_name = other_step["name"]
                            if dep_name in graph and dep_name != step_name:
                                graph[dep_name].append(step_name)
                                in_degree[step_name] += 1
        
        # Perform topological sort
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            
            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(result) != len(steps):
            raise ValueError("Workflow contains circular dependencies")
        
        return result
    
    def _resolve_variables(self, input_data: Any, context: dict) -> Any:
        """Resolve {{variable}} references in input data."""
        if isinstance(input_data, str):
            # Replace {{var}} patterns with values from context
            import re
            def replacer(match):
                var_name = match.group(1)
                return str(context.get(var_name, match.group(0)))
            
            return re.sub(r'\{\{(\w+)\}\}', replacer, input_data)
        
        elif isinstance(input_data, dict):
            return {k: self._resolve_variables(v, context) for k, v in input_data.items()}
        
        elif isinstance(input_data, list):
            return [self._resolve_variables(item, context) for item in input_data]
        
        return input_data
    
    def get_run_status(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a workflow run."""
        dag_run = self.dag_store.get(run_id)
        if not dag_run:
            return None
        
        return {
            "run_id": run_id,
            "dag_id": dag_run.dag_id,
            "status": dag_run.status.value,
            "started_at": dag_run.start_time.isoformat() if dag_run.start_time else datetime.utcnow().isoformat(),
            "updated_at": dag_run.end_time.isoformat() if dag_run.end_time else datetime.utcnow().isoformat(),
            "steps": {
                name: {
                    "status": step.status.value,
                    "started_at": step.start_time.isoformat() if step.start_time else None,
                    "completed_at": step.end_time.isoformat() if step.end_time else None,
                    "retry_count": step.retry_count,
                    "error": step.error
                }
                for name, step in dag_run.steps.items()
            },
            "error": dag_run.error
        }
    
    def list_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent workflow runs."""
        runs = self.dag_store.list_runs(limit=limit)
        return runs  # DAGRunStore already returns dict format
    
    async def resume_workflow(self, run_id: str) -> bool:
        """Resume a paused or failed workflow."""
        dag_run = self.dag_store.get(run_id)
        if not dag_run:
            logger.error(f"Cannot resume: DAGRun {run_id} not found")
            return False
        
        if dag_run.status not in [DAGRunStatus.PAUSED, DAGRunStatus.FAILED]:
            logger.warning(f"Cannot resume workflow in status: {dag_run.status}")
            return False
        
        # Create new runner for resumed execution
        runner = StatefulDAGRunner(
            dag_id=dag_run.dag_id,
            store=self.dag_store,
            run_id=run_id
        )
        
        # Load workflow definition from metadata or file
        workflow_def = dag_run.metadata.get("workflow_def")
        if not workflow_def:
            loader = WorkflowLoader()
            workflow_def = loader.load_workflow(dag_run.dag_id)
        
        # Resume execution
        asyncio.create_task(self._execute_workflow(
            runner, workflow_def, dag_run.metadata.get("inputs", {}), run_id
        ))
        
        return True