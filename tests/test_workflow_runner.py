#!/usr/bin/env python3
"""
Unit tests for the workflow runner functionality.
Tests YAML workflow loading, validation, and execution.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import yaml
import uuid

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from runner.workflow_executor import WorkflowExecutor
from runner.workflow_loader import WorkflowLoader
from interfaces.agent_models import AgentInput, AgentOutput


@pytest.fixture
def workflow_executor():
    """Create a WorkflowExecutor instance for testing."""
    return WorkflowExecutor()


@pytest.fixture
def sample_workflow_yaml(tmp_path):
    """Create a sample workflow YAML file."""
    workflow = {
        "workflow": {
            "name": "Test Workflow",
            "description": "Test workflow for unit tests",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": "ingest",
                "name": "Ingest PDF",
                "agent": "ingestion_agent",
                "input_file": "tests/sample.pdf"
            },
            {
                "id": "digest",
                "name": "Generate Digest",
                "agent": "digest_agent",
                "input_from": "ingest",
                "config": {
                    "format": "markdown"
                }
            }
        ]
    }
    
    workflow_file = tmp_path / "test_workflow.yaml"
    workflow_file.write_text(yaml.dump(workflow))
    return workflow_file


def test_workflow_loading(workflow_executor, sample_workflow_yaml):
    """Test that workflow YAML is loaded correctly."""
    loader = WorkflowLoader(sample_workflow_yaml)
    workflow_data = loader.load()
    steps = loader.parse_steps()
    
    assert workflow_data["workflow"]["name"] == "Test Workflow"
    assert len(steps) == 2
    assert steps[0].id == "ingest"
    assert steps[1].id == "digest"


def test_execution_order(workflow_executor, sample_workflow_yaml):
    """Test that steps are executed in correct order."""
    loader = WorkflowLoader(sample_workflow_yaml)
    execution_order = loader.get_execution_order()
    
    assert execution_order == ["ingest", "digest"]


@pytest.mark.asyncio
async def test_workflow_execution(workflow_executor, sample_workflow_yaml):
    """Test complete workflow execution."""
    # Mock agent responses
    ingest_output = AgentOutput(
        status="success",
        result={
            "content_id": "test_pdf_123",
            "content_type": "pdf",
            "content_length": 1024
        }
    )
    
    digest_output = AgentOutput(
        status="success",
        result={
            "digest": "# Test Digest\n\n- Point 1\n- Point 2",
            "summary_count": 2,
            "format": "markdown"
        }
    )
    
    with patch('agents.ingestion_agent.IngestionAgent.process', return_value=ingest_output), \
         patch('agents.digest_agent.DigestAgent.process', return_value=digest_output):
        
        # Run workflow
        step_outputs = await workflow_executor.run_workflow(sample_workflow_yaml)
        
        # Verify outputs
        assert "ingest" in step_outputs
        assert "digest" in step_outputs
        assert step_outputs["ingest"]["status"] == "success"
        assert step_outputs["digest"]["status"] == "success"
        assert step_outputs["digest"]["result"]["format"] == "markdown"


@pytest.mark.asyncio
async def test_step_failure_handling(workflow_executor, sample_workflow_yaml):
    """Test that step failures are handled correctly."""
    # Mock first step success, second step failure
    ingest_output = AgentOutput(
        status="success",
        result={
            "content_id": "test_pdf_123",
            "content_type": "pdf",
            "content_length": 1024
        }
    )
    
    with patch('agents.ingestion_agent.IngestionAgent.process', return_value=ingest_output), \
         patch('agents.digest_agent.DigestAgent.process', side_effect=Exception("Test error")):
        
        # Run workflow
        step_outputs = await workflow_executor.run_workflow(sample_workflow_yaml)
        
        # Verify outputs
        assert step_outputs["ingest"]["status"] == "success"
        assert step_outputs["digest"]["status"] == "error"
        assert "test error" in step_outputs["digest"]["error"].lower()


def test_invalid_workflow_yaml(workflow_executor, tmp_path):
    """Test that invalid YAML is caught."""
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("invalid: yaml: content: [")
    
    with pytest.raises(ValueError) as exc_info:
        loader = WorkflowLoader(invalid_yaml)
        loader.load()
    
    assert "invalid yaml" in str(exc_info.value).lower()


def test_missing_input_file(workflow_executor, tmp_path):
    """Test that missing input files are caught."""
    workflow = {
        "workflow": {
            "name": "Test Workflow",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": "ingest",
                "agent": "ingestion_agent",
                "input_file": "nonexistent.pdf"
            }
        ]
    }
    
    workflow_file = tmp_path / "test_workflow.yaml"
    workflow_file.write_text(yaml.dump(workflow))
    
    with pytest.raises(ValueError) as exc_info:
        loader = WorkflowLoader(workflow_file)
        loader.load()
    
    assert "input file not found" in str(exc_info.value).lower()


def test_circular_dependency(workflow_executor, tmp_path):
    """Test that circular dependencies are caught."""
    workflow = {
        "workflow": {
            "name": "Test Workflow",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": "step1",
                "agent": "digest_agent",
                "input_from": "step2"
            },
            {
                "id": "step2",
                "agent": "digest_agent",
                "input_from": "step1"
            }
        ]
    }
    
    workflow_file = tmp_path / "test_workflow.yaml"
    workflow_file.write_text(yaml.dump(workflow))
    
    with pytest.raises(ValueError) as exc_info:
        loader = WorkflowLoader(workflow_file)
        loader.get_execution_order()
    
    assert "circular dependency" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_output_storage(workflow_executor, sample_workflow_yaml, tmp_path):
    """Test that workflow outputs are stored correctly."""
    # Mock agent responses
    ingest_output = AgentOutput(
        status="success",
        result={
            "content_id": "test_pdf_123",
            "content_type": "pdf",
            "content_length": 1024
        }
    )
    
    digest_output = AgentOutput(
        status="success",
        result={
            "digest": "# Test Digest",
            "summary_count": 1,
            "format": "markdown"
        }
    )
    
    with patch('agents.ingestion_agent.IngestionAgent.process', return_value=ingest_output), \
         patch('agents.digest_agent.DigestAgent.process', return_value=digest_output), \
         patch('pathlib.Path.mkdir') as mock_mkdir:
        
        # Run workflow
        workflow_executor.workflow_output_path = tmp_path
        step_outputs = await workflow_executor.run_workflow(sample_workflow_yaml)
        
        # Verify directory creation
        mock_mkdir.assert_called_once()
        
        # Verify output files
        workflow_dir = tmp_path / str(uuid.uuid4())
        assert (workflow_dir / "workflow.yaml").exists()
        assert (workflow_dir / "summary.json").exists()
        assert (workflow_dir / "ingest.json").exists()
        assert (workflow_dir / "digest.json").exists() 