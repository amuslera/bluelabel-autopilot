#!/usr/bin/env python3
"""
Ingestion to Digest Workflow Integration Demo

This script demonstrates the pipeline where content processed by IngestionAgent
is passed to DigestAgent to generate a summary. This is the first integration
step toward full orchestration.

Usage:
    python runner/ingestion_to_digest_demo.py --source pdf
    python runner/ingestion_to_digest_demo.py --source url
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.agent_models import AgentInput, AgentOutput
from agents.ingestion_agent import IngestionAgent
from agents.digest_agent import DigestAgent


class IngestionToDigestWorkflow:
    """Orchestrates the flow from ingestion to digest generation."""
    
    def __init__(self, storage_path: Path = None):
        """Initialize the workflow with agent instances.
        
        Args:
            storage_path: Path to store intermediate results
        """
        self.storage_path = storage_path or Path("./data/knowledge")
        self.ingestion_agent = IngestionAgent(storage_path=self.storage_path)
        self.digest_agent = DigestAgent(storage_path=self.storage_path)
        
    async def initialize(self):
        """Initialize both agents."""
        await self.ingestion_agent.initialize()
        await self.digest_agent.initialize()
        
    def transform_ingestion_to_digest(self, ingestion_output: AgentOutput) -> Dict[str, Any]:
        """Transform ingestion output into digest input format.
        
        This is the bridge logic that converts the output from IngestionAgent
        into a format suitable for DigestAgent input.
        
        Args:
            ingestion_output: Output from IngestionAgent
            
        Returns:
            Dictionary formatted for DigestAgent input
        """
        if ingestion_output.status != "success":
            raise ValueError(f"Ingestion failed: {ingestion_output.error}")
            
        # Extract metadata from ingestion result
        result = ingestion_output.result
        metadata = result.get("metadata", {})
        
        # Create a summary entry for the digest agent
        summary_entry = {
            "id": result.get("content_id"),
            "type": result.get("content_type"),
            "title": metadata.get("title", "Untitled"),
            "source": metadata.get("source", "Unknown"),
            "created_at": datetime.utcnow().isoformat(),
            "content": "Content processed and stored",  # Placeholder
            "summary": f"Processed {result.get('content_type')} with {result.get('content_length', 0)} characters",
            "tags": [result.get("content_type", "unknown")],
            "metadata": metadata
        }
        
        # The digest agent will read from storage, but we can pass parameters
        return {
            "action": "generate_digest",
            "parameters": {
                "limit": 10,
                "format": "markdown"
            }
        }
        
    async def run_workflow(self, source_type: str) -> AgentOutput:
        """Run the complete ingestion to digest workflow.
        
        Args:
            source_type: Either "pdf" or "url"
            
        Returns:
            Final AgentOutput from DigestAgent
        """
        # Load sample input based on source type
        if source_type == "pdf":
            input_file = Path("tests/sample_pdf_input.json")
        else:
            input_file = Path("tests/sample_url_input.json")
            
        if not input_file.exists():
            raise FileNotFoundError(f"Sample input file not found: {input_file}")
            
        with open(input_file, 'r') as f:
            input_data = json.load(f)
            
        # Step 1: Run IngestionAgent
        print(f"\n=== Step 1: Running IngestionAgent on {source_type} ===")
        ingestion_input = AgentInput(**input_data)
        
        # For PDF, we need to read the actual file
        if source_type == "pdf" and "file_path" in ingestion_input.content:
            pdf_path = Path(ingestion_input.content["file_path"])
            if pdf_path.exists():
                with open(pdf_path, 'rb') as pdf_file:
                    ingestion_input.content["pdf_data"] = pdf_file.read()
                    ingestion_input.content["filename"] = pdf_path.name
        
        ingestion_output = await self.ingestion_agent.process(ingestion_input)
        
        print(f"Ingestion Status: {ingestion_output.status}")
        if ingestion_output.status == "success":
            print(f"Content ID: {ingestion_output.result.get('content_id')}")
            print(f"Content Length: {ingestion_output.result.get('content_length')} characters")
            print(f"Duration: {ingestion_output.duration_ms}ms")
        else:
            print(f"Error: {ingestion_output.error}")
            return ingestion_output
            
        # Step 2: Transform output for DigestAgent
        print("\n=== Step 2: Transforming data for DigestAgent ===")
        try:
            digest_params = self.transform_ingestion_to_digest(ingestion_output)
            print("Transformation successful")
        except Exception as e:
            print(f"Transformation error: {e}")
            raise
            
        # Step 3: Run DigestAgent
        print("\n=== Step 3: Running DigestAgent ===")
        digest_input = AgentInput(
            task_id=f"digest-{ingestion_input.task_id}",
            source="workflow",
            content=digest_params
        )
        
        digest_output = await self.digest_agent.process(digest_input)
        
        print(f"Digest Status: {digest_output.status}")
        if digest_output.status == "success":
            print(f"Summary Count: {digest_output.result.get('summary_count')}")
            print(f"Format: {digest_output.result.get('format')}")
            print(f"Duration: {digest_output.duration_ms}ms")
            
            # Print the actual digest
            print("\n=== Generated Digest ===")
            print(digest_output.result.get('digest', 'No digest generated'))
        else:
            print(f"Error: {digest_output.error}")
            
        return digest_output


async def main():
    """Main entry point for the demo."""
    parser = argparse.ArgumentParser(
        description='Demonstrate ingestion to digest workflow integration'
    )
    parser.add_argument(
        '--source',
        choices=['pdf', 'url'],
        default='pdf',
        help='Source type to process (default: pdf)'
    )
    parser.add_argument(
        '--storage-path',
        type=Path,
        default='./data/knowledge',
        help='Path to storage directory'
    )
    
    args = parser.parse_args()
    
    # Create workflow instance
    workflow = IngestionToDigestWorkflow(storage_path=args.storage_path)
    
    try:
        # Initialize agents
        await workflow.initialize()
        
        # Run the workflow
        result = await workflow.run_workflow(args.source)
        
        # Exit with appropriate code
        sys.exit(0 if result.status == "success" else 1)
        
    except Exception as e:
        print(f"\nWorkflow error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())