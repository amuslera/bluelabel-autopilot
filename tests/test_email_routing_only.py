#!/usr/bin/env python3
"""
Test Email Routing Logic
Tests just the email routing component without Gmail dependencies.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.email.email_workflow_router import EmailWorkflowRouter


def test_routing_logic():
    """Test email routing with various scenarios"""
    print("Email Routing Logic Test")
    print("=" * 50)
    
    # Create router configuration
    config = {
        "rules": [
            {
                "name": "pdf_processor",
                "workflow_path": "email/pdf_attachment_processor.yaml",
                "has_attachment": True,
                "attachment_type": "application/pdf",
                "priority": 20
            },
            {
                "name": "ai_newsletter",
                "workflow_path": "ai_newsletter_digest.yaml",
                "from_domain": ["aiweekly.com", "mlnews.org"],
                "subject_contains": ["AI", "machine learning"],
                "priority": 15
            },
            {
                "name": "customer_support",
                "workflow_path": "customer_support.yaml",
                "from_email": ["support@", "feedback@"],
                "priority": 10
            },
            {
                "name": "url_extractor",
                "workflow_path": "url_content_digest.yaml",
                "subject_contains": ["link:", "check out", "interesting article"],
                "priority": 5
            }
        ],
        "default_workflow": "email/generic_email_handler.yaml"
    }
    
    router = EmailWorkflowRouter(config)
    
    # Test cases
    test_cases = [
        {
            "name": "PDF Report Email",
            "metadata": {
                "from": "reports@company.com",
                "subject": "Q4 Financial Report",
                "attachments": [
                    {"filename": "report.pdf", "mimeType": "application/pdf", "size": 1024000}
                ]
            },
            "expected": "workflows/email/pdf_attachment_processor.yaml"
        },
        {
            "name": "AI Newsletter",
            "metadata": {
                "from": "editor@aiweekly.com",
                "subject": "AI Weekly: Latest in Machine Learning",
                "attachments": []
            },
            "expected": "workflows/ai_newsletter_digest.yaml"
        },
        {
            "name": "Customer Support",
            "metadata": {
                "from": "support@customerservice.com",
                "subject": "Re: Issue with your product",
                "attachments": []
            },
            "expected": "workflows/customer_support.yaml"
        },
        {
            "name": "Article Link",
            "metadata": {
                "from": "colleague@example.com",
                "subject": "Check out this interesting article on Python",
                "attachments": []
            },
            "expected": "workflows/url_content_digest.yaml"
        },
        {
            "name": "Generic Email",
            "metadata": {
                "from": "random@example.com",
                "subject": "Meeting tomorrow",
                "attachments": []
            },
            "expected": "workflows/email/generic_email_handler.yaml"
        },
        {
            "name": "Multiple Match (PDF wins by priority)",
            "metadata": {
                "from": "editor@aiweekly.com",
                "subject": "AI Report - check out the attached PDF",
                "attachments": [
                    {"filename": "ai_report.pdf", "mimeType": "application/pdf", "size": 500000}
                ]
            },
            "expected": "workflows/email/pdf_attachment_processor.yaml"
        }
    ]
    
    # Run tests
    print("\nTest Results:")
    print("-" * 50)
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        workflow = router.select_workflow(test["metadata"])
        success = workflow == test["expected"]
        
        if success:
            passed += 1
            status = "✅ PASS"
        else:
            failed += 1
            status = "❌ FAIL"
        
        print(f"\n{status} {test['name']}")
        print(f"  From: {test['metadata']['from']}")
        print(f"  Subject: {test['metadata']['subject']}")
        print(f"  Attachments: {len(test['metadata']['attachments'])}")
        print(f"  Expected: {test['expected']}")
        print(f"  Got: {workflow}")
    
    # Summary
    print("\n" + "=" * 50)
    print(f"Total: {len(test_cases)} | Passed: {passed} | Failed: {failed}")
    
    # List all rules
    print("\nConfigured Rules (by priority):")
    for rule in router.list_rules():
        print(f"  {rule['priority']:2d}: {rule['name']} -> {rule['workflow']}")
    
    return failed == 0


if __name__ == "__main__":
    success = test_routing_logic()
    sys.exit(0 if success else 1)