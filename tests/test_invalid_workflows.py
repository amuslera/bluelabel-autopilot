#!/usr/bin/env python3
"""
Test script for validating DAG parser error handling with invalid workflows.
"""

import os
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Invalid workflow test cases
TEST_CASES = [
    {
        "file": "missing_steps.yaml",
        "description": "Workflow missing required 'steps' section",
        "expected_error": "Workflow file must contain a 'steps' section"
    },
    {
        "file": "bad_reference.yaml", 
        "description": "Step references nonexistent step",
        "expected_error": "references unknown step"
    },
    {
        "file": "circular_dependency.yaml",
        "description": "Workflow has circular dependencies",
        "expected_error": "Circular dependency detected"
    },
    {
        "file": "invalid_agent.yaml",
        "description": "Workflow uses nonexistent agent names",
        "expected_error": None  # Loader doesn't validate agents
    },
    {
        "file": "incomplete_steps.yaml",
        "description": "Steps missing required fields",
        "expected_error": "must have an 'agent' field"
    }
]

def test_workflow_loader(workflow_path):
    """Test workflow_loader.py with the given workflow file."""
    cmd = [
        sys.executable,
        "runner/workflow_loader.py",
        "--workflow",
        workflow_path
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    return result.returncode, result.stdout, result.stderr

def test_workflow_executor(workflow_path):
    """Test workflow_executor.py with the given workflow file."""
    cmd = [
        sys.executable,
        "runner/workflow_executor.py",
        workflow_path
    ]
    
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent
    )
    
    return result.returncode, result.stdout, result.stderr

def main():
    """Run all invalid workflow tests."""
    print("=" * 60)
    print("DAG Parser Validation Test Suite")
    print("=" * 60)
    
    invalid_dir = Path(__file__).parent / "invalid_workflows"
    results = []
    
    for test_case in TEST_CASES:
        workflow_path = invalid_dir / test_case["file"]
        print(f"\nTest: {test_case['description']}")
        print(f"File: {test_case['file']}")
        print("-" * 40)
        
        # Test with workflow_loader.py
        print("Testing with workflow_loader.py...")
        loader_code, loader_out, loader_err = test_workflow_loader(str(workflow_path))
        
        if test_case["expected_error"]:
            if test_case["expected_error"] in (loader_out + loader_err):
                print("✅ Loader correctly rejected with expected error")
                loader_passed = True
            else:
                print("❌ Loader did not show expected error")
                loader_passed = False
        else:
            if loader_code == 0:
                print("⚠️  Loader accepted invalid workflow (no validation for this case)")
                loader_passed = True  # Expected behavior
            else:
                print("❌ Loader rejected workflow unexpectedly")
                loader_passed = False
        
        # Test with workflow_executor.py (only if loader passes)
        executor_passed = None
        if loader_code == 0:  # Loader accepted it
            print("\nTesting with workflow_executor.py...")
            exec_code, exec_out, exec_err = test_workflow_executor(str(workflow_path))
            
            if exec_code != 0:
                print("✅ Executor correctly failed during execution")
                executor_passed = True
            else:
                print("❌ Executor succeeded with invalid workflow")
                executor_passed = False
        
        results.append({
            "test": test_case["description"],
            "loader_passed": loader_passed,
            "executor_passed": executor_passed,
            "error_output": loader_err if loader_err else loader_out
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    total_tests = len(results)
    loader_passes = sum(1 for r in results if r["loader_passed"])
    
    print(f"\nTotal tests: {total_tests}")
    print(f"Loader validation passed: {loader_passes}/{total_tests}")
    
    print("\nDetailed Results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['test']}")
        print(f"   Loader: {'✅ PASS' if result['loader_passed'] else '❌ FAIL'}")
        if result['executor_passed'] is not None:
            print(f"   Executor: {'✅ PASS' if result['executor_passed'] else '❌ FAIL'}")

if __name__ == "__main__":
    main()