"""Unit tests for the run_dag CLI command."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from apps.cli.commands.run_dag import (
    parse_args,
    get_dag_run,
    run_dag,
    check_status,
    retry_failed
)
from interfaces.run_models import DAGRun, DAGRunStatus

def test_parse_args_workflow():
    """Test parsing workflow argument."""
    args = parse_args(["workflow.yaml"])
    assert args.workflow == "workflow.yaml"
    assert not args.status
    assert not args.retry

def test_parse_args_status():
    """Test parsing status argument."""
    args = parse_args(["--status", "run123"])
    assert args.status == "run123"
    assert not args.workflow
    assert not args.retry

def test_parse_args_retry():
    """Test parsing retry argument."""
    args = parse_args(["--retry", "run123"])
    assert args.retry == "run123"
    assert not args.workflow
    assert not args.status

def test_parse_args_verbose():
    """Test parsing verbose flag."""
    args = parse_args(["workflow.yaml", "--verbose"])
    assert args.verbose
    assert args.workflow == "workflow.yaml"

def test_parse_args_output_dir():
    """Test parsing output directory."""
    args = parse_args(["workflow.yaml", "--output-dir", "output"])
    assert args.output_dir == "output"
    assert args.workflow == "workflow.yaml"

def test_get_dag_run():
    """Test getting DAG run from tracker."""
    run_id = "test123"
    dag_run = get_dag_run(run_id)
    
    assert isinstance(dag_run, DAGRun)
    assert dag_run.run_id == run_id
    assert dag_run.workflow_id == "test_workflow"
    assert dag_run.status == DAGRunStatus.RUNNING
    assert len(dag_run.steps) == 2

@patch("apps.cli.commands.run_dag.WorkflowEngine")
def test_run_dag(mock_engine):
    """Test running a new DAG."""
    mock_engine.return_value.execute_workflow.return_value = "new_run_id"
    
    run_dag("workflow.yaml", "output")
    
    mock_engine.return_value.execute_workflow.assert_called_once_with(
        "workflow.yaml",
        "output"
    )

@patch("apps.cli.commands.run_dag.get_dag_run")
@patch("apps.cli.commands.run_dag.print_dag_status")
def test_check_status(mock_print, mock_get):
    """Test checking DAG status."""
    mock_run = DAGRun(
        run_id="test123",
        workflow_id="test_workflow",
        status=DAGRunStatus.RUNNING,
        steps=[]
    )
    mock_get.return_value = mock_run
    
    check_status("test123", verbose=True)
    
    mock_get.assert_called_once_with("test123")
    mock_print.assert_called_once_with(mock_run, True)

@patch("apps.cli.commands.run_dag.get_dag_run")
@patch("apps.cli.commands.run_dag.WorkflowEngine")
def test_retry_failed(mock_engine, mock_get):
    """Test retrying failed steps."""
    mock_run = DAGRun(
        run_id="test123",
        workflow_id="test_workflow",
        status=DAGRunStatus.FAILED,
        steps=[]
    )
    mock_get.return_value = mock_run
    mock_engine.return_value.retry_failed_steps.return_value = "new_run_id"
    
    retry_failed("test123")
    
    mock_get.assert_called_once_with("test123")
    mock_engine.return_value.retry_failed_steps.assert_called_once_with(mock_run)

def test_check_status_not_found():
    """Test checking status of non-existent DAG run."""
    with pytest.raises(SystemExit):
        check_status("nonexistent")

def test_retry_failed_not_found():
    """Test retrying non-existent DAG run."""
    with pytest.raises(SystemExit):
        retry_failed("nonexistent") 