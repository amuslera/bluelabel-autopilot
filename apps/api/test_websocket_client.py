#!/usr/bin/env python3
"""
WebSocket test client to verify real-time updates.
"""

import asyncio
import websockets
import json
from datetime import datetime


async def test_websocket():
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Connected to WebSocket")
        
        # Listen for messages
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Event: {data['event']}")
                print(f"  Data: {json.dumps(data['data'], indent=2)}")
                print("-" * 50)
                
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket connection closed")


if __name__ == "__main__":
    print("Starting WebSocket test client...")
    print("This will show all real-time events from the server")
    print("-" * 50)
    
    asyncio.run(test_websocket())