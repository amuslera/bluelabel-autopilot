import json
import os
import pytest
from pathlib import Path
from datetime import datetime
from runner.workflow_storage import WorkflowStorage

@pytest.fixture
def storage(tmp_path):
    """Create a WorkflowStorage instance with a temporary base path."""
    return WorkflowStorage(base_path=str(tmp_path))

@pytest.fixture
def sample_workflow_yaml():
    """Sample workflow YAML content."""
    return """
workflow:
  name: "Test Workflow"
  description: "A test workflow"
  version: "1.0.0"

steps:
  - id: step1
    agent: test_agent
    input: test_input
"""

@pytest.fixture
def sample_metadata():
    """Sample run metadata."""
    return {
        "workflow_name": "Test Workflow",
        "version": "1.0.0",
        "config": {
            "use_uuid": False,
            "max_retries": 3
        }
    }

def test_create_run_directory(storage):
    """Test creating a run directory."""
    workflow_id = "test_workflow"
    run_path = storage.create_run_directory(workflow_id)
    
    assert run_path.exists()
    assert run_path.is_dir()
    assert run_path.parent.name == workflow_id
    assert run_path.name.startswith("202")  # Timestamp format

def test_create_run_directory_with_uuid(storage):
    """Test creating a run directory with UUID."""
    workflow_id = "test_workflow"
    run_path = storage.create_run_directory(workflow_id, use_uuid=True)
    
    assert run_path.exists()
    assert run_path.is_dir()
    assert run_path.parent.name == workflow_id
    assert len(run_path.name) == 36  # UUID length

def test_save_workflow_definition(storage, sample_workflow_yaml):
    """Test saving workflow definition."""
    workflow_id = "test_workflow"
    run_path = storage.create_run_directory(workflow_id)
    storage.save_workflow_definition(run_path, sample_workflow_yaml)
    
    workflow_file = run_path / "workflow.yaml"
    assert workflow_file.exists()
    with open(workflow_file) as f:
        content = f.read()
    assert "Test Workflow" in content

def test_save_run_metadata(storage, sample_metadata):
    """Test saving run metadata."""
    workflow_id = "test_workflow"
    run_path = storage.create_run_directory(workflow_id)
    storage.save_run_metadata(run_path, sample_metadata)
    
    metadata_file = run_path / "run_metadata.json"
    assert metadata_file.exists()
    with open(metadata_file) as f:
        data = json.load(f)
    assert data["workflow_name"] == "Test Workflow"
    assert "timestamp" in data

def test_save_step_output(storage):
    """Test saving step output."""
    workflow_id = "test_workflow"
    run_path = storage.create_run_directory(workflow_id)
    step_id = "step1"
    output = {"status": "success", "result": "test result"}
    
    storage.save_step_output(run_path, step_id, output)
    
    output_file = run_path / f"{step_id}_output.json"
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
    assert data["status"] == "success"
    assert "timestamp" in data

def test_list_runs(storage):
    """Test listing runs for a workflow."""
    workflow_id = "test_workflow"
    run_path1 = storage.create_run_directory(workflow_id)
    run_path2 = storage.create_run_directory(workflow_id)
    
    runs = storage.list_runs(workflow_id)
    assert len(runs) == 2
    assert run_path1.name in runs
    assert run_path2.name in runs

def test_get_run_metadata(storage, sample_metadata):
    """Test retrieving run metadata."""
    workflow_id = "test_workflow"
    run_path = storage.create_run_directory(workflow_id)
    storage.save_run_metadata(run_path, sample_metadata)
    
    metadata = storage.get_run_metadata(workflow_id, run_path.name)
    assert metadata is not None
    assert metadata["workflow_name"] == "Test Workflow"

def test_get_step_output(storage):
    """Test retrieving step output."""
    workflow_id = "test_workflow"
    run_path = storage.create_run_directory(workflow_id)
    step_id = "step1"
    output = {"status": "success", "result": "test result"}
    
    storage.save_step_output(run_path, step_id, output)
    
    retrieved_output = storage.get_step_output(workflow_id, run_path.name, step_id)
    assert retrieved_output is not None
    assert retrieved_output["status"] == "success" 