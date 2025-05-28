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

from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType
from core.agent_registry import registry, register_agent
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
from apps.api.routes import email_processor


logger = logging.getLogger(__name__)


# WebSocket manager for real-time updates
ws_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    logger.info("Starting Bluelabel Autopilot API")
    
    # Register agents with the registry
    register_agent('ingestion_agent', IngestionAgent, version="1.0.0", tags=["ingestion", "pdf", "url"])
    register_agent('digest_agent', DigestAgent, version="1.0.0", tags=["digest", "summary"])
    
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
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(log_requests)
app.middleware("http")(handle_errors)
app.middleware("http")(metrics)

# Mount static files for test page
app.mount("/static", StaticFiles(directory="apps/api/static", html=True), name="static")

# Store active runs in memory (in production, use a database)
active_runs: Dict[str, WorkflowRunResult] = {}
run_engines: Dict[str, UnifiedWorkflowEngine] = {}

# Initialize email processor router with dependencies
email_processor.init_router(ws_manager, active_runs)

# Include routers
app.include_router(email_processor.router)


@app.get("/api/dag-runs", response_model=DAGRunListResponse)
async def list_dag_runs(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None
) -> DAGRunListResponse:
    """List all DAG runs with optional filtering."""
    # Filter runs by status if provided
    filtered_runs = active_runs.values()
    if status:
        try:
            status_enum = WorkflowStatus(status.lower())
            filtered_runs = [r for r in filtered_runs if r.status == status_enum]
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    # Sort by start time (newest first)
    sorted_runs = sorted(filtered_runs, key=lambda r: r.started_at, reverse=True)
    
    # Apply pagination
    total = len(sorted_runs)
    paginated = sorted_runs[offset:offset + limit]
    
    # Convert to response format
    items = []
    for run in paginated:
        items.append(DAGRunResponse(
            id=run.run_id,
            workflow_name=run.workflow_name,
            workflow_version=run.workflow_version,
            status=run.status.value,
            started_at=run.started_at.isoformat(),
            completed_at=run.completed_at.isoformat() if run.completed_at else None,
            duration_ms=run.duration_ms,
            step_count=len(run.step_outputs),
            failed_step=run.failed_step,
            errors=run.errors
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
    if run_id not in active_runs:
        raise HTTPException(status_code=404, detail=f"DAG run {run_id} not found")
    
    run = active_runs[run_id]
    
    # Include detailed step information
    steps = []
    for step_id, step_result in run.step_outputs.items():
        steps.append({
            "id": step_id,
            "name": step_result.step_name,
            "status": step_result.status,
            "duration_ms": step_result.duration_ms,
            "error": step_result.error,
            "timestamp": step_result.timestamp.isoformat()
        })
    
    return DAGRunResponse(
        id=run.run_id,
        workflow_name=run.workflow_name,
        workflow_version=run.workflow_version,
        status=run.status.value,
        started_at=run.started_at.isoformat(),
        completed_at=run.completed_at.isoformat() if run.completed_at else None,
        duration_ms=run.duration_ms,
        step_count=len(run.step_outputs),
        steps=steps,
        failed_step=run.failed_step,
        errors=run.errors,
        execution_order=run.execution_order
    )


@app.post("/api/dag-runs", response_model=DAGRunResponse)
async def create_dag_run(request: DAGRunCreateRequest) -> DAGRunResponse:
    """Create a new DAG run."""
    # Validate workflow file exists
    workflow_path = Path(request.workflow_path)
    if not workflow_path.exists():
        raise HTTPException(status_code=404, detail=f"Workflow file not found: {request.workflow_path}")
    
    # Check if a run is already active for this workflow
    active_workflow_runs = [
        r for r in active_runs.values() 
        if r.workflow_file == request.workflow_path and r.status == WorkflowStatus.RUNNING
    ]
    if active_workflow_runs and not request.force:
        raise HTTPException(
            status_code=409, 
            detail=f"Workflow already running. Use force=true to start anyway."
        )
    
    # Create engine with specified type
    engine_type = EngineType(request.engine_type) if request.engine_type else None
    engine = UnifiedWorkflowEngine(
        engine_type=engine_type,
        storage_path=Path(request.storage_path) if request.storage_path else None
    )
    
    # Generate run ID
    run_id = str(uuid.uuid4())
    
    # Store engine reference
    run_engines[run_id] = engine
    
    # Define callback for real-time updates
    async def on_step_complete(result: WorkflowRunResult):
        """Send WebSocket updates as steps complete."""
        # Update stored result
        active_runs[result.run_id] = result
        
        # Send WebSocket update
        await ws_manager.broadcast(WebSocketMessage(
            event="dag.step.status.updated",
            data={
                "run_id": result.run_id,
                "status": result.status.value,
                "steps_completed": len([s for s in result.step_outputs.values() if s.status == "success"]),
                "steps_total": len(result.step_outputs)
            }
        ))
    
    # Start workflow execution in background
    async def execute_workflow():
        try:
            # Send creation event
            await ws_manager.broadcast(WebSocketMessage(
                event="dag.run.created",
                data={
                    "run_id": run_id,
                    "workflow_name": request.workflow_path,
                    "engine_type": request.engine_type or "sequential"
                }
            ))
            
            # Execute workflow
            result = await engine.execute_workflow(
                workflow_path=workflow_path,
                persist=request.persist,
                initial_input=request.initial_input,
                on_complete=on_step_complete
            )
            
            # Store result
            active_runs[run_id] = result
            
            # Send completion event
            await ws_manager.broadcast(WebSocketMessage(
                event="dag.run.completed",
                data={
                    "run_id": result.run_id,
                    "status": result.status.value,
                    "duration_ms": result.duration_ms
                }
            ))
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            # Create error result
            error_result = WorkflowRunResult(
                run_id=run_id,
                workflow_name=workflow_path.name,
                workflow_version="0.0.0",
                status=WorkflowStatus.FAILED,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                duration_ms=0,
                workflow_file=str(workflow_path),
                errors=[str(e)]
            )
            active_runs[run_id] = error_result
            
            # Send error event
            await ws_manager.broadcast(WebSocketMessage(
                event="dag.run.completed",
                data={
                    "run_id": run_id,
                    "status": "failed",
                    "error": str(e)
                }
            ))
    
    # Start execution in background
    asyncio.create_task(execute_workflow())
    
    # Return immediate response with run ID
    return DAGRunResponse(
        id=run_id,
        workflow_name=workflow_path.name,
        workflow_version="0.0.0",  # Will be updated when workflow loads
        status="running",
        started_at=datetime.utcnow().isoformat(),
        step_count=0
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
async def create_test_workflow(background_tasks: BackgroundTasks):
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
    
    # Create workflow request
    request = CreateDAGRunRequest(
        workflow=workflow_yaml,
        inputs={"test_mode": True},
        metadata={"source": "integration_test", "created_by": "CA"}
    )
    
    # Use existing create endpoint logic
    run_id = str(uuid.uuid4())
    
    # Store run info
    run_result = WorkflowRunResult(
        run_id=run_id,
        workflow_name="test-integration-workflow",
        workflow_version="1.0.0",
        status=WorkflowStatus.RUNNING,
        started_at=datetime.utcnow(),
        step_outputs={},
        errors=[]
    )
    active_runs[run_id] = run_result
    
    # Execute workflow asynchronously
    background_tasks.add_task(execute_workflow_task, run_id, request.workflow, request.inputs)
    
    # Send initial WebSocket update
    await ws_manager.broadcast(WebSocketMessage(
        event="dag.run.created",
        data={
            "run_id": run_id,
            "workflow_name": "test-integration-workflow",
            "status": "running",
            "message": "Test workflow created for integration testing"
        }
    ))
    
    return DAGRunResponse(
        id=run_id,
        workflow_name="test-integration-workflow",
        workflow_version="1.0.0",
        status="running",
        started_at=datetime.utcnow().isoformat(),
        step_count=2,
        message="Test workflow started successfully"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)