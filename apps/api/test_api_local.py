#!/usr/bin/env python3
"""
Quick local test script for the API.

Run this to verify the API is working before CA connects their frontend.
"""

import requests
import json
import asyncio
import websockets
from datetime import datetime


def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    response = requests.get("http://localhost:8000/health")
    if response.status_code == 200:
        print("✅ Health check passed:", response.json())
    else:
        print("❌ Health check failed:", response.status_code)


def test_list_runs():
    """Test listing DAG runs."""
    print("\nTesting list DAG runs...")
    response = requests.get("http://localhost:8000/api/dag-runs")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ List runs passed: {data['total']} runs found")
    else:
        print("❌ List runs failed:", response.status_code)


def test_create_run():
    """Test creating a DAG run."""
    print("\nTesting create DAG run...")
    
    # Check if we have a sample workflow
    from pathlib import Path
    workflow_path = Path("../../workflows/sample_ingestion_digest.yaml")
    if not workflow_path.exists():
        print("⚠️  Sample workflow not found, skipping create test")
        return None
    
    payload = {
        "workflow_path": str(workflow_path.absolute()),
        "persist": False,
        "engine_type": "sequential"
    }
    
    response = requests.post(
        "http://localhost:8000/api/dag-runs",
        json=payload
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Create run passed: ID={data['id']}")
        return data['id']
    else:
        print("❌ Create run failed:", response.status_code, response.text)
        return None


async def test_websocket():
    """Test WebSocket connection."""
    print("\nTesting WebSocket connection...")
    try:
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            # Receive connection message
            message = await websocket.recv()
            data = json.loads(message)
            
            if data.get("event") == "connection.established":
                print("✅ WebSocket connected:", data)
                
                # Test ping/pong
                await websocket.send("ping")
                pong = await websocket.recv()
                if pong == "pong":
                    print("✅ Ping/pong working")
            else:
                print("❌ Unexpected connection message:", data)
                
    except Exception as e:
        print("❌ WebSocket failed:", e)


def main():
    """Run all tests."""
    print("=" * 60)
    print("API Local Test Suite")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print("\nMake sure the API is running at http://localhost:8000")
    print("Run with: python apps/api/main.py")
    print("-" * 60)
    
    try:
        # Test basic endpoints
        test_health()
        test_list_runs()
        
        # Test creating a run
        run_id = test_create_run()
        
        # Test WebSocket
        asyncio.run(test_websocket())
        
        print("\n" + "=" * 60)
        print("Test Summary: All basic tests completed!")
        print("API is ready for frontend integration.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API at http://localhost:8000")
        print("Please start the API first with:")
        print("  cd apps/api")
        print("  python main.py")


if __name__ == "__main__":
    main()