"""
Unit tests for DAG trace exporter.
"""

import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch

from services.workflow.dag_run_tracker import DAGRun, DAGStepState, DAGRunStatus
from services.workflow.dag_trace_exporter import DAGTraceExporter

class TestDAGTraceExporter:
    """Test DAG trace exporter functionality."""
    
    @pytest.fixture
    def mock_dag_run(self):
        """Create a mock DAG run for testing."""
        # Create mock steps
        steps = {
            "step1": DAGStepState(
                step_id="step1",
                status=DAGRunStatus.SUCCESS,
                started_at=datetime.now(),
                completed_at=datetime.now() + timedelta(seconds=5),
                duration=5.0,
                retry_count=0,
                result={"output": "Step 1 completed"}
            ),
            "step2": DAGStepState(
                step_id="step2",
                status=DAGRunStatus.FAILED,
                started_at=datetime.now() + timedelta(seconds=5),
                completed_at=datetime.now() + timedelta(seconds=8),
                duration=3.0,
                retry_count=2,
                error="Step 2 failed"
            ),
            "step3": DAGStepState(
                step_id="step3",
                status=DAGRunStatus.PENDING,
                started_at=None,
                completed_at=None,
                duration=None,
                retry_count=0
            )
        }
        
        # Create mock DAG run
        dag_run = Mock(spec=DAGRun)
        dag_run.dag_id = "test_dag"
        dag_run.run_id = "test_run_123"
        dag_run.status = DAGRunStatus.PARTIAL_SUCCESS
        dag_run.created_at = datetime.now()
        dag_run.updated_at = datetime.now() + timedelta(seconds=10)
        dag_run.duration = 10.0
        dag_run.steps = steps
        dag_run.metadata = {
            "input": {"source": "test"},
            "metrics": {"total_time": 10.0}
        }
        dag_run.error = None
        
        return dag_run
    
    @pytest.fixture
    def mock_dag_store(self, mock_dag_run):
        """Create a mock DAG store."""
        store = Mock()
        store.get.return_value = mock_dag_run
        return store
    
    def test_export_html_success(self, mock_dag_store, tmp_path):
        """Test successful HTML export."""
        # Setup
        exporter = DAGTraceExporter(dag_store=mock_dag_store)
        
        # Export trace
        content = exporter.export_trace("test_run_123", "html")
        
        # Verify HTML content
        assert "<!DOCTYPE html>" in content
        assert "test_dag" in content
        assert "test_run_123" in content
        assert "PARTIAL_SUCCESS" in content
        
        # Verify step data
        assert "step1" in content
        assert "step2" in content
        assert "step3" in content
        assert "Step 1 completed" in content
        assert "Step 2 failed" in content
        
        # Verify metadata
        assert "input" in content
        assert "metrics" in content
    
    def test_export_missing_trace(self, mock_dag_store):
        """Test export with missing trace."""
        # Setup
        mock_dag_store.get.return_value = None
        exporter = DAGTraceExporter(dag_store=mock_dag_store)
        
        # Attempt export
        with pytest.raises(FileNotFoundError):
            exporter.export_trace("nonexistent_run", "html")
    
    def test_export_unsupported_format(self, mock_dag_store):
        """Test export with unsupported format."""
        # Setup
        exporter = DAGTraceExporter(dag_store=mock_dag_store)
        
        # Attempt export
        with pytest.raises(ValueError):
            exporter.export_trace("test_run_123", "unsupported")
    
    def test_format_duration(self, mock_dag_store):
        """Test duration formatting."""
        exporter = DAGTraceExporter(dag_store=mock_dag_store)
        
        # Test milliseconds
        assert exporter._format_duration(0.5) == "500ms"
        
        # Test seconds
        assert exporter._format_duration(5.5) == "5.5s"
        
        # Test minutes
        assert exporter._format_duration(65.5) == "1m 5.5s"
        
        # Test None
        assert exporter._format_duration(None) == "N/A"
    
    def test_prepare_step_data(self, mock_dag_store, mock_dag_run):
        """Test step data preparation."""
        exporter = DAGTraceExporter(dag_store=mock_dag_store)
        
        # Prepare step data
        step_data = exporter._prepare_step_data(mock_dag_run.steps)
        
        # Verify structure
        assert len(step_data) == 3
        
        # Verify step1 data
        step1 = next(s for s in step_data if s["id"] == "step1")
        assert step1["status"] == "SUCCESS"
        assert step1["duration"] == "5.0s"
        assert step1["retries"] == 0
        assert step1["result"] == {"output": "Step 1 completed"}
        
        # Verify step2 data
        step2 = next(s for s in step_data if s["id"] == "step2")
        assert step2["status"] == "FAILED"
        assert step2["duration"] == "3.0s"
        assert step2["retries"] == 2
        assert step2["error"] == "Step 2 failed"
        
        # Verify step3 data
        step3 = next(s for s in step_data if s["id"] == "step3")
        assert step3["status"] == "PENDING"
        assert step3["duration"] == "N/A"
        assert step3["retries"] == 0 