#!/usr/bin/env python3
"""
Stress test the agent execution pipeline with large PDF files.
"""

import asyncio
import json
import time
import psutil
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.ingestion_agent import IngestionAgent
from agents.digest_agent import DigestAgent
from interfaces.agent_models import AgentInput

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

async def test_ingestion_agent(pdf_path):
    """Test IngestionAgent with a large PDF."""
    print(f"\n{'='*60}")
    print(f"Testing IngestionAgent with: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path) / (1024*1024):.2f}MB")
    print(f"{'='*60}\n")
    
    # Prepare input - load PDF data
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    agent_input = AgentInput(
        task_id="stress-test-ingestion",
        task_type="pdf",
        source="stress_test",
        content={
            "file_path": str(pdf_path),
            "pdf_data": pdf_data,
            "filename": os.path.basename(pdf_path)
        },
        metadata={"test": "stress_test"}
    )
    
    # Create agent
    agent = IngestionAgent(
        storage_path=Path("./data/knowledge"),
        temp_path=Path("./data/temp")
    )
    
    # Measure performance
    start_time = time.time()
    start_memory = get_memory_usage()
    
    print(f"Starting ingestion...")
    print(f"Initial memory: {start_memory:.2f}MB")
    
    try:
        result = await agent.process(agent_input)
        
        end_time = time.time()
        end_memory = get_memory_usage()
        
        duration = end_time - start_time
        memory_increase = end_memory - start_memory
        
        print(f"\nIngestion completed!")
        print(f"Status: {result.status}")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Memory increase: {memory_increase:.2f}MB")
        print(f"Final memory: {end_memory:.2f}MB")
        
        if result.status == "success":
            print(f"Content length: {result.result.get('content_length', 'N/A')} characters")
            print(f"Content ID: {result.result.get('content_id', 'N/A')}")
        else:
            print(f"Error: {result.error}")
            
        return result, duration, memory_increase
        
    except Exception as e:
        print(f"ERROR during ingestion: {e}")
        return None, None, None

async def test_full_workflow(pdf_path):
    """Test the full workflow: Ingestion -> Digest."""
    print(f"\n{'='*60}")
    print(f"Testing Full Workflow with: {pdf_path}")
    print(f"File size: {os.path.getsize(pdf_path) / (1024*1024):.2f}MB")
    print(f"{'='*60}\n")
    
    # Overall timing
    workflow_start = time.time()
    workflow_start_memory = get_memory_usage()
    
    # Step 1: Ingestion
    print("Step 1: Ingestion")
    print("-" * 40)
    
    # Load PDF data
    with open(pdf_path, 'rb') as f:
        pdf_data = f.read()
    
    ingestion_input = AgentInput(
        task_id="stress-test-workflow-ingestion",
        task_type="pdf",
        source="stress_test",
        content={
            "file_path": str(pdf_path),
            "pdf_data": pdf_data,
            "filename": os.path.basename(pdf_path)
        },
        metadata={"test": "stress_test_workflow"}
    )
    
    ingestion_agent = IngestionAgent(
        storage_path=Path("./data/knowledge"),
        temp_path=Path("./data/temp")
    )
    
    ingestion_start = time.time()
    ingestion_result = await ingestion_agent.process(ingestion_input)
    ingestion_duration = time.time() - ingestion_start
    
    if ingestion_result.status != "success":
        print(f"Ingestion failed: {ingestion_result.error}")
        return
    
    print(f"Ingestion completed in {ingestion_duration:.2f}s")
    print(f"Extracted {ingestion_result.result['content_length']} characters")
    
    # Step 2: Digest
    print("\nStep 2: Digest Generation")
    print("-" * 40)
    
    digest_input = AgentInput(
        task_id="stress-test-workflow-digest",
        source="stress_test",
        content={
            "content_id": ingestion_result.result['content_id'],
            "format": "markdown",
            "limit": 10
        },
        metadata={"test": "stress_test_workflow"}
    )
    
    digest_agent = DigestAgent(storage_path=Path("./data/knowledge"))
    
    digest_start = time.time()
    digest_result = await digest_agent.process(digest_input)
    digest_duration = time.time() - digest_start
    
    if digest_result.status != "success":
        print(f"Digest generation failed: {digest_result.error}")
        return
    
    print(f"Digest generated in {digest_duration:.2f}s")
    print(f"Digest length: {len(digest_result.result.get('digest', ''))} characters")
    
    # Overall stats
    workflow_duration = time.time() - workflow_start
    workflow_memory_increase = get_memory_usage() - workflow_start_memory
    
    print(f"\n{'='*60}")
    print("Workflow Summary")
    print(f"{'='*60}")
    print(f"Total duration: {workflow_duration:.2f}s")
    print(f"  - Ingestion: {ingestion_duration:.2f}s ({ingestion_duration/workflow_duration*100:.1f}%)")
    print(f"  - Digest: {digest_duration:.2f}s ({digest_duration/workflow_duration*100:.1f}%)")
    print(f"Memory increase: {workflow_memory_increase:.2f}MB")
    print(f"Final memory usage: {get_memory_usage():.2f}MB")
    
    return workflow_duration, workflow_memory_increase

async def main():
    """Run stress tests on agent pipeline."""
    print("Agent Execution Pipeline Stress Test")
    print("=" * 60)
    
    # Test files
    test_files = [
        "tests/sample.pdf",  # Small baseline
        "tests/stress_test_100pages.pdf",  # Medium
        "tests/stress_test_200pages.pdf",  # Medium+
        "tests/stress_test_5mb.pdf"  # Large
    ]
    
    # Filter to existing files
    test_files = [f for f in test_files if os.path.exists(f)]
    
    print(f"Found {len(test_files)} test files:")
    for f in test_files:
        size_mb = os.path.getsize(f) / (1024*1024)
        print(f"  - {f}: {size_mb:.2f}MB")
    
    # Test each file
    results = []
    
    for pdf_file in test_files:
        # Test ingestion only
        result, duration, memory = await test_ingestion_agent(pdf_file)
        
        if result and result.status == "success":
            results.append({
                "file": pdf_file,
                "size_mb": os.path.getsize(pdf_file) / (1024*1024),
                "ingestion_time": duration,
                "memory_increase": memory,
                "content_length": result.result.get('content_length', 0)
            })
        
        # Test full workflow for smaller files
        if os.path.getsize(pdf_file) < 5 * 1024 * 1024:  # Less than 5MB
            await test_full_workflow(pdf_file)
        
        # Give system time to recover
        await asyncio.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print("Stress Test Summary")
    print(f"{'='*60}")
    
    for result in results:
        print(f"\nFile: {result['file']}")
        print(f"  Size: {result['size_mb']:.2f}MB")
        print(f"  Ingestion time: {result['ingestion_time']:.2f}s")
        print(f"  Speed: {result['size_mb']/result['ingestion_time']:.2f}MB/s")
        print(f"  Memory increase: {result['memory_increase']:.2f}MB")
        print(f"  Extracted text: {result['content_length']:,} characters")

if __name__ == "__main__":
    asyncio.run(main())