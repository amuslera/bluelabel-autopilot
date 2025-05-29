#!/usr/bin/env python3
"""
Recovery Manager for the orchestration system.

Provides error handling, retry logic, state preservation, and rollback capabilities
for failed tasks and operations.
"""

import json
import os
import time
import shutil
import traceback
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from enum import Enum
from dataclasses import dataclass, asdict
from functools import wraps

from file_lock import FileLock, file_transaction, get_task_lock


class RecoveryStrategy(Enum):
    """Available recovery strategies for failed operations."""
    RETRY = "retry"
    ROLLBACK = "rollback"
    SKIP = "skip"
    MANUAL = "manual"
    ESCALATE = "escalate"


class TaskState(Enum):
    """Possible states for a task during execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


@dataclass
class TaskCheckpoint:
    """Represents a checkpoint in task execution."""
    task_id: str
    checkpoint_id: str
    timestamp: str
    state: TaskState
    data: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class RecoveryRecord:
    """Record of a recovery attempt."""
    task_id: str
    timestamp: str
    error_type: str
    error_message: str
    strategy: RecoveryStrategy
    success: bool
    details: Dict[str, Any]


class RecoveryManager:
    """
    Manages error recovery for the orchestration system.
    
    Features:
    - Automatic retry with exponential backoff
    - State checkpointing and restoration
    - Rollback mechanisms
    - Error escalation
    - Recovery history tracking
    """
    
    def __init__(self, 
                 base_path: Optional[Path] = None,
                 max_retries: int = 3,
                 initial_retry_delay: float = 1.0,
                 max_retry_delay: float = 60.0,
                 checkpoint_dir: Optional[Path] = None,
                 recovery_log_dir: Optional[Path] = None):
        """
        Initialize the Recovery Manager.
        
        Args:
            base_path: Base path for orchestration system
            max_retries: Maximum number of retry attempts
            initial_retry_delay: Initial delay between retries (seconds)
            max_retry_delay: Maximum delay between retries (seconds)
            checkpoint_dir: Directory for storing checkpoints
            recovery_log_dir: Directory for recovery logs
        """
        self.base_path = base_path or Path.home() / "Development/Projects/bluelabel-autopilot"
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.max_retry_delay = max_retry_delay
        
        # Set up directories
        self.checkpoint_dir = checkpoint_dir or self.base_path / "data" / "checkpoints"
        self.recovery_log_dir = recovery_log_dir or self.base_path / "logs" / "recovery"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.recovery_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Recovery strategies configuration
        self.recovery_strategies = {
            "FileNotFoundError": RecoveryStrategy.SKIP,
            "PermissionError": RecoveryStrategy.ESCALATE,
            "json.JSONDecodeError": RecoveryStrategy.ROLLBACK,
            "ConnectionError": RecoveryStrategy.RETRY,
            "TimeoutError": RecoveryStrategy.RETRY,
            "default": RecoveryStrategy.RETRY
        }
    
    def with_recovery(self, 
                     task_id: str,
                     strategy: Optional[RecoveryStrategy] = None,
                     checkpoint_enabled: bool = True):
        """
        Decorator for functions with automatic recovery.
        
        Args:
            task_id: Unique identifier for the task
            strategy: Recovery strategy to use (auto-detected if None)
            checkpoint_enabled: Enable state checkpointing
            
        Example:
            @recovery_manager.with_recovery("TASK-001")
            def process_task(data):
                # Task implementation
                return result
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute_with_recovery(
                    task_id=task_id,
                    func=func,
                    args=args,
                    kwargs=kwargs,
                    strategy=strategy,
                    checkpoint_enabled=checkpoint_enabled
                )
            return wrapper
        return decorator
    
    def execute_with_recovery(self,
                            task_id: str,
                            func: Callable,
                            args: tuple = (),
                            kwargs: dict = None,
                            strategy: Optional[RecoveryStrategy] = None,
                            checkpoint_enabled: bool = True) -> Any:
        """
        Execute a function with recovery mechanisms.
        
        Args:
            task_id: Unique identifier for the task
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            strategy: Recovery strategy (auto-detected if None)
            checkpoint_enabled: Enable state checkpointing
            
        Returns:
            Result of the function execution
            
        Raises:
            Exception: If all recovery attempts fail
        """
        kwargs = kwargs or {}
        attempt = 0
        last_error = None
        
        # Load any existing checkpoint
        checkpoint = self.load_checkpoint(task_id) if checkpoint_enabled else None
        
        while attempt <= self.max_retries:
            try:
                # Create checkpoint before execution
                if checkpoint_enabled and attempt == 0:
                    self.create_checkpoint(
                        task_id,
                        TaskState.RUNNING,
                        {"args": str(args), "kwargs": str(kwargs)}
                    )
                
                # Execute the function
                result = func(*args, **kwargs)
                
                # Success - create completion checkpoint
                if checkpoint_enabled:
                    self.create_checkpoint(
                        task_id,
                        TaskState.COMPLETED,
                        {"result": str(result)}
                    )
                
                # Log successful recovery if this was a retry
                if attempt > 0:
                    self._log_recovery(
                        task_id,
                        type(last_error).__name__ if last_error else "Unknown",
                        str(last_error) if last_error else "Unknown error",
                        RecoveryStrategy.RETRY,
                        True,
                        {"attempts": attempt}
                    )
                
                return result
                
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                
                # Determine recovery strategy
                if strategy is None:
                    strategy = self.recovery_strategies.get(
                        error_type,
                        self.recovery_strategies["default"]
                    )
                
                # Log the error
                self._log_recovery(
                    task_id,
                    error_type,
                    str(e),
                    strategy,
                    False,
                    {
                        "attempt": attempt + 1,
                        "traceback": traceback.format_exc()
                    }
                )
                
                # Handle based on strategy
                if strategy == RecoveryStrategy.RETRY and attempt < self.max_retries:
                    delay = self._calculate_retry_delay(attempt)
                    print(f"Error in {task_id}: {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                    attempt += 1
                    
                    if checkpoint_enabled:
                        self.create_checkpoint(
                            task_id,
                            TaskState.RETRYING,
                            {"attempt": attempt, "error": str(e)}
                        )
                    
                elif strategy == RecoveryStrategy.ROLLBACK:
                    print(f"Error in {task_id}: {e}. Attempting rollback...")
                    self.rollback_task(task_id)
                    raise
                    
                elif strategy == RecoveryStrategy.SKIP:
                    print(f"Error in {task_id}: {e}. Skipping task...")
                    if checkpoint_enabled:
                        self.create_checkpoint(
                            task_id,
                            TaskState.SKIPPED,
                            {"error": str(e)}
                        )
                    return None
                    
                elif strategy == RecoveryStrategy.ESCALATE:
                    print(f"Error in {task_id}: {e}. Escalating to manual intervention...")
                    self._escalate_error(task_id, e)
                    raise
                    
                else:
                    raise
        
        # All retries exhausted
        if checkpoint_enabled:
            self.create_checkpoint(
                task_id,
                TaskState.FAILED,
                {"error": str(last_error), "attempts": attempt}
            )
        
        raise Exception(f"Task {task_id} failed after {attempt} retries: {last_error}")
    
    def create_checkpoint(self, 
                         task_id: str,
                         state: TaskState,
                         data: Dict[str, Any],
                         metadata: Optional[Dict[str, Any]] = None) -> TaskCheckpoint:
        """Create a checkpoint for a task."""
        checkpoint = TaskCheckpoint(
            task_id=task_id,
            checkpoint_id=f"{task_id}_{int(time.time() * 1000)}",
            timestamp=datetime.now().isoformat(),
            state=state,
            data=data,
            metadata=metadata or {}
        )
        
        # Save checkpoint
        checkpoint_file = self.checkpoint_dir / f"{task_id}_checkpoint.json"
        with file_transaction(checkpoint_file) as f:
            with open(f, 'w') as fp:
                json.dump(asdict(checkpoint), fp, indent=2)
        
        # Also save to history
        history_file = self.checkpoint_dir / f"{task_id}_history.jsonl"
        with open(history_file, 'a') as f:
            f.write(json.dumps(asdict(checkpoint)) + '\n')
        
        return checkpoint
    
    def load_checkpoint(self, task_id: str) -> Optional[TaskCheckpoint]:
        """Load the latest checkpoint for a task."""
        checkpoint_file = self.checkpoint_dir / f"{task_id}_checkpoint.json"
        
        if not checkpoint_file.exists():
            return None
        
        try:
            with open(checkpoint_file) as f:
                data = json.load(f)
            
            return TaskCheckpoint(
                task_id=data['task_id'],
                checkpoint_id=data['checkpoint_id'],
                timestamp=data['timestamp'],
                state=TaskState(data['state']),
                data=data['data'],
                metadata=data['metadata']
            )
        except Exception as e:
            print(f"Error loading checkpoint for {task_id}: {e}")
            return None
    
    def rollback_task(self, task_id: str) -> bool:
        """
        Rollback a task to its previous state.
        
        Returns:
            True if rollback successful, False otherwise
        """
        rollback_marker = self.checkpoint_dir / f"{task_id}_rollback.marker"
        
        try:
            # Find files modified by this task
            task_files = self._find_task_files(task_id)
            
            # Restore backups
            for file_path in task_files:
                backup_path = file_path.parent / f".{file_path.name}.backup_{task_id}"
                if backup_path.exists():
                    shutil.copy2(backup_path, file_path)
                    backup_path.unlink()
            
            # Create rollback checkpoint
            self.create_checkpoint(
                task_id,
                TaskState.ROLLED_BACK,
                {"rolled_back_files": [str(f) for f in task_files]}
            )
            
            # Mark rollback complete
            rollback_marker.write_text(datetime.now().isoformat())
            
            return True
            
        except Exception as e:
            print(f"Rollback failed for {task_id}: {e}")
            return False
    
    def cleanup_checkpoints(self, 
                           task_id: Optional[str] = None,
                           older_than_days: int = 7) -> int:
        """
        Clean up old checkpoints.
        
        Args:
            task_id: Specific task to clean (all if None)
            older_than_days: Remove checkpoints older than this
            
        Returns:
            Number of checkpoints removed
        """
        removed = 0
        cutoff_date = datetime.now() - timedelta(days=older_than_days)
        
        pattern = f"{task_id}_*" if task_id else "*"
        
        for checkpoint_file in self.checkpoint_dir.glob(f"{pattern}_checkpoint.json"):
            try:
                if checkpoint_file.stat().st_mtime < cutoff_date.timestamp():
                    checkpoint_file.unlink()
                    removed += 1
                    
                    # Also remove history
                    history_file = checkpoint_file.parent / checkpoint_file.name.replace(
                        "_checkpoint.json", "_history.jsonl"
                    )
                    if history_file.exists():
                        history_file.unlink()
                        
            except Exception as e:
                print(f"Error cleaning checkpoint {checkpoint_file}: {e}")
        
        return removed
    
    def get_recovery_stats(self, 
                          task_id: Optional[str] = None,
                          since: Optional[datetime] = None) -> Dict[str, Any]:
        """Get recovery statistics."""
        stats = {
            "total_recoveries": 0,
            "successful_recoveries": 0,
            "failed_recoveries": 0,
            "by_strategy": {},
            "by_error_type": {},
            "tasks_affected": set()
        }
        
        # Read recovery logs
        pattern = f"{task_id}_*" if task_id else "*"
        since_timestamp = since.timestamp() if since else 0
        
        for log_file in self.recovery_log_dir.glob(f"{pattern}_recovery.jsonl"):
            if log_file.stat().st_mtime < since_timestamp:
                continue
                
            with open(log_file) as f:
                for line in f:
                    try:
                        record = json.loads(line)
                        stats["total_recoveries"] += 1
                        
                        if record["success"]:
                            stats["successful_recoveries"] += 1
                        else:
                            stats["failed_recoveries"] += 1
                        
                        strategy = record["strategy"]
                        stats["by_strategy"][strategy] = stats["by_strategy"].get(strategy, 0) + 1
                        
                        error_type = record["error_type"]
                        stats["by_error_type"][error_type] = stats["by_error_type"].get(error_type, 0) + 1
                        
                        stats["tasks_affected"].add(record["task_id"])
                        
                    except Exception:
                        continue
        
        stats["tasks_affected"] = len(stats["tasks_affected"])
        stats["success_rate"] = (
            stats["successful_recoveries"] / stats["total_recoveries"]
            if stats["total_recoveries"] > 0 else 0
        )
        
        return stats
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt using exponential backoff."""
        delay = min(
            self.initial_retry_delay * (2 ** attempt),
            self.max_retry_delay
        )
        # Add jitter to prevent thundering herd
        import random
        jitter = random.uniform(0, delay * 0.1)
        return delay + jitter
    
    def _log_recovery(self,
                     task_id: str,
                     error_type: str,
                     error_message: str,
                     strategy: RecoveryStrategy,
                     success: bool,
                     details: Dict[str, Any]):
        """Log a recovery attempt."""
        record = RecoveryRecord(
            task_id=task_id,
            timestamp=datetime.now().isoformat(),
            error_type=error_type,
            error_message=error_message,
            strategy=strategy.value,
            success=success,
            details=details
        )
        
        log_file = self.recovery_log_dir / f"{task_id}_recovery.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(asdict(record)) + '\n')
    
    def _find_task_files(self, task_id: str) -> List[Path]:
        """Find files modified by a task."""
        # This would integrate with the orchestration system
        # to track which files were modified by each task
        # For now, return empty list
        return []
    
    def _escalate_error(self, task_id: str, error: Exception):
        """Escalate an error for manual intervention."""
        escalation_file = self.recovery_log_dir / f"{task_id}_escalation.json"
        
        escalation_data = {
            "task_id": task_id,
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "status": "requires_manual_intervention"
        }
        
        with open(escalation_file, 'w') as f:
            json.dump(escalation_data, f, indent=2)
        
        # In a real system, this would also notify administrators


# Utility functions for common recovery patterns

def retry_on_error(max_retries: int = 3,
                  delay: float = 1.0,
                  exceptions: tuple = (Exception,)):
    """
    Simple retry decorator for functions.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries
        exceptions: Tuple of exceptions to catch
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(delay * (attempt + 1))
                    else:
                        raise
            
            raise last_exception
        return wrapper
    return decorator


def checkpoint_task(recovery_manager: RecoveryManager,
                   task_id: str,
                   checkpoint_name: str):
    """
    Decorator to create checkpoints at specific points in task execution.
    
    Args:
        recovery_manager: RecoveryManager instance
        task_id: Task identifier
        checkpoint_name: Name for this checkpoint
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create checkpoint before execution
            recovery_manager.create_checkpoint(
                task_id,
                TaskState.RUNNING,
                {
                    "checkpoint": checkpoint_name,
                    "function": func.__name__,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            try:
                result = func(*args, **kwargs)
                
                # Create success checkpoint
                recovery_manager.create_checkpoint(
                    task_id,
                    TaskState.RUNNING,
                    {
                        "checkpoint": f"{checkpoint_name}_completed",
                        "function": func.__name__,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                return result
                
            except Exception as e:
                # Create failure checkpoint
                recovery_manager.create_checkpoint(
                    task_id,
                    TaskState.FAILED,
                    {
                        "checkpoint": f"{checkpoint_name}_failed",
                        "function": func.__name__,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                )
                raise
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    recovery_manager = RecoveryManager()
    
    # Example 1: Function with automatic recovery
    @recovery_manager.with_recovery("TASK-TEST-001")
    def risky_operation(value: int) -> int:
        if value < 0:
            raise ValueError("Negative value not allowed")
        return value * 2
    
    # This will retry on error
    try:
        result = risky_operation(-5)
    except Exception as e:
        print(f"Operation failed: {e}")
    
    # Example 2: Manual recovery execution
    def another_operation(data: dict) -> dict:
        data["processed"] = True
        return data
    
    result = recovery_manager.execute_with_recovery(
        task_id="TASK-TEST-002",
        func=another_operation,
        args=({"value": 42},),
        strategy=RecoveryStrategy.RETRY
    )
    print(f"Result: {result}")
    
    # Example 3: Get recovery statistics
    stats = recovery_manager.get_recovery_stats()
    print(f"Recovery stats: {json.dumps(stats, indent=2)}")