#!/usr/bin/env python3
"""
Demo workflow generator for showcasing different scenarios.
Creates realistic workflows with various patterns: success, failure, parallel, etc.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
import random
import aiohttp


class DemoWorkflowGenerator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    async def create_demo_workflows(self):
        """Create all demo workflows."""
        print("🚀 Creating Demo Workflows...")
        print("-" * 50)
        
        # Create each demo scenario
        workflows = [
            await self.create_success_workflow(),
            await self.create_failure_workflow(),
            await self.create_parallel_workflow(),
            await self.create_complex_workflow()
        ]
        
        print("\n✅ All demo workflows created!")
        print(f"Total workflows: {len(workflows)}")
        return workflows
    
    async def create_success_workflow(self):
        """Scenario 1: Complete success flow."""
        print("\n📋 Creating Success Workflow...")
        
        workflow = {
            "workflow": """
name: demo-success-flow
version: 1.0.0
description: Demonstrates successful PDF to summary pipeline

steps:
  - name: ingest_pdf
    agent: ingestion
    input:
      file: "quarterly_report.pdf"
      pages: 15
    output: pdf_content
    estimated_duration: 5

  - name: extract_text
    agent: ingestion
    input:
      content: "{{pdf_content}}"
      mode: "ocr_enhanced"
    output: extracted_text
    estimated_duration: 3

  - name: generate_summary
    agent: digest
    input:
      text: "{{extracted_text}}"
      style: "executive"
      max_length: 500
    output: summary
    estimated_duration: 4

  - name: format_output
    agent: digest
    input:
      summary: "{{summary}}"
      template: "email"
    output: final_output
    estimated_duration: 2
""",
            "inputs": {
                "demo_type": "success",
                "created_by": "demo_generator"
            },
            "metadata": {
                "scenario": "Complete Success Flow",
                "expected_duration": "14 seconds",
                "complexity": "medium"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/dag-runs",
                json=workflow
            ) as resp:
                data = await resp.json()
                print(f"✅ Success workflow created: {data['id']}")
                return data
    
    async def create_failure_workflow(self):
        """Scenario 2: Failure with retry."""
        print("\n⚠️  Creating Failure/Retry Workflow...")
        
        workflow = {
            "workflow": """
name: demo-failure-recovery
version: 1.0.0
description: Demonstrates error handling and retry logic

steps:
  - name: ingest_pdf
    agent: ingestion
    input:
      file: "corrupted_report.pdf"
      pages: 10
    output: pdf_content
    estimated_duration: 5

  - name: extract_text
    agent: ingestion
    input:
      content: "{{pdf_content}}"
      mode: "standard"
      simulate_failure: true
      failure_probability: 0.7
    output: extracted_text
    estimated_duration: 3
    retry_count: 3
    retry_delay: 2

  - name: generate_summary
    agent: digest
    input:
      text: "{{extracted_text}}"
      style: "brief"
    output: summary
    estimated_duration: 4
""",
            "inputs": {
                "demo_type": "failure_recovery",
                "simulate_errors": True
            },
            "metadata": {
                "scenario": "Failure Recovery Demo",
                "expected_behavior": "Fails 2-3 times then succeeds",
                "demonstrates": "Retry mechanism"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/dag-runs",
                json=workflow
            ) as resp:
                data = await resp.json()
                print(f"✅ Failure/retry workflow created: {data['id']}")
                return data
    
    async def create_parallel_workflow(self):
        """Scenario 3: Parallel processing."""
        print("\n⚡ Creating Parallel Processing Workflow...")
        
        workflow = {
            "workflow": """
name: demo-parallel-processing
version: 1.0.0
description: Demonstrates parallel step execution

steps:
  - name: split_document
    agent: ingestion
    input:
      file: "large_document.pdf"
      chunks: 4
    output: document_chunks
    estimated_duration: 2

  - name: process_chunk_1
    agent: ingestion
    input:
      chunk: "{{document_chunks[0]}}"
    output: processed_1
    estimated_duration: 5
    parallel_group: "chunk_processing"

  - name: process_chunk_2
    agent: ingestion
    input:
      chunk: "{{document_chunks[1]}}"
    output: processed_2
    estimated_duration: 4
    parallel_group: "chunk_processing"

  - name: process_chunk_3
    agent: ingestion
    input:
      chunk: "{{document_chunks[2]}}"
    output: processed_3
    estimated_duration: 6
    parallel_group: "chunk_processing"

  - name: process_chunk_4
    agent: ingestion
    input:
      chunk: "{{document_chunks[3]}}"
    output: processed_4
    estimated_duration: 3
    parallel_group: "chunk_processing"

  - name: merge_results
    agent: digest
    input:
      chunks: ["{{processed_1}}", "{{processed_2}}", "{{processed_3}}", "{{processed_4}}"]
    output: merged_result
    estimated_duration: 3
    depends_on: ["process_chunk_1", "process_chunk_2", "process_chunk_3", "process_chunk_4"]
""",
            "inputs": {
                "demo_type": "parallel",
                "optimization": "chunk_processing"
            },
            "metadata": {
                "scenario": "Parallel Processing Demo",
                "optimization": "4x speedup on chunk processing",
                "total_time": "11 seconds (vs 23 sequential)"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/dag-runs",
                json=workflow
            ) as resp:
                data = await resp.json()
                print(f"✅ Parallel workflow created: {data['id']}")
                return data
    
    async def create_complex_workflow(self):
        """Scenario 4: Complex multi-stage pipeline."""
        print("\n🔄 Creating Complex Pipeline Workflow...")
        
        workflow = {
            "workflow": """
name: demo-complex-pipeline
version: 1.0.0
description: Complex multi-stage document processing pipeline

steps:
  - name: validate_input
    agent: ingestion
    input:
      source: "email_attachment"
      validation_rules: ["pdf", "max_size_50mb"]
    output: validated_input
    estimated_duration: 1

  - name: extract_metadata
    agent: ingestion
    input:
      file: "{{validated_input}}"
    output: metadata
    estimated_duration: 2
    parallel_group: "preprocessing"

  - name: detect_language
    agent: ingestion
    input:
      file: "{{validated_input}}"
    output: language
    estimated_duration: 1
    parallel_group: "preprocessing"

  - name: extract_images
    agent: ingestion
    input:
      file: "{{validated_input}}"
    output: images
    estimated_duration: 3
    parallel_group: "preprocessing"

  - name: process_text
    agent: ingestion
    input:
      file: "{{validated_input}}"
      language: "{{language}}"
    output: text_content
    estimated_duration: 5
    depends_on: ["detect_language"]

  - name: analyze_images
    agent: digest
    input:
      images: "{{images}}"
    output: image_analysis
    estimated_duration: 4
    depends_on: ["extract_images"]

  - name: generate_summary
    agent: digest
    input:
      text: "{{text_content}}"
      metadata: "{{metadata}}"
      images: "{{image_analysis}}"
    output: comprehensive_summary
    estimated_duration: 6
    depends_on: ["process_text", "analyze_images", "extract_metadata"]

  - name: quality_check
    agent: digest
    input:
      summary: "{{comprehensive_summary}}"
      original: "{{validated_input}}"
    output: quality_report
    estimated_duration: 2

  - name: deliver_results
    agent: digest
    input:
      summary: "{{comprehensive_summary}}"
      quality: "{{quality_report}}"
      format: "email"
    output: final_delivery
    estimated_duration: 1
""",
            "inputs": {
                "demo_type": "complex",
                "stages": 5,
                "parallel_steps": 3
            },
            "metadata": {
                "scenario": "Complex Pipeline Demo",
                "features": ["validation", "parallel processing", "quality checks"],
                "total_steps": 9,
                "optimization": "3 parallel preprocessing steps"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/dag-runs",
                json=workflow
            ) as resp:
                data = await resp.json()
                print(f"✅ Complex workflow created: {data['id']}")
                return data
    
    async def monitor_workflows(self, workflow_ids: List[str]):
        """Monitor all workflows until completion."""
        print("\n📊 Monitoring Workflows...")
        print("-" * 50)
        
        completed = set()
        while len(completed) < len(workflow_ids):
            for wf_id in workflow_ids:
                if wf_id in completed:
                    continue
                    
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}/api/dag-runs/{wf_id}") as resp:
                        data = await resp.json()
                        
                        if data['status'] in ['success', 'failed', 'cancelled']:
                            completed.add(wf_id)
                            print(f"✅ Workflow {wf_id[:8]}... completed with status: {data['status']}")
                        else:
                            print(f"⏳ Workflow {wf_id[:8]}... status: {data['status']}")
            
            if len(completed) < len(workflow_ids):
                await asyncio.sleep(2)
        
        print("\n🎉 All workflows completed!")
    
    async def get_performance_metrics(self):
        """Calculate performance metrics."""
        print("\n📈 Performance Metrics")
        print("-" * 50)
        
        async with aiohttp.ClientSession() as session:
            # Get all runs
            async with session.get(f"{self.base_url}/api/dag-runs") as resp:
                data = await resp.json()
                
                completed_runs = [r for r in data['items'] if r['status'] == 'success']
                if completed_runs:
                    durations = [r['duration_ms'] for r in completed_runs if r.get('duration_ms')]
                    if durations:
                        avg_duration = sum(durations) / len(durations)
                        print(f"Average completion time: {avg_duration:.0f}ms")
                        print(f"Fastest workflow: {min(durations)}ms")
                        print(f"Slowest workflow: {max(durations)}ms")
                
                print(f"Total workflows: {len(data['items'])}")
                print(f"Success rate: {len(completed_runs) / len(data['items']) * 100:.1f}%")
            
            # Get metrics endpoint
            async with session.get(f"{self.base_url}/metrics") as resp:
                if resp.status == 200:
                    metrics = await resp.json()
                    print(f"\nAPI Metrics:")
                    print(f"Active runs: {metrics['dag_metrics']['active_runs']}")
                    print(f"WebSocket clients: {metrics['websocket_metrics']['connected_clients']}")


async def main():
    """Run the demo workflow generator."""
    generator = DemoWorkflowGenerator()
    
    print("🎯 Bluelabel Autopilot Demo Workflow Generator")
    print("=" * 50)
    
    # Create demo workflows
    workflows = await generator.create_demo_workflows()
    workflow_ids = [w['id'] for w in workflows]
    
    # Monitor until completion
    await generator.monitor_workflows(workflow_ids)
    
    # Show performance metrics
    await generator.get_performance_metrics()
    
    print("\n✅ Demo preparation complete!")
    print("Workflows are ready for demonstration.")


if __name__ == "__main__":
    asyncio.run(main())