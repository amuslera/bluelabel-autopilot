"""Unit tests for email simulation functionality."""

import asyncio
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from services.email.email_dag_connector import EmailDAGConnector
from apps.cli.commands.simulate_email import simulate_email

# Test data
TEST_PDF_PATH = Path("tests/data/sample.pdf")
TEST_EMAIL_DATA = {
    'from': 'test@example.com',
    'to': 'recipient@example.com',
    'subject': 'Test Email',
    'timestamp': '2024-03-21T10:00:00Z',
    'attachments': [{
        'filename': 'sample.pdf',
        'content_type': 'application/pdf',
        'file_path': str(TEST_PDF_PATH)
    }]
}

@pytest.fixture
def mock_connector():
    """Create a mock EmailDAGConnector."""
    with patch('services.email.email_dag_connector.EmailDAGConnector') as mock:
        connector = mock.return_value
        connector.process_email_event.return_value = "test_dag_123"
        yield connector

@pytest.fixture
def sample_pdf():
    """Create a sample PDF file for testing."""
    TEST_PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEST_PDF_PATH.write_text("%PDF-1.4\nTest PDF content")
    yield TEST_PDF_PATH
    TEST_PDF_PATH.unlink()

def test_simulate_email_success(mock_connector, sample_pdf, runner):
    """Test successful email simulation."""
    result = runner.invoke(simulate_email, ['--file', str(sample_pdf)])
    
    assert result.exit_code == 0
    assert "Successfully triggered DAG" in result.output
    assert "test_dag_123" in result.output
    
    # Verify connector was called with correct data
    mock_connector.process_email_event.assert_called_once()
    call_args = mock_connector.process_email_event.call_args[0][0]
    assert call_args['from'] == 'simulator@example.com'  # default value
    assert call_args['attachments'][0]['filename'] == 'sample.pdf'

def test_simulate_email_custom_metadata(mock_connector, sample_pdf, runner):
    """Test email simulation with custom metadata."""
    result = runner.invoke(simulate_email, [
        '--file', str(sample_pdf),
        '--subject', 'Custom Subject',
        '--from', 'custom@example.com',
        '--to', 'custom@recipient.com'
    ])
    
    assert result.exit_code == 0
    
    # Verify custom metadata was used
    call_args = mock_connector.process_email_event.call_args[0][0]
    assert call_args['subject'] == 'Custom Subject'
    assert call_args['from'] == 'custom@example.com'
    assert call_args['to'] == 'custom@recipient.com'

def test_simulate_email_invalid_file(runner):
    """Test email simulation with invalid file."""
    result = runner.invoke(simulate_email, ['--file', 'nonexistent.pdf'])
    assert result.exit_code != 0
    assert "File not found" in result.output

def test_simulate_email_non_pdf(runner, tmp_path):
    """Test email simulation with non-PDF file."""
    txt_file = tmp_path / "test.txt"
    txt_file.write_text("Not a PDF")
    
    result = runner.invoke(simulate_email, ['--file', str(txt_file)])
    assert result.exit_code != 0
    assert "File must be a PDF" in result.output

def test_simulate_email_dag_failure(mock_connector, sample_pdf, runner):
    """Test email simulation when DAG trigger fails."""
    mock_connector.process_email_event.return_value = None
    
    result = runner.invoke(simulate_email, ['--file', str(sample_pdf)])
    assert result.exit_code == 0
    assert "Failed to trigger DAG" in result.output

@pytest.mark.asyncio
async def test_email_dag_connector_integration(sample_pdf):
    """Test integration with EmailDAGConnector."""
    connector = EmailDAGConnector()
    dag_id = await connector.process_email_event(TEST_EMAIL_DATA)
    
    assert dag_id is not None
    assert dag_id.startswith("email_")
    
    # Verify files were created
    run_dir = connector.input_base_path / dag_id
    assert (run_dir / "source.pdf").exists()
    assert (run_dir / "metadata.json").exists()
    
    # Verify metadata
    with open(run_dir / "metadata.json") as f:
        metadata = json.load(f)
        assert metadata["source"] == "email"
        assert metadata["email_metadata"]["from"] == TEST_EMAIL_DATA["from"]
        assert metadata["email_metadata"]["subject"] == TEST_EMAIL_DATA["subject"] 