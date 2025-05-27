#!/usr/bin/env python3
"""
Manual test script for Email to DAG bridge.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from services.email.email_dag_connector import EmailDAGConnector, MockEmailListener
from services.workflow.dag_run_store import DAGRunStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main():
    """Run email to DAG bridge test."""
    print("=== Email to DAG Bridge Test ===\n")
    
    # Create storage directories
    base_dir = Path("data/test_email_dag")
    input_dir = base_dir / "inputs"
    dag_store_dir = base_dir / "dag_runs"
    
    input_dir.mkdir(parents=True, exist_ok=True)
    dag_store_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample PDF
    sample_pdf = input_dir / "test_document.pdf"
    sample_pdf.write_bytes(b"%PDF-1.4\n%Test PDF content for email trigger\n")
    print(f"Created sample PDF: {sample_pdf}")
    
    # Initialize components
    dag_store = DAGRunStore(storage_path=str(dag_store_dir))
    connector = EmailDAGConnector(
        dag_store=dag_store,
        input_base_path=str(input_dir)
    )
    listener = MockEmailListener(connector)
    
    # Start listener
    await listener.start()
    print("\n✅ Email listener started")
    
    # Simulate email with PDF
    print("\n📧 Simulating email with PDF attachment...")
    email_data = {
        "from": "user@example.com",
        "subject": "Important Document for Processing",
        "timestamp": datetime.now().isoformat(),
        "attachments": [
            {
                "filename": "quarterly_report.pdf",
                "content_type": "application/pdf",
                "file_path": str(sample_pdf)
            }
        ]
    }
    
    run_id = await listener.simulate_email(email_data)
    
    if run_id:
        print(f"\n✅ DAG triggered successfully!")
        print(f"   Run ID: {run_id}")
        
        # Wait for DAG to execute
        print("\n⏳ Waiting for DAG execution...")
        await asyncio.sleep(2)
        
        # Check DAG status
        dag_run = dag_store.get(run_id)
        if dag_run:
            print(f"\n📊 DAG Status: {dag_run.status}")
            print(f"   Started: {dag_run.start_time}")
            print(f"   Steps:")
            for step_id, step in dag_run.steps.items():
                print(f"     - {step_id}: {step.status}")
                
            # Check saved files
            run_name = run_id.replace("contentmind_", "")
            run_dir = input_dir / run_name
            print(f"\n📁 Files saved in: {run_dir}")
            if run_dir.exists():
                for file in run_dir.iterdir():
                    print(f"   - {file.name}")
        else:
            print("\n❌ DAG run not found in store")
    else:
        print("\n❌ No DAG was triggered")
    
    # Test email without PDF
    print("\n\n📧 Simulating email without PDF...")
    email_no_pdf = {
        "from": "another@example.com",
        "subject": "Just a message",
        "timestamp": datetime.now().isoformat(),
        "attachments": [
            {
                "filename": "photo.jpg",
                "content_type": "image/jpeg"
            }
        ]
    }
    
    run_id2 = await listener.simulate_email(email_no_pdf)
    if not run_id2:
        print("✅ Correctly skipped - no PDF attachment")
    else:
        print("❌ Unexpected: DAG was triggered without PDF")
    
    # Stop listener
    await listener.stop()
    print("\n✅ Email listener stopped")
    
    print("\n=== Test Complete ===")


if __name__ == "__main__":
    asyncio.run(main())