from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
import json
from typing import Set
from services.workflow.dag_run_store import DAGRunStore

router = APIRouter()
store = DAGRunStore()

# Active WebSocket connections
active_connections: Set[WebSocket] = set()

@router.websocket("/ws/dag-updates")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)
    
    try:
        # Send initial connection confirmation
        await websocket.send_json({
            "event": "connected",
            "message": "WebSocket connected"
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Listen for client messages
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle subscription requests
                if message.get("action") == "subscribe" and message.get("run_id"):
                    run_id = message["run_id"]
                    dag_run = store.get(run_id)
                    
                    if dag_run:
                        # Send current state
                        await websocket.send_json({
                            "event": "dag_run_status",
                            "run_id": run_id,
                            "data": dag_run.to_dict()
                        })
                    else:
                        await websocket.send_json({
                            "event": "error",
                            "message": f"DAG run {run_id} not found"
                        })
                        
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_json({"event": "ping"})
                
    except WebSocketDisconnect:
        active_connections.discard(websocket)
    except Exception as e:
        active_connections.discard(websocket)
        print(f"WebSocket error: {e}")

async def broadcast_dag_update(run_id: str, event_type: str, data: dict):
    """Broadcast DAG run updates to all connected clients"""
    if not active_connections:
        return
        
    message = {
        "event": event_type,
        "run_id": run_id,
        "data": data,
        "timestamp": asyncio.get_event_loop().time()
    }
    
    # Send to all active connections
    disconnected = set()
    for websocket in active_connections:
        try:
            await websocket.send_json(message)
        except:
            disconnected.add(websocket)
    
    # Remove disconnected clients
    active_connections -= disconnected 