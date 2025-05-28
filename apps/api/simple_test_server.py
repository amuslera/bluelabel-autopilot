#!/usr/bin/env python3
"""
Simple test server for CA's integration testing.
Provides basic DAG run endpoints and WebSocket support.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import json
import uuid
import random

app = FastAPI(title="Test API Server")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active connections
websocket_connections: List[WebSocket] = []

# Store test runs
test_runs: Dict[str, dict] = {}


class CreateTestRunRequest(BaseModel):
    workflow: str
    inputs: Optional[Dict] = {}
    metadata: Optional[Dict] = {}
    

@app.get("/")
async def root():
    return {"message": "Test API Server Running", "time": datetime.now().isoformat()}


@app.post("/api/test/create-sample-workflow")
async def create_test_workflow():
    """Create a test workflow for integration testing."""
    run_id = str(uuid.uuid4())
    
    run_data = {
        "id": run_id,
        "workflow_name": "test-integration-workflow",
        "workflow_version": "1.0.0",
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "duration_ms": None,
        "step_count": 2,
        "steps": [
            {"name": "analyze_text", "status": "pending"},
            {"name": "generate_summary", "status": "pending"}
        ],
        "errors": []
    }
    
    test_runs[run_id] = run_data
    
    # Send WebSocket notification
    await broadcast_message({
        "event": "dag.run.created",
        "data": {
            "run_id": run_id,
            "workflow_name": "test-integration-workflow",
            "status": "running",
            "message": "Test workflow created"
        }
    })
    
    # Simulate workflow execution
    asyncio.create_task(simulate_workflow_execution(run_id))
    
    return run_data


@app.post("/api/dag-runs")
async def create_dag_run(request: CreateTestRunRequest):
    """Create a DAG run from workflow definition."""
    run_id = str(uuid.uuid4())
    
    # Parse workflow to extract metadata
    workflow_name = "demo-workflow"
    step_count = 4  # Default for demos
    
    if hasattr(request, 'workflow') and 'name:' in request.workflow:
        # Extract workflow name
        for line in request.workflow.split('\n'):
            if line.strip().startswith('name:'):
                workflow_name = line.split(':', 1)[1].strip()
                break
        
        # Count steps
        step_count = request.workflow.count('- name:')
    
    run_data = {
        "id": run_id,
        "workflow_name": workflow_name,
        "workflow_version": "1.0.0",
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "duration_ms": None,
        "step_count": step_count,
        "steps": [],
        "errors": [],
        "metadata": getattr(request, 'metadata', {})
    }
    
    # Extract steps from workflow
    if hasattr(request, 'workflow'):
        steps = []
        lines = request.workflow.split('\n')
        for i, line in enumerate(lines):
            if '- name:' in line:
                step_name = line.split(':', 1)[1].strip()
                steps.append({"name": step_name, "status": "pending"})
        run_data["steps"] = steps
    
    test_runs[run_id] = run_data
    
    # Send WebSocket notification
    await broadcast_message({
        "event": "dag.run.created",
        "data": {
            "run_id": run_id,
            "workflow_name": workflow_name,
            "status": "running",
            "message": f"Workflow '{workflow_name}' started"
        }
    })
    
    # Simulate workflow execution based on type
    demo_type = request.inputs.get('demo_type', 'standard') if hasattr(request, 'inputs') else 'standard'
    if demo_type == 'failure_recovery':
        asyncio.create_task(simulate_failure_workflow(run_id))
    elif demo_type == 'parallel':
        asyncio.create_task(simulate_parallel_workflow(run_id))
    else:
        asyncio.create_task(simulate_workflow_execution(run_id))
    
    return run_data


@app.get("/api/dag-runs")
async def list_runs():
    """List all test runs."""
    return {
        "items": list(test_runs.values()),
        "total": len(test_runs),
        "limit": 20,
        "offset": 0
    }


@app.get("/api/dag-runs/{run_id}")
async def get_run(run_id: str):
    """Get a specific run."""
    if run_id not in test_runs:
        return {"error": "Run not found"}, 404
    return test_runs[run_id]


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    websocket_connections.append(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "event": "connection.established",
            "data": {"message": "Connected to test WebSocket"}
        })
        
        # Keep connection alive
        while True:
            # Wait for messages (or timeout)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                # Echo back any received messages
                await websocket.send_json({
                    "event": "echo",
                    "data": {"received": data}
                })
            except asyncio.TimeoutError:
                # Send ping to keep alive
                await websocket.send_json({
                    "event": "ping",
                    "data": {"time": datetime.now().isoformat()}
                })
                
    except WebSocketDisconnect:
        websocket_connections.remove(websocket)


async def broadcast_message(message: dict):
    """Broadcast message to all connected WebSocket clients."""
    disconnected = []
    for ws in websocket_connections:
        try:
            await ws.send_json(message)
        except:
            disconnected.append(ws)
    
    # Remove disconnected clients
    for ws in disconnected:
        if ws in websocket_connections:
            websocket_connections.remove(ws)


async def simulate_workflow_execution(run_id: str):
    """Simulate workflow execution with WebSocket updates."""
    if run_id not in test_runs:
        return
        
    run = test_runs[run_id]
    
    # Simulate step execution
    for i, step in enumerate(run["steps"]):
        await asyncio.sleep(1)  # Simulate processing time
        
        # Update step status to running
        step["status"] = "running"
        await broadcast_message({
            "event": "dag.run.step.started",
            "data": {
                "run_id": run_id,
                "step_name": step["name"],
                "step_index": i
            }
        })
        
        await asyncio.sleep(random.uniform(0.5, 1.5))  # Simulate work
        
        # Update step status to completed
        step["status"] = "completed"
        await broadcast_message({
            "event": "dag.run.step.completed",
            "data": {
                "run_id": run_id,
                "step_name": step["name"],
                "step_index": i,
                "output": f"Output from {step['name']}"
            }
        })
    
    # Complete the workflow
    run["status"] = "success"
    run["completed_at"] = datetime.utcnow().isoformat()
    run["duration_ms"] = 3000  # Simulated duration
    
    await broadcast_message({
        "event": "dag.run.completed",
        "data": {
            "run_id": run_id,
            "status": "success",
            "duration_ms": run["duration_ms"],
            "message": "Workflow completed successfully"
        }
    })


async def simulate_failure_workflow(run_id: str):
    """Simulate workflow with failures and retries."""
    if run_id not in test_runs:
        return
        
    run = test_runs[run_id]
    
    for i, step in enumerate(run["steps"]):
        await asyncio.sleep(1)
        
        # Start the step
        step["status"] = "running"
        await broadcast_message({
            "event": "dag.run.step.started",
            "data": {
                "run_id": run_id,
                "step_name": step["name"],
                "step_index": i
            }
        })
        
        # Simulate failure on second step
        if i == 1:  # extract_text step
            for retry in range(3):
                await asyncio.sleep(2)
                
                if retry < 2:  # Fail first 2 attempts
                    await broadcast_message({
                        "event": "dag.run.step.retry",
                        "data": {
                            "run_id": run_id,
                            "step_name": step["name"],
                            "retry_count": retry + 1,
                            "error": "Simulated extraction failure"
                        }
                    })
                else:  # Succeed on 3rd attempt
                    step["status"] = "completed"
                    await broadcast_message({
                        "event": "dag.run.step.completed",
                        "data": {
                            "run_id": run_id,
                            "step_name": step["name"],
                            "step_index": i,
                            "retries": 2,
                            "output": f"Output after {retry + 1} retries"
                        }
                    })
                    break
        else:
            # Normal completion
            await asyncio.sleep(random.uniform(1, 3))
            step["status"] = "completed"
            await broadcast_message({
                "event": "dag.run.step.completed",
                "data": {
                    "run_id": run_id,
                    "step_name": step["name"],
                    "step_index": i,
                    "output": f"Output from {step['name']}"
                }
            })
    
    # Complete workflow
    run["status"] = "success"
    run["completed_at"] = datetime.utcnow().isoformat()
    run["duration_ms"] = 12000  # Longer due to retries
    
    await broadcast_message({
        "event": "dag.run.completed",
        "data": {
            "run_id": run_id,
            "status": "success",
            "duration_ms": run["duration_ms"],
            "message": "Workflow completed after retries"
        }
    })


async def simulate_parallel_workflow(run_id: str):
    """Simulate workflow with parallel execution."""
    if run_id not in test_runs:
        return
        
    run = test_runs[run_id]
    
    # Group steps by parallel execution
    parallel_groups = {}
    sequential_steps = []
    
    for step in run["steps"]:
        if "process_chunk" in step["name"]:
            parallel_groups.setdefault("chunks", []).append(step)
        else:
            sequential_steps.append(step)
    
    # Execute split_document first
    if sequential_steps:
        first_step = sequential_steps[0]
        first_step["status"] = "running"
        await broadcast_message({
            "event": "dag.run.step.started",
            "data": {
                "run_id": run_id,
                "step_name": first_step["name"],
                "step_index": 0
            }
        })
        
        await asyncio.sleep(2)
        first_step["status"] = "completed"
        await broadcast_message({
            "event": "dag.run.step.completed",
            "data": {
                "run_id": run_id,
                "step_name": first_step["name"],
                "output": "Document split into 4 chunks"
            }
        })
    
    # Execute parallel chunks
    if "chunks" in parallel_groups:
        # Start all parallel steps
        for step in parallel_groups["chunks"]:
            step["status"] = "running"
            await broadcast_message({
                "event": "dag.run.step.started",
                "data": {
                    "run_id": run_id,
                    "step_name": step["name"],
                    "parallel": True
                }
            })
        
        # Complete them with different timings
        tasks = []
        for i, step in enumerate(parallel_groups["chunks"]):
            duration = random.uniform(2, 5)
            tasks.append(complete_parallel_step(run_id, step, duration))
        
        await asyncio.gather(*tasks)
    
    # Execute merge_results
    if len(sequential_steps) > 1:
        last_step = sequential_steps[-1]
        last_step["status"] = "running"
        await broadcast_message({
            "event": "dag.run.step.started",
            "data": {
                "run_id": run_id,
                "step_name": last_step["name"]
            }
        })
        
        await asyncio.sleep(3)
        last_step["status"] = "completed"
        await broadcast_message({
            "event": "dag.run.step.completed",
            "data": {
                "run_id": run_id,
                "step_name": last_step["name"],
                "output": "All chunks merged successfully"
            }
        })
    
    # Complete workflow
    run["status"] = "success"
    run["completed_at"] = datetime.utcnow().isoformat()
    run["duration_ms"] = 8000  # Faster due to parallel execution
    
    await broadcast_message({
        "event": "dag.run.completed",
        "data": {
            "run_id": run_id,
            "status": "success",
            "duration_ms": run["duration_ms"],
            "message": "Parallel workflow completed"
        }
    })


async def complete_parallel_step(run_id: str, step: dict, duration: float):
    """Complete a parallel step after specified duration."""
    await asyncio.sleep(duration)
    step["status"] = "completed"
    await broadcast_message({
        "event": "dag.run.step.completed",
        "data": {
            "run_id": run_id,
            "step_name": step["name"],
            "parallel": True,
            "duration": duration,
            "output": f"Chunk processed in {duration:.1f}s"
        }
    })


if __name__ == "__main__":
    import uvicorn
    print("Starting test server on http://localhost:8000")
    print("CORS enabled for all origins (*)")
    print("WebSocket available at ws://localhost:8000/ws")
    print("-" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")