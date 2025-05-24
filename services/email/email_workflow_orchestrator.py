"""Email Workflow Orchestrator
Integrates email monitoring, routing, and workflow execution into a cohesive service.

This module connects:
1. GmailInboxWatcher - monitors inbox for new emails
2. EmailWorkflowRouter - determines which workflow to run
3. WorkflowEngine - executes the selected workflow
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.email.email_gateway import GmailInboxWatcher, EmailEvent
from services.email.email_workflow_router import EmailWorkflowRouter
from core.workflow_engine import WorkflowEngine, run_workflow
from interfaces.run_models import WorkflowRunResult

logger = logging.getLogger(__name__)


@dataclass
class EmailProcessingResult:
    """Result of processing an email through a workflow"""
    email_id: str
    from_address: str
    subject: str
    received_at: datetime
    workflow_path: Optional[str]
    workflow_run_id: Optional[str]
    workflow_status: Optional[str]
    processing_time_ms: Optional[int]
    error: Optional[str] = None


class EmailWorkflowOrchestrator:
    """
    Orchestrates the complete email-to-workflow pipeline.
    
    This class:
    1. Monitors Gmail inbox for new emails
    2. Routes emails to appropriate workflows based on rules
    3. Executes workflows with email data as input
    4. Tracks processing results
    
    Example usage:
        >>> config = {
        ...     "gmail": {
        ...         "credentials_path": "credentials.json",
        ...         "token_path": "token.json"
        ...     },
        ...     "routing": {
        ...         "rules": [...],
        ...         "default_workflow": "workflows/generic_email.yaml"
        ...     },
        ...     "engine": {
        ...         "storage_path": "./data/knowledge",
        ...         "temp_path": "./data/temp"
        ...     }
        ... }
        >>> orchestrator = EmailWorkflowOrchestrator(config)
        >>> await orchestrator.start()
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config: Configuration dictionary containing:
                - gmail: Gmail API configuration
                - routing: Email routing rules configuration
                - engine: Workflow engine configuration
                - processing: Processing options (optional)
        """
        self.config = config
        
        # Initialize components
        gmail_config = config.get('gmail', {})
        self.inbox_watcher = GmailInboxWatcher(
            credentials_path=gmail_config.get('credentials_path', 'credentials.json'),
            token_path=gmail_config.get('token_path', 'token.json'),
            scopes=gmail_config.get('scopes')
        )
        
        routing_config = config.get('routing', {})
        self.router = EmailWorkflowRouter(routing_config)
        
        engine_config = config.get('engine', {})
        self.storage_path = Path(engine_config.get('storage_path', './data/knowledge'))
        self.temp_path = Path(engine_config.get('temp_path', './data/temp'))
        
        # Processing options
        processing_config = config.get('processing', {})
        self.mark_as_read = processing_config.get('mark_as_read', True)
        self.add_label = processing_config.get('add_label', 'Processed')
        self.error_label = processing_config.get('error_label', 'ProcessingError')
        self.save_attachments = processing_config.get('save_attachments', True)
        
        # State tracking
        self.is_running = False
        self.processed_emails: List[EmailProcessingResult] = []
        
        logger.info("Initialized EmailWorkflowOrchestrator")
    
    async def start(self, one_shot: bool = False):
        """
        Start the email monitoring and processing loop.
        
        Args:
            one_shot: If True, process one email and stop. If False, run continuously.
        """
        logger.info("Starting email workflow orchestrator")
        self.is_running = True
        
        try:
            while self.is_running:
                # Watch for new email
                logger.info("Waiting for new email...")
                email_event = await self.inbox_watcher.watch()
                
                # Process the email
                result = await self.process_email(email_event)
                self.processed_emails.append(result)
                
                # Log result
                if result.error:
                    logger.error(f"Failed to process email {result.email_id}: {result.error}")
                else:
                    logger.info(f"Successfully processed email {result.email_id} "
                              f"with workflow {result.workflow_path}")
                
                # Stop if one-shot mode
                if one_shot:
                    break
                    
        except KeyboardInterrupt:
            logger.info("Orchestrator interrupted by user")
        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            raise
        finally:
            self.is_running = False
            logger.info("Email workflow orchestrator stopped")
    
    async def process_email(self, email_event: EmailEvent) -> EmailProcessingResult:
        """
        Process a single email through the workflow pipeline.
        
        Args:
            email_event: Email event from the inbox watcher
            
        Returns:
            Processing result
        """
        start_time = datetime.now()
        
        # Create result object
        result = EmailProcessingResult(
            email_id=email_event.message_id,
            from_address=email_event.sender,
            subject=email_event.subject,
            received_at=email_event.timestamp,
            workflow_path=None,
            workflow_run_id=None,
            workflow_status=None,
            processing_time_ms=None
        )
        
        try:
            # Convert email event to metadata for routing
            metadata = self._email_event_to_metadata(email_event)
            
            # Select workflow
            workflow_path = self.router.select_workflow(metadata)
            result.workflow_path = workflow_path
            
            if not workflow_path:
                raise ValueError("No matching workflow found for email")
            
            # Prepare workflow input
            workflow_input = await self._prepare_workflow_input(email_event, metadata)
            
            # Save input to temporary file
            input_file = self.temp_path / f"email_input_{email_event.message_id}.json"
            input_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(input_file, 'w') as f:
                json.dump(workflow_input, f, indent=2)
            
            # Execute workflow
            logger.info(f"Executing workflow: {workflow_path}")
            workflow_result = await run_workflow(
                path=workflow_path,
                persist=True,
                storage_path=str(self.storage_path),
                temp_path=str(self.temp_path),
                initial_input=workflow_input
            )
            
            # Update result
            result.workflow_run_id = workflow_result.run_id
            result.workflow_status = workflow_result.status.value
            
            # Mark email as processed
            if self.mark_as_read:
                await self._mark_email_processed(email_event, success=True)
            
            # Clean up temp file
            if input_file.exists():
                input_file.unlink()
                
        except Exception as e:
            logger.error(f"Error processing email {email_event.message_id}: {e}")
            result.error = str(e)
            result.workflow_status = "failed"
            
            # Mark email with error label
            if self.error_label:
                await self._mark_email_processed(email_event, success=False)
        
        finally:
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result.processing_time_ms = int(processing_time)
        
        return result
    
    def _email_event_to_metadata(self, email_event: EmailEvent) -> Dict[str, Any]:
        """Convert EmailEvent to metadata dict for routing"""
        metadata = {
            'from': email_event.sender,
            'subject': email_event.subject,
            'attachments': []
        }
        
        # Add attachment info
        for attachment in email_event.attachments:
            metadata['attachments'].append({
                'filename': attachment.filename,
                'mimeType': attachment.mime_type,
                'size': attachment.size
            })
        
        # Add body preview
        if email_event.body_plain:
            metadata['body'] = email_event.body_plain[:500]  # First 500 chars
        
        return metadata
    
    async def _prepare_workflow_input(self, email_event: EmailEvent, 
                                    metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare workflow input from email data.
        
        This method creates a standardized input format that workflows can use.
        """
        workflow_input = {
            'task_id': f"email-{email_event.message_id}",
            'task_type': 'email',
            'source': 'gmail',
            'timestamp': email_event.timestamp.isoformat(),
            'metadata': {
                'email_id': email_event.message_id,
                'thread_id': email_event.thread_id,
                'from': email_event.sender,
                'to': email_event.recipient,
                'subject': email_event.subject,
                'labels': email_event.labels,
                'snippet': email_event.snippet
            },
            'content': {
                'body_plain': email_event.body_plain,
                'body_html': email_event.body_html
            }
        }
        
        # Handle attachments
        if email_event.attachments and self.save_attachments:
            attachments_data = []
            attachments_dir = self.temp_path / f"email_attachments_{email_event.message_id}"
            attachments_dir.mkdir(parents=True, exist_ok=True)
            
            for attachment in email_event.attachments:
                # Save attachment
                attachment_path = attachments_dir / attachment.filename
                with open(attachment_path, 'wb') as f:
                    f.write(attachment.data)
                
                attachments_data.append({
                    'filename': attachment.filename,
                    'mime_type': attachment.mime_type,
                    'size': attachment.size,
                    'path': str(attachment_path)
                })
            
            workflow_input['attachments'] = attachments_data
        
        return workflow_input
    
    async def _mark_email_processed(self, email_event: EmailEvent, success: bool):
        """Mark email as processed in Gmail"""
        try:
            service = self.inbox_watcher.service
            
            # Mark as read
            if self.mark_as_read:
                service.users().messages().modify(
                    userId='me',
                    id=email_event.message_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
            
            # Add label
            label = self.add_label if success else self.error_label
            if label:
                # Note: In production, you'd need to create/fetch label ID first
                logger.info(f"Would add label '{label}' to email {email_event.message_id}")
                
        except Exception as e:
            logger.error(f"Failed to mark email as processed: {e}")
    
    def stop(self):
        """Stop the orchestrator"""
        logger.info("Stopping email workflow orchestrator")
        self.is_running = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        total = len(self.processed_emails)
        successful = sum(1 for r in self.processed_emails if not r.error)
        failed = total - successful
        
        avg_time = 0
        if total > 0:
            avg_time = sum(r.processing_time_ms or 0 for r in self.processed_emails) / total
        
        return {
            'total_processed': total,
            'successful': successful,
            'failed': failed,
            'average_processing_time_ms': avg_time,
            'is_running': self.is_running
        }


# Example configuration
EXAMPLE_CONFIG = {
    "gmail": {
        "credentials_path": "credentials.json",
        "token_path": "token.json"
    },
    "routing": {
        "rules": [
            {
                "name": "pdf_processor",
                "workflow_path": "workflows/pdf_ingestion_digest.yaml",
                "has_attachment": True,
                "attachment_type": "application/pdf",
                "priority": 10
            },
            {
                "name": "url_extractor",
                "workflow_path": "workflows/url_content_digest.yaml",
                "subject_contains": ["link:", "url:", "check out"],
                "priority": 5
            }
        ],
        "default_workflow": "workflows/generic_email_handler.yaml"
    },
    "engine": {
        "storage_path": "./data/knowledge",
        "temp_path": "./data/temp"
    },
    "processing": {
        "mark_as_read": True,
        "add_label": "Processed",
        "error_label": "ProcessingError",
        "save_attachments": True
    }
}


if __name__ == "__main__":
    # Example usage
    import asyncio
    
    async def main():
        orchestrator = EmailWorkflowOrchestrator(EXAMPLE_CONFIG)
        
        # Process one email for testing
        await orchestrator.start(one_shot=True)
        
        # Print stats
        stats = orchestrator.get_stats()
        print(f"\nProcessing stats: {json.dumps(stats, indent=2)}")
    
    asyncio.run(main())