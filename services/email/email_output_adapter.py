"""
Email Output Adapter

This module provides the EmailOutAdapter class for sending workflow output via email.
Supports SMTP backend with configurable settings, graceful error handling,
and email output snapshots for debugging and auditing.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

# Import the email snapshot functionality
from .email_snapshot import save_email_snapshot

logger = logging.getLogger(__name__)


class EmailOutAdapter:
    """
    Adapter for sending workflow output via email.
    
    Example usage:
        >>> config = {
        ...     'smtp_server': 'smtp.gmail.com',
        ...     'smtp_port': 587,
        ...     'smtp_username': 'your-email@gmail.com',
        ...     'smtp_password': 'your-app-password',
        ...     'from_email': 'your-email@gmail.com'
        ... }
        >>> adapter = EmailOutAdapter(config)
        >>> await adapter.send_output(
        ...     content='Workflow completed successfully!',
        ...     subject='Workflow Results',
        ...     recipient='recipient@example.com'
        ... )
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the email output adapter.
        
        Args:
            config: Optional configuration dictionary. If not provided,
                    will use Config instance for values:
                - smtp_server: SMTP server hostname
                - smtp_port: SMTP server port (default: 587)
                - smtp_username: SMTP authentication username
                - smtp_password: SMTP authentication password
                - from_email: Sender email address
                - use_tls: Whether to use TLS (default: True)
        """
        # If no config provided, use singleton Config instance
        if config is None:
            app_config = get_config()
            config = app_config.get_smtp_config()
            config['from_email'] = app_config.default_sender_email or 'noreply@localhost'
        
        self.smtp_server = config.get('smtp_server', 'localhost')
        self.smtp_port = config.get('smtp_port', 587)
        self.smtp_username = config.get('smtp_username')
        self.smtp_password = config.get('smtp_password')
        self.from_email = config.get('from_email', 'noreply@localhost')
        self.use_tls = config.get('use_tls', True)
        
        logger.info(f"Initialized EmailOutAdapter with server {self.smtp_server}:{self.smtp_port}")
    
    async def send_output(self, content: str, subject: str, recipient: str,
                         content_type: str = 'plain') -> bool:
        """
        Send workflow output via email.
        
        Args:
            content: The content to send (formatted text or HTML)
            subject: Email subject line
            recipient: Recipient email address
            content_type: Content type ('plain' or 'html')
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Run synchronous SMTP operations in thread pool
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                self._send_email_sync,
                content, subject, recipient, content_type
            )
            return result
            
        except Exception as e:
            logger.error(f"Failed to send email to {recipient}: {e}")
            return False
    
    def _send_email_sync(self, content: str, subject: str, recipient: str,
                        content_type: str) -> bool:
        """
        Synchronous email sending implementation.
        
        Args:
            content: The content to send
            subject: Email subject line
            recipient: Recipient email address
            content_type: Content type ('plain' or 'html')
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Create message
            if content_type == 'html':
                msg = MIMEMultipart('alternative')
                msg.attach(MIMEText(content, 'html'))
            else:
                msg = MIMEText(content, 'plain')
            
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = recipient
            
            # Connect to SMTP server
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                
                server.send_message(msg)
                
            logger.info(f"Successfully sent email to {recipient} with subject: {subject}")
            return True
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending email to {recipient}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email to {recipient}: {e}")
            return False
    
    async def send_formatted_output(self, workflow_result: Dict[str, Any],
                                   formatter_func: callable,
                                   subject: str, recipient: str,
                                   save_snapshot: bool = True,
                                   run_id: Optional[str] = None) -> bool:
        """
        Send formatted workflow output via email with optional snapshot.
        
        Args:
            workflow_result: Workflow execution result data
            formatter_func: Function to format the result (e.g., format_digest_markdown)
            subject: Email subject line
            recipient: Recipient email address
            save_snapshot: Whether to save a snapshot of the email content
            run_id: Optional run ID for snapshot organization. If not provided, one will be generated.
            
        Returns:
            bool: True if email was sent successfully, False otherwise
            
        Note:
            If save_snapshot is True, the email content will be saved to disk in the
            data/logs/output_snapshots/<run_id>/ directory with the following files:
            - email_output.md: Markdown formatted content (if available)
            - email_output.txt: Plaintext formatted content
            - email_output.html: HTML formatted content (if available)
            - metadata.json: Additional information about the email
        """
        try:
            # Format the content
            formatted_content = formatter_func(workflow_result)
            
            # Determine content type based on formatter
            content_type = 'html' if 'html' in formatter_func.__name__ else 'plain'
            
            # Generate run_id if not provided
            if run_id is None:
                run_id = f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            # Save snapshot if enabled
            if save_snapshot:
                self._save_email_snapshot(
                    run_id=run_id,
                    workflow_result=workflow_result,
                    formatter_func=formatter_func,
                    subject=subject,
                    recipient=recipient,
                    content_type=content_type
                )
            
            # Send the email
            return await self.send_output(
                content=formatted_content,
                subject=subject,
                recipient=recipient,
                content_type=content_type
            )
            
        except Exception as e:
            logger.error(f"Failed to format and send output: {e}")
            return False
    
    def _save_email_snapshot(self, run_id: str, workflow_result: Dict[str, Any],
                            formatter_func: callable, subject: str,
                            recipient: str, content_type: str) -> Dict[str, str]:
        """
        Save a snapshot of the email content for debugging and auditing.
        
        Args:
            run_id: Unique identifier for the workflow run
            workflow_result: Original workflow result data
            formatter_func: Function used to format the content
            subject: Email subject line
            recipient: Recipient email address
            content_type: Content type ('plain' or 'html')
            
        Returns:
            Dictionary containing paths to the saved files
        """
        try:
            # Import formatters here to avoid circular imports
            from .email_output_formatter import (
                format_digest_markdown,
                format_digest_plaintext,
                format_digest_html
            )
            
            # Format content in all available formats
            content = {}
            
            # Always include plaintext
            try:
                content['plaintext'] = format_digest_plaintext(workflow_result)
            except Exception as e:
                logger.warning(f"Failed to generate plaintext snapshot: {e}")
            
            # Try to include markdown if available
            try:
                content['markdown'] = format_digest_markdown(workflow_result)
            except Exception as e:
                logger.warning(f"Failed to generate markdown snapshot: {e}")
            
            # Try to include HTML if available
            try:
                content['html'] = format_digest_html(workflow_result)
            except Exception as e:
                logger.warning(f"Failed to generate HTML snapshot: {e}")
            
            # Prepare metadata
            metadata = {
                'workflow': workflow_result.get('workflow_name', 'unknown'),
                'sender': self.from_email,
                'recipient': recipient,
                'subject': subject,
                'content_type': content_type,
                'formatter': formatter_func.__name__,
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            # Save the snapshot
            saved_paths = save_email_snapshot(
                run_id=run_id,
                content=content,
                metadata=metadata
            )
            
            logger.info(f"Saved email snapshot for run {run_id} to {saved_paths}")
            return saved_paths
            
        except Exception as e:
            logger.error(f"Failed to save email snapshot: {e}", exc_info=True)
            return {}