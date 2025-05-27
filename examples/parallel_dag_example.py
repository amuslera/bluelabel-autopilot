"""
Example of using the Parallel DAG Runner.

This example demonstrates how to create and execute a DAG with parallel steps,
including proper dependency management and error handling.
"""

import asyncio
import logging
from datetime import datetime

from services.workflow.dag_runner_parallel import (
    ParallelStatefulDAGRunner, ParallelDAGRunnerFactory
)
from services.workflow.dag_run_store import DAGRunStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def fetch_user_data():
    """Simulate fetching user data from an API."""
    logger.info("Fetching user data...")
    await asyncio.sleep(0.5)  # Simulate API call
    return {"users": ["alice", "bob", "charlie"], "timestamp": datetime.utcnow().isoformat()}


async def fetch_product_data():
    """Simulate fetching product data from a database."""
    logger.info("Fetching product data...")
    await asyncio.sleep(0.7)  # Simulate DB query
    return {"products": ["laptop", "phone", "tablet"], "count": 3}


async def fetch_analytics_data():
    """Simulate fetching analytics data."""
    logger.info("Fetching analytics data...")
    await asyncio.sleep(0.6)  # Simulate analytics API
    return {"page_views": 1000, "conversions": 50}


async def process_user_data():
    """Process user data (depends on user fetch)."""
    logger.info("Processing user data...")
    await asyncio.sleep(0.3)
    return {"processed_users": 3, "status": "completed"}


async def process_product_data():
    """Process product data (depends on product fetch)."""
    logger.info("Processing product data...")
    await asyncio.sleep(0.4)
    return {"processed_products": 3, "status": "completed"}


async def generate_user_report():
    """Generate user report (depends on processed user data)."""
    logger.info("Generating user report...")
    await asyncio.sleep(0.2)
    return {"report": "user_report.pdf", "size": "2.5MB"}


async def generate_combined_report():
    """Generate combined report (depends on all processing)."""
    logger.info("Generating combined report...")
    await asyncio.sleep(0.5)
    return {"report": "combined_report.pdf", "size": "5.0MB"}


async def send_notifications():
    """Send notifications (depends on all reports)."""
    logger.info("Sending notifications...")
    await asyncio.sleep(0.1)
    return {"notifications_sent": 10, "status": "delivered"}


async def main():
    """Main function demonstrating parallel DAG execution."""
    
    # Create a DAG runner with parallel execution support
    store = DAGRunStore(storage_dir="./dag_runs")
    runner = ParallelStatefulDAGRunner(
        dag_id="data-processing-pipeline",
        store=store,
        max_concurrent_steps=3  # Allow up to 3 steps to run in parallel
    )
    
    # Register steps with dependencies
    # Stage 1: Fetch data from multiple sources (parallel)
    runner.register_step("fetch_users", fetch_user_data)
    runner.register_step("fetch_products", fetch_product_data)
    runner.register_step("fetch_analytics", fetch_analytics_data)
    
    # Stage 2: Process data (parallel, but depends on respective fetches)
    runner.register_step(
        "process_users",
        process_user_data,
        dependencies=["fetch_users"]
    )
    runner.register_step(
        "process_products",
        process_product_data,
        dependencies=["fetch_products"]
    )
    
    # Stage 3: Generate reports
    runner.register_step(
        "user_report",
        generate_user_report,
        dependencies=["process_users"]
    )
    runner.register_step(
        "combined_report",
        generate_combined_report,
        dependencies=["process_users", "process_products", "fetch_analytics"]
    )
    
    # Stage 4: Send notifications (depends on all reports)
    runner.register_step(
        "notifications",
        send_notifications,
        dependencies=["user_report", "combined_report"]
    )
    
    # Validate dependencies before execution
    validation_errors = runner.validate_dependencies()
    if validation_errors:
        logger.error(f"Dependency validation failed: {validation_errors}")
        return
    
    # Visualize the dependency graph
    logger.info("Dependency Graph:")
    for step_id, deps in runner.get_dependency_graph().items():
        logger.info(f"  {step_id} <- {deps if deps else 'no dependencies'}")
    
    # Execute the DAG
    logger.info(f"Starting DAG execution (run_id: {runner.run_id})")
    start_time = datetime.utcnow()
    
    try:
        result = await runner.execute()
        
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        # Print execution summary
        logger.info(f"\nExecution completed in {duration:.2f} seconds")
        logger.info(f"Status: {result.status.value}")
        
        summary = result.get_execution_summary()
        logger.info(f"Steps completed: {summary['completed_steps']}/{summary['total_steps']}")
        logger.info(f"Success rate: {summary['success_rate']:.1f}%")
        
        # Print individual step results
        logger.info("\nStep Results:")
        for step_id, step in result.steps.items():
            logger.info(f"  {step_id}: {step.status.value} "
                       f"(duration: {step.duration_seconds:.2f}s if step.duration_seconds else 'N/A')")
            if step.result:
                logger.info(f"    Result: {step.result}")
        
    except Exception as e:
        logger.error(f"DAG execution failed: {e}")
        
        # Get current status
        status = runner.get_status()
        logger.error(f"Final status: {status}")


async def demonstrate_resume():
    """Demonstrate resuming a failed DAG run."""
    store = DAGRunStore(storage_dir="./dag_runs")
    
    # Create a DAG that will fail
    runner = ParallelStatefulDAGRunner(
        dag_id="resumable-pipeline",
        store=store
    )
    
    async def failing_step():
        raise Exception("Simulated failure!")
    
    # Register steps
    runner.register_step("step1", fetch_user_data)
    runner.register_step("step2", failing_step, max_retries=0)  # Will fail
    runner.register_step("step3", fetch_product_data, dependencies=["step2"])
    
    run_id = runner.run_id
    logger.info(f"Starting DAG that will fail (run_id: {run_id})")
    
    try:
        await runner.execute()
    except Exception as e:
        logger.error(f"DAG failed as expected: {e}")
    
    # Now fix the failing step and resume
    logger.info(f"\nResuming failed DAG run {run_id}")
    
    # Create a new runner to resume the failed run
    resumed_runner = ParallelDAGRunnerFactory.resume_runner(run_id, store)
    
    # Re-register the fixed step
    async def fixed_step():
        return {"status": "fixed!"}
    
    resumed_runner.register_step("step2", fixed_step)
    
    # Resume execution
    try:
        result = await resumed_runner.execute()
        logger.info(f"Resume completed with status: {result.status.value}")
    except Exception as e:
        logger.error(f"Resume failed: {e}")


if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
    
    # Uncomment to see resume example
    # asyncio.run(demonstrate_resume())