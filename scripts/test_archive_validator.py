#!/usr/bin/env python3
"""
Test script for archive validator
Creates test scenarios with broken paths and missing files.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

def create_test_scenarios():
    """Create various test scenarios for validation."""
    print("Creating test scenarios...")
    
    # Create a test workflow directory
    test_workflow = Path("data/workflows/test_validation_workflow")
    test_workflow.mkdir(parents=True, exist_ok=True)
    
    # Scenario 1: Valid run with all files
    valid_run = test_workflow / "valid-run-001"
    valid_run.mkdir(exist_ok=True)
    
    # Create workflow.yaml
    (valid_run / "workflow.yaml").write_text("""workflow:
  name: Test Workflow
  version: 1.0.0
steps:
  - id: step1
    agent: test
""")
    
    # Create run_metadata.json
    (valid_run / "run_metadata.json").write_text(json.dumps({
        "workflow_name": "Test Workflow",
        "version": "1.0.0",
        "run_id": "valid-run-001",
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "duration_ms": 1000
    }, indent=2))
    
    # Create step output
    (valid_run / "step1_output.json").write_text(json.dumps({
        "status": "success",
        "result": {"data": "test"}
    }, indent=2))
    
    # Scenario 2: Run with missing metadata
    partial_run = test_workflow / "partial-run-002"
    partial_run.mkdir(exist_ok=True)
    (partial_run / "workflow.yaml").write_text("workflow:\n  name: Test\n")
    # Missing run_metadata.json and step outputs
    
    # Scenario 3: Run with corrupt JSON
    corrupt_run = test_workflow / "corrupt-run-003"
    corrupt_run.mkdir(exist_ok=True)
    (corrupt_run / "workflow.yaml").write_text("workflow:\n  name: Test\n")
    (corrupt_run / "run_metadata.json").write_text("{invalid json")
    (corrupt_run / "step1_output.json").write_text('{"status": ')
    
    # Add test entries to archive
    test_archive = [
        {
            "workflow_id": "test_validation_workflow",
            "run_id": "valid-run-001",
            "timestamp": datetime.now().isoformat(),
            "workflow_name": "Test Workflow",
            "version": "1.0.0",
            "status": "success",
            "duration_ms": 1000,
            "tags": ["test"],
            "summary": "Valid test run",
            "source": {"type": "test"}
        },
        {
            "workflow_id": "test_validation_workflow",
            "run_id": "partial-run-002",
            "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
            "workflow_name": "Test Workflow",
            "version": "1.0.0",
            "status": "success",
            "duration_ms": 500,
            "tags": [],
            "summary": "",
            "source": {}
        },
        {
            "workflow_id": "test_validation_workflow",
            "run_id": "corrupt-run-003",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "workflow_name": "Test Workflow",
            "version": "1.0.0",
            "status": "failed",
            "duration_ms": -100,  # Invalid duration
            "tags": [],
            "summary": "",
            "source": "invalid"  # Should be dict
        },
        {
            "workflow_id": "test_validation_workflow",
            "run_id": "missing-run-004",
            "timestamp": "invalid-timestamp",
            "workflow_name": "Test Workflow",
            "version": "1.0.0",
            "status": "unknown",  # Invalid status
            "duration_ms": 200,
            "tags": [],
            "summary": "",
            "source": {}
        },
        {
            # Missing required fields
            "workflow_id": "test_validation_workflow",
            "run_id": "incomplete-run-005",
            # Missing timestamp
            # Missing workflow_name
            "status": "success"
        }
    ]
    
    # Create test archive file
    test_archive_path = Path("data/workflows/test_archive.json")
    with open(test_archive_path, 'w') as f:
        json.dump(test_archive, f, indent=2)
    
    print(f"✓ Created {len(test_archive)} test scenarios")
    return test_archive_path


def main():
    """Run validation tests."""
    print("=== Archive Validator Test ===\n")
    
    # 1. Create test scenarios
    test_archive_path = create_test_scenarios()
    
    # 2. Run validator on test data
    print("\n2. Running validator on test scenarios...")
    result = subprocess.run([
        sys.executable, "runner/validate_archive_integrity.py",
        "--archive", str(test_archive_path),
        "--output", "logs/test_validation_results.json",
        "--log", "logs/test_validation.log"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print("   ✓ Validator correctly detected issues")
    else:
        print("   ✗ Validator should have found issues")
    
    # 3. Check results file
    print("\n3. Checking validation results...")
    results_path = Path("logs/test_validation_results.json")
    
    if results_path.exists():
        with open(results_path) as f:
            results = json.load(f)
        
        summary = results.get('summary', {})
        print(f"   Total entries: {summary.get('total_entries', 0)}")
        print(f"   Valid entries: {summary.get('valid_entries', 0)}")
        print(f"   Invalid entries: {summary.get('invalid_entries', 0)}")
        
        if summary.get('error_types'):
            print("\n   Error types found:")
            for error_type, count in summary['error_types'].items():
                print(f"     - {error_type}: {count}")
        
        if summary.get('warning_types'):
            print("\n   Warning types found:")
            for warning_type, count in summary['warning_types'].items():
                print(f"     - {warning_type}: {count}")
    
    # 4. Test date filtering
    print("\n4. Testing date filtering...")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    result = subprocess.run([
        sys.executable, "runner/validate_archive_integrity.py",
        "--archive", str(test_archive_path),
        "--start", tomorrow,
        "--verbose"
    ], capture_output=True, text=True)
    
    if "Filtered to 0 entries" in result.stdout:
        print("   ✓ Date filtering works correctly")
    else:
        print("   ✗ Date filtering issue")
    
    # 5. Test on real archive
    print("\n5. Testing on real archive (sample)...")
    result = subprocess.run([
        sys.executable, "runner/validate_archive_integrity.py",
        "--start", datetime.now().strftime('%Y-%m-%d'),
        "--end", datetime.now().strftime('%Y-%m-%d')
    ], capture_output=True, text=True)
    
    print("   ✓ Real archive validation completed")
    
    # 6. Clean up test data
    print("\n6. Cleaning up test data...")
    test_workflow = Path("data/workflows/test_validation_workflow")
    if test_workflow.exists():
        shutil.rmtree(test_workflow)
    
    test_archive_path.unlink(missing_ok=True)
    
    print("\n✅ All tests completed!")
    
    # Show log files created
    print("\nLog files created:")
    for log_file in sorted(Path("logs").glob("*.json")):
        print(f"   - {log_file}")
    for log_file in sorted(Path("logs").glob("*.log")):
        print(f"   - {log_file}")


if __name__ == "__main__":
    main()