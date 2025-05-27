"""Test script for the PDF processing workflow.

This script tests the end-to-end workflow of processing a PDF file
through ingestion, summarization, and digest generation.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

from agents.ingestion_agent import IngestionAgent
from agents.contentmind_agent import ContentMindAgent
from agents.digest_agent import DigestAgent
from interfaces.agent_models import AgentInput

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test data paths
TEST_DATA_DIR = Path("tests/data")
TEST_PDF_PATH = TEST_DATA_DIR / "sample.pdf"
WORKFLOW_OUTPUT_PATH = TEST_DATA_DIR / "workflow_output.json"


async def run_workflow() -> Dict[str, Any]:
    """Run the PDF processing workflow.
    
    Returns:
        Dictionary containing workflow results
    """
    logger.info("Starting PDF processing workflow test")
    
    # Initialize agents
    ingestion_agent = IngestionAgent()
    contentmind_agent = ContentMindAgent()
    digest_agent = DigestAgent()
    
    await ingestion_agent.initialize()
    await contentmind_agent.initialize()
    await digest_agent.initialize()
    
    try:
        # Step 1: Ingest PDF
        logger.info("Step 1: Ingesting PDF")
        with open(TEST_PDF_PATH, "rb") as f:
            pdf_data = f.read()
            
        ingest_input = AgentInput(
            task_id="test_ingest_001",
            task_type="pdf",
            content={
                "action": "process_pdf",
                "parameters": {
                    "pdf_data": pdf_data,
                    "filename": TEST_PDF_PATH.name,
                    "extract_metadata": True
                }
            }
        )
        
        ingest_output = await ingestion_agent.process(ingest_input)
        if ingest_output.status != "success":
            raise Exception(f"Ingestion failed: {ingest_output.error}")
            
        content_id = ingest_output.result["content_id"]
        logger.info(f"PDF ingested successfully. Content ID: {content_id}")
        
        # Step 2: Generate Summary
        logger.info("Step 2: Generating Summary")
        summary_input = AgentInput(
            task_id="test_summary_001",
            task_type="summary",
            content={
                "action": "generate_summary",
                "parameters": {
                    "content_id": content_id,
                    "max_length": 1000,
                    "format": "markdown"
                }
            }
        )
        
        summary_output = await contentmind_agent.process(summary_input)
        if summary_output.status != "success":
            raise Exception(f"Summary generation failed: {summary_output.error}")
            
        summary_id = summary_output.result["content_id"]
        logger.info(f"Summary generated successfully. Summary ID: {summary_id}")
        
        # Step 3: Create Digest
        logger.info("Step 3: Creating Digest")
        digest_input = AgentInput(
            task_id="test_digest_001",
            task_type="digest",
            content={
                "action": "generate_digest",
                "parameters": {
                    "content_id": summary_id,
                    "format": "markdown"
                }
            }
        )
        
        digest_output = await digest_agent.process(digest_input)
        if digest_output.status != "success":
            raise Exception(f"Digest generation failed: {digest_output.error}")
            
        digest_id = digest_output.result["content_id"]
        logger.info(f"Digest created successfully. Digest ID: {digest_id}")
        
        # Compile results
        results = {
            "content_id": content_id,
            "summary_id": summary_id,
            "digest_id": digest_id,
            "final_digest": digest_output.result["digest"],
            "status": "success",
            "steps": {
                "ingest": {
                    "status": ingest_output.status,
                    "duration_ms": ingest_output.duration_ms
                },
                "summary": {
                    "status": summary_output.status,
                    "duration_ms": summary_output.duration_ms
                },
                "digest": {
                    "status": digest_output.status,
                    "duration_ms": digest_output.duration_ms
                }
            }
        }
        
        # Save results
        WORKFLOW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(WORKFLOW_OUTPUT_PATH, "w") as f:
            json.dump(results, f, indent=2)
            
        logger.info(f"Workflow completed successfully. Results saved to {WORKFLOW_OUTPUT_PATH}")
        return results
        
    except Exception as e:
        logger.error(f"Workflow failed: {e}")
        raise
        
    finally:
        # Cleanup
        await ingestion_agent.shutdown()
        await contentmind_agent.shutdown()
        await digest_agent.shutdown()


if __name__ == "__main__":
    # Create test data directory if it doesn't exist
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run workflow
    try:
        results = asyncio.run(run_workflow())
        print("\nWorkflow Results:")
        print(f"Content ID: {results['content_id']}")
        print(f"Summary ID: {results['summary_id']}")
        print(f"Digest ID: {results['digest_id']}")
        print("\nFinal Digest:")
        print(results['final_digest'])
        
    except Exception as e:
        print(f"\nWorkflow failed: {e}")
        exit(1) 