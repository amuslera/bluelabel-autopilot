#!/usr/bin/env python3
"""
WhatsApp Webhook Simulator

This script simulates incoming WhatsApp webhook events for testing the WhatsApp adapter.
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.whatsapp_adapter import WhatsAppAdapter, process_webhook

# Sample payloads
SAMPLE_PAYLOADS = {
    "url": {
        "type": "url",
        "value": "https://example.com"
    },
    "pdf": {
        "type": "pdf",
        "value": "/path/to/document.pdf"
    },
    "invalid": {
        "type": "invalid",
        "value": "should_fail"
    }
}

async def simulate_webhook(payload: Dict[str, Any], output_file: Optional[str] = None) -> Dict[str, Any]:
    """Simulate a webhook event with the given payload.
    
    Args:
        payload: The webhook payload
        output_file: Optional file to save the response
        
    Returns:
        The webhook response
    """
    print(f"\n=== Simulating Webhook ===")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        # Process the webhook
        response = await process_webhook(payload)
        
        # Print the response
        print("\n=== Response ===")
        print(json.dumps(response, indent=2))
        
        # Save to file if requested
        if output_file:
            with open(output_file, 'w') as f:
                json.dump({
                    "payload": payload,
                    "response": response,
                    "timestamp": {"$date": {"$numberLong": str(int(asyncio.get_event_loop().time() * 1000))}}
                }, f, indent=2)
            print(f"\nResponse saved to: {output_file}")
            
        return response
        
    except Exception as e:
        error_msg = f"Error processing webhook: {str(e)}"
        print(f"\n=== Error ===\n{error_msg}", file=sys.stderr)
        return {"status": "error", "message": error_msg}

def get_payload_from_file(file_path: str) -> Dict[str, Any]:
    """Load a payload from a JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        The parsed JSON payload
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading payload from {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    """Main function to run the simulator."""
    parser = argparse.ArgumentParser(description="Simulate WhatsApp webhook events")
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--type", 
        choices=SAMPLE_PAYLOADS.keys(),
        help="Type of sample payload to use"
    )
    input_group.add_argument(
        "--file",
        type=str,
        help="Path to a JSON file containing the payload"
    )
    input_group.add_argument(
        "--custom",
        type=str,
        help="Custom payload as a JSON string"
    )
    
    # Output options
    parser.add_argument(
        "--output",
        type=str,
        help="Save the response to a file"
    )
    
    args = parser.parse_args()
    
    # Get the payload
    if args.type:
        payload = SAMPLE_PAYLOADS[args.type]
    elif args.file:
        payload = get_payload_from_file(args.file)
    else:  # args.custom
        try:
            payload = json.loads(args.custom)
        except json.JSONDecodeError as e:
            print(f"Error parsing custom JSON: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Run the simulation
    asyncio.run(simulate_webhook(payload, args.output))

if __name__ == "__main__":
    main()
