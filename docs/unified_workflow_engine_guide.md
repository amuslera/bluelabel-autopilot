# UnifiedWorkflowEngine Guide

## Overview

The UnifiedWorkflowEngine is an adapter that provides a unified interface for different workflow execution engines in the Bluelabel AIOS platform. It implements the strategy pattern to allow seamless switching between:

- **Sequential Engine** (`WorkflowEngine`) - The original workflow execution engine
- **Stateful DAG Engine** (`StatefulDAGRunner`) - The enhanced DAG runner with persistent state and retry capabilities

## Features

- **Engine Abstraction**: Single interface for multiple workflow engines
- **Feature Flag Support**: Configure engine selection via environment variables
- **Performance Monitoring**: Built-in performance tracking with <100ms overhead requirement
- **Backward Compatibility**: Maintains compatibility with existing workflow definitions
- **Failure Recovery**: Supports resumable execution with stateful DAG engine
- **Comprehensive Testing**: Full test suite with mocking support

## Quick Start

### Basic Usage

```python
from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType
from pathlib import Path

# Create engine with specific type
engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)

# Execute workflow
result = await engine.execute_workflow(
    workflow_path=Path("workflows/my_workflow.yaml"),
    persist=True,
    initial_input={"source": "api", "data": {...}}
)

print(f"Workflow completed with status: {result.status}")
```

### Using Factory Function

```python
from core.unified_workflow_engine import create_unified_engine

# Create with string
engine = create_unified_engine(engine_type="stateful_dag")

# Create with environment variable
# Set WORKFLOW_ENGINE_TYPE=sequential in environment
engine = create_unified_engine()  # Uses env var
```

## Configuration

### Environment Variables

Set the default engine type using environment variables:

```bash
# Use sequential engine (default)
export WORKFLOW_ENGINE_TYPE=sequential

# Use stateful DAG engine
export WORKFLOW_ENGINE_TYPE=stateful_dag
```

### Engine Types

#### Sequential Engine (`EngineType.SEQUENTIAL`)

- **Use Case**: Simple, linear workflow execution
- **Features**: Fast execution, low overhead
- **Limitations**: No state persistence, no resume capability
- **Best For**: Development, simple workflows, high-throughput scenarios

```python
engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
```

#### Stateful DAG Engine (`EngineType.STATEFUL_DAG`)

- **Use Case**: Complex workflows requiring state persistence
- **Features**: Resume from failure, retry logic, state tracking
- **Limitations**: Higher overhead, more complex setup
- **Best For**: Production workflows, long-running processes, critical pipelines

```python
engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)
```

## Advanced Usage

### Resuming Failed Workflows

Only available with the Stateful DAG engine:

```python
engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)

# First execution (fails partway through)
try:
    result = await engine.execute_workflow(workflow_path, persist=True)
except Exception as e:
    run_id = engine._current_run_id
    print(f"Workflow failed, run_id: {run_id}")

# Resume from failure
result = await engine.execute_workflow(
    workflow_path=workflow_path,
    run_id=run_id,  # Resume from this run
    persist=True
)
```

### Performance Monitoring

The unified engine automatically tracks performance metrics:

```python
engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
result = await engine.execute_workflow(workflow_path)

# Check performance
status = engine.get_status()
print(f"Engine overhead: {status.get('adapter_overhead_ms', 'N/A')}ms")
```

### Completion Callbacks

Execute custom logic after successful workflow completion:

```python
async def send_notification(result):
    print(f"Workflow {result.workflow_name} completed successfully!")
    # Send email, update database, etc.

result = await engine.execute_workflow(
    workflow_path=workflow_path,
    on_complete=send_notification
)
```

## Engine Capabilities

### Checking Engine Features

```python
engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)

# Check what the engine supports
if engine.supports_resume:
    print("This engine can resume from failures")

if engine.supports_parallel_execution:
    print("This engine supports parallel step execution")

# Get detailed status
status = engine.get_status()
print(f"Current engine: {status['engine_type']}")
print(f"Current run: {status['current_run_id']}")
```

## Migration Guide

### From WorkflowEngine

```python
# Old code
from core.workflow_engine import WorkflowEngine
engine = WorkflowEngine()
result = await engine.execute_workflow(workflow_path)

# New code
from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType
engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
result = await engine.execute_workflow(workflow_path)
```

### From StatefulDAGRunner

```python
# Old code
from services.workflow.dag_runner import StatefulDAGRunner
runner = StatefulDAGRunner(dag_id="my_dag")
# ... register steps manually
dag_run = await runner.execute()

# New code
from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType
engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)
result = await engine.execute_workflow(workflow_path)
```

## Testing

### Unit Testing with Mocks

```python
import pytest
from unittest.mock import patch, AsyncMock
from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType

@pytest.mark.asyncio
async def test_workflow_execution():
    engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
    
    # Mock the underlying engine
    mock_result = WorkflowRunResult(...)
    with patch.object(engine, '_engine') as mock_engine:
        mock_engine.execute_workflow = AsyncMock(return_value=mock_result)
        
        result = await engine.execute_workflow(workflow_path)
        
    assert result.status == WorkflowStatus.SUCCESS
```

### Integration Testing

```python
@pytest.mark.asyncio
async def test_engine_switching():
    # Test with sequential engine
    engine1 = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
    result1 = await engine1.execute_workflow(workflow_path)
    
    # Test with stateful DAG engine
    engine2 = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)
    result2 = await engine2.execute_workflow(workflow_path)
    
    # Both should succeed with same workflow
    assert result1.status == WorkflowStatus.SUCCESS
    assert result2.status == WorkflowStatus.SUCCESS
```

## Performance Requirements

The UnifiedWorkflowEngine maintains strict performance requirements:

- **Adapter Overhead**: <100ms per workflow execution
- **Memory Overhead**: Minimal additional memory usage
- **CPU Overhead**: <5% additional CPU usage

### Performance Monitoring

```python
import time
from core.unified_workflow_engine import performance_monitor

start_time = time.time()
result = await engine.execute_workflow(workflow_path)
total_time = time.time() - start_time

# Check overhead
overhead = (total_time * 1000) - result.duration_ms
assert overhead < 100, f"Overhead {overhead}ms exceeds requirement"

# Get performance metrics
metrics = performance_monitor.get_metrics()
print(f"Recent overhead: {metrics.get('adapter_overhead_ms', [])}ms")
```

## Error Handling

### Engine Selection Errors

```python
try:
    engine = UnifiedWorkflowEngine(engine_type="invalid_type")
except ValueError as e:
    print(f"Invalid engine type: {e}")
    # Falls back to sequential engine
```

### Workflow Execution Errors

```python
try:
    result = await engine.execute_workflow(workflow_path)
except WorkflowValidationError as e:
    print(f"Workflow validation failed: {e}")
except Exception as e:
    print(f"Execution failed: {e}")
    
    # Check engine status for details
    status = engine.get_status()
    if 'dag_status' in status:
        print(f"DAG status: {status['dag_status']}")
```

## Best Practices

### Engine Selection

1. **Development**: Use `EngineType.SEQUENTIAL` for faster iteration
2. **Testing**: Use `EngineType.SEQUENTIAL` for unit tests, `EngineType.STATEFUL_DAG` for integration tests
3. **Production**: Use `EngineType.STATEFUL_DAG` for critical workflows requiring reliability
4. **High Throughput**: Use `EngineType.SEQUENTIAL` for simple, fast workflows

### Configuration Management

1. Use environment variables for deployment-specific engine selection
2. Override with explicit engine type for specific use cases
3. Document engine requirements in workflow definitions

### Error Recovery

1. Always check `supports_resume` before attempting to resume workflows
2. Store run IDs for critical workflows when using stateful engine
3. Implement proper error handling and logging

### Performance Optimization

1. Monitor adapter overhead and optimize if it exceeds 100ms
2. Use caching for frequently executed workflows
3. Consider engine type based on workflow complexity and execution frequency

## Troubleshooting

### Common Issues

#### Engine Type Not Found
```
ValueError: Unsupported engine type: invalid_type
```
**Solution**: Use valid engine types: `sequential` or `stateful_dag`

#### Resume Not Supported
```
AttributeError: 'WorkflowEngine' object has no attribute 'resume'
```
**Solution**: Use `EngineType.STATEFUL_DAG` for resume functionality

#### Performance Overhead Warning
```
WARNING: Performance overhead 150ms exceeds 100ms target
```
**Solution**: Check for heavy operations in adapter logic, consider workflow optimization

### Debug Mode

Enable debug logging for detailed execution information:

```python
import logging
logging.getLogger('core.unified_workflow_engine').setLevel(logging.DEBUG)

# This will log which engine is being used and performance metrics
result = await engine.execute_workflow(workflow_path)
```

## Contributing

When extending the UnifiedWorkflowEngine:

1. Maintain the IWorkflowEngine interface contract
2. Add comprehensive tests for new functionality
3. Ensure performance overhead stays <100ms
4. Update this documentation with new features
5. Follow the existing error handling patterns

## Future Enhancements

Planned improvements:

- **Parallel Execution**: Support for parallel step execution in both engines
- **Engine Auto-Selection**: Automatic engine selection based on workflow complexity
- **Performance Analytics**: Detailed performance tracking and optimization suggestions
- **Custom Engines**: Plugin system for custom workflow engines
- **Workflow Migration**: Tools for migrating between engine types