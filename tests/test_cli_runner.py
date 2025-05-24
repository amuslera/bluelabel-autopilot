#!/usr/bin/env python3
"""
Unit tests for the CLI runner functionality.
Tests both digest and ingestion agent scenarios.
"""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from runner.cli_runner import CLIRunner
from interfaces.agent_models import AgentInput, AgentOutput


@pytest.fixture
def cli_runner():
    """Create a CLIRunner instance for testing."""
    return CLIRunner()


@pytest.fixture
def sample_digest_input():
    """Sample valid digest input."""
    return {
        "task_id": "test-digest",
        "source": "test",
        "content": {
            "text": "This is a test document for digest generation.",
            "format": "markdown"
        }
    }


@pytest.fixture
def sample_ingestion_input():
    """Sample valid ingestion input."""
    return {
        "task_id": "test-ingest",
        "task_type": "pdf",
        "source": "test",
        "content": {
            "file_path": "tests/sample.pdf"
        }
    }


def test_valid_digest_input(cli_runner, sample_digest_input):
    """Test that valid digest input is processed correctly."""
    with patch('agents.digest_agent.DigestAgent.process') as mock_process:
        # Mock successful digest generation
        mock_process.return_value = AgentOutput(
            status="success",
            result={
                "digest": "# Test Digest\n\n- Point 1\n- Point 2",
                "summary_count": 2,
                "format": "markdown"
            }
        )
        
        # Run digest command
        result = cli_runner.run_agent("digest", json.dumps(sample_digest_input))
        
        # Verify result
        assert result.status == "success"
        assert "digest" in result.result
        assert result.result["format"] == "markdown"
        assert result.result["summary_count"] == 2


def test_valid_ingestion_input(cli_runner, sample_ingestion_input):
    """Test that valid ingestion input is processed correctly."""
    with patch('agents.ingestion_agent.IngestionAgent.process') as mock_process:
        # Mock successful ingestion
        mock_process.return_value = AgentOutput(
            status="success",
            result={
                "content_id": "test_pdf_123",
                "content_type": "pdf",
                "content_length": 1024
            }
        )
        
        # Run ingestion command
        result = cli_runner.run_agent("ingestion", json.dumps(sample_ingestion_input))
        
        # Verify result
        assert result.status == "success"
        assert "content_id" in result.result
        assert result.result["content_type"] == "pdf"


def test_missing_required_fields(cli_runner):
    """Test that missing required fields are caught."""
    invalid_input = {
        "task_id": "test",
        # Missing source field
        "content": {}
    }
    
    with pytest.raises(ValueError) as exc_info:
        cli_runner.run_agent("digest", json.dumps(invalid_input))
    
    assert "source" in str(exc_info.value)


def test_invalid_pdf_path(cli_runner):
    """Test that invalid PDF paths are caught."""
    invalid_input = {
        "task_id": "test",
        "task_type": "pdf",
        "source": "test",
        "content": {
            "file_path": "nonexistent.pdf"
        }
    }
    
    with pytest.raises(ValueError) as exc_info:
        cli_runner.run_agent("ingestion", json.dumps(invalid_input))
    
    assert "file not found" in str(exc_info.value).lower()


def test_invalid_json_input(cli_runner):
    """Test that invalid JSON input is caught."""
    with pytest.raises(ValueError) as exc_info:
        cli_runner.run_agent("digest", "invalid json")
    
    assert "invalid json" in str(exc_info.value).lower()


def test_agent_execution_error(cli_runner, sample_digest_input):
    """Test that agent execution errors are handled."""
    with patch('agents.digest_agent.DigestAgent.process') as mock_process:
        # Mock agent error
        mock_process.side_effect = Exception("Test error")
        
        with pytest.raises(ValueError) as exc_info:
            cli_runner.run_agent("digest", json.dumps(sample_digest_input))
        
        assert "test error" in str(exc_info.value).lower()


def test_file_path_input(cli_runner, tmp_path):
    """Test that file path input works correctly."""
    # Create test input file
    input_file = tmp_path / "test_input.json"
    input_data = {
        "task_id": "test-file",
        "source": "test",
        "content": {
            "text": "Test content",
            "format": "markdown"
        }
    }
    input_file.write_text(json.dumps(input_data))
    
    with patch('agents.digest_agent.DigestAgent.process') as mock_process:
        mock_process.return_value = AgentOutput(
            status="success",
            result={
                "digest": "# Test Digest",
                "summary_count": 1,
                "format": "markdown"
            }
        )
        
        # Run with file path
        result = cli_runner.run_agent("digest", str(input_file))
        
        assert result.status == "success"
        assert "digest" in result.result
        assert result.result["format"] == "markdown"
        assert result.result["summary_count"] == 1 