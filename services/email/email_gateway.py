"""Gmail Email Gateway for workflow triggering

This module provides Gmail inbox monitoring functionality extracted and refactored
from the legacy bluelabel-AIOS-V2 system. It uses OAuth 2.0 authentication and
the Gmail API to watch for new emails and trigger workflows.
"""

import os
import base64
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional, NamedTuple
from datetime import datetime
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from services.config import get_config
from services.security import store_oauth_token, retrieve_oauth_token

logger = logging.getLogger(__name__)


class EmailEvent(NamedTuple):
    """Represents a new email event that can trigger workflows"""
    message_id: str
    sender: str
    subject: str
    body: str
    attachments: List[Dict[str, Any]]
    received_at: datetime
    raw_data: Dict[str, Any]


class GmailInboxWatcher:
    """
    Gmail inbox watcher for monitoring new emails and triggering workflows.
    
    This implementation is extracted from the legacy system and simplified
    to focus on inbox monitoring without event bus or Celery dependencies.
    """
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, 
                 credentials_file: Optional[str] = None,
                 token_file: Optional[str] = None,
                 watch_label: str = 'INBOX',
                 poll_interval: int = 30,
                 config: Optional[Any] = None):
        """
        Initialize Gmail inbox watcher.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store/load OAuth2 tokens
            watch_label: Gmail label to monitor (default: INBOX)
            poll_interval: Seconds between inbox checks (default: 30)
            config: Optional Config instance (will create one if not provided)
        """
        # Use provided config or get singleton instance
        self.config = config or get_config()
        
        # Use config values with explicit overrides
        self.credentials_file = credentials_file or self.config.gmail_credentials_path or "credentials.json"
        self.token_file = token_file or self.config.gmail_credentials_path or "data/gmail_token.json"
        self.watch_label = watch_label
        self.poll_interval = poll_interval
        
        self.service = None
        self.credentials = None
        self._last_history_id = None
        self._processed_messages = set()
        
        logger.info(f"Initialized GmailInboxWatcher (label={watch_label}, poll={poll_interval}s)")
    
    def _load_credentials(self) -> bool:
        """Load saved OAuth credentials from secure storage"""
        try:
            # Retrieve from secure storage
            token_data = retrieve_oauth_token('gmail')
            if not token_data:
                return False
                
            self.credentials = Credentials.from_authorized_user_info(
                token_data, self.SCOPES
            )
            
            # Refresh if expired
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    self._save_credentials()
                    logger.info("Refreshed expired OAuth credentials")
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {e}")
                    return False
            
            logger.info("Loaded saved OAuth credentials securely")
            return True
        except Exception as e:
            logger.error(f"Error loading credentials: {e}")
            return False
    
    def _save_credentials(self):
        """Save OAuth credentials securely using encryption"""
        if self.credentials:
            try:
                # Convert credentials to dict for secure storage
                token_data = json.loads(self.credentials.to_json())
                
                # Store securely with encryption
                store_oauth_token('gmail', token_data)
                
                logger.info("Saved OAuth credentials securely")
            except Exception as e:
                logger.error(f"Error saving credentials: {e}")
    
    async def authenticate(self, auth_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Authenticate with Gmail API using OAuth 2.0.
        
        Args:
            auth_code: Authorization code from OAuth flow
            
        Returns:
            Authentication status and details
        """
        try:
            # Try to load existing credentials
            if self._load_credentials():
                # Check if token needs refresh
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    self._save_credentials()
                    logger.info("Refreshed OAuth token")
            
            # If no valid credentials, need new authorization
            if not self.credentials or not self.credentials.valid:
                if not auth_code:
                    # Check if we have client credentials
                    if not os.path.exists(self.credentials_file):
                        return {
                            "status": "error",
                            "message": f"Missing credentials file: {self.credentials_file}",
                            "needs_setup": True
                        }
                    
                    # Create OAuth flow with local redirect
                    flow = Flow.from_client_secrets_file(
                        self.credentials_file,
                        scopes=self.SCOPES,
                        redirect_uri='http://localhost:8080'
                    )
                    
                    auth_url, state = flow.authorization_url(
                        prompt='consent',
                        access_type='offline',
                        include_granted_scopes='true'
                    )
                    
                    return {
                        "status": "authorization_required",
                        "auth_url": auth_url,
                        "state": state,
                        "message": "Visit the URL to authorize Gmail access. Run the local server to capture the response."
                    }
                
                # Exchange auth code for credentials
                flow = Flow.from_client_secrets_file(
                    self.credentials_file,
                    scopes=self.SCOPES,
                    redirect_uri='http://localhost:8080'
                )
                flow.fetch_token(code=auth_code)
                self.credentials = flow.credentials
                self._save_credentials()
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            
            # Test connection and get email
            profile = self.service.users().getProfile(userId='me').execute()
            email = profile.get('emailAddress')
            
            # Get initial history ID for watching
            messages = self.service.users().messages().list(
                userId='me',
                labelIds=[self.watch_label],
                maxResults=1
            ).execute()
            
            if messages.get('messages'):
                msg = self.service.users().messages().get(
                    userId='me',
                    id=messages['messages'][0]['id']
                ).execute()
                self._last_history_id = msg['historyId']
            
            logger.info(f"Authenticated as: {email}")
            
            return {
                "status": "authenticated",
                "email": email,
                "message": "Successfully authenticated with Gmail"
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {
                "status": "error",
                "message": str(e),
                "error_type": type(e).__name__
            }
    
    async def watch(self) -> EmailEvent:
        """
        Watch for new emails in the inbox. This method blocks until a new
        email is detected and returns it as an EmailEvent.
        
        Returns:
            EmailEvent when a new email is detected
            
        Raises:
            RuntimeError: If not authenticated
            Exception: For Gmail API errors
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        logger.info(f"Starting inbox watch (polling every {self.poll_interval}s)")
        
        while True:
            try:
                # Check for new messages
                new_messages = await self._check_for_new_messages()
                
                if new_messages:
                    # Process and return the first new message
                    for msg_data in new_messages:
                        event = await self._process_message(msg_data)
                        if event:
                            logger.info(f"New email detected: {event.subject}")
                            return event
                
                # Wait before next check
                await asyncio.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error during inbox watch: {e}")
                # TODO: Implement exponential backoff for repeated errors
                await asyncio.sleep(self.poll_interval)
    
    async def _check_for_new_messages(self) -> List[Dict[str, Any]]:
        """Check for new messages since last check"""
        try:
            # Use history API if we have a history ID
            if self._last_history_id:
                history = self.service.users().history().list(
                    userId='me',
                    startHistoryId=self._last_history_id,
                    labelId=self.watch_label
                ).execute()
                
                new_messages = []
                if 'history' in history:
                    for record in history['history']:
                        if 'messagesAdded' in record:
                            for msg_added in record['messagesAdded']:
                                msg_id = msg_added['message']['id']
                                if msg_id not in self._processed_messages:
                                    new_messages.append(msg_added['message'])
                    
                    # Update history ID
                    self._last_history_id = history.get('historyId', self._last_history_id)
                
                return new_messages
            
            else:
                # First run - get recent messages
                result = self.service.users().messages().list(
                    userId='me',
                    labelIds=[self.watch_label],
                    maxResults=10
                ).execute()
                
                messages = result.get('messages', [])
                
                # Mark existing messages as processed
                for msg in messages:
                    self._processed_messages.add(msg['id'])
                
                # Get history ID from most recent message
                if messages:
                    msg_detail = self.service.users().messages().get(
                        userId='me',
                        id=messages[0]['id']
                    ).execute()
                    self._last_history_id = msg_detail['historyId']
                
                # Don't return any messages on first run
                return []
                
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return []
    
    async def _process_message(self, msg_data: Dict[str, Any]) -> Optional[EmailEvent]:
        """Process a Gmail message into an EmailEvent"""
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=msg_data['id']
            ).execute()
            
            # Mark as processed
            self._processed_messages.add(msg_data['id'])
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
            
            sender = headers.get('From', '')
            subject = headers.get('Subject', '')
            date_str = headers.get('Date', '')
            
            # Parse date
            try:
                from email.utils import parsedate_to_datetime
                received_at = parsedate_to_datetime(date_str) if date_str else datetime.now()
            except (ValueError, TypeError) as e:
                logger.warning(f"Error parsing email date '{date_str}': {e}")
                received_at = datetime.now()
            
            # Extract body and attachments
            body = self._extract_body(msg['payload'])
            attachments = self._extract_attachments(msg['payload'])
            
            return EmailEvent(
                message_id=msg['id'],
                sender=sender,
                subject=subject,
                body=body,
                attachments=attachments,
                received_at=received_at,
                raw_data=msg
            )
            
        except Exception as e:
            logger.error(f"Error processing message {msg_data.get('id')}: {e}")
            return None
    
    def _extract_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from Gmail payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
                elif part['mimeType'] == 'multipart/alternative':
                    # Recursive call for nested parts
                    body = self._extract_body(part)
                    if body:
                        break
        else:
            # Single part message
            if payload.get('body', {}).get('data'):
                body = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='ignore')
        
        return body.strip()
    
    def _extract_attachments(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract attachment information from Gmail payload"""
        attachments = []
        
        def _process_parts(parts):
            for part in parts:
                filename = part.get('filename')
                if filename:
                    attachments.append({
                        'filename': filename,
                        'mimeType': part.get('mimeType'),
                        'size': part.get('body', {}).get('size', 0),
                        'attachmentId': part.get('body', {}).get('attachmentId')
                    })
                
                # Check nested parts
                if 'parts' in part:
                    _process_parts(part['parts'])
        
        if 'parts' in payload:
            _process_parts(payload['parts'])
        
        return attachments
    
    async def stop(self):
        """Stop watching the inbox (cleanup method)"""
        logger.info("Stopping Gmail inbox watcher")
        # TODO: Implement any cleanup needed


# Example usage and testing
async def test_gmail_watcher():
    """Test function for the Gmail watcher"""
    watcher = GmailInboxWatcher(poll_interval=10)
    
    # Authenticate
    auth_result = await watcher.authenticate()
    print(f"Authentication result: {auth_result}")
    
    if auth_result['status'] == 'authorization_required':
        print(f"Please visit: {auth_result['auth_url']}")
        auth_code = input("Enter authorization code: ")
        auth_result = await watcher.authenticate(auth_code)
        print(f"Authentication result: {auth_result}")
    
    if auth_result['status'] == 'authenticated':
        print("Watching for new emails...")
        try:
            # This will block until a new email arrives
            email_event = await watcher.watch()
            print(f"New email received!")
            print(f"From: {email_event.sender}")
            print(f"Subject: {email_event.subject}")
            print(f"Body preview: {email_event.body[:100]}...")
            print(f"Attachments: {len(email_event.attachments)}")
        except KeyboardInterrupt:
            print("\nStopping watcher...")
            await watcher.stop()


if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_gmail_watcher())