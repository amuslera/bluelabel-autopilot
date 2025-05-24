#!/usr/bin/env python3
"""
Test Input Generator for Bluelabel Agent OS

This script generates valid AgentInput JSON files for testing the IngestionAgent
and DigestAgent. It supports different input types (URL, PDF) and provides
sensible defaults for all required fields.

Usage:
    python generate_test_input.py --agent ingestion --type url --output tests/sample_url_input.json
    python generate_test_input.py --agent ingestion --type pdf --output tests/sample_pdf_input.json
    python generate_test_input.py --agent digest --output tests/sample_digest_input.json
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, Any
import uuid

def generate_ingestion_url_input() -> Dict[str, Any]:
    """Generate a sample URL input for the IngestionAgent."""
    return {
        "task_id": str(uuid.uuid4()),
        "task_type": "url",
        "source": "cli",
        "content": {
            "url": "https://example.com/sample-article",
            "title": "Sample Article",
            "author": "John Doe",
            "published_date": datetime.utcnow().isoformat()
        },
        "metadata": {
            "content_type": "article",
            "language": "en",
            "word_count": 1500
        },
        "context": {
            "priority": "normal",
            "processing_mode": "standard"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_ingestion_pdf_input() -> Dict[str, Any]:
    """Generate a sample PDF input for the IngestionAgent."""
    return {
        "task_id": str(uuid.uuid4()),
        "task_type": "pdf",
        "source": "cli",
        "content": {
            "file_path": "data/sample.pdf",
            "title": "Sample Document",
            "author": "Jane Smith",
            "page_count": 10
        },
        "metadata": {
            "content_type": "document",
            "language": "en",
            "file_size": 1024000
        },
        "context": {
            "priority": "normal",
            "processing_mode": "standard"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

def generate_digest_input() -> Dict[str, Any]:
    """Generate a sample input for the DigestAgent."""
    return {
        "task_id": str(uuid.uuid4()),
        "source": "cli",
        "content": {
            "content_id": str(uuid.uuid4()),
            "content_type": "article",
            "text": "This is a sample text to be digested...",
            "metadata": {
                "title": "Sample Content",
                "author": "AI Assistant",
                "created_at": datetime.utcnow().isoformat()
            }
        },
        "metadata": {
            "digest_type": "summary",
            "max_length": 200
        },
        "context": {
            "priority": "normal",
            "processing_mode": "standard"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

def main():
    parser = argparse.ArgumentParser(description="Generate test input files for Bluelabel Agent OS")
    parser.add_argument("--agent", choices=["ingestion", "digest"], required=True,
                      help="Type of agent to generate input for")
    parser.add_argument("--type", choices=["url", "pdf"], required=False,
                      help="Type of input (required for ingestion agent)")
    parser.add_argument("--output", required=False,
                      help="Output file path (default: tests/sample_{agent}_{type}_input.json)")

    args = parser.parse_args()

    # Validate arguments
    if args.agent == "ingestion" and not args.type:
        parser.error("--type is required for ingestion agent")

    # Generate input data
    if args.agent == "ingestion":
        if args.type == "url":
            data = generate_ingestion_url_input()
        else:  # pdf
            data = generate_ingestion_pdf_input()
    else:  # digest
        data = generate_digest_input()

    # Determine output path
    if not args.output:
        output_dir = "tests"
        os.makedirs(output_dir, exist_ok=True)
        if args.agent == "ingestion":
            args.output = f"{output_dir}/sample_{args.agent}_{args.type}_input.json"
        else:
            args.output = f"{output_dir}/sample_{args.agent}_input.json"

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Write to file
    with open(args.output, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Generated test input file: {args.output}")

if __name__ == "__main__":
    main() 