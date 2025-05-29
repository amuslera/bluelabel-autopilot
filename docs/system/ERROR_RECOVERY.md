# Error Recovery System Documentation

## Overview

The orchestration system includes comprehensive error recovery mechanisms to ensure resilience and graceful failure handling. This document describes the recovery procedures, tools, and best practices for handling errors in the agent orchestration system.

## Key Components

### 1. File Locking (`tools/file_lock.py`)

Prevents race conditions during concurrent operations by providing both file-based and directory-based locking mechanisms.

#### Features:
- **FileLock**: Process-safe file locking using fcntl for Unix systems
- **DirectoryLock**: Cross-platform locking using marker directories
- **File Transactions**: Atomic file operations with automatic rollback
- **Lock Timeouts**: Configurable timeouts to prevent deadlocks
- **Stale Lock Detection**: Automatic cleanup of abandoned locks

#### Usage Examples:

```python
from file_lock import FileLock, file_transaction, get_task_lock

# Basic file locking
with FileLock("/path/to/lockfile") as lock:
    # Protected code here
    pass

# File transaction with automatic rollback
with file_transaction("/path/to/data.json") as filepath:
    with open(filepath) as f:
        data = json.load(f)
    data['key'] = 'new_value'
    with open(filepath, 'w') as f:
        json.dump(data, f)
    # If exception occurs, file is automatically rolled back

# Task-specific locking
with get_task_lock("TASK-123") as lock:
    # Task-specific operations
    pass
```

### 2. Recovery Manager (`tools/recovery_manager.py`)

Provides automatic retry logic, state preservation, and rollback capabilities for failed operations.

#### Recovery Strategies:
- **RETRY**: Automatic retry with exponential backoff
- **ROLLBACK**: Restore to previous state
- **SKIP**: Skip failed operation and continue
- **MANUAL**: Flag for manual intervention
- **ESCALATE**: Escalate to administrators

#### Features:
- **Automatic Retry**: Configurable retry attempts with exponential backoff
- **State Checkpointing**: Save and restore task state
- **Rollback Mechanism**: Automatic restoration on failure
- **Recovery Statistics**: Track success rates and patterns
- **Error Escalation**: Notify administrators of critical failures

#### Usage Examples:

```python
from recovery_manager import RecoveryManager, RecoveryStrategy

recovery_mgr = RecoveryManager()

# Decorator usage
@recovery_mgr.with_recovery("TASK-001")
def risky_operation(data):
    # Operation that might fail
    return process_data(data)

# Manual execution with recovery
result = recovery_mgr.execute_with_recovery(
    task_id="TASK-002",
    func=another_operation,
    args=(data,),
    strategy=RecoveryStrategy.RETRY
)

# Create checkpoints
recovery_mgr.create_checkpoint(
    "TASK-003",
    TaskState.RUNNING,
    {"progress": 50, "stage": "processing"}
)
```

### 3. Enhanced Task Completion Script (`tools/complete_task_with_recovery.sh`)

An improved version of the task completion script with built-in recovery mechanisms.

#### Features:
- **Automatic Retry**: Retries failed operations up to 3 times
- **File Locking**: Prevents concurrent modifications
- **Backup Creation**: Creates backups before modifications
- **Rollback Support**: Restores original state on failure
- **Checkpoint Tracking**: Records progress for recovery

#### Usage:

```bash
# Basic usage (same as original)
./complete_task_with_recovery.sh CC TASK-165J "Task completed"

# The script automatically:
# - Creates backups of files before modification
# - Retries on failure with delays
# - Rolls back changes if critical errors occur
# - Creates checkpoints for recovery tracking
```

## Recovery Procedures

### 1. Handling Concurrent Operations

When multiple agents or scripts need to modify the same resource:

```bash
# Scripts automatically use file locking
./assign_task.sh CA TASK-001 "New task" HIGH

# Python operations use file_lock module
from file_lock import file_transaction

with file_transaction("/path/to/outbox.json") as f:
    # Safe concurrent modification
    update_outbox(f)
```

### 2. Recovering from Failed Tasks

#### Automatic Recovery

Most failures are handled automatically:

1. **Transient Errors** (network, temporary file locks):
   - Automatically retried with exponential backoff
   - Default: 3 attempts with 2-second initial delay

2. **Data Corruption** (invalid JSON, missing fields):
   - Automatic rollback to previous state
   - Backup files preserved for manual inspection

3. **Permission Errors**:
   - Escalated for manual intervention
   - Error details logged in recovery logs

#### Manual Recovery

For tasks requiring manual intervention:

1. Check escalation files:
   ```bash
   ls logs/recovery/*_escalation.json
   ```

2. Review recovery logs:
   ```bash
   cat logs/recovery/TASK-XXX_recovery.jsonl | jq .
   ```

3. Manually rollback if needed:
   ```bash
   # Restore from backup
   cp postbox/CC/outbox.json.backup_TASK-XXX postbox/CC/outbox.json
   ```

### 3. Checkpoint Recovery

To resume from a checkpoint:

```python
from recovery_manager import RecoveryManager

recovery_mgr = RecoveryManager()

# Load last checkpoint
checkpoint = recovery_mgr.load_checkpoint("TASK-001")
if checkpoint:
    print(f"Resuming from state: {checkpoint.state}")
    print(f"Last data: {checkpoint.data}")
    
    # Resume from checkpoint
    resume_task_from_checkpoint(checkpoint)
```

### 4. Monitoring Recovery Health

#### Recovery Statistics

Get system-wide recovery statistics:

```python
stats = recovery_mgr.get_recovery_stats()
print(f"Success rate: {stats['success_rate']:.2%}")
print(f"Total recoveries: {stats['total_recoveries']}")
print(f"By strategy: {stats['by_strategy']}")
```

#### Health Checks

Regular health checks for the recovery system:

```bash
# Check for stale locks
find /tmp/orchestration/locks -name "*.lock" -mtime +1

# Check recovery log sizes
du -sh logs/recovery/*

# Clean old checkpoints (older than 7 days)
python3 -c "
from recovery_manager import RecoveryManager
mgr = RecoveryManager()
removed = mgr.cleanup_checkpoints(older_than_days=7)
print(f'Removed {removed} old checkpoints')
"
```

## Best Practices

### 1. Always Use File Transactions for Critical Updates

```python
# Good: Atomic updates with automatic rollback
with file_transaction("critical_data.json") as f:
    update_critical_data(f)

# Bad: Direct file modification without protection
with open("critical_data.json", "w") as f:
    json.dump(data, f)  # No rollback if error occurs
```

### 2. Choose Appropriate Recovery Strategies

```python
# Network operations: Use RETRY
@recovery_mgr.with_recovery("API-CALL", strategy=RecoveryStrategy.RETRY)
def call_external_api():
    return requests.get("https://api.example.com/data")

# Data validation: Use ROLLBACK
@recovery_mgr.with_recovery("VALIDATE", strategy=RecoveryStrategy.ROLLBACK)
def validate_and_save(data):
    if not validate(data):
        raise ValueError("Invalid data")
    save_data(data)

# Optional operations: Use SKIP
@recovery_mgr.with_recovery("OPTIONAL", strategy=RecoveryStrategy.SKIP)
def optional_enhancement():
    # Non-critical enhancement
    pass
```

### 3. Create Meaningful Checkpoints

```python
# Good: Detailed checkpoint with progress
recovery_mgr.create_checkpoint(
    task_id,
    TaskState.RUNNING,
    {
        "stage": "processing",
        "files_processed": 45,
        "total_files": 100,
        "current_file": "data_045.json"
    }
)

# Bad: Minimal checkpoint
recovery_mgr.create_checkpoint(task_id, TaskState.RUNNING, {})
```

### 4. Clean Up Resources

```python
# Set up automatic cleanup
recovery_mgr = RecoveryManager()

# Clean up old checkpoints weekly
recovery_mgr.cleanup_checkpoints(older_than_days=7)

# Remove completed task locks
for task_id in completed_tasks:
    lock_file = Path(f"/tmp/orchestration/locks/tasks/{task_id}.lock")
    if lock_file.exists():
        lock_file.unlink()
```

## Troubleshooting

### Common Issues and Solutions

1. **"Failed to acquire lock after timeout"**
   - Check for stale locks: `ls -la /tmp/orchestration/locks/`
   - Increase timeout if needed: `FileLock(path, timeout=60)`
   - Check if another process is holding the lock

2. **"Task failed after N retries"**
   - Review recovery logs: `logs/recovery/TASK-XXX_recovery.jsonl`
   - Check if error is transient or permanent
   - Consider changing recovery strategy

3. **"Rollback failed"**
   - Check if backup files exist
   - Verify file permissions
   - Manually restore from backup if needed

4. **"Checkpoint not found"**
   - Check checkpoint directory: `data/checkpoints/`
   - Verify task ID is correct
   - Check if checkpoint was cleaned up

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug environment variable
export RECOVERY_DEBUG=1

# Run with debug output
./complete_task_with_recovery.sh CC TASK-001 "Test"
```

## Integration with CI/CD

### Automated Testing

The error recovery system includes comprehensive tests:

```bash
# Run all recovery tests
pytest tests/integration/test_orchestration.py::TestErrorRecovery -v

# Specific recovery tests
pytest -k "test_file_locking" -v
pytest -k "test_recovery_manager" -v
pytest -k "test_rollback" -v
```

### Performance Monitoring

Monitor recovery system performance:

```python
# Get recovery metrics
metrics = {
    "avg_retry_time": calculate_avg_retry_time(),
    "lock_wait_time": measure_lock_wait_time(),
    "checkpoint_size": get_checkpoint_storage_size(),
    "recovery_success_rate": recovery_mgr.get_recovery_stats()["success_rate"]
}

# Alert if success rate drops
if metrics["recovery_success_rate"] < 0.95:
    send_alert("Recovery success rate below threshold")
```

## Future Enhancements

1. **Distributed Locking**: Support for distributed systems using Redis/etcd
2. **Advanced Retry Strategies**: Circuit breakers, adaptive timeouts
3. **Machine Learning**: Predict failure patterns and optimize recovery
4. **Real-time Monitoring**: Dashboard for recovery system health
5. **Automated Recovery Tuning**: Self-adjusting retry parameters

## Summary

The error recovery system provides robust mechanisms for handling failures in the orchestration system:

- **File locking** prevents race conditions
- **Recovery manager** provides automatic retry and rollback
- **Checkpointing** enables resumption from known states
- **Enhanced scripts** include built-in recovery logic

By following the procedures and best practices in this document, the orchestration system can handle failures gracefully and maintain high availability.