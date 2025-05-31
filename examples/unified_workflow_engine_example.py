"""
Example demonstrating the UnifiedWorkflowEngine usage.

This example shows how to use the UnifiedWorkflowEngine with different
engine types and configuration options.
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.unified_workflow_engine import (
    UnifiedWorkflowEngine, 
    EngineType, 
    create_unified_engine
)
from interfaces.run_models import WorkflowStatus


async def example_basic_usage():
    """Basic usage example with sequential engine."""
    print("=== Basic Usage Example ===")
    
    # Create engine with specific type
    engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
    
    # Check engine capabilities
    print(f"Engine type: {engine.engine_type.value}")
    print(f"Supports resume: {engine.supports_resume}")
    print(f"Supports parallel: {engine.supports_parallel_execution}")
    
    # Note: In a real scenario, you would have a valid workflow file
    # For this example, we'll just show the structure
    workflow_path = Path("workflows/sample_workflow.yaml")
    
    try:
        # This would execute a real workflow if the file existed
        print(f"Would execute workflow: {workflow_path}")
        print("(Skipping actual execution as workflow file may not exist)")
        
        # result = await engine.execute_workflow(
        #     workflow_path=workflow_path,
        #     persist=True,
        #     initial_input={"source": "example", "timestamp": datetime.utcnow().isoformat()}
        # )
        # print(f"Workflow completed with status: {result.status}")
        
    except Exception as e:
        print(f"Would handle execution error: {e}")


async def example_engine_switching():
    """Example showing different engine types."""
    print("\n=== Engine Switching Example ===")
    
    # Sequential engine - fast but no state persistence
    sequential_engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
    print(f"Sequential engine - Resume support: {sequential_engine.supports_resume}")
    
    # Stateful DAG engine - slower but with state persistence and resume
    dag_engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)
    print(f"Stateful DAG engine - Resume support: {dag_engine.supports_resume}")
    
    # Using factory function
    factory_engine = create_unified_engine(engine_type="sequential")
    print(f"Factory created engine type: {factory_engine.engine_type.value}")


async def example_environment_configuration():
    """Example using environment variable configuration."""
    print("\n=== Environment Configuration Example ===")
    
    # Save original environment
    original_env = os.environ.get('WORKFLOW_ENGINE_TYPE')
    
    try:
        # Set environment variable
        os.environ['WORKFLOW_ENGINE_TYPE'] = 'stateful_dag'
        
        # Create engine without specifying type (uses env var)
        engine = UnifiedWorkflowEngine()
        print(f"Engine type from env var: {engine.engine_type.value}")
        
        # Test invalid environment variable
        os.environ['WORKFLOW_ENGINE_TYPE'] = 'invalid_type'
        engine_with_invalid_env = UnifiedWorkflowEngine()
        print(f"With invalid env var, defaults to: {engine_with_invalid_env.engine_type.value}")
        
    finally:
        # Restore original environment
        if original_env:
            os.environ['WORKFLOW_ENGINE_TYPE'] = original_env
        elif 'WORKFLOW_ENGINE_TYPE' in os.environ:
            del os.environ['WORKFLOW_ENGINE_TYPE']


async def example_completion_callback():
    """Example with completion callback."""
    print("\n=== Completion Callback Example ===")
    
    async def on_workflow_complete(result):
        """Callback function called after successful workflow completion."""
        print(f"✅ Workflow '{result.workflow_name}' completed successfully!")
        print(f"   Duration: {result.duration_ms}ms")
        print(f"   Steps completed: {len(result.step_outputs)}")
        
        # In a real scenario, you might:
        # - Send email notifications
        # - Update database records
        # - Trigger downstream processes
        # - Log to monitoring systems
    
    engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
    
    print("Would execute workflow with callback:")
    print("- on_complete function would be called on success")
    print("- Useful for notifications, cleanup, or triggering next steps")
    
    # In practice:
    # result = await engine.execute_workflow(
    #     workflow_path=Path("workflow.yaml"),
    #     on_complete=on_workflow_complete
    # )


async def example_performance_monitoring():
    """Example showing performance monitoring."""
    print("\n=== Performance Monitoring Example ===")
    
    engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
    
    # Get initial status
    status = engine.get_status()
    print(f"Engine status: {status}")
    
    # Performance monitoring would happen during actual execution
    print("During workflow execution:")
    print("- Adapter overhead is automatically tracked")
    print("- Performance metrics are recorded")
    print("- Warnings are logged if overhead exceeds 100ms")
    
    # In practice, after execution:
    # status = engine.get_status()
    # print(f"Current run ID: {status['current_run_id']}")
    # print(f"Adapter overhead: {status.get('adapter_overhead_ms', 'N/A')}ms")


async def example_error_handling():
    """Example showing error handling patterns."""
    print("\n=== Error Handling Example ===")
    
    try:
        # Invalid engine type
        invalid_engine = UnifiedWorkflowEngine(engine_type="nonexistent")
    except ValueError as e:
        print(f"❌ Invalid engine type error: {e}")
    
    # Proper error handling during workflow execution
    engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
    
    try:
        # This would be a real workflow execution
        print("Would handle workflow execution errors:")
        print("- WorkflowValidationError for invalid YAML")
        print("- FileNotFoundError for missing workflow files")
        print("- RuntimeError for agent execution failures")
        
        # result = await engine.execute_workflow(Path("nonexistent.yaml"))
        
    except Exception as e:
        print(f"Would catch and handle: {type(e).__name__}: {e}")
        
        # Get engine status for debugging
        status = engine.get_status()
        print(f"Engine status during error: {status}")


async def example_migration_from_old_engines():
    """Example showing migration from legacy engines."""
    print("\n=== Migration Example ===")
    
    print("OLD CODE (WorkflowEngine):")
    print("""
    from core.workflow_engine import WorkflowEngine
    engine = WorkflowEngine(storage_path=Path("./data"))
    result = await engine.execute_workflow(workflow_path)
    """)
    
    print("\nNEW CODE (UnifiedWorkflowEngine):")
    print("""
    from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType
    engine = UnifiedWorkflowEngine(
        engine_type=EngineType.SEQUENTIAL,
        storage_path=Path("./data")
    )
    result = await engine.execute_workflow(workflow_path)
    """)
    
    # Actual migration example
    storage_path = Path("./data/knowledge")
    temp_path = Path("./data/temp")
    
    # New unified approach
    unified_engine = UnifiedWorkflowEngine(
        engine_type=EngineType.SEQUENTIAL,
        storage_path=storage_path,
        temp_path=temp_path
    )
    
    print(f"✅ Migrated to unified engine with paths:")
    print(f"   Storage: {unified_engine.storage_path}")
    print(f"   Temp: {unified_engine.temp_path}")


async def main():
    """Run all examples."""
    print("🚀 UnifiedWorkflowEngine Examples")
    print("=" * 50)
    
    await example_basic_usage()
    await example_engine_switching()
    await example_environment_configuration()
    await example_completion_callback()
    await example_performance_monitoring()
    await example_error_handling()
    await example_migration_from_old_engines()
    
    print("\n" + "=" * 50)
    print("✅ All examples completed!")
    print("\nFor more information, see:")
    print("- docs/unified_workflow_engine_guide.md")
    print("- tests/unit/test_unified_workflow_engine.py")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())