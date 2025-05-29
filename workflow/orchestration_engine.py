#!/usr/bin/env python3
"""
Advanced Workflow Orchestration Engine

Sophisticated workflow engine for complex multi-agent orchestration with conditional logic,
parallel execution, dependency resolution, monitoring, and automatic rollback mechanisms.
"""

import asyncio
import json
import threading
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Set, Union
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import copy
import time


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ExecutionMode(Enum):
    """Task execution mode"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


@dataclass
class TaskCondition:
    """Conditional logic for task execution"""
    type: str  # "dependency", "expression", "custom"
    expression: str  # Boolean expression or dependency specification
    params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowTask:
    """Individual task within a workflow"""
    id: str
    name: str
    agent_id: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    conditions: List[TaskCondition] = field(default_factory=list)
    timeout_seconds: int = 3600
    retry_count: int = 3
    retry_delay: int = 5
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL


@dataclass
class WorkflowCheckpoint:
    """Workflow state checkpoint for rollback"""
    checkpoint_id: str
    workflow_id: str
    timestamp: datetime
    task_states: Dict[str, Dict[str, Any]]
    workflow_state: Dict[str, Any]
    

@dataclass
class Workflow:
    """Complete workflow definition"""
    id: str
    name: str
    version: str
    description: str
    tasks: Dict[str, WorkflowTask] = field(default_factory=dict)
    status: WorkflowStatus = WorkflowStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    checkpoints: List[WorkflowCheckpoint] = field(default_factory=list)
    execution_history: List[Dict[str, Any]] = field(default_factory=list)


class WorkflowOrchestrator:
    """Advanced workflow orchestration engine"""
    
    def __init__(self, base_path: str = "/Users/arielmuslera/Development/Projects/bluelabel-autopilot"):
        self.base_path = Path(base_path)
        self.workflows_dir = self.base_path / "workflow" / "instances"
        self.templates_dir = self.base_path / "workflow" / "templates"
        self.checkpoints_dir = self.base_path / "workflow" / "checkpoints"
        
        # Create directories
        for dir_path in [self.workflows_dir, self.templates_dir, self.checkpoints_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Runtime state
        self.active_workflows: Dict[str, Workflow] = {}
        self.task_executors: Dict[str, Callable] = {}
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Performance tracking
        self.execution_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Register built-in task executors
        self._register_builtin_executors()
        
    def _register_builtin_executors(self):
        """Register built-in task executors"""
        self.task_executors.update({
            "agent_task": self._execute_agent_task,
            "file_operation": self._execute_file_operation,
            "api_call": self._execute_api_call,
            "workflow_trigger": self._execute_workflow_trigger,
            "condition_check": self._execute_condition_check,
            "parallel_group": self._execute_parallel_group,
            "approval_gate": self._execute_approval_gate
        })
        
    async def create_workflow(self, workflow_def: Dict[str, Any]) -> str:
        """Create a new workflow from definition"""
        workflow_id = workflow_def.get('id', str(uuid.uuid4()))
        
        # Convert task definitions to WorkflowTask objects
        tasks = {}
        for task_id, task_def in workflow_def.get('tasks', {}).items():
            conditions = []
            for cond_def in task_def.get('conditions', []):
                conditions.append(TaskCondition(**cond_def))
                
            tasks[task_id] = WorkflowTask(
                id=task_id,
                name=task_def['name'],
                agent_id=task_def.get('agent_id', 'system'),
                action=task_def['action'],
                parameters=task_def.get('parameters', {}),
                dependencies=task_def.get('dependencies', []),
                conditions=conditions,
                timeout_seconds=task_def.get('timeout_seconds', 3600),
                retry_count=task_def.get('retry_count', 3),
                retry_delay=task_def.get('retry_delay', 5),
                execution_mode=ExecutionMode(task_def.get('execution_mode', 'sequential'))
            )
            
        workflow = Workflow(
            id=workflow_id,
            name=workflow_def['name'],
            version=workflow_def.get('version', '1.0.0'),
            description=workflow_def.get('description', ''),
            tasks=tasks,
            metadata=workflow_def.get('metadata', {})
        )
        
        # Validate workflow
        await self._validate_workflow(workflow)
        
        # Save workflow
        await self._save_workflow(workflow)
        
        return workflow_id
        
    async def _validate_workflow(self, workflow: Workflow):
        """Validate workflow definition"""
        # Check for circular dependencies
        visited = set()
        rec_stack = set()
        
        def has_cycle(task_id: str) -> bool:
            if task_id in rec_stack:
                return True
            if task_id in visited:
                return False
                
            visited.add(task_id)
            rec_stack.add(task_id)
            
            task = workflow.tasks.get(task_id)
            if task:
                for dep in task.dependencies:
                    if has_cycle(dep):
                        return True
                        
            rec_stack.remove(task_id)
            return False
            
        for task_id in workflow.tasks.keys():
            if has_cycle(task_id):
                raise ValueError(f"Circular dependency detected involving task: {task_id}")
                
        # Validate dependencies exist
        for task in workflow.tasks.values():
            for dep in task.dependencies:
                if dep not in workflow.tasks:
                    raise ValueError(f"Task {task.id} depends on non-existent task: {dep}")
                    
    async def start_workflow(self, workflow_id: str) -> bool:
        """Start workflow execution"""
        workflow = await self._load_workflow(workflow_id)
        if not workflow:
            return False
            
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()
        
        # Create initial checkpoint
        await self._create_checkpoint(workflow)
        
        # Add to active workflows
        self.active_workflows[workflow_id] = workflow
        
        # Start execution in background
        asyncio.create_task(self._execute_workflow(workflow))
        
        return True
        
    async def _execute_workflow(self, workflow: Workflow):
        """Execute workflow with dependency resolution and parallel execution"""
        try:
            # Build execution graph
            execution_graph = await self._build_execution_graph(workflow)
            
            # Execute tasks in dependency order
            completed_tasks = set()
            running_tasks = set()
            failed_tasks = set()
            
            while len(completed_tasks) + len(failed_tasks) < len(workflow.tasks):
                # Find ready tasks (dependencies satisfied)
                ready_tasks = []
                for task_id, task in workflow.tasks.items():
                    if (task_id not in completed_tasks and 
                        task_id not in running_tasks and 
                        task_id not in failed_tasks and
                        all(dep in completed_tasks for dep in task.dependencies)):
                        
                        # Check conditions
                        if await self._check_task_conditions(task, workflow):
                            ready_tasks.append(task)
                            
                # Start ready tasks
                for task in ready_tasks:
                    if task.execution_mode == ExecutionMode.PARALLEL:
                        # Start in parallel
                        asyncio.create_task(self._execute_task(task, workflow))
                        running_tasks.add(task.id)
                    else:
                        # Execute sequentially
                        success = await self._execute_task(task, workflow)
                        if success:
                            completed_tasks.add(task.id)
                        else:
                            failed_tasks.add(task.id)
                            
                        running_tasks.discard(task.id)
                        
                # Wait for parallel tasks to complete
                if running_tasks:
                    await asyncio.sleep(1)  # Check running tasks periodically
                    
                    # Check for completed parallel tasks
                    for task_id in list(running_tasks):
                        task = workflow.tasks[task_id]
                        if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                            running_tasks.remove(task_id)
                            if task.status == TaskStatus.COMPLETED:
                                completed_tasks.add(task_id)
                            else:
                                failed_tasks.add(task_id)
                                
                # Check for deadlock
                if not ready_tasks and not running_tasks:
                    break
                    
            # Determine final status
            if failed_tasks:
                workflow.status = WorkflowStatus.FAILED
                workflow.error = f"Tasks failed: {', '.join(failed_tasks)}"
            elif len(completed_tasks) == len(workflow.tasks):
                workflow.status = WorkflowStatus.COMPLETED
            else:
                workflow.status = WorkflowStatus.FAILED
                workflow.error = "Workflow incomplete - possible deadlock"
                
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.error = str(e)
            
        finally:
            workflow.completed_at = datetime.now()
            await self._save_workflow(workflow)
            
            # Remove from active workflows
            if workflow.id in self.active_workflows:
                del self.active_workflows[workflow.id]
                
    async def _build_execution_graph(self, workflow: Workflow) -> Dict[str, List[str]]:
        """Build task execution dependency graph"""
        graph = defaultdict(list)
        
        for task in workflow.tasks.values():
            for dep in task.dependencies:
                graph[dep].append(task.id)
                
        return dict(graph)
        
    async def _check_task_conditions(self, task: WorkflowTask, workflow: Workflow) -> bool:
        """Check if task conditions are met"""
        for condition in task.conditions:
            if condition.type == "dependency":
                # Check if specific dependencies completed successfully
                dep_task_id = condition.expression
                if dep_task_id in workflow.tasks:
                    dep_task = workflow.tasks[dep_task_id]
                    if dep_task.status != TaskStatus.COMPLETED:
                        return False
                        
            elif condition.type == "expression":
                # Evaluate boolean expression
                try:
                    # Simple expression evaluation (can be extended)
                    result = eval(condition.expression, {"workflow": workflow, "task": task})
                    if not result:
                        return False
                except:
                    return False
                    
            elif condition.type == "custom":
                # Custom condition check
                handler = self.task_executors.get("condition_check")
                if handler:
                    result = await handler(condition, workflow)
                    if not result:
                        return False
                        
        return True
        
    async def _execute_task(self, task: WorkflowTask, workflow: Workflow) -> bool:
        """Execute individual task with retry logic"""
        attempts = 0
        
        while attempts <= task.retry_count:
            try:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                
                # Record execution attempt
                workflow.execution_history.append({
                    "task_id": task.id,
                    "attempt": attempts + 1,
                    "timestamp": datetime.now().isoformat(),
                    "action": "start"
                })
                
                # Get executor
                executor = self.task_executors.get(task.action)
                if not executor:
                    raise ValueError(f"No executor found for action: {task.action}")
                    
                # Execute with timeout
                result = await asyncio.wait_for(
                    executor(task, workflow),
                    timeout=task.timeout_seconds
                )
                
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                
                # Record success
                workflow.execution_history.append({
                    "task_id": task.id,
                    "attempt": attempts + 1,
                    "timestamp": datetime.now().isoformat(),
                    "action": "complete",
                    "result": result
                })
                
                return True
                
            except asyncio.TimeoutError:
                task.error = f"Task timed out after {task.timeout_seconds} seconds"
                attempts += 1
                
            except Exception as e:
                task.error = str(e)
                attempts += 1
                
                # Record failure
                workflow.execution_history.append({
                    "task_id": task.id,
                    "attempt": attempts,
                    "timestamp": datetime.now().isoformat(),
                    "action": "error",
                    "error": str(e)
                })
                
            # Wait before retry
            if attempts <= task.retry_count:
                await asyncio.sleep(task.retry_delay)
                
        task.status = TaskStatus.FAILED
        task.completed_at = datetime.now()
        return False
        
    async def _execute_agent_task(self, task: WorkflowTask, workflow: Workflow) -> Dict[str, Any]:
        """Execute task on specified agent"""
        # Create task in agent's outbox
        agent_outbox = self.base_path / f"postbox/{task.agent_id}/outbox.json"
        
        if not agent_outbox.exists():
            raise ValueError(f"Agent {task.agent_id} not found")
            
        # Load current outbox
        with open(agent_outbox, 'r') as f:
            outbox_data = json.load(f)
            
        # Add new task
        new_task = {
            "task_id": f"WF-{workflow.id}-{task.id}",
            "title": task.name,
            "priority": "HIGH",
            "status": "pending",
            "created_at": datetime.now().isoformat() + 'Z',
            "estimated_hours": task.parameters.get('estimated_hours', 1),
            "description": task.parameters.get('description', ''),
            "workflow_id": workflow.id,
            "workflow_task_id": task.id,
            **task.parameters
        }
        
        outbox_data['tasks'].append(new_task)
        
        # Save updated outbox
        with open(agent_outbox, 'w') as f:
            json.dump(outbox_data, f, indent=2)
            
        # Wait for task completion (polling)
        timeout = time.time() + task.timeout_seconds
        while time.time() < timeout:
            with open(agent_outbox, 'r') as f:
                current_data = json.load(f)
                
            # Check if task moved to history
            for history_item in current_data.get('history', []):
                if history_item.get('task_id') == new_task['task_id']:
                    if history_item.get('status') == 'completed':
                        return {"status": "completed", "result": history_item}
                    elif history_item.get('status') == 'failed':
                        raise Exception(f"Agent task failed: {history_item.get('summary', 'Unknown error')}")
                        
            await asyncio.sleep(5)  # Poll every 5 seconds
            
        raise asyncio.TimeoutError("Agent task did not complete within timeout")
        
    async def _execute_file_operation(self, task: WorkflowTask, workflow: Workflow) -> Dict[str, Any]:
        """Execute file operation"""
        operation = task.parameters.get('operation')
        file_path = Path(task.parameters.get('path'))
        
        if operation == "read":
            content = file_path.read_text()
            return {"operation": "read", "content": content}
            
        elif operation == "write":
            content = task.parameters.get('content')
            file_path.write_text(content)
            return {"operation": "write", "path": str(file_path)}
            
        elif operation == "copy":
            dest_path = Path(task.parameters.get('destination'))
            dest_path.write_text(file_path.read_text())
            return {"operation": "copy", "source": str(file_path), "destination": str(dest_path)}
            
        else:
            raise ValueError(f"Unknown file operation: {operation}")
            
    async def _execute_api_call(self, task: WorkflowTask, workflow: Workflow) -> Dict[str, Any]:
        """Execute API call"""
        # Placeholder for API call implementation
        url = task.parameters.get('url')
        method = task.parameters.get('method', 'GET')
        
        # Simulate API call
        await asyncio.sleep(1)
        
        return {"status": "success", "url": url, "method": method}
        
    async def _execute_workflow_trigger(self, task: WorkflowTask, workflow: Workflow) -> Dict[str, Any]:
        """Execute sub-workflow"""
        sub_workflow_id = task.parameters.get('workflow_id')
        
        # Start sub-workflow
        success = await self.start_workflow(sub_workflow_id)
        
        if success:
            # Wait for completion
            while sub_workflow_id in self.active_workflows:
                await asyncio.sleep(1)
                
            # Check result
            sub_workflow = await self._load_workflow(sub_workflow_id)
            if sub_workflow.status == WorkflowStatus.COMPLETED:
                return {"status": "completed", "sub_workflow_id": sub_workflow_id}
            else:
                raise Exception(f"Sub-workflow failed: {sub_workflow.error}")
        else:
            raise Exception(f"Failed to start sub-workflow: {sub_workflow_id}")
            
    async def _execute_condition_check(self, condition: TaskCondition, workflow: Workflow) -> bool:
        """Execute custom condition check"""
        # Placeholder for custom condition logic
        return True
        
    async def _execute_parallel_group(self, task: WorkflowTask, workflow: Workflow) -> Dict[str, Any]:
        """Execute group of tasks in parallel"""
        task_ids = task.parameters.get('task_ids', [])
        
        # Start all tasks in parallel
        tasks = []
        for task_id in task_ids:
            if task_id in workflow.tasks:
                tasks.append(self._execute_task(workflow.tasks[task_id], workflow))
                
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if r is True)
        
        return {
            "total_tasks": len(tasks),
            "successful": success_count,
            "failed": len(tasks) - success_count
        }
        
    async def _execute_approval_gate(self, task: WorkflowTask, workflow: Workflow) -> Dict[str, Any]:
        """Execute approval gate (manual intervention)"""
        # Create approval request file
        approval_file = self.base_path / "workflow" / "approvals" / f"{workflow.id}-{task.id}.json"
        approval_file.parent.mkdir(exist_ok=True)
        
        approval_data = {
            "workflow_id": workflow.id,
            "task_id": task.id,
            "request": task.parameters.get('request', 'Approval required'),
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        with open(approval_file, 'w') as f:
            json.dump(approval_data, f, indent=2)
            
        # Wait for approval
        timeout = time.time() + task.timeout_seconds
        while time.time() < timeout:
            if approval_file.exists():
                with open(approval_file, 'r') as f:
                    data = json.load(f)
                    
                if data.get('status') == 'approved':
                    return {"status": "approved", "approver": data.get('approver')}
                elif data.get('status') == 'rejected':
                    raise Exception(f"Approval rejected: {data.get('reason')}")
                    
            await asyncio.sleep(10)  # Check every 10 seconds
            
        raise asyncio.TimeoutError("Approval timeout")
        
    async def _create_checkpoint(self, workflow: Workflow):
        """Create workflow checkpoint for rollback"""
        checkpoint_id = str(uuid.uuid4())
        
        # Capture current state
        task_states = {}
        for task_id, task in workflow.tasks.items():
            task_states[task_id] = {
                "status": task.status.value,
                "result": task.result,
                "error": task.error,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            
        checkpoint = WorkflowCheckpoint(
            checkpoint_id=checkpoint_id,
            workflow_id=workflow.id,
            timestamp=datetime.now(),
            task_states=task_states,
            workflow_state={
                "status": workflow.status.value,
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "error": workflow.error
            }
        )
        
        workflow.checkpoints.append(checkpoint)
        
        # Save checkpoint to file
        checkpoint_file = self.checkpoints_dir / f"{workflow.id}-{checkpoint_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2, default=str)
            
    async def rollback_workflow(self, workflow_id: str, checkpoint_id: Optional[str] = None) -> bool:
        """Rollback workflow to checkpoint"""
        workflow = await self._load_workflow(workflow_id)
        if not workflow:
            return False
            
        # Find checkpoint
        target_checkpoint = None
        if checkpoint_id:
            for checkpoint in workflow.checkpoints:
                if checkpoint.checkpoint_id == checkpoint_id:
                    target_checkpoint = checkpoint
                    break
        else:
            # Use latest checkpoint
            if workflow.checkpoints:
                target_checkpoint = workflow.checkpoints[-1]
                
        if not target_checkpoint:
            return False
            
        # Restore state
        for task_id, task_state in target_checkpoint.task_states.items():
            if task_id in workflow.tasks:
                task = workflow.tasks[task_id]
                task.status = TaskStatus(task_state['status'])
                task.result = task_state['result']
                task.error = task_state['error']
                task.started_at = datetime.fromisoformat(task_state['started_at']) if task_state['started_at'] else None
                task.completed_at = datetime.fromisoformat(task_state['completed_at']) if task_state['completed_at'] else None
                
        # Restore workflow state
        workflow_state = target_checkpoint.workflow_state
        workflow.status = WorkflowStatus(workflow_state['status'])
        workflow.started_at = datetime.fromisoformat(workflow_state['started_at']) if workflow_state['started_at'] else None
        workflow.completed_at = datetime.fromisoformat(workflow_state['completed_at']) if workflow_state['completed_at'] else None
        workflow.error = workflow_state['error']
        
        await self._save_workflow(workflow)
        return True
        
    async def _save_workflow(self, workflow: Workflow):
        """Save workflow to file"""
        workflow_file = self.workflows_dir / f"{workflow.id}.json"
        
        # Convert workflow to dict for serialization
        workflow_dict = asdict(workflow)
        
        # Handle datetime serialization
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, (TaskStatus, WorkflowStatus, ExecutionMode)):
                return obj.value
            return str(obj)
            
        with open(workflow_file, 'w') as f:
            json.dump(workflow_dict, f, indent=2, default=default_serializer)
            
    async def _load_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Load workflow from file"""
        workflow_file = self.workflows_dir / f"{workflow_id}.json"
        
        if not workflow_file.exists():
            return None
            
        with open(workflow_file, 'r') as f:
            workflow_dict = json.load(f)
            
        # Convert back to objects
        tasks = {}
        for task_id, task_data in workflow_dict.get('tasks', {}).items():
            # Convert conditions
            conditions = []
            for cond_data in task_data.get('conditions', []):
                conditions.append(TaskCondition(**cond_data))
                
            # Create task
            task = WorkflowTask(
                id=task_data['id'],
                name=task_data['name'],
                agent_id=task_data['agent_id'],
                action=task_data['action'],
                parameters=task_data.get('parameters', {}),
                dependencies=task_data.get('dependencies', []),
                conditions=conditions,
                timeout_seconds=task_data.get('timeout_seconds', 3600),
                retry_count=task_data.get('retry_count', 3),
                retry_delay=task_data.get('retry_delay', 5),
                status=TaskStatus(task_data.get('status', 'pending')),
                result=task_data.get('result'),
                error=task_data.get('error'),
                execution_mode=ExecutionMode(task_data.get('execution_mode', 'sequential'))
            )
            
            # Handle datetime fields
            if task_data.get('started_at'):
                task.started_at = datetime.fromisoformat(task_data['started_at'])
            if task_data.get('completed_at'):
                task.completed_at = datetime.fromisoformat(task_data['completed_at'])
                
            tasks[task_id] = task
            
        # Convert checkpoints
        checkpoints = []
        for cp_data in workflow_dict.get('checkpoints', []):
            checkpoint = WorkflowCheckpoint(
                checkpoint_id=cp_data['checkpoint_id'],
                workflow_id=cp_data['workflow_id'],
                timestamp=datetime.fromisoformat(cp_data['timestamp']),
                task_states=cp_data['task_states'],
                workflow_state=cp_data['workflow_state']
            )
            checkpoints.append(checkpoint)
            
        # Create workflow
        workflow = Workflow(
            id=workflow_dict['id'],
            name=workflow_dict['name'],
            version=workflow_dict['version'],
            description=workflow_dict['description'],
            tasks=tasks,
            status=WorkflowStatus(workflow_dict.get('status', 'created')),
            created_at=datetime.fromisoformat(workflow_dict['created_at']),
            metadata=workflow_dict.get('metadata', {}),
            checkpoints=checkpoints,
            execution_history=workflow_dict.get('execution_history', [])
        )
        
        # Handle datetime fields
        if workflow_dict.get('started_at'):
            workflow.started_at = datetime.fromisoformat(workflow_dict['started_at'])
        if workflow_dict.get('completed_at'):
            workflow.completed_at = datetime.fromisoformat(workflow_dict['completed_at'])
            
        workflow.error = workflow_dict.get('error')
        
        return workflow
        
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status and progress"""
        workflow_file = self.workflows_dir / f"{workflow_id}.json"
        
        if not workflow_file.exists():
            return None
            
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
            
        # Calculate progress
        tasks = workflow_data.get('tasks', {})
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks.values() if t.get('status') == 'completed')
        failed_tasks = sum(1 for t in tasks.values() if t.get('status') == 'failed')
        running_tasks = sum(1 for t in tasks.values() if t.get('status') == 'running')
        
        return {
            "workflow_id": workflow_id,
            "name": workflow_data.get('name'),
            "status": workflow_data.get('status'),
            "progress": {
                "total": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "running": running_tasks,
                "percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "created_at": workflow_data.get('created_at'),
            "started_at": workflow_data.get('started_at'),
            "completed_at": workflow_data.get('completed_at'),
            "error": workflow_data.get('error')
        }
        
    def list_workflows(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all workflows"""
        workflows = []
        
        for workflow_file in self.workflows_dir.glob("*.json"):
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
                
            if status_filter and workflow_data.get('status') != status_filter:
                continue
                
            status_info = self.get_workflow_status(workflow_data['id'])
            if status_info:
                workflows.append(status_info)
                
        return sorted(workflows, key=lambda x: x.get('created_at', ''), reverse=True)
        
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel running workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            
            # Cancel running tasks
            for task in workflow.tasks.values():
                if task.status == TaskStatus.RUNNING:
                    task.status = TaskStatus.CANCELLED
                    
            await self._save_workflow(workflow)
            del self.active_workflows[workflow_id]
            return True
            
        return False
        
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause running workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.PAUSED
            await self._save_workflow(workflow)
            return True
            
        return False
        
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume paused workflow"""
        workflow = await self._load_workflow(workflow_id)
        if workflow and workflow.status == WorkflowStatus.PAUSED:
            workflow.status = WorkflowStatus.RUNNING
            self.active_workflows[workflow_id] = workflow
            asyncio.create_task(self._execute_workflow(workflow))
            return True
            
        return False