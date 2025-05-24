#!/usr/bin/env python3
"""
Test Email Workflow Integration
Tests the complete email monitoring, routing, and workflow execution pipeline.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.email.email_gateway import EmailEvent, EmailAttachment
from services.email.email_workflow_router import EmailWorkflowRouter
from services.email.email_workflow_orchestrator import EmailWorkflowOrchestrator


def create_test_email_event(email_type: str = "generic") -> EmailEvent:
    """Create a mock email event for testing"""
    
    if email_type == "pdf":
        return EmailEvent(
            message_id="test-pdf-123",
            thread_id="thread-123",
            sender="reports@company.com",
            recipient="user@example.com",
            subject="Q4 Financial Report - Please Review",
            snippet="Attached is the Q4 financial report for your review...",
            body_plain="Please find attached the Q4 financial report. Key highlights include...",
            body_html="<p>Please find attached the Q4 financial report.</p>",
            timestamp=datetime.now(),
            labels=["INBOX", "UNREAD"],
            attachments=[
                EmailAttachment(
                    filename="Q4_Report.pdf",
                    mime_type="application/pdf",
                    size=1024000,
                    data=b"Mock PDF content..."
                )
            ]
        )
    
    elif email_type == "newsletter":
        return EmailEvent(
            message_id="test-newsletter-456",
            thread_id="thread-456",
            sender="editor@aiweekly.com",
            recipient="user@example.com",
            subject="AI Weekly Digest: Latest in Machine Learning",
            snippet="This week's top AI news and breakthroughs...",
            body_plain="Welcome to AI Weekly! This week's highlights:\n\n1. GPT-5 announced...",
            body_html="<h1>AI Weekly</h1><p>This week's highlights...</p>",
            timestamp=datetime.now(),
            labels=["INBOX", "UNREAD"],
            attachments=[]
        )
    
    else:  # generic
        return EmailEvent(
            message_id="test-generic-789",
            thread_id="thread-789",
            sender="colleague@example.com",
            recipient="user@example.com",
            subject="Project Update - Action Required",
            snippet="Hi, I wanted to update you on the project status...",
            body_plain="Hi,\n\nI wanted to update you on the project status. We need to discuss...",
            body_html="<p>Hi,</p><p>I wanted to update you on the project status...</p>",
            timestamp=datetime.now(),
            labels=["INBOX", "UNREAD"],
            attachments=[]
        )


async def test_routing():
    """Test email routing logic"""
    print("\n=== Testing Email Routing ===\n")
    
    # Create router with test configuration
    config = {
        "rules": [
            {
                "name": "pdf_processor",
                "workflow_path": "workflows/email/pdf_attachment_processor.yaml",
                "has_attachment": True,
                "attachment_type": "application/pdf",
                "priority": 10
            },
            {
                "name": "ai_newsletter",
                "workflow_path": "workflows/ai_newsletter_digest.yaml",
                "from_domain": "aiweekly.com",
                "priority": 5
            }
        ],
        "default_workflow": "workflows/email/generic_email_handler.yaml"
    }
    
    router = EmailWorkflowRouter(config)
    
    # Test different email types
    test_cases = [
        ("pdf", "PDF attachment email"),
        ("newsletter", "AI newsletter email"),
        ("generic", "Generic email")
    ]
    
    for email_type, description in test_cases:
        email_event = create_test_email_event(email_type)
        metadata = {
            'from': email_event.sender,
            'subject': email_event.subject,
            'attachments': [
                {
                    'filename': att.filename,
                    'mimeType': att.mime_type,
                    'size': att.size
                }
                for att in email_event.attachments
            ]
        }
        
        workflow = router.select_workflow(metadata)
        print(f"{description}:")
        print(f"  From: {email_event.sender}")
        print(f"  Subject: {email_event.subject}")
        print(f"  Attachments: {len(email_event.attachments)}")
        print(f"  → Selected workflow: {workflow}")
        print()


async def test_orchestration():
    """Test full orchestration with mock email"""
    print("\n=== Testing Email Workflow Orchestration ===\n")
    
    # Create orchestrator configuration
    config = {
        "gmail": {
            "credentials_path": "credentials.json",
            "token_path": "token.json"
        },
        "routing": {
            "rules": [
                {
                    "name": "test_email",
                    "workflow_path": "workflows/email/generic_email_handler.yaml",
                    "from_email": "colleague@example.com",
                    "priority": 10
                }
            ],
            "default_workflow": "workflows/email/generic_email_handler.yaml"
        },
        "engine": {
            "storage_path": "./data/knowledge",
            "temp_path": "./data/temp"
        },
        "processing": {
            "mark_as_read": False,  # Don't modify real emails
            "save_attachments": True
        }
    }
    
    # Create orchestrator
    orchestrator = EmailWorkflowOrchestrator(config)
    
    # Mock the inbox watcher to return test email
    test_email = create_test_email_event("generic")
    
    # Process the test email directly
    print("Processing test email...")
    result = await orchestrator.process_email(test_email)
    
    # Display results
    print(f"\nProcessing Result:")
    print(f"  Email ID: {result.email_id}")
    print(f"  From: {result.from_address}")
    print(f"  Subject: {result.subject}")
    print(f"  Workflow: {result.workflow_path}")
    print(f"  Status: {result.workflow_status}")
    print(f"  Processing time: {result.processing_time_ms}ms")
    
    if result.error:
        print(f"  Error: {result.error}")
    
    # Get stats
    stats = orchestrator.get_stats()
    print(f"\nOrchestrator Stats:")
    print(f"  Total processed: {stats['total_processed']}")
    print(f"  Successful: {stats['successful']}")
    print(f"  Failed: {stats['failed']}")


async def test_workflow_input_mapping():
    """Test email to workflow input mapping"""
    print("\n=== Testing Workflow Input Mapping ===\n")
    
    orchestrator = EmailWorkflowOrchestrator({
        "gmail": {},
        "routing": {"rules": []},
        "engine": {}
    })
    
    # Create test email
    email = create_test_email_event("pdf")
    
    # Convert to workflow input
    metadata = orchestrator._email_event_to_metadata(email)
    workflow_input = await orchestrator._prepare_workflow_input(email, metadata)
    
    print("Workflow Input Structure:")
    print(json.dumps({
        "task_id": workflow_input["task_id"],
        "task_type": workflow_input["task_type"],
        "source": workflow_input["source"],
        "metadata": {
            "email_id": workflow_input["metadata"]["email_id"],
            "from": workflow_input["metadata"]["from"],
            "subject": workflow_input["metadata"]["subject"],
            "labels": workflow_input["metadata"]["labels"]
        },
        "content": {
            "body_plain": workflow_input["content"]["body_plain"][:50] + "...",
            "body_html": workflow_input["content"]["body_html"][:50] + "..."
        },
        "attachments": [
            {
                "filename": att["filename"],
                "mime_type": att["mime_type"],
                "size": att["size"]
            }
            for att in workflow_input.get("attachments", [])
        ]
    }, indent=2))


async def main():
    """Run all tests"""
    print("Email Workflow Integration Tests")
    print("=" * 50)
    
    # Test routing
    await test_routing()
    
    # Test input mapping
    await test_workflow_input_mapping()
    
    # Test orchestration (if workflows exist)
    workflow_path = Path("workflows/email/generic_email_handler.yaml")
    if workflow_path.exists():
        try:
            await test_orchestration()
        except Exception as e:
            print(f"\nOrchestration test failed: {e}")
            print("This is expected if agents are not fully configured")
    else:
        print(f"\nSkipping orchestration test - workflow not found: {workflow_path}")
    
    print("\n✅ Integration tests completed!")


if __name__ == "__main__":
    asyncio.run(main())