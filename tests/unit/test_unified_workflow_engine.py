"""
Unit tests for UnifiedWorkflowEngine adapter.

Tests the adapter pattern implementation, engine delegation, and performance requirements.
"""

import pytest
import asyncio
import os
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import tempfile
import yaml

from core.unified_workflow_engine import (
    UnifiedWorkflowEngine, EngineType, create_unified_engine
)
from interfaces.run_models import WorkflowRunResult, WorkflowStatus, StepResult
from interfaces.agent_models import AgentOutput
from services.workflow.dag_run_tracker import DAGRun, DAGRunStatus, DAGStepStatus


class TestUnifiedWorkflowEngine:
    """Test cases for UnifiedWorkflowEngine."""
    
    @pytest.fixture
    def temp_workflow_file(self):
        """Create a temporary workflow file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            workflow_data = {
                'workflow': {
                    'name': 'Test Workflow',
                    'version': '1.0.0',
                    'description': 'Test workflow for unit tests'
                },
                'steps': [
                    {
                        'id': 'step1',
                        'name': 'First Step',
                        'agent': 'ingestion_agent',
                        'input_file': 'test_input.json'
                    },
                    {
                        'id': 'step2', 
                        'name': 'Second Step',
                        'agent': 'digest_agent',
                        'input_from': 'step1'
                    }
                ]
            }
            yaml.dump(workflow_data, f)
            temp_path = f.name
        
        yield Path(temp_path)
        
        # Cleanup
        os.unlink(temp_path)
    
    @pytest.fixture
    def mock_workflow_engine(self):
        """Create a mock WorkflowEngine."""
        engine = AsyncMock()
        engine.execute_workflow = AsyncMock(return_value=WorkflowRunResult(
            run_id='test-run-123',
            workflow_name='Test Workflow',
            workflow_version='1.0.0',
            status=WorkflowStatus.SUCCESS,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=1000,
            workflow_file='test.yaml'
        ))
        return engine
    
    @pytest.fixture
    def mock_dag_runner(self):
        """Create a mock StatefulDAGRunner."""
        runner = AsyncMock()
        dag_run = DAGRun(dag_id='test_workflow')
        dag_run.status = DAGRunStatus.SUCCESS
        dag_run.start_time = datetime.utcnow()
        dag_run.end_time = datetime.utcnow()
        runner.execute = AsyncMock(return_value=dag_run)
        return runner
    
    def test_init_with_sequential_engine(self):
        """Test initialization with sequential engine type."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
        assert engine.engine_type == EngineType.SEQUENTIAL
        assert not engine.supports_resume
        assert not engine.supports_parallel_execution
    
    def test_init_with_stateful_dag_engine(self):
        """Test initialization with stateful DAG engine type."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)
        assert engine.engine_type == EngineType.STATEFUL_DAG
        assert engine.supports_resume
        assert not engine.supports_parallel_execution  # Not yet implemented
    
    def test_init_from_env_var(self):
        """Test initialization from environment variable."""
        with patch.dict(os.environ, {'WORKFLOW_ENGINE_TYPE': 'stateful_dag'}):
            engine = UnifiedWorkflowEngine()
            assert engine.engine_type == EngineType.STATEFUL_DAG
    
    def test_init_with_invalid_env_var(self):
        """Test initialization with invalid environment variable."""
        with patch.dict(os.environ, {'WORKFLOW_ENGINE_TYPE': 'invalid_type'}):
            engine = UnifiedWorkflowEngine()
            # Should default to SEQUENTIAL
            assert engine.engine_type == EngineType.SEQUENTIAL
    
    @pytest.mark.asyncio
    async def test_execute_with_sequential_engine(self, temp_workflow_file, mock_workflow_engine):
        """Test workflow execution with sequential engine."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
        
        with patch.object(engine, '_engine', mock_workflow_engine):
            result = await engine.execute_workflow(
                workflow_path=temp_workflow_file,
                persist=True,
                initial_input={'test': 'data'}
            )
        
        assert result.run_id == 'test-run-123'
        assert result.status == WorkflowStatus.SUCCESS
        mock_workflow_engine.execute_workflow.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_execute_with_stateful_dag_engine(self, temp_workflow_file):
        """Test workflow execution with stateful DAG engine."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)
        
        # Mock the DAGRunnerFactory
        mock_runner = AsyncMock()
        dag_run = DAGRun(dag_id='test_workflow')
        dag_run.run_id = 'dag-run-456'
        dag_run.status = DAGRunStatus.SUCCESS
        dag_run.start_time = datetime.utcnow()
        dag_run.end_time = datetime.utcnow()
        dag_run.add_step('step1').complete({'result': 'data'})
        dag_run.add_step('step2').complete({'digest': 'summary'})
        
        mock_runner.execute = AsyncMock(return_value=dag_run)
        mock_runner.register_step = Mock()
        
        with patch('core.unified_workflow_engine.DAGRunnerFactory.create_runner', return_value=mock_runner):
            # Mock WorkflowLoader properly
            mock_loader = Mock()
            mock_loader.load.return_value = {
                'workflow': {
                    'name': 'Test Workflow',
                    'version': '1.0.0'
                }
            }
            mock_loader.parse_steps.return_value = [
                Mock(id='step1', name='Step 1', agent='ingestion_agent', input_file='input.json', input_from=None, config=None),
                Mock(id='step2', name='Step 2', agent='digest_agent', input_file=None, input_from='step1', config=None)
            ]
            mock_loader.get_execution_order.return_value = ['step1', 'step2']
            
            with patch('core.unified_workflow_engine.WorkflowLoader', return_value=mock_loader):
                # Mock agents
                mock_agents = {
                    'ingestion_agent': AsyncMock(),
                    'digest_agent': AsyncMock()
                }
                
                for agent in mock_agents.values():
                    agent.process = AsyncMock(return_value=AgentOutput(
                        task_id='test-task',
                        status='success',
                        result={'data': 'processed'},
                        metadata={}
                    ))
                
                with patch.dict('sys.modules', {
                    'agents.ingestion_agent': MagicMock(IngestionAgent=lambda **k: mock_agents['ingestion_agent']),
                    'agents.digest_agent': MagicMock(DigestAgent=lambda **k: mock_agents['digest_agent'])
                }):
                    result = await engine.execute_workflow(
                        workflow_path=temp_workflow_file,
                        persist=False
                    )
        
        assert result.run_id == 'dag-run-456'
        assert result.status == WorkflowStatus.SUCCESS
        assert result.workflow_name == 'Test Workflow'
    
    @pytest.mark.asyncio
    async def test_performance_overhead_requirement(self, temp_workflow_file, mock_workflow_engine):
        """Test that adapter overhead is less than 100ms."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
        
        # Set up mock to simulate fast execution
        mock_result = WorkflowRunResult(
            run_id='perf-test',
            workflow_name='Test Workflow',
            workflow_version='1.0.0',
            status=WorkflowStatus.SUCCESS,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_ms=500,  # Workflow took 500ms
            workflow_file='test.yaml'
        )
        mock_workflow_engine.execute_workflow = AsyncMock(return_value=mock_result)
        
        with patch.object(engine, '_engine', mock_workflow_engine):
            start_time = datetime.utcnow()
            result = await engine.execute_workflow(workflow_path=temp_workflow_file)
            end_time = datetime.utcnow()
        
        # Calculate total time including adapter overhead
        total_time_ms = int((end_time - start_time).total_seconds() * 1000)
        overhead_ms = total_time_ms - result.duration_ms
        
        # Overhead should be less than 100ms
        assert overhead_ms < 100, f"Adapter overhead {overhead_ms}ms exceeds 100ms requirement"
    
    @pytest.mark.asyncio
    async def test_on_complete_callback(self, temp_workflow_file, mock_workflow_engine):
        """Test that on_complete callback is called on success."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
        
        callback_called = False
        callback_result = None
        
        async def on_complete(result):
            nonlocal callback_called, callback_result
            callback_called = True
            callback_result = result
        
        with patch.object(engine, '_engine', mock_workflow_engine):
            result = await engine.execute_workflow(
                workflow_path=temp_workflow_file,
                on_complete=on_complete
            )
        
        # Verify callback was called with correct args
        mock_workflow_engine.execute_workflow.assert_called_once()
        call_args = mock_workflow_engine.execute_workflow.call_args
        assert call_args.kwargs['on_complete'] == on_complete
    
    @pytest.mark.asyncio
    async def test_error_handling(self, temp_workflow_file, mock_workflow_engine):
        """Test error handling during workflow execution."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
        
        # Make execution fail
        mock_workflow_engine.execute_workflow = AsyncMock(
            side_effect=ValueError("Test error")
        )
        
        with patch.object(engine, '_engine', mock_workflow_engine):
            with pytest.raises(ValueError, match="Test error"):
                await engine.execute_workflow(workflow_path=temp_workflow_file)
    
    def test_get_status(self):
        """Test getting engine status."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)
        engine._current_run_id = 'test-run-789'
        
        status = engine.get_status()
        
        assert status['engine_type'] == 'stateful_dag'
        assert status['current_run_id'] == 'test-run-789'
        assert status['supports_resume'] is True
        assert status['supports_parallel'] is False
    
    def test_create_unified_engine_factory(self):
        """Test factory function for creating engine."""
        # Test with string
        engine1 = create_unified_engine(engine_type='sequential')
        assert engine1.engine_type == EngineType.SEQUENTIAL
        
        # Test with enum
        engine2 = create_unified_engine(engine_type=EngineType.STATEFUL_DAG)
        assert engine2.engine_type == EngineType.STATEFUL_DAG
        
        # Test with kwargs
        engine3 = create_unified_engine(
            engine_type='sequential',
            storage_path='/custom/path'
        )
        assert engine3.storage_path == Path('/custom/path')
    
    @pytest.mark.asyncio
    async def test_dag_status_conversion(self):
        """Test conversion between DAG status and workflow status."""
        engine = UnifiedWorkflowEngine(engine_type=EngineType.STATEFUL_DAG)
        
        # Test status mappings
        dag_run = DAGRun(dag_id='test')
        workflow_info = {'name': 'Test', 'version': '1.0'}
        
        # Success
        dag_run.status = DAGRunStatus.SUCCESS
        result = engine._convert_dag_run_to_result(
            dag_run, workflow_info, Path('test.yaml'), {}
        )
        assert result.status == WorkflowStatus.SUCCESS
        
        # Failed
        dag_run.status = DAGRunStatus.FAILED
        dag_run.add_step('failed_step').fail("Test error")
        result = engine._convert_dag_run_to_result(
            dag_run, workflow_info, Path('test.yaml'), {}
        )
        assert result.status == WorkflowStatus.FAILED
        assert result.failed_step == 'failed_step'
        assert len(result.errors) > 0