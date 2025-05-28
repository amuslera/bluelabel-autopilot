#!/usr/bin/env python3
"""
Direct demo triggers for simplified coordination.
Ready to trigger scenarios on human command.
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from rich.console import Console

console = Console()


class DirectDemoTrigger:
    def __init__(self):
        self.base_url = "http://localhost:8000"
    
    async def scenario_1_success(self):
        """Scenario 1: Success path (5-page PDF)."""
        console.print("[green]🎬 TRIGGERING SCENARIO 1 - Success Path[/green]")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/test/create-sample-workflow") as resp:
                data = await resp.json()
                console.print(f"✅ Created: {data['id'][:8]}... | Status: {data['status']}")
                return data['id']
    
    async def scenario_2_large_file(self):
        """Scenario 2: Large file (200-page PDF)."""
        console.print("[yellow]🎬 TRIGGERING SCENARIO 2 - Large File[/yellow]")
        
        workflow = {
            "workflow": """name: large-file-demo
version: 1.0.0
steps:
  - name: receive_large_email
    agent: ingestion
    input:
      attachment: "200page_report.pdf"
      size_mb: 45
    output: large_data
  - name: process_large_pdf
    agent: ingestion
    input:
      data: "{{large_data}}"
      streaming: true
    output: processed
  - name: generate_summary
    agent: digest
    input:
      content: "{{processed}}"
    output: summary""",
            "inputs": {"demo_type": "large_file"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/dag-runs", json=workflow) as resp:
                data = await resp.json()
                console.print(f"✅ Created: {data['id'][:8]}... | Large file workflow")
                return data['id']
    
    async def scenario_3_error_recovery(self):
        """Scenario 3: Error recovery (corrupted file)."""
        console.print("[red]🎬 TRIGGERING SCENARIO 3 - Error Recovery[/red]")
        
        workflow = {
            "workflow": """name: error-recovery-demo
version: 1.0.0
steps:
  - name: receive_corrupted
    agent: ingestion
    input:
      attachment: "corrupted.pdf"
    output: corrupt_data
  - name: attempt_extraction
    agent: ingestion
    input:
      data: "{{corrupt_data}}"
      retry_on_failure: true
    output: extracted
    retry_count: 3
  - name: recovery_summary
    agent: digest
    input:
      content: "{{extracted}}"
    output: summary""",
            "inputs": {"demo_type": "failure_recovery"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/dag-runs", json=workflow) as resp:
                data = await resp.json()
                console.print(f"✅ Created: {data['id'][:8]}... | Will retry on failure")
                return data['id']
    
    async def scenario_4_parallel(self):
        """Scenario 4: Parallel processing showcase."""
        console.print("[blue]🎬 TRIGGERING SCENARIO 4 - Parallel Processing[/blue]")
        
        workflow = {
            "workflow": """name: parallel-demo
version: 1.0.0
steps:
  - name: split_work
    agent: ingestion
    input:
      chunks: 4
    output: work_chunks
  - name: process_chunk_1
    agent: ingestion
    input:
      chunk: "{{work_chunks[0]}}"
    output: result_1
    parallel_group: "processing"
  - name: process_chunk_2
    agent: ingestion
    input:
      chunk: "{{work_chunks[1]}}"
    output: result_2
    parallel_group: "processing"
  - name: process_chunk_3
    agent: ingestion
    input:
      chunk: "{{work_chunks[2]}}"
    output: result_3
    parallel_group: "processing"
  - name: process_chunk_4
    agent: ingestion
    input:
      chunk: "{{work_chunks[3]}}"
    output: result_4
    parallel_group: "processing"
  - name: merge_results
    agent: digest
    input:
      results: ["{{result_1}}", "{{result_2}}", "{{result_3}}", "{{result_4}}"]
    output: final_result""",
            "inputs": {"demo_type": "parallel"}
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/dag-runs", json=workflow) as resp:
                data = await resp.json()
                console.print(f"✅ Created: {data['id'][:8]}... | 4 parallel chunks")
                return data['id']
    
    async def get_server_status(self):
        """Check server status."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/") as resp:
                    data = await resp.json()
                    console.print(f"[green]✅ Server: {self.base_url} | Running[/green]")
                    return True
        except:
            console.print(f"[red]❌ Server: {self.base_url} | Not responding[/red]")
            return False


# Global trigger instance for easy access
trigger = DirectDemoTrigger()


async def main():
    console.print("[bold blue]🎬 Direct Demo Trigger Ready![/bold blue]")
    console.print("Scenarios available:")
    console.print("  1. Success path")
    console.print("  2. Large file")
    console.print("  3. Error recovery")
    console.print("  4. Parallel processing")
    console.print("\nServer status:")
    await trigger.get_server_status()
    console.print("\n[yellow]Ready for commands![/yellow]")


if __name__ == "__main__":
    asyncio.run(main())