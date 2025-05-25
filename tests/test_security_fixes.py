"""
Test script to verify security fixes are working correctly.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import tempfile
import json
from services.security import CredentialManager, store_oauth_token, retrieve_oauth_token
from services.validation import validate_workflow_file, WorkflowValidator
from services.pdf import PDFStreamHandler, process_pdf_safely


def test_credential_encryption():
    """Test that credentials are properly encrypted."""
    print("\n=== Testing Credential Encryption ===")
    
    # Create test credentials
    test_creds = {
        "access_token": "ya29.test_access_token",
        "refresh_token": "1//test_refresh_token",
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": "test_client_id.apps.googleusercontent.com",
        "client_secret": "test_client_secret",
        "scopes": ["https://www.googleapis.com/auth/gmail.readonly"]
    }
    
    # Store credentials
    store_oauth_token('test_service', test_creds)
    print("✓ Stored test OAuth token")
    
    # Retrieve credentials
    retrieved = retrieve_oauth_token('test_service')
    print("✓ Retrieved OAuth token")
    
    # Verify they match
    assert retrieved == test_creds, "Retrieved credentials don't match"
    print("✓ Credentials match after encryption/decryption")
    
    # Check that the stored file is encrypted (not readable as JSON)
    manager = CredentialManager()
    cred_path = manager._get_credential_path('oauth_test_service')
    
    if cred_path.exists():
        with open(cred_path, 'rb') as f:
            encrypted_content = f.read()
        
        # Try to parse as JSON - should fail because it's encrypted
        try:
            json.loads(encrypted_content)
            print("✗ ERROR: Credentials are stored in plain text!")
            return False
        except:
            print("✓ Credentials are properly encrypted on disk")
    
    # Clean up
    manager.delete_credential('oauth_test_service')
    print("✓ Cleaned up test credentials")
    
    return True


def test_workflow_validation():
    """Test workflow validation for security issues."""
    print("\n=== Testing Workflow Validation ===")
    
    validator = WorkflowValidator()
    
    # Test 1: Valid workflow
    valid_workflow = {
        "workflow": {
            "name": "Test Workflow",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": "step1",
                "agent": "ingestion_agent",
                "input_file": "test.json"
            }
        ]
    }
    
    is_valid, error = validator.validate_workflow(valid_workflow)
    assert is_valid, f"Valid workflow rejected: {error}"
    print("✓ Valid workflow accepted")
    
    # Test 2: Command injection attempt
    malicious_workflow1 = {
        "workflow": {
            "name": "Test `rm -rf /`",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": "step1",
                "agent": "ingestion_agent",
                "input_file": "test.json"
            }
        ]
    }
    
    is_valid, error = validator.validate_workflow(malicious_workflow1)
    assert not is_valid, "Command injection not detected"
    assert "Dangerous pattern" in error
    print("✓ Command injection blocked")
    
    # Test 3: Path traversal attempt
    malicious_workflow2 = {
        "workflow": {
            "name": "Test Workflow",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": "step1",
                "agent": "ingestion_agent",
                "input_file": "../../etc/passwd"
            }
        ]
    }
    
    is_valid, error = validator.validate_workflow(malicious_workflow2)
    assert not is_valid, "Path traversal not detected"
    assert "Dangerous pattern" in error
    print("✓ Path traversal blocked")
    
    # Test 4: Python code injection
    malicious_workflow3 = {
        "workflow": {
            "name": "Test Workflow",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": "step1",
                "agent": "ingestion_agent",
                "input_file": "test.json",
                "config": {
                    "code": "__import__('os').system('ls')"
                }
            }
        ]
    }
    
    is_valid, error = validator.validate_workflow(malicious_workflow3)
    assert not is_valid, "Python code injection not detected"
    assert "Dangerous pattern" in error
    print("✓ Python code injection blocked")
    
    # Test 5: Unknown agent
    invalid_workflow = {
        "workflow": {
            "name": "Test Workflow",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": "step1",
                "agent": "malicious_agent",
                "input_file": "test.json"
            }
        ]
    }
    
    is_valid, error = validator.validate_workflow(invalid_workflow)
    assert not is_valid, "Unknown agent not detected"
    assert "disallowed agent" in error
    print("✓ Unknown agent blocked")
    
    return True


def test_pdf_streaming():
    """Test PDF streaming for large files."""
    print("\n=== Testing PDF Streaming ===")
    
    # Create a test PDF path (would need actual PDF for real test)
    test_pdf = Path("tests/sample.pdf")
    
    if test_pdf.exists():
        handler = PDFStreamHandler(str(test_pdf))
        
        # Get metadata without loading full file
        metadata = handler.get_metadata()
        print(f"✓ Got PDF metadata: {metadata.get('page_count', 'unknown')} pages")
        
        # Check if should stream
        should_stream = handler.should_stream()
        print(f"✓ Stream decision: {'Yes' if should_stream else 'No'} (file size: {handler.file_size} bytes)")
        
        # Validate PDF
        is_valid, error = handler.validate_pdf()
        assert is_valid, f"PDF validation failed: {error}"
        print("✓ PDF validation passed")
        
        return True
    else:
        print("⚠ Skipping PDF test - no sample.pdf found")
        return True


def test_size_limits():
    """Test that size limits are enforced."""
    print("\n=== Testing Size Limits ===")
    
    # Test workflow size limit
    validator = WorkflowValidator()
    
    # Create oversized workflow
    huge_workflow = {
        "workflow": {
            "name": "Test",
            "version": "1.0.0",
            "description": "x" * (validator.MAX_STRING_LENGTH + 1)
        },
        "steps": [{
            "id": "step1",
            "agent": "ingestion_agent",
            "input_file": "test.json"
        }]
    }
    
    is_valid, error = validator.validate_workflow(huge_workflow)
    assert not is_valid, "Oversized string not detected"
    assert "String too long" in error
    print("✓ String size limit enforced")
    
    # Test too many steps
    many_steps_workflow = {
        "workflow": {
            "name": "Test",
            "version": "1.0.0"
        },
        "steps": [
            {
                "id": f"step{i}",
                "agent": "ingestion_agent",
                "input_file": "test.json" if i == 0 else None,
                "input_from": f"step{i-1}" if i > 0 else None
            }
            for i in range(validator.MAX_STEPS + 1)
        ]
    }
    
    is_valid, error = validator.validate_workflow(many_steps_workflow)
    assert not is_valid, "Too many steps not detected"
    assert "Too many steps" in error
    print("✓ Step count limit enforced")
    
    return True


async def main():
    """Run all security tests."""
    print("🔒 Security Fix Verification Tests")
    print("=" * 50)
    
    all_passed = True
    
    # Test 1: Credential Encryption
    try:
        if not test_credential_encryption():
            all_passed = False
    except Exception as e:
        print(f"✗ Credential encryption test failed: {e}")
        all_passed = False
    
    # Test 2: Workflow Validation
    try:
        if not test_workflow_validation():
            all_passed = False
    except Exception as e:
        print(f"✗ Workflow validation test failed: {e}")
        all_passed = False
    
    # Test 3: PDF Streaming
    try:
        if not test_pdf_streaming():
            all_passed = False
    except Exception as e:
        print(f"✗ PDF streaming test failed: {e}")
        all_passed = False
    
    # Test 4: Size Limits
    try:
        if not test_size_limits():
            all_passed = False
    except Exception as e:
        print(f"✗ Size limit test failed: {e}")
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ All security tests passed!")
    else:
        print("❌ Some security tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())