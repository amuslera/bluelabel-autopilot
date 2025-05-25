#!/usr/bin/env python3
"""
End-to-End Workflow Test Script
Tests workflow execution with archive generation and email snapshots.
"""

import asyncio
import sys
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflow_engine import run_workflow
from services.email.email_snapshot import EmailSnapshot


async def test_workflow_with_snapshots():
    """Run workflow and verify all outputs including archives and snapshots."""
    
    print("=== End-to-End Workflow Test ===\n")
    
    # 1. Run a sample workflow
    workflow_path = "workflows/sample_ingestion_digest.yaml"
    print(f"1. Running workflow: {workflow_path}")
    
    try:
        result = await run_workflow(workflow_path, persist=True)
        print(f"   ✓ Workflow completed: {result.status.value}")
        print(f"   ✓ Run ID: {result.run_id}")
        print(f"   ✓ Duration: {result.duration_ms}ms")
        print(f"   ✓ Output directory: {result.output_directory}")
    except Exception as e:
        print(f"   ✗ Workflow failed: {e}")
        return False
    
    # 2. Check run_archive.json
    print("\n2. Checking run_archive.json")
    archive_path = Path("data/workflows/run_archive.json")
    
    if archive_path.exists():
        with open(archive_path) as f:
            archive = json.load(f)
        print(f"   ✓ Archive exists with {len(archive)} entries")
        if archive:
            latest = archive[-1]
            print(f"   ✓ Latest entry: {latest['workflow_name']} ({latest['run_id'][:8]}...)")
            print(f"   ✓ Status: {latest['status']}")
            print(f"   ✓ Summary: {latest.get('summary', 'N/A')[:100]}...")
    else:
        print("   ✗ run_archive.json not found")
        return False
    
    # 3. Test email snapshot
    print("\n3. Testing email snapshot functionality")
    
    # Extract output from workflow
    output_content = None
    for step_id in reversed(result.execution_order or []):
        step_result = result.step_outputs.get(step_id)
        if step_result and step_result.status == "success":
            output_content = step_result.result.get('digest', 
                            step_result.result.get('summary', 'No content'))
            break
    
    if output_content:
        # Create email snapshot
        snapshot = EmailSnapshot()
        
        # Prepare content
        content = {
            'markdown': output_content,
            'plaintext': output_content
        }
        
        # Prepare metadata
        metadata = {
            'workflow': result.workflow_name,
            'sender': 'workflow@example.com',
            'recipient': 'user@example.com',
            'subject': f'Workflow Complete: {result.workflow_name}',
            'content_type': 'markdown',
            'formatter': 'format_digest_markdown',
            'timestamp': result.completed_at.isoformat() if result.completed_at else None
        }
        
        # Save snapshot
        snapshot_paths = snapshot.save_snapshot(
            run_id=result.run_id,
            content=content,
            metadata=metadata
        )
        
        print(f"   ✓ Email snapshot saved to: {snapshot.base_dir / result.run_id}")
        
        # Verify snapshot files
        for file_type, file_path in snapshot_paths.items():
            if Path(file_path).exists():
                print(f"   ✓ Found: {file_type} -> {Path(file_path).name}")
            else:
                print(f"   ✗ Missing: {file_type}")
    else:
        print("   ✗ No output content found")
        return False
    
    # 4. List workflow runs
    print("\n4. Workflow storage contents")
    workflows_dir = Path("data/workflows")
    
    for workflow_dir in workflows_dir.iterdir():
        if workflow_dir.is_dir() and workflow_dir.name != "run_archive.json":
            print(f"\n   Workflow: {workflow_dir.name}")
            runs = list(workflow_dir.iterdir())
            print(f"   Runs: {len(runs)}")
            
            for run in runs[-3:]:  # Show last 3 runs
                if run.is_dir():
                    files = list(run.iterdir())
                    print(f"     - {run.name}: {len(files)} files")
    
    print("\n✅ All tests completed successfully!")
    return True


def main():
    """Run the test."""
    success = asyncio.run(test_workflow_with_snapshots())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()