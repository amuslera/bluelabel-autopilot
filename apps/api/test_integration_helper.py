#!/usr/bin/env python3
"""
Integration test helper for CA's frontend testing.
Provides easy ways to create test workflows and monitor their progress.
"""

import asyncio
import aiohttp
import json
from datetime import datetime


class IntegrationTestHelper:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    async def create_test_workflow(self):
        """Create a test workflow and return the run ID."""
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/test/create-sample-workflow") as resp:
                data = await resp.json()
                return data["id"]
    
    async def get_workflow_status(self, run_id):
        """Get the current status of a workflow."""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/api/dag-runs/{run_id}") as resp:
                return await resp.json()
    
    async def monitor_workflow(self, run_id, callback=None):
        """Monitor a workflow until completion."""
        while True:
            status = await self.get_workflow_status(run_id)
            
            if callback:
                callback(status)
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Status: {status['status']}")
                
            if status["status"] in ["success", "failed", "cancelled"]:
                return status
                
            await asyncio.sleep(1)
    
    async def create_complex_test_workflow(self):
        """Create a more complex test workflow with multiple steps."""
        workflow = {
            "workflow": """
name: complex-test-workflow
version: 1.0.0
description: Complex test workflow with multiple agents

steps:
  - name: ingest_data
    agent: ingestion
    input:
      text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    output: ingested_data

  - name: analyze_data
    agent: ingestion
    input:
      data: "{{ingested_data}}"
      mode: "detailed"
    output: analysis

  - name: generate_summary
    agent: digest
    input:
      content: "{{analysis}}"
      format: "executive"
    output: summary

  - name: final_report
    agent: digest
    input:
      summary: "{{summary}}"
      original: "{{ingested_data}}"
    output: final_report
""",
            "inputs": {"test_mode": True},
            "metadata": {"source": "complex_integration_test"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/dag-runs",
                json=workflow
            ) as resp:
                data = await resp.json()
                return data["id"]
    
    async def test_concurrent_workflows(self, count=3):
        """Create multiple workflows concurrently for load testing."""
        tasks = []
        for i in range(count):
            tasks.append(self.create_test_workflow())
        
        run_ids = await asyncio.gather(*tasks)
        print(f"Created {count} workflows: {run_ids}")
        
        # Monitor all workflows
        monitor_tasks = []
        for run_id in run_ids:
            monitor_tasks.append(self.monitor_workflow(run_id))
        
        results = await asyncio.gather(*monitor_tasks)
        return results


async def main():
    """Run integration tests."""
    helper = IntegrationTestHelper()
    
    print("Creating test workflow...")
    run_id = await helper.create_test_workflow()
    print(f"Created workflow: {run_id}")
    
    print("\nMonitoring workflow progress...")
    result = await helper.monitor_workflow(run_id)
    
    print(f"\nWorkflow completed with status: {result['status']}")
    if result.get('errors'):
        print(f"Errors: {result['errors']}")
    
    print("\n--- Testing concurrent workflows ---")
    results = await helper.test_concurrent_workflows(3)
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\nConcurrent test results: {success_count}/{len(results)} successful")


if __name__ == "__main__":
    asyncio.run(main())