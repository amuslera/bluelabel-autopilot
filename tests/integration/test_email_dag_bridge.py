"""
Integration tests for Email to DAG trigger bridge.
"""

import asyncio
import json
import os
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

import pytest

from services.email.email_dag_connector import EmailDAGConnector, MockEmailListener
from services.workflow.dag_run_store import DAGRunStore
from services.workflow.dag_run_tracker import DAGRunStatus


class TestEmailDAGBridge:
    """Test email to DAG trigger functionality."""
    
    @pytest.fixture
    def temp_dirs(self):
        """Create temporary directories for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_dir = Path(temp_dir) / "inputs"
            dag_store_dir = Path(temp_dir) / "dag_runs"
            input_dir.mkdir()
            dag_store_dir.mkdir()
            
            yield {
                "input": str(input_dir),
                "dag_store": str(dag_store_dir)
            }
    
    @pytest.fixture
    def sample_pdf(self, temp_dirs):
        """Create a sample PDF file for testing."""
        pdf_path = Path(temp_dirs["input"]) / "sample.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n%Sample PDF content\n")
        return str(pdf_path)
    
    @pytest.mark.asyncio
    async def test_email_with_pdf_triggers_dag(self, temp_dirs, sample_pdf):
        """Test that email with PDF attachment triggers DAG execution."""
        # Setup
        dag_store = DAGRunStore(storage_path=temp_dirs["dag_store"])
        connector = EmailDAGConnector(
            dag_store=dag_store,
            input_base_path=temp_dirs["input"]
        )
        
        # Create email event with PDF
        email_data = {
            "from": "user@example.com",
            "subject": "Test Document",
            "timestamp": datetime.now().isoformat(),
            "attachments": [
                {
                    "filename": "document.pdf",
                    "content_type": "application/pdf",
                    "file_path": sample_pdf
                }
            ]
        }
        
        # Process email
        run_id = await connector.process_email_event(email_data)
        
        # Verify DAG was triggered
        assert run_id is not None
        
        # Get DAG from store to verify it was created
        dag_run = dag_store.get(run_id)
        assert dag_run is not None
        assert dag_run.dag_id.startswith("contentmind_email_")
        
        # Verify file was saved
        # Extract the email run ID from the DAG ID
        email_run_id = dag_run.dag_id.replace("contentmind_", "")
        run_dir = Path(temp_dirs["input"]) / email_run_id
        assert run_dir.exists()
        assert (run_dir / "source.pdf").exists()
        assert (run_dir / "metadata.json").exists()
        
        # Verify metadata
        with open(run_dir / "metadata.json") as f:
            metadata = json.load(f)
            assert metadata["source"] == "email"
            assert metadata["email_metadata"]["from"] == "user@example.com"
            assert metadata["input_file"].endswith("source.pdf")
            
        # Wait a bit for async DAG execution to start
        await asyncio.sleep(0.1)
        
        # Verify DAG run was created with correct ID
        dag_run = dag_store.get(run_id)
        assert dag_run is not None
        assert dag_run.dag_id.startswith("contentmind_email_")
    
    @pytest.mark.asyncio
    async def test_email_without_pdf_skips_dag(self, temp_dirs):
        """Test that email without PDF doesn't trigger DAG."""
        # Setup
        connector = EmailDAGConnector(input_base_path=temp_dirs["input"])
        
        # Create email event without PDF
        email_data = {
            "from": "user@example.com",
            "subject": "Just a message",
            "timestamp": datetime.now().isoformat(),
            "attachments": [
                {
                    "filename": "image.jpg",
                    "content_type": "image/jpeg"
                }
            ]
        }
        
        # Process email
        run_id = await connector.process_email_event(email_data)
        
        # Verify no DAG was triggered
        assert run_id is None
    
    @pytest.mark.asyncio
    async def test_mock_email_listener(self, temp_dirs, sample_pdf):
        """Test the mock email listener functionality."""
        # Setup
        dag_store = DAGRunStore(storage_path=temp_dirs["dag_store"])
        connector = EmailDAGConnector(
            dag_store=dag_store,
            input_base_path=temp_dirs["input"]
        )
        listener = MockEmailListener(connector)
        
        # Start listener
        await listener.start()
        assert listener.running
        
        # Simulate email
        email_data = {
            "from": "test@example.com",
            "subject": "Test via listener",
            "timestamp": datetime.now().isoformat(),
            "attachments": [
                {
                    "filename": "report.pdf",
                    "content_type": "application/pdf",
                    "file_path": sample_pdf
                }
            ]
        }
        
        run_id = await listener.simulate_email(email_data)
        assert run_id is not None
        
        # Stop listener
        await listener.stop()
        assert not listener.running
    
    @pytest.mark.asyncio
    async def test_dag_execution_creates_state(self, temp_dirs, sample_pdf):
        """Test that DAG execution creates proper state entries."""
        # Setup
        dag_store = DAGRunStore(storage_path=temp_dirs["dag_store"])
        connector = EmailDAGConnector(
            dag_store=dag_store,
            input_base_path=temp_dirs["input"]
        )
        
        # Process email
        email_data = {
            "from": "user@example.com",
            "subject": "Test Document",
            "timestamp": datetime.now().isoformat(),
            "attachments": [
                {
                    "filename": "document.pdf",
                    "content_type": "application/pdf",
                    "file_path": sample_pdf
                }
            ]
        }
        
        run_id = await connector.process_email_event(email_data)
        
        # Wait for DAG to complete
        await asyncio.sleep(1.0)
        
        # Check DAG state
        dag_run = dag_store.get(run_id)
        assert dag_run is not None
        assert dag_run.status in [DAGRunStatus.RUNNING, DAGRunStatus.SUCCESS]
        
        # Check that steps were registered
        assert len(dag_run.steps) == 3
        assert "extract_text" in dag_run.steps
        assert "generate_summary" in dag_run.steps
        assert "create_digest" in dag_run.steps
        
        # Check metadata contains input
        assert "input" in dag_run.metadata
        assert dag_run.metadata["input"]["source"] == "email"