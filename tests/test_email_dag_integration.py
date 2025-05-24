#!/usr/bin/env python3
"""
Test Email DAG Integration
Demonstrates workflow execution with email delivery on completion.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.email.email_output_adapter import EmailOutAdapter
from services.email.email_output_formatter import format_digest_markdown, format_digest_plaintext
from core.workflow_engine import run_workflow
from interfaces.run_models import WorkflowRunResult


async def email_delivery_callback(config: dict, format_type: str = 'markdown'):
    """
    Create a callback function for email delivery.
    
    Args:
        config: Email adapter configuration
        format_type: 'markdown' or 'plaintext'
    
    Returns:
        Async callback function
    """
    adapter = EmailOutAdapter(config)
    
    async def send_output(result: WorkflowRunResult):
        """Send workflow output via email"""
        print(f"\n📧 Email delivery callback triggered")
        print(f"Workflow status: {result.status.value}")
        
        # Extract output from last successful step
        output_data = None
        for step_id in reversed(result.execution_order or []):
            step_result = result.step_outputs.get(step_id)
            if step_result and step_result.status == "success" and step_result.result:
                output_data = step_result.result
                break
        
        if not output_data:
            print("❌ No output data found")
            return
        
        # Prepare digest data
        digest_data = {
            'title': f"Workflow Complete: {result.workflow_name}",
            'content': output_data.get('digest', output_data.get('summary', 'No summary available')),
            'source': {
                'tags': [result.workflow_name, f"v{result.workflow_version}"]
            },
            'timestamp': result.completed_at.isoformat() if result.completed_at else None
        }
        
        # Format content
        if format_type == 'plaintext':
            content = format_digest_plaintext(digest_data)
            content_type = 'plain'
        else:
            content = format_digest_markdown(digest_data)
            content_type = 'html'
        
        # Send email
        success = await adapter.send_output(
            content=content,
            subject=f"Workflow Result: {result.workflow_name}",
            recipient=config.get('recipient', 'test@example.com'),
            content_type=content_type
        )
        
        if success:
            print("✅ Email sent successfully!")
        else:
            print("❌ Email delivery failed")
    
    return send_output


async def test_workflow_with_email():
    """Test workflow execution with email delivery"""
    print("=== Testing Workflow with Email Delivery ===\n")
    
    # Email configuration (using local test server)
    email_config = {
        'smtp_server': 'localhost',
        'smtp_port': 1025,  # Local test server
        'from_email': 'workflow@example.com',
        'recipient': 'user@example.com',
        'use_tls': False
    }
    
    # Create callback
    on_complete = await email_delivery_callback(email_config, 'markdown')
    
    # Run workflow with email delivery
    print("🚀 Starting workflow execution...")
    result = await run_workflow(
        path='workflows/sample_ingestion_digest.yaml',
        persist=True,
        on_complete=on_complete
    )
    
    print(f"\n✅ Workflow completed: {result.status.value}")
    print(f"Run ID: {result.run_id}")
    print(f"Duration: {result.duration_ms}ms")
    
    # Display step results
    print("\n📊 Step Results:")
    for step_id, step_result in result.step_outputs.items():
        print(f"  - {step_result.step_name}: {step_result.status}")


async def test_email_adapter_directly():
    """Test email adapter directly"""
    print("\n=== Testing Email Adapter Directly ===\n")
    
    config = {
        'smtp_server': 'localhost',
        'smtp_port': 1025,
        'from_email': 'test@example.com',
        'use_tls': False
    }
    
    adapter = EmailOutAdapter(config)
    
    # Test markdown email
    digest_data = {
        'title': 'Test Email Integration',
        'content': 'This is a test of the email delivery system with workflow integration.',
        'source': {
            'url': 'https://example.com',
            'tags': ['test', 'integration']
        },
        'timestamp': datetime.utcnow().isoformat()
    }
    
    markdown_content = format_digest_markdown(digest_data)
    success = await adapter.send_output(
        content=markdown_content,
        subject='Test: Markdown Email',
        recipient='test@example.com',
        content_type='html'
    )
    
    print(f"Markdown email sent: {'✅' if success else '❌'}")
    
    # Test plaintext email
    plaintext_content = format_digest_plaintext(digest_data)
    success = await adapter.send_output(
        content=plaintext_content,
        subject='Test: Plaintext Email',
        recipient='test@example.com',
        content_type='plain'
    )
    
    print(f"Plaintext email sent: {'✅' if success else '❌'}")


def start_test_smtp_server():
    """Instructions for starting a test SMTP server"""
    print("\n📮 To test email delivery, start a local SMTP server:")
    print("   python -m smtpd -n -c DebuggingServer localhost:1025")
    print("\nThis will print all emails to the console.\n")


async def main():
    """Run all tests"""
    start_test_smtp_server()
    
    # Test direct adapter
    await test_email_adapter_directly()
    
    # Test workflow integration
    await test_workflow_with_email()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())