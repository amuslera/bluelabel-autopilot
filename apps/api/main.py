"""
FastAPI application for Bluelabel Autopilot DAG workflow management.

This module provides REST API endpoints and WebSocket support for:
- DAG run management (create, list, get, update)
- Real-time status updates via WebSocket
- Integration with UnifiedWorkflowEngine
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import uuid

# Add parent directory to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.unified_workflow_adapter import UnifiedWorkflowAdapter
from core.agent_registry import register_agent
from interfaces.run_models import WorkflowRunResult, WorkflowStatus
from agents.ingestion_agent import IngestionAgent
from agents.digest_agent import DigestAgent

# Import API models and routes
from apps.api.models import (
    DAGRunResponse, DAGRunCreateRequest, DAGRunStatusUpdate,
    DAGRunListResponse, WebSocketMessage
)
from apps.api.websocket_manager import WebSocketManager
from apps.api.middleware import log_requests, handle_errors, metrics
from apps.api.routes import email_processor, workflows


logger = logging.getLogger(__name__)


# WebSocket manager for real-time updates
ws_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    logger.info("Starting Bluelabel Autopilot API")
    
    # Register agents with the registry
    register_agent('ingestion_agent', IngestionAgent)
    register_agent('digest_agent', DigestAgent)
    
    logger.info("Agents registered successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Bluelabel Autopilot API")
    await ws_manager.disconnect_all()


# Create FastAPI app
app = FastAPI(
    title="Bluelabel Autopilot API",
    description="API for DAG workflow orchestration with real-time updates",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(log_requests)
app.middleware("http")(handle_errors)
app.middleware("http")(metrics)

# Mount static files for test page
# app.mount("/static", StaticFiles(directory="apps/api/static", html=True), name="static")

# Initialize unified workflow adapter
unified_adapter = UnifiedWorkflowAdapter()

# Store active runs in memory (in production, use a database)
active_runs: Dict[str, WorkflowRunResult] = {}

# Initialize email processor router with dependencies
email_processor.init_router(ws_manager, active_runs)

# Include routers
app.include_router(email_processor.router)
app.include_router(workflows.router, prefix="/api")


@app.get("/api/dag-runs", response_model=DAGRunListResponse)
async def list_dag_runs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None
) -> DAGRunListResponse:
    """List all DAG runs with optional filtering."""
    # Get all runs from unified adapter
    all_runs = unified_adapter.list_runs(limit=100)  # Get more than needed for filtering
    
    # Filter by status if provided
    if status:
        all_runs = [r for r in all_runs if r["status"] == status.lower()]
    
    # Apply pagination
    total = len(all_runs)
    paginated = all_runs[offset:offset + limit]
    
    # Convert to response format
    items = []
    for run in paginated:
        items.append(DAGRunResponse(
            id=run["run_id"],
            workflow_name=run["dag_id"],
            workflow_version="1.0.0",
            status=run["status"],
            started_at=run["created_at"],
            completed_at=run["updated_at"] if run["status"] != "running" else None,
            duration_ms=0,  # TODO: Calculate duration
            step_count=0,  # TODO: Get step count
            failed_step=None,
            errors=[]
        ))
    
    return DAGRunListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


@app.get("/api/dag-runs/{run_id}", response_model=DAGRunResponse)
async def get_dag_run(run_id: str) -> DAGRunResponse:
    """Get a specific DAG run by ID."""
    status = unified_adapter.get_run_status(run_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"DAG run {run_id} not found")
    
    # Convert step information to expected format
    steps = []
    for step_id, step_info in status.get("steps", {}).items():
        steps.append({
            "id": step_id,
            "name": step_id,  # TODO: Get proper step names
            "status": step_info["status"],
            "duration_ms": 0,  # TODO: Calculate from timestamps
            "error": step_info.get("error"),
            "timestamp": step_info.get("started_at", "")
        })
    
    # Calculate duration if completed
    duration_ms = 0
    if status.get("started_at") and status["status"] in ["success", "failed", "cancelled"]:
        # TODO: Calculate actual duration
        duration_ms = 1000  # Placeholder
    
    return DAGRunResponse(
        id=run_id,
        workflow_name=status.get("dag_id", "unknown"),
        workflow_version="1.0.0",
        status=status["status"],
        started_at=status["started_at"],
        completed_at=status.get("updated_at") if status["status"] != "running" else None,
        duration_ms=duration_ms,
        step_count=len(steps),
        steps=steps,
        failed_step=None,  # TODO: Determine from step statuses
        errors=[status.get("error")] if status.get("error") else [],
        execution_order=list(status.get("steps", {}).keys())
    )


@app.post("/api/dag-runs", response_model=DAGRunResponse)
async def create_dag_run(request: DAGRunCreateRequest) -> DAGRunResponse:
    """Create a new DAG run."""
    # Extract workflow name from path or YAML
    workflow_name = request.workflow_path
    workflow_yaml = None
    
    # If workflow_path ends with .yaml, it's a file path
    if workflow_name.endswith('.yaml'):
        workflow_path = Path(workflow_name)
        if not workflow_path.exists():
            raise HTTPException(status_code=404, detail=f"Workflow file not found: {workflow_name}")
        workflow_name = workflow_path.stem
    else:
        # Otherwise it might be inline YAML
        if hasattr(request, 'workflow_yaml'):
            workflow_yaml = request.workflow_yaml
    
    # Start workflow with unified adapter
    try:
        run_id = await unified_adapter.run_workflow(
            workflow_name=workflow_name,
            inputs=request.initial_input or {},
            workflow_yaml=workflow_yaml
        )
        
        # Get initial status
        status = unified_adapter.get_run_status(run_id)
        if not status:
            raise HTTPException(status_code=500, detail="Failed to get workflow status")
    
        # Send creation event via WebSocket
        await ws_manager.broadcast(WebSocketMessage(
            event="dag.run.created",
            data={
                "run_id": run_id,
                "workflow_name": workflow_name,
                "status": status["status"]
            }
        ))
        
        # Start monitoring workflow status in background
        async def monitor_workflow():
            try:
                prev_status = None
                while True:
                    await asyncio.sleep(0.5)  # Poll every 500ms
                    
                    current_status = unified_adapter.get_run_status(run_id)
                    if not current_status:
                        break
                    
                    # Send updates when status changes
                    if current_status != prev_status:
                        await ws_manager.broadcast(WebSocketMessage(
                            event="dag.step.status.updated",
                            data={
                                "run_id": run_id,
                                "status": current_status["status"],
                                "steps": current_status["steps"]
                            }
                        ))
                        prev_status = current_status
                    
                    # Check if workflow is complete
                    if current_status["status"] in ["success", "failed", "cancelled"]:
                        await ws_manager.broadcast(WebSocketMessage(
                            event="dag.run.completed",
                            data={
                                "run_id": run_id,
                                "status": current_status["status"],
                                "error": current_status.get("error")
                            }
                        ))
                        break
                        
            except Exception as e:
                logger.error(f"Error monitoring workflow: {e}")
        
        # Start monitoring in background
        asyncio.create_task(monitor_workflow())
        
    except Exception as e:
        logger.error(f"Failed to create workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Return immediate response with run ID
    return DAGRunResponse(
        id=run_id,
        workflow_name=workflow_name,
        workflow_version="1.0.0",  # TODO: Get from workflow definition
        status=status["status"],
        started_at=status["started_at"],
        step_count=len(status.get("steps", {}))
    )


@app.patch("/api/dag-runs/{run_id}/status")
async def update_dag_run_status(run_id: str, update: DAGRunStatusUpdate):
    """Update the status of a DAG run (e.g., cancel)."""
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail=f"DAG run {run_id} not found")
    
    run = active_runs[run_id]
    
    # Only allow cancelling running workflows
    if update.status == "cancelled":
        if run.status != WorkflowStatus.RUNNING:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel workflow in {run.status.value} state"
            )
        
        # Cancel the workflow
        # TODO: Implement cancellation in UnifiedWorkflowEngine
        run.status = WorkflowStatus.FAILED
        run.errors.append("Cancelled by user")
        run.completed_at = datetime.utcnow()
        
        # Send WebSocket update
        await ws_manager.broadcast(WebSocketMessage(
            event="dag.run.status.updated",
            data={
                "run_id": run_id,
                "status": "cancelled",
                "message": update.message
            }
        ))
        
        return {"status": "cancelled", "message": "Workflow cancelled"}
    
    else:
        raise HTTPException(status_code=400, detail=f"Invalid status update: {update.status}")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time DAG updates."""
    await ws_manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "event": "connection.established",
            "data": {"message": "Connected to DAG updates"}
        })
        
        # Keep connection alive
        while True:
            # Wait for client messages (ping/pong)
            data = await websocket.receive_text()
            # Echo back for ping/pong
            if data == "ping":
                await websocket.send_text("pong")
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "active_runs": len(active_runs),
        "connected_clients": len(ws_manager.active_connections)
    }


@app.get("/metrics")
async def get_metrics():
    """Get API performance metrics."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "api_metrics": metrics.get_metrics(),
        "dag_metrics": {
            "active_runs": len(active_runs),
            "total_runs": len(active_runs),
            "runs_by_status": {
                "running": len([r for r in active_runs.values() if r.status == WorkflowStatus.RUNNING]),
                "success": len([r for r in active_runs.values() if r.status == WorkflowStatus.SUCCESS]),
                "failed": len([r for r in active_runs.values() if r.status == WorkflowStatus.FAILED])
            }
        },
        "websocket_metrics": {
            "connected_clients": ws_manager.get_connection_count()
        }
    }


@app.post("/api/test/create-sample-workflow")
async def create_test_workflow():
    """Create a sample workflow for testing. Used by CA for integration testing."""
    # Create a simple test workflow
    workflow_yaml = """
name: test-integration-workflow
version: 1.0.0
description: Test workflow for frontend integration

steps:
  - name: analyze_text
    agent: ingestion
    input:
      text: "This is a test document for integration testing. The quick brown fox jumps over the lazy dog."
    output: analysis_result

  - name: generate_summary
    agent: digest
    input:
      content: "{{analysis_result}}"
      format: "brief"
    output: summary_result
"""
    
    # Run workflow using unified adapter
    try:
        run_id = await unified_adapter.run_workflow(
            workflow_name="test-integration-workflow",
            inputs={"test_mode": True},
            workflow_yaml=workflow_yaml
        )
        
        # Get initial status
        status = unified_adapter.get_run_status(run_id)
        
        # Send initial WebSocket update
        await ws_manager.broadcast(WebSocketMessage(
            event="dag.run.created",
            data={
                "run_id": run_id,
                "workflow_name": "test-integration-workflow",
                "status": status["status"],
                "message": "Test workflow created for integration testing"
            }
        ))
        
        return DAGRunResponse(
            id=run_id,
            workflow_name="test-integration-workflow",
            workflow_version="1.0.0",
            status=status["status"],
            started_at=status["started_at"],
            step_count=2,
            message="Test workflow started successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)