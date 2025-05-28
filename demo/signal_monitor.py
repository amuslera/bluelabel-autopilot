#!/usr/bin/env python3
"""
Demo signal monitoring for CA-CC coordination.
Monitors /data/demo_signals/ for CA's recording cues.
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


class DemoSignalMonitor:
    def __init__(self):
        self.signals_dir = Path("/Users/arielmuslera/Development/Projects/bluelabel-autopilot/data/demo_signals")
        self.base_url = "http://localhost:8000"
        self.monitoring = True
        
        # Create signals directory if it doesn't exist
        self.signals_dir.mkdir(parents=True, exist_ok=True)
        
        # Clear any existing signals
        for file in self.signals_dir.glob("*.txt"):
            file.unlink()
    
    async def trigger_scenario(self, scenario_num: str):
        """Trigger the specified demo scenario."""
        console.print(f"\n[green]🎬 Triggering Scenario {scenario_num}...[/green]")
        
        try:
            if scenario_num == "1":
                await self.trigger_success_scenario()
            elif scenario_num == "2":
                await self.trigger_large_file_scenario()
            elif scenario_num == "3":
                await self.trigger_error_scenario()
            elif scenario_num == "4":
                await self.trigger_custom_scenario()
            else:
                raise ValueError(f"Unknown scenario: {scenario_num}")
                
            # Signal back to CA
            status_file = self.signals_dir / "scenario_triggered.txt"
            with open(status_file, "w") as f:
                f.write(f"Scenario {scenario_num} triggered successfully at {datetime.now().isoformat()}")
                
            console.print(f"[blue]✅ Scenario {scenario_num} triggered successfully![/blue]")
            
        except Exception as e:
            console.print(f"[red]❌ Error triggering scenario {scenario_num}: {e}[/red]")
            
            # Signal error back to CA
            status_file = self.signals_dir / "scenario_triggered.txt"
            with open(status_file, "w") as f:
                f.write(f"ERROR: Scenario {scenario_num} failed: {str(e)}")
    
    async def trigger_success_scenario(self):
        """Scenario 1: Success path (5-page PDF)."""
        workflow = {
            "workflow": """name: demo-success-email-pdf
version: 1.0.0
description: Success path - Email with 5-page PDF processing

steps:
  - name: receive_email
    agent: ingestion
    input:
      from: "test-success@example.com"
      subject: "Research Report - Q4 Analysis"
      attachment: "research_report_5pages.pdf"
      size_mb: 2.3
    output: email_data

  - name: extract_pdf_content
    agent: ingestion
    input:
      email: "{{email_data}}"
      pages: 5
      quality: "high"
    output: pdf_content

  - name: analyze_document
    agent: ingestion
    input:
      content: "{{pdf_content}}"
      analysis_type: "comprehensive"
    output: analysis

  - name: generate_executive_summary
    agent: digest
    input:
      analysis: "{{analysis}}"
      format: "executive"
      length: "concise"
    output: summary

  - name: send_response_email
    agent: digest
    input:
      summary: "{{summary}}"
      recipient: "test-success@example.com"
      template: "professional"
    output: response_sent""",
            "inputs": {
                "demo_scenario": "success",
                "demo_type": "email_pdf_flow"
            },
            "metadata": {
                "scenario": "Demo Recording - Success Path",
                "expected_duration": "4 seconds",
                "file_size": "5 pages"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/dag-runs", json=workflow) as resp:
                data = await resp.json()
                console.print(f"   Created workflow: [cyan]{data['id']}[/cyan]")
                return data['id']
    
    async def trigger_large_file_scenario(self):
        """Scenario 2: Large file (200-page PDF)."""
        workflow = {
            "workflow": """name: demo-large-file-processing
version: 1.0.0
description: Large file processing - 200-page PDF with streaming

steps:
  - name: receive_large_email
    agent: ingestion
    input:
      from: "test-large@example.com"
      subject: "Annual Report - Complete Document"
      attachment: "annual_report_200pages.pdf"
      size_mb: 45.7
    output: large_email_data

  - name: stream_pdf_processing
    agent: ingestion
    input:
      email: "{{large_email_data}}"
      pages: 200
      streaming: true
      chunk_size: 25
    output: streamed_content

  - name: parallel_analysis
    agent: ingestion
    input:
      content: "{{streamed_content}}"
      parallel_chunks: 8
    output: parallel_analysis

  - name: comprehensive_digest
    agent: digest
    input:
      analysis: "{{parallel_analysis}}"
      format: "detailed"
      sections: ["executive", "financial", "operational"]
    output: comprehensive_summary

  - name: generate_response
    agent: digest
    input:
      summary: "{{comprehensive_summary}}"
      recipient: "test-large@example.com"
      priority: "high"
    output: large_response""",
            "inputs": {
                "demo_scenario": "large_file",
                "demo_type": "streaming_processing"
            },
            "metadata": {
                "scenario": "Demo Recording - Large File",
                "expected_duration": "8 seconds",
                "file_size": "200 pages"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/dag-runs", json=workflow) as resp:
                data = await resp.json()
                console.print(f"   Created large file workflow: [cyan]{data['id']}[/cyan]")
                return data['id']
    
    async def trigger_error_scenario(self):
        """Scenario 3: Error recovery (corrupted file)."""
        workflow = {
            "workflow": """name: demo-error-recovery
version: 1.0.0
description: Error recovery - Corrupted file with retry mechanism

steps:
  - name: receive_problematic_email
    agent: ingestion
    input:
      from: "test-error@example.com"
      subject: "Corrupted Document"
      attachment: "corrupted_file.pdf"
      corruption_level: "moderate"
    output: problematic_email

  - name: attempt_pdf_extraction
    agent: ingestion
    input:
      email: "{{problematic_email}}"
      retry_on_failure: true
      max_retries: 3
      fallback_ocr: true
    output: extracted_content
    retry_count: 3

  - name: validate_content
    agent: ingestion
    input:
      content: "{{extracted_content}}"
      validation_strict: false
    output: validated_content

  - name: generate_recovery_summary
    agent: digest
    input:
      content: "{{validated_content}}"
      include_recovery_notes: true
    output: recovery_summary

  - name: send_status_update
    agent: digest
    input:
      summary: "{{recovery_summary}}"
      recipient: "test-error@example.com"
      include_technical_details: true
    output: status_sent""",
            "inputs": {
                "demo_scenario": "error_recovery",
                "demo_type": "failure_recovery",
                "simulate_errors": True
            },
            "metadata": {
                "scenario": "Demo Recording - Error Recovery",
                "expected_behavior": "Fails 2 times, succeeds on 3rd",
                "expected_duration": "12 seconds"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/dag-runs", json=workflow) as resp:
                data = await resp.json()
                console.print(f"   Created error recovery workflow: [cyan]{data['id']}[/cyan]")
                return data['id']
    
    async def trigger_custom_scenario(self):
        """Scenario 4: Custom demo (your choice)."""
        console.print("   [yellow]Creating parallel processing showcase...[/yellow]")
        
        workflow = {
            "workflow": """name: demo-parallel-showcase
version: 1.0.0
description: Parallel processing showcase - Multiple documents

steps:
  - name: batch_email_receive
    agent: ingestion
    input:
      batch_size: 4
      documents: ["doc1.pdf", "doc2.pdf", "doc3.pdf", "doc4.pdf"]
    output: document_batch

  - name: parallel_processing_1
    agent: ingestion
    input:
      document: "{{document_batch[0]}}"
    output: processed_1
    parallel_group: "batch_processing"

  - name: parallel_processing_2
    agent: ingestion
    input:
      document: "{{document_batch[1]}}"
    output: processed_2
    parallel_group: "batch_processing"

  - name: parallel_processing_3
    agent: ingestion
    input:
      document: "{{document_batch[2]}}"
    output: processed_3
    parallel_group: "batch_processing"

  - name: parallel_processing_4
    agent: ingestion
    input:
      document: "{{document_batch[3]}}"
    output: processed_4
    parallel_group: "batch_processing"

  - name: merge_results
    agent: digest
    input:
      results: ["{{processed_1}}", "{{processed_2}}", "{{processed_3}}", "{{processed_4}}"]
    output: merged_summary
    depends_on: ["parallel_processing_1", "parallel_processing_2", "parallel_processing_3", "parallel_processing_4"]""",
            "inputs": {
                "demo_scenario": "parallel_showcase",
                "demo_type": "parallel"
            },
            "metadata": {
                "scenario": "Demo Recording - Parallel Processing",
                "optimization": "4x speedup demonstration",
                "expected_duration": "6 seconds"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/api/dag-runs", json=workflow) as resp:
                data = await resp.json()
                console.print(f"   Created parallel showcase: [cyan]{data['id']}[/cyan]")
                return data['id']
    
    async def monitor(self):
        """Main monitoring loop."""
        console.print(Panel(
            "[bold blue]🎬 Demo Signal Monitor Active[/bold blue]\n"
            "[dim]Waiting for CA's recording signals...[/dim]\n\n"
            "[yellow]Monitoring:[/yellow] /data/demo_signals/ready_for_recording.txt\n"
            "[yellow]Will trigger:[/yellow] Scenarios 1-4 on demand\n"
            "[yellow]Status updates:[/yellow] scenario_triggered.txt",
            title="Backend Controller Ready",
            border_style="blue"
        ))
        
        signal_file = self.signals_dir / "ready_for_recording.txt"
        last_modified = 0
        
        while self.monitoring:
            try:
                if signal_file.exists():
                    current_modified = signal_file.stat().st_mtime
                    
                    if current_modified > last_modified:
                        # New signal received
                        last_modified = current_modified
                        
                        with open(signal_file, "r") as f:
                            scenario_num = f.read().strip()
                        
                        console.print(f"\n[bold green]📡 Signal received: Scenario {scenario_num}[/bold green]")
                        
                        await self.trigger_scenario(scenario_num)
                        
                        # Remove the signal file to prevent re-triggering
                        signal_file.unlink()
                
                await asyncio.sleep(0.5)  # Check every 500ms for responsive demo
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Demo monitoring stopped[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Monitor error: {e}[/red]")
                await asyncio.sleep(1)


async def main():
    monitor = DemoSignalMonitor()
    await monitor.monitor()


if __name__ == "__main__":
    asyncio.run(main())