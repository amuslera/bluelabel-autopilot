"""
Email to DAG Connector - Bridges email ingestion with DAG execution.

This module monitors email events and triggers DAG execution when PDFs are detected.
"""

import asyncio
import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from uuid import uuid4

from services.workflow.dag_runner import StatefulDAGRunner
from services.workflow.dag_run_store import DAGRunStore

logger = logging.getLogger(__name__)


class EmailDAGConnector:
    """Connects email ingestion events to DAG execution."""
    
    def __init__(self, 
                 dag_store: Optional[DAGRunStore] = None,
                 input_base_path: str = "/inputs"):
        """
        Initialize the email-to-DAG connector.
        
        Args:
            dag_store: DAGRunStore instance for state persistence
            input_base_path: Base path for storing input files
        """
        self.dag_store = dag_store or DAGRunStore()
        self.input_base_path = Path(input_base_path)
        self.input_base_path.mkdir(parents=True, exist_ok=True)
        
    async def process_email_event(self, email_data: Dict[str, Any]) -> Optional[str]:
        """
        Process an email event and trigger DAG if PDF is detected.
        
        Args:
            email_data: Email event data containing:
                - from: sender email
                - subject: email subject
                - timestamp: when received
                - attachments: list of attachment metadata
                
        Returns:
            DAG run ID if triggered, None otherwise
        """
        logger.info(f"Processing email event from {email_data.get('from')}")
        
        # Check for PDF attachments
        pdf_attachments = [
            att for att in email_data.get('attachments', [])
            if att.get('content_type') == 'application/pdf'
        ]
        
        if not pdf_attachments:
            logger.info("No PDF attachments found, skipping DAG trigger")
            return None
            
        # Use first PDF attachment
        pdf_info = pdf_attachments[0]
        logger.info(f"Found PDF attachment: {pdf_info.get('filename')}")
        
        # Generate run ID
        run_id = f"email_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
        
        # Create run directory and save file
        run_dir = self.input_base_path / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Save PDF file (in real scenario, would download/extract from email)
        pdf_path = run_dir / "source.pdf"
        if 'file_path' in pdf_info:
            # For testing: copy from provided path
            shutil.copy2(pdf_info['file_path'], pdf_path)
            logger.info(f"Saved PDF to {pdf_path}")
        else:
            # In production: extract from email attachment data
            logger.warning("No file_path provided, creating placeholder")
            pdf_path.write_text("PDF placeholder content")
        
        # Create DAG input payload
        dag_input = {
            "run_id": run_id,
            "source": "email",
            "email_metadata": {
                "from": email_data.get('from'),
                "subject": email_data.get('subject'),
                "timestamp": email_data.get('timestamp'),
                "attachment": pdf_info.get('filename')
            },
            "input_file": str(pdf_path),
            "workflow": "pdf_to_digest"  # Default workflow
        }
        
        # Save metadata
        metadata_path = run_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(dag_input, f, indent=2)
        
        # Trigger DAG execution
        dag_id = await self._trigger_dag(dag_input)
        
        logger.info(f"Triggered DAG {dag_id} for email from {email_data.get('from')}")
        return dag_id
        
    async def _trigger_dag(self, dag_input: Dict[str, Any]) -> str:
        """
        Trigger DAG execution with the given input.
        
        Args:
            dag_input: Input data for DAG execution
            
        Returns:
            DAG run ID
        """
        # Create DAG runner
        dag_id = f"contentmind_{dag_input['run_id']}"
        runner = StatefulDAGRunner(
            dag_id=dag_id,
            store=self.dag_store
        )
        
        # Register steps for content processing workflow
        # These would be real agent executors in production
        async def extract_text() -> Dict[str, Any]:
            """Mock PDF text extraction."""
            logger.info(f"Extracting text from {dag_input['input_file']}")
            return {
                "status": "success",
                "content": "Extracted PDF content...",
                "pages": 10,
                "extraction_time": "2.5s"
            }
            
        async def generate_summary() -> Dict[str, Any]:
            """Mock summary generation."""
            logger.info("Generating summary from extracted content")
            return {
                "status": "success",
                "summary": "This document discusses important topics...",
                "key_points": ["Point 1", "Point 2", "Point 3"],
                "generation_time": "5.2s"
            }
            
        async def create_digest() -> Dict[str, Any]:
            """Mock digest creation."""
            logger.info("Creating final digest")
            return {
                "status": "success",
                "digest": "# Document Digest\n\n## Summary\n...",
                "format": "markdown",
                "creation_time": "1.8s"
            }
        
        # Register workflow steps
        runner.register_step(
            step_id="extract_text",
            executor=extract_text,
            max_retries=3,
            critical=True
        )
        
        runner.register_step(
            step_id="generate_summary", 
            executor=generate_summary,
            max_retries=2,
            critical=True
        )
        
        runner.register_step(
            step_id="create_digest",
            executor=create_digest,
            max_retries=2,
            critical=True
        )
        
        # Execute DAG asynchronously (fire and forget)
        asyncio.create_task(self._execute_dag_async(runner, dag_input))
        
        return runner.dag_run.run_id
        
    async def _execute_dag_async(self, runner: StatefulDAGRunner, dag_input: Dict[str, Any]):
        """Execute DAG asynchronously."""
        try:
            logger.info(f"Starting DAG execution: {runner.dag_run.run_id}")
            
            # Set initial context
            runner.dag_run.metadata["input"] = dag_input
            
            # Execute the DAG with specified step order
            result = await runner.execute(step_order=["extract_text", "generate_summary", "create_digest"])
            
            logger.info(f"DAG execution completed: {runner.dag_run.run_id} - Status: {runner.dag_run.status}")
            
        except Exception as e:
            logger.error(f"DAG execution failed: {e}")


# Mock email event listener (for testing)
class MockEmailListener:
    """Mock email listener for testing."""
    
    def __init__(self, connector: EmailDAGConnector):
        self.connector = connector
        self.running = False
        
    async def start(self):
        """Start listening for email events."""
        self.running = True
        logger.info("Mock email listener started")
        
        # In production, this would connect to real email service
        # For testing, we'll just wait for manual triggers
        
    async def stop(self):
        """Stop listening."""
        self.running = False
        logger.info("Mock email listener stopped")
        
    async def simulate_email(self, email_data: Dict[str, Any]) -> Optional[str]:
        """Simulate receiving an email."""
        if not self.running:
            await self.start()
            
        return await self.connector.process_email_event(email_data)