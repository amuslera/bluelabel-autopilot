#!/usr/bin/env python3
"""
Test script for weekly digest generator
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add some test entries to the archive
def add_test_entries():
    """Add varied test entries to demonstrate digest capabilities."""
    archive_path = Path("data/workflows/run_archive.json")
    
    # Load existing archive
    if archive_path.exists():
        with open(archive_path) as f:
            archive = json.load(f)
    else:
        archive = []
    
    # Add some varied test entries
    test_entries = [
        {
            "workflow_id": "email_to_digest",
            "run_id": "test-001",
            "timestamp": (datetime.now() - timedelta(days=2)).isoformat(),
            "workflow_name": "Email to Digest",
            "version": "1.0.0",
            "status": "success",
            "duration_ms": 1250,
            "tags": ["email", "daily"],
            "summary": "Daily news digest with 5 articles processed",
            "source": {"type": "email", "from": "news@example.com"}
        },
        {
            "workflow_id": "url_scraper",
            "run_id": "test-002",
            "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
            "workflow_name": "URL Scraper",
            "version": "1.0.0",
            "status": "failed",
            "duration_ms": 500,
            "tags": ["web", "scraping"],
            "summary": "",
            "source": {"type": "url", "url": "https://example.com"}
        },
        {
            "workflow_id": "email_to_digest",
            "run_id": "test-003",
            "timestamp": datetime.now().isoformat(),
            "workflow_name": "Email to Digest",
            "version": "1.0.0",
            "status": "success",
            "duration_ms": 980,
            "tags": ["email", "weekly"],
            "summary": "Weekly summary: 15 items processed, 3 high priority",
            "source": {"type": "email", "from": "summary@example.com"}
        }
    ]
    
    # Add to archive if not already present
    existing_ids = {e.get('run_id') for e in archive}
    for entry in test_entries:
        if entry['run_id'] not in existing_ids:
            archive.append(entry)
    
    # Save updated archive
    with open(archive_path, 'w') as f:
        json.dump(archive, f, indent=2)
    
    print(f"✅ Added {len(test_entries)} test entries to archive")


def main():
    """Run comprehensive tests."""
    print("=== Weekly Digest Generator Test ===\n")
    
    # 1. Add test data
    print("1. Adding test data to archive...")
    add_test_entries()
    
    # 2. Test basic generation
    print("\n2. Testing basic digest generation...")
    result = subprocess.run([
        sys.executable, "runner/weekly_digest_generator.py",
        "--start", (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
        "--end", datetime.now().strftime("%Y-%m-%d")
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("   ✓ Basic generation successful")
        # Show output file
        for line in result.stdout.split('\n'):
            if 'Digest generated successfully:' in line:
                path = line.split(': ')[1]
                print(f"   ✓ Output: {path}")
    else:
        print(f"   ✗ Generation failed: {result.stderr}")
        return 1
    
    # 3. Test date range with no data
    print("\n3. Testing empty date range...")
    result = subprocess.run([
        sys.executable, "runner/weekly_digest_generator.py",
        "--start", "2020-01-01",
        "--end", "2020-01-07"
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and "No workflow runs found" in result.stdout:
        print("   ✓ Empty range handled correctly")
    else:
        print("   ✗ Empty range test failed")
    
    # 4. Test help
    print("\n4. Testing help output...")
    result = subprocess.run([
        sys.executable, "runner/weekly_digest_generator.py",
        "--help"
    ], capture_output=True, text=True)
    
    if result.returncode == 0 and "Generate weekly digest" in result.stdout:
        print("   ✓ Help works correctly")
    else:
        print("   ✗ Help test failed")
    
    # 5. List generated digests
    print("\n5. Generated digest files:")
    digest_dir = Path("data/digests")
    if digest_dir.exists():
        for digest_file in sorted(digest_dir.glob("*.md")):
            print(f"   - {digest_file.name}")
    
    print("\n✅ All tests completed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())