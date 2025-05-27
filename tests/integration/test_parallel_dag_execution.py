"""
Integration tests for parallel DAG execution.

This module tests the parallel execution capabilities in real-world scenarios
including data processing pipelines and multi-agent workflows.
"""

import asyncio
import pytest
import time
from typing import Dict, Any, List

from services.workflow.dag_runner_parallel import (
    ParallelStatefulDAGRunner, ParallelDAGRunnerFactory
)
from services.workflow.dag_run_tracker import DAGStepStatus, DAGRunStatus
from services.workflow.dag_run_store import DAGRunStore


class TestParallelDataPipeline:
    """Test parallel execution of a data processing pipeline."""
    
    @pytest.fixture
    def store(self, tmp_path):
        """Create a temporary DAGRunStore."""
        return DAGRunStore(storage_dir=str(tmp_path / "dag_runs"))
    
    @pytest.fixture
    def shared_data(self):
        """Shared data structure for the pipeline."""
        return {
            "raw_data": [],
            "processed_data": {},
            "aggregated_data": {},
            "reports": []
        }
    
    async def create_data_loader(self, source: str, shared_data: Dict):
        """Create a data loader step."""
        async def load_data():
            # Simulate loading data from source
            await asyncio.sleep(0.1)  # Simulate I/O
            data = [f"{source}_item_{i}" for i in range(10)]
            shared_data["raw_data"].extend(data)
            return {"source": source, "items_loaded": len(data)}
        return load_data
    
    async def create_data_processor(self, processor_id: str, shared_data: Dict):
        """Create a data processor step."""
        async def process_data():
            # Simulate processing a portion of data
            await asyncio.sleep(0.2)  # Simulate CPU-intensive work
            
            # Process assigned items
            start_idx = int(processor_id[-1]) * 5
            end_idx = start_idx + 5
            
            processed_items = {}
            for i in range(start_idx, min(end_idx, len(shared_data["raw_data"]))):
                if i < len(shared_data["raw_data"]):
                    item = shared_data["raw_data"][i]
                    processed_items[item] = f"processed_{item}"
            
            shared_data["processed_data"].update(processed_items)
            return {"processor": processor_id, "items_processed": len(processed_items)}
        return process_data
    
    async def create_aggregator(self, agg_type: str, shared_data: Dict):
        """Create an aggregator step."""
        async def aggregate_data():
            await asyncio.sleep(0.1)
            
            if agg_type == "count":
                result = len(shared_data["processed_data"])
            elif agg_type == "summary":
                result = list(shared_data["processed_data"].keys())[:5]
            else:
                result = "unknown"
            
            shared_data["aggregated_data"][agg_type] = result
            return {"aggregator": agg_type, "result": result}
        return aggregate_data
    
    async def create_report_generator(self, report_type: str, shared_data: Dict):
        """Create a report generator step."""
        async def generate_report():
            await asyncio.sleep(0.05)
            
            report = {
                "type": report_type,
                "timestamp": time.time(),
                "data_summary": shared_data["aggregated_data"]
            }
            shared_data["reports"].append(report)
            return {"report": report_type, "generated": True}
        return generate_report
    
    @pytest.mark.asyncio
    async def test_data_pipeline_parallel_execution(self, store, shared_data):
        """Test a complex data pipeline with parallel stages."""
        runner = ParallelStatefulDAGRunner(
            dag_id="data-pipeline",
            store=store,
            max_concurrent_steps=4
        )
        
        # Stage 1: Load data from multiple sources (parallel)
        runner.register_step(
            "load_source_a", 
            await self.create_data_loader("source_a", shared_data)
        )
        runner.register_step(
            "load_source_b", 
            await self.create_data_loader("source_b", shared_data)
        )
        
        # Stage 2: Process data in parallel (depends on loaders)
        runner.register_step(
            "process_1", 
            await self.create_data_processor("processor_1", shared_data),
            dependencies=["load_source_a", "load_source_b"]
        )
        runner.register_step(
            "process_2", 
            await self.create_data_processor("processor_2", shared_data),
            dependencies=["load_source_a", "load_source_b"]
        )
        runner.register_step(
            "process_3", 
            await self.create_data_processor("processor_3", shared_data),
            dependencies=["load_source_a", "load_source_b"]
        )
        runner.register_step(
            "process_4", 
            await self.create_data_processor("processor_4", shared_data),
            dependencies=["load_source_a", "load_source_b"]
        )
        
        # Stage 3: Aggregate results (depends on all processors)
        processor_deps = ["process_1", "process_2", "process_3", "process_4"]
        runner.register_step(
            "aggregate_count",
            await self.create_aggregator("count", shared_data),
            dependencies=processor_deps
        )
        runner.register_step(
            "aggregate_summary",
            await self.create_aggregator("summary", shared_data),
            dependencies=processor_deps
        )
        
        # Stage 4: Generate reports (depends on aggregators)
        runner.register_step(
            "report_full",
            await self.create_report_generator("full", shared_data),
            dependencies=["aggregate_count", "aggregate_summary"]
        )
        runner.register_step(
            "report_summary",
            await self.create_report_generator("summary", shared_data),
            dependencies=["aggregate_summary"]
        )
        
        # Execute pipeline
        start_time = time.time()
        result = await runner.execute()
        execution_time = time.time() - start_time
        
        # Verify successful completion
        assert result.status == DAGRunStatus.SUCCESS
        assert all(
            step.status == DAGStepStatus.SUCCESS 
            for step in result.steps.values()
        )
        
        # Verify data was processed correctly
        assert len(shared_data["raw_data"]) == 20  # 10 from each source
        assert len(shared_data["processed_data"]) == 20
        assert "count" in shared_data["aggregated_data"]
        assert "summary" in shared_data["aggregated_data"]
        assert len(shared_data["reports"]) == 2
        
        # Verify parallel execution improved performance
        # Sequential would take: 0.1*2 + 0.2*4 + 0.1*2 + 0.05*2 = 1.3s minimum
        # Parallel should be significantly faster
        assert execution_time < 0.8, f"Execution took {execution_time}s, expected < 0.8s"
        
        # Log execution summary
        print(f"\nPipeline executed in {execution_time:.2f}s")
        print(f"Total steps: {len(result.steps)}")
        print(f"Execution summary: {result.get_execution_summary()}")


class TestMultiAgentWorkflow:
    """Test parallel execution of a multi-agent workflow."""
    
    @pytest.fixture
    def store(self, tmp_path):
        """Create a temporary DAGRunStore."""
        return DAGRunStore(storage_dir=str(tmp_path / "dag_runs"))
    
    async def create_agent_task(self, agent_name: str, task_type: str, duration: float = 0.1):
        """Create an agent task executor."""
        async def execute_task():
            await asyncio.sleep(duration)
            return {
                "agent": agent_name,
                "task": task_type,
                "result": f"{agent_name} completed {task_type}",
                "duration": duration
            }
        return execute_task
    
    @pytest.mark.asyncio
    async def test_multi_agent_parallel_workflow(self, store):
        """Test a workflow with multiple agents working in parallel."""
        runner = ParallelStatefulDAGRunner(
            dag_id="multi-agent-workflow",
            store=store,
            max_concurrent_steps=5
        )
        
        # Phase 1: Initial analysis by different agents (parallel)
        runner.register_step(
            "content_analysis",
            await self.create_agent_task("ContentAgent", "analyze", 0.15)
        )
        runner.register_step(
            "sentiment_analysis",
            await self.create_agent_task("SentimentAgent", "analyze", 0.1)
        )
        runner.register_step(
            "topic_extraction",
            await self.create_agent_task("TopicAgent", "extract", 0.12)
        )
        
        # Phase 2: Enrichment based on initial analysis
        runner.register_step(
            "content_enrichment",
            await self.create_agent_task("ContentAgent", "enrich", 0.1),
            dependencies=["content_analysis", "topic_extraction"]
        )
        runner.register_step(
            "metadata_generation",
            await self.create_agent_task("MetadataAgent", "generate", 0.08),
            dependencies=["content_analysis", "sentiment_analysis"]
        )
        
        # Phase 3: Summarization (depends on enrichment)
        runner.register_step(
            "summary_generation",
            await self.create_agent_task("SummaryAgent", "summarize", 0.15),
            dependencies=["content_enrichment", "metadata_generation"]
        )
        
        # Phase 4: Final outputs (parallel)
        runner.register_step(
            "report_generation",
            await self.create_agent_task("ReportAgent", "generate", 0.1),
            dependencies=["summary_generation"]
        )
        runner.register_step(
            "notification_dispatch",
            await self.create_agent_task("NotificationAgent", "dispatch", 0.05),
            dependencies=["summary_generation"]
        )
        
        # Validate no circular dependencies
        errors = runner.validate_dependencies()
        assert len(errors) == 0, f"Dependency validation errors: {errors}"
        
        # Execute workflow
        start_time = time.time()
        result = await runner.execute()
        execution_time = time.time() - start_time
        
        # Verify successful completion
        assert result.status == DAGRunStatus.SUCCESS
        
        # Verify parallel execution
        # Sequential would take: 0.15+0.1+0.12+0.1+0.08+0.15+0.1+0.05 = 0.85s
        # Parallel should be significantly faster
        assert execution_time < 0.6, f"Execution took {execution_time}s, expected < 0.6s"
        
        # Verify execution order respected dependencies
        summary_step = result.steps["summary_generation"]
        enrichment_step = result.steps["content_enrichment"]
        metadata_step = result.steps["metadata_generation"]
        
        assert summary_step.start_time > enrichment_step.end_time
        assert summary_step.start_time > metadata_step.end_time


class TestErrorHandlingInParallel:
    """Test error handling during parallel execution."""
    
    @pytest.fixture
    def store(self, tmp_path):
        """Create a temporary DAGRunStore."""
        return DAGRunStore(storage_dir=str(tmp_path / "dag_runs"))
    
    @pytest.mark.asyncio
    async def test_partial_failure_with_parallel_branches(self, store):
        """Test handling of failures in parallel branches."""
        runner = ParallelStatefulDAGRunner(
            dag_id="parallel-failure-test",
            store=store
        )
        
        async def successful_task():
            await asyncio.sleep(0.05)
            return {"status": "success"}
        
        async def failing_task():
            await asyncio.sleep(0.1)
            raise Exception("Task failed!")
        
        # Create two parallel branches
        # Branch A: step1 -> step2 -> step3
        # Branch B: step4 (fails) -> step5
        
        runner.register_step("step1", successful_task)
        runner.register_step("step2", successful_task, dependencies=["step1"])
        runner.register_step("step3", successful_task, dependencies=["step2"])
        
        runner.register_step("step4", failing_task, critical=False)  # Non-critical
        runner.register_step("step5", successful_task, dependencies=["step4"])
        
        # Final step depends on both branches
        runner.register_step(
            "final_step", 
            successful_task, 
            dependencies=["step3", "step5"]
        )
        
        # Execute
        result = await runner.execute()
        
        # Verify partial success
        assert result.status == DAGRunStatus.PARTIAL_SUCCESS
        
        # Branch A should complete successfully
        assert result.steps["step1"].status == DAGStepStatus.SUCCESS
        assert result.steps["step2"].status == DAGStepStatus.SUCCESS
        assert result.steps["step3"].status == DAGStepStatus.SUCCESS
        
        # Branch B should fail and skip dependent
        assert result.steps["step4"].status == DAGStepStatus.FAILED
        assert result.steps["step5"].status == DAGStepStatus.SKIPPED
        
        # Final step should be skipped
        assert result.steps["final_step"].status == DAGStepStatus.SKIPPED
    
    @pytest.mark.asyncio
    async def test_retry_in_parallel_execution(self, store):
        """Test retry mechanism during parallel execution."""
        runner = ParallelStatefulDAGRunner(
            dag_id="parallel-retry-test",
            store=store
        )
        
        attempt_counts = {}
        
        async def flaky_task(task_id: str, fail_attempts: int = 2):
            if task_id not in attempt_counts:
                attempt_counts[task_id] = 0
            
            attempt_counts[task_id] += 1
            
            if attempt_counts[task_id] < fail_attempts:
                raise Exception(f"Attempt {attempt_counts[task_id]} failed")
            
            return {"task": task_id, "attempts": attempt_counts[task_id]}
        
        # Register parallel tasks with retry
        runner.register_step(
            "flaky1",
            lambda: flaky_task("flaky1", 2),
            max_retries=3
        )
        runner.register_step(
            "flaky2",
            lambda: flaky_task("flaky2", 3),
            max_retries=3
        )
        runner.register_step(
            "dependent",
            lambda: flaky_task("dependent", 1),
            dependencies=["flaky1", "flaky2"]
        )
        
        # Execute
        result = await runner.execute()
        
        # Verify success after retries
        assert result.status == DAGRunStatus.SUCCESS
        
        # Verify retry counts
        assert result.steps["flaky1"].retry_count == 1  # Failed once, succeeded on retry
        assert result.steps["flaky2"].retry_count == 2  # Failed twice, succeeded on 3rd attempt
        assert result.steps["dependent"].retry_count == 0  # Succeeded on first try