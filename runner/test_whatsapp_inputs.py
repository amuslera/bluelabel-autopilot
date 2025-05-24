#!/usr/bin/env python3
"""
WhatsApp Input Validation Tests

This script tests the WhatsApp webhook input validation by sending various
payloads to the WhatsApp adapter and verifying the responses.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.whatsapp_adapter import process_webhook

# Test data
TEST_PAYLOADS = {
    "valid_url": {
        "type": "url",
        "value": "https://example.com"
    },
    "valid_pdf": {
        "type": "pdf",
        "value": "/tmp/test.pdf"  # Note: This file doesn't exist, but we're testing input validation
    },
    "missing_type": {
        "value": "some value"
    },
    "missing_value": {
        "type": "url"
    },
    "invalid_type": {
        "type": "unsupported_type",
        "value": "some value"
    },
    "empty_value": {
        "type": "url",
        "value": ""
    },
    "null_value": {
        "type": "url",
        "value": None
    },
    "extra_fields": {
        "type": "url",
        "value": "https://example.com",
        "extra": "should be ignored"
    }
}

async def run_test(payload_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single test case and return the result."""
    print(f"\n=== Testing: {payload_name} ===")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = await process_webhook(payload)
        print(f"Response: {json.dumps(response, indent=2)}")
        return {"status": "success", "response": response}
    except Exception as e:
        error = str(e)
        print(f"Error: {error}")
        return {"status": "error", "error": error}

async def run_all_tests():
    """Run all test cases and collect results."""
    results = {}
    
    for name, payload in TEST_PAYLOADS.items():
        results[name] = await run_test(name, payload)
    
    return results

def generate_report(results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a test report from the results."""
    report = {
        "timestamp": {"$date": {"$numberLong": str(int(asyncio.get_event_loop().time() * 1000))}},
        "test_cases": {},
        "summary": {
            "total": len(results),
            "passed": 0,
            "failed": 0,
            "success_rate": 0.0
        }
    }
    
    for name, result in results.items():
        is_success = result["status"] == "success"
        report["test_cases"][name] = {
            "status": "PASS" if is_success else "FAIL",
            "result": result
        }
        
        if is_success:
            report["summary"]["passed"] += 1
        else:
            report["summary"]["failed"] += 1
    
    report["summary"]["success_rate"] = (
        report["summary"]["passed"] / report["summary"]["total"] * 100
    )
    
    return report

async def main():
    """Main function to run the tests."""
    parser = argparse.ArgumentParser(description="Run WhatsApp input validation tests")
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        default="whatsapp_test_report.json",
        help="Output file for the test report"
    )
    args = parser.parse_args()
    
    print("=== Starting WhatsApp Input Validation Tests ===")
    results = await run_all_tests()
    report = generate_report(results)
    
    # Save the report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n=== Test Report ===")
    print(f"Total tests: {report['summary']['total']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Success rate: {report['summary']['success_rate']:.1f}%")
    print(f"\nReport saved to: {args.output}")
    
    # Return non-zero exit code if any tests failed
    sys.exit(1 if report['summary']['failed'] > 0 else 0)

if __name__ == "__main__":
    asyncio.run(main())
