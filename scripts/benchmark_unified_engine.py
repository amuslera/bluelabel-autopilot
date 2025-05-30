#!/usr/bin/env python3
"""
Performance benchmark for UnifiedWorkflowEngine adapter overhead.

This script measures the performance overhead introduced by the UnifiedWorkflowEngine
adapter compared to direct engine usage.
"""

import asyncio
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import yaml
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType
from core.workflow_engine import WorkflowEngine
from interfaces.agent_models import AgentInput, AgentOutput, AgentCapability
from core.agent_registry import AgentRegistry, register_agent
from agents.base_agent import BaseAgent


class MockAgent(BaseAgent):
    """Mock agent for performance testing."""
    
    def __init__(self, delay_ms: int = 10):
        super().__init__(
            name="Mock Agent",
            description="Mock agent for performance testing"
        )
        self.delay_ms = delay_ms
        self.capabilities = []
    
    async def initialize(self) -> None:
        """Initialize the agent."""
        self._initialized = True
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process input with controlled delay."""
        # Simulate processing with controlled delay
        await asyncio.sleep(self.delay_ms / 1000)
        
        return AgentOutput(
            task_id=input_data.task_id,
            status="success",
            result={"processed": True, "data": input_data.content},
            metadata={"processing_time_ms": self.delay_ms}
        )
    
    async def shutdown(self) -> None:
        """Shutdown the agent."""
        pass
    
    def get_capabilities(self) -> List[AgentCapability]:
        """Get agent capabilities."""
        return self.capabilities


def create_test_workflow(temp_dir: Path, num_steps: int = 3) -> Path:
    """Create a test workflow file."""
    workflow_data = {
        'workflow': {
            'name': 'Performance Test Workflow',
            'version': '1.0.0',
            'description': 'Workflow for performance testing'
        },
        'steps': []
    }
    
    # Create steps
    for i in range(num_steps):
        if i == 0:
            # First step with file input
            input_file = temp_dir / f"input_{i}.json"
            with open(input_file, 'w') as f:
                json.dump({
                    'task_id': f'perf-test-{i}',
                    'source': 'test',
                    'content': {'step': i, 'data': 'test'},
                    'metadata': {}
                }, f)
            
            step = {
                'id': f'step{i}',
                'name': f'Step {i}',
                'agent': 'mock_agent',
                'input_file': str(input_file)
            }
        else:
            # Subsequent steps with input from previous
            step = {
                'id': f'step{i}',
                'name': f'Step {i}',
                'agent': 'mock_agent',
                'input_from': f'step{i-1}'
            }
        
        workflow_data['steps'].append(step)
    
    # Write workflow file
    workflow_file = temp_dir / "test_workflow.yaml"
    with open(workflow_file, 'w') as f:
        yaml.dump(workflow_data, f)
    
    return workflow_file


async def benchmark_direct_engine(workflow_path: Path, runs: int = 10) -> List[float]:
    """Benchmark direct WorkflowEngine execution."""
    times = []
    
    # Temporarily add mock_agent to allowed agents
    from services.validation.workflow_validator import WorkflowValidator
    original_agents = WorkflowValidator.ALLOWED_AGENTS.copy()
    WorkflowValidator.ALLOWED_AGENTS.add('mock_agent')
    
    try:
        for _ in range(runs):
            engine = WorkflowEngine()
            
            # Register mock agent
            engine.agent_registry.register('mock_agent', MockAgent)
            
            start_time = time.perf_counter()
            result = await engine.execute_workflow(
                workflow_path=workflow_path,
                persist=False
            )
            end_time = time.perf_counter()
            
            if result.status.value != "success":
                raise Exception(f"Workflow failed: {result.errors}")
            
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            times.append(execution_time)
    finally:
        # Restore original allowed agents
        WorkflowValidator.ALLOWED_AGENTS = original_agents
    
    return times


async def benchmark_unified_engine(workflow_path: Path, engine_type: EngineType, runs: int = 10) -> List[float]:
    """Benchmark UnifiedWorkflowEngine execution."""
    times = []
    
    # Temporarily add mock_agent to allowed agents
    from services.validation.workflow_validator import WorkflowValidator
    from core.performance import workflow_cache
    
    original_agents = WorkflowValidator.ALLOWED_AGENTS.copy()
    WorkflowValidator.ALLOWED_AGENTS.add('mock_agent')
    
    try:
        # Clear workflow cache to ensure fresh execution
        workflow_cache.clear()
        
        # Register mock agent globally for unified engine
        register_agent('mock_agent', MockAgent)
        
        for i in range(runs):
            # Clear cache between runs for accurate measurements
            workflow_cache.clear()
            
            engine = UnifiedWorkflowEngine(engine_type=engine_type)
            
            start_time = time.perf_counter()
            result = await engine.execute_workflow(
                workflow_path=workflow_path,
                persist=False
            )
            end_time = time.perf_counter()
            
            if result.status.value != "success":
                raise Exception(f"Workflow failed: {result.errors}")
            
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            times.append(execution_time)
    finally:
        # Restore original allowed agents
        WorkflowValidator.ALLOWED_AGENTS = original_agents
    
    return times


def calculate_stats(times: List[float]) -> Dict[str, float]:
    """Calculate statistics from timing data."""
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times)
    }


async def run_benchmarks():
    """Run performance benchmarks."""
    print("UnifiedWorkflowEngine Performance Benchmark")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test with different workflow sizes
        for num_steps in [1, 3, 5]:
            print(f"\nTesting with {num_steps} steps:")
            print("-" * 30)
            
            workflow_path = create_test_workflow(temp_path, num_steps)
            
            # Warm-up run
            print("Warming up...")
            await benchmark_direct_engine(workflow_path, runs=2)
            await benchmark_unified_engine(workflow_path, EngineType.SEQUENTIAL, runs=2)
            
            # Actual benchmarks
            print("Running benchmarks...")
            
            # Direct engine
            direct_times = await benchmark_direct_engine(workflow_path, runs=20)
            direct_stats = calculate_stats(direct_times)
            
            # Unified engine - Sequential
            unified_seq_times = await benchmark_unified_engine(workflow_path, EngineType.SEQUENTIAL, runs=20)
            unified_seq_stats = calculate_stats(unified_seq_times)
            
            # Calculate overhead
            overhead_ms = unified_seq_stats['mean'] - direct_stats['mean']
            overhead_percent = (overhead_ms / direct_stats['mean']) * 100
            
            # Print results
            print(f"\nDirect WorkflowEngine:")
            print(f"  Mean: {direct_stats['mean']:.2f}ms")
            print(f"  Median: {direct_stats['median']:.2f}ms")
            print(f"  StdDev: {direct_stats['stdev']:.2f}ms")
            print(f"  Range: {direct_stats['min']:.2f}ms - {direct_stats['max']:.2f}ms")
            
            print(f"\nUnified (Sequential):")
            print(f"  Mean: {unified_seq_stats['mean']:.2f}ms")
            print(f"  Median: {unified_seq_stats['median']:.2f}ms")
            print(f"  StdDev: {unified_seq_stats['stdev']:.2f}ms")
            print(f"  Range: {unified_seq_stats['min']:.2f}ms - {unified_seq_stats['max']:.2f}ms")
            
            print(f"\nAdapter Overhead:")
            print(f"  Absolute: {overhead_ms:.2f}ms")
            print(f"  Relative: {overhead_percent:.1f}%")
            print(f"  Requirement: <100ms {'✅ PASS' if overhead_ms < 100 else '❌ FAIL'}")
    
    print("\n" + "=" * 50)
    print("Benchmark complete!")


if __name__ == "__main__":
    asyncio.run(run_benchmarks())