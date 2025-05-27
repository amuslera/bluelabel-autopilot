"""
Unit tests for DAGRun export functionality.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, Mock

from services.workflow.dag_run_tracker import DAGRun, DAGStepState, DAGStepStatus, DAGRunStatus
from services.workflow.dag_run_exporter import (
    DAGRunExporter,
    ExportFormat,
    ExportValidationError
)
from services.workflow.dag_run_store import DAGRunStore


@pytest.fixture
def sample_dag_run():
    """Create a sample DAGRun for testing."""
    dag_run = DAGRun(dag_id="test_dag")
    dag_run.start()
    
    # Add some steps
    step1 = dag_run.add_step("step1")
    step1.start()
    step1.complete({"result": "success"})
    
    step2 = dag_run.add_step("step2")
    step2.start()
    step2.fail("Test error")
    
    step3 = dag_run.add_step("step3")
    step3.start()
    step3.retry()
    step3.complete({"result": "retry_success"})
    
    dag_run.complete()
    return dag_run


@pytest.fixture
def mock_dag_store():
    """Create a mock DAGRunStore."""
    store = Mock(spec=DAGRunStore)
    return store


@pytest.fixture
def mock_dag_run():
    """Create a mock DAGRun."""
    run = Mock(spec=DAGRun)
    run.to_dict.return_value = {
        "id": "test-run-123",
        "status": DAGRunStatus.SUCCESS.value,
        "steps": {
            "step1": {"status": "success"},
            "step2": {"status": "success"}
        }
    }
    return run


@pytest.fixture
def exporter(mock_dag_store):
    """Create a DAGRunExporter instance."""
    return DAGRunExporter(mock_dag_store)


def test_export_json(exporter, sample_dag_run, tmp_path):
    """Test JSON export functionality."""
    output_path = tmp_path / "test_export.json"
    
    # Export
    result_path = exporter.export_json(sample_dag_run, output_path)
    
    # Verify file exists
    assert result_path.exists()
    
    # Load and verify content
    with open(result_path) as f:
        data = json.load(f)
    
    assert data["dag_id"] == "test_dag"
    assert data["status"] == "partial_success"
    assert len(data["steps"]) == 3
    
    # Verify step data
    assert data["steps"]["step1"]["status"] == "success"
    assert data["steps"]["step2"]["status"] == "failed"
    assert data["steps"]["step3"]["status"] == "success"
    
    # Verify summary
    assert "summary" in data
    assert data["summary"]["total_steps"] == 3
    assert data["summary"]["success_rate"] > 0


def test_export_html(exporter, sample_dag_run, tmp_path):
    """Test HTML export functionality."""
    output_path = tmp_path / "test_export.html"
    
    # Export
    result_path = exporter.export_html(sample_dag_run, output_path)
    
    # Verify file exists
    assert result_path.exists()
    
    # Load and verify content
    content = result_path.read_text()
    
    # Check for key elements
    assert "DAG Run Report" in content
    assert "test_dag" in content
    assert "step1" in content
    assert "step2" in content
    assert "step3" in content
    assert "Test error" in content


def test_status_class_mapping(exporter):
    """Test status class mapping for HTML export."""
    assert exporter._get_status_class(DAGStepStatus.SUCCESS) == "success"
    assert exporter._get_status_class(DAGStepStatus.FAILED) == "danger"
    assert exporter._get_status_class(DAGStepStatus.RUNNING) == "info"
    assert exporter._get_status_class(DAGStepStatus.PENDING) == "secondary"
    assert exporter._get_status_class(DAGStepStatus.RETRY) == "warning"
    assert exporter._get_status_class(DAGStepStatus.SKIPPED) == "light"
    assert exporter._get_status_class(DAGStepStatus.CANCELLED) == "dark"


def test_duration_formatting(exporter):
    """Test duration formatting."""
    assert exporter._format_duration(None) == "N/A"
    assert exporter._format_duration(30) == "30.0s"
    assert exporter._format_duration(90) == "1.5m"
    assert exporter._format_duration(3600) == "1.0h"
    assert exporter._format_duration(7200) == "2.0h"


def test_export_with_missing_data(exporter, tmp_path):
    """Test export with minimal DAGRun data."""
    # Create minimal DAGRun
    dag_run = DAGRun(dag_id="minimal_dag")
    dag_run.start()
    step = dag_run.add_step("minimal_step")
    step.start()
    dag_run.complete()
    
    # Test JSON export
    json_path = tmp_path / "minimal.json"
    exporter.export_json(dag_run, json_path)
    with open(json_path) as f:
        data = json.load(f)
    assert data["dag_id"] == "minimal_dag"
    assert len(data["steps"]) == 1
    
    # Test HTML export
    html_path = tmp_path / "minimal.html"
    exporter.export_html(dag_run, html_path)
    content = html_path.read_text()
    assert "minimal_dag" in content
    assert "minimal_step" in content


def test_validate_format_valid(exporter):
    """Test format validation with valid formats."""
    assert exporter.validate_format("json") == ExportFormat.JSON
    assert exporter.validate_format("HTML") == ExportFormat.HTML
    assert exporter.validate_format("Json") == ExportFormat.JSON


def test_validate_format_invalid(exporter):
    """Test format validation with invalid formats."""
    with pytest.raises(ExportValidationError) as exc:
        exporter.validate_format("xml")
    assert "Unsupported export format" in str(exc.value)
    assert "json, html" in str(exc.value).lower()


def test_check_size_within_limit(exporter):
    """Test size check with content within limit."""
    content = "x" * (DAGRunExporter.SIZE_LIMIT - 100)
    assert exporter._check_size(content) is None


def test_check_size_exceeds_limit(exporter):
    """Test size check with content exceeding limit."""
    content = "x" * (DAGRunExporter.SIZE_LIMIT + 100)
    warning = exporter._check_size(content)
    assert warning is not None
    assert "Warning" in warning
    assert "KB" in warning


def test_export_json(exporter, mock_dag_store, mock_dag_run):
    """Test JSON export."""
    mock_dag_store.get.return_value = mock_dag_run
    
    result = exporter.export("test-run-123", "json")
    
    assert result["format"] == "json"
    assert result["warning"] is None
    assert json.loads(result["content"]) == mock_dag_run.to_dict()


def test_export_html(exporter, mock_dag_store, mock_dag_run):
    """Test HTML export."""
    mock_dag_store.get.return_value = mock_dag_run
    
    with patch("jinja2.Environment.get_template") as mock_template:
        mock_template.return_value.render.return_value = "<html>Test</html>"
        
        result = exporter.export("test-run-123", "html")
        
        assert result["format"] == "html"
        assert result["content"] == "<html>Test</html>"
        mock_template.assert_called_once_with("dag_run_report.html")


def test_export_dag_not_found(exporter, mock_dag_store):
    """Test export with non-existent DAGRun."""
    mock_dag_store.get.return_value = None
    
    with pytest.raises(ValueError) as exc:
        exporter.export("non-existent", "json")
    assert "DAGRun not found" in str(exc.value)


def test_export_large_content(exporter, mock_dag_store, mock_dag_run):
    """Test export with large content."""
    mock_dag_store.get.return_value = mock_dag_run
    mock_dag_run.to_dict.return_value = {
        "id": "test-run-123",
        "content": "x" * (DAGRunExporter.SIZE_LIMIT + 1000)
    }
    
    result = exporter.export("test-run-123", "json")
    
    assert result["format"] == "json"
    assert result["warning"] is not None
    assert "Warning" in result["warning"]
    assert "KB" in result["warning"] 