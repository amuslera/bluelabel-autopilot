from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import os
import sys

# Add parent dirs to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.workflow_engine import run_workflow
from services.workflow.dag_run_store import DAGRunStore

router = APIRouter(prefix="/workflows", tags=["workflows"])
store = DAGRunStore()

class WorkflowRunRequest(BaseModel):
    workflow_path: str
    inputs: Optional[dict] = {}

@router.post("/run")
async def run_workflow_endpoint(request: WorkflowRunRequest):
    try:
        # Load workflow YAML to get step info
        import yaml
        with open(request.workflow_path, 'r') as f:
            workflow_def = yaml.safe_load(f)
        
        # THIS IS THE REAL CALL - NO MOCKS!
        result = await run_workflow(
            path=request.workflow_path,
            initial_input=request.inputs
        )
        
        # Store the run in DAGRunStore
        from services.workflow.dag_run_tracker import DAGRun, DAGRunStatus, DAGStepStatus
        dag_run = DAGRun(
            dag_id=result.workflow_name,
            run_id=result.run_id
        )
        dag_run.status = DAGRunStatus.SUCCESS if result.status.value.lower() == "success" else DAGRunStatus.FAILED
        dag_run.workflow_name = result.workflow_name  # Add as attribute
        dag_run.started_at = result.started_at.isoformat() if hasattr(result, 'started_at') else None
        
        # Add steps from the workflow definition
        if 'steps' in workflow_def:
            for step in workflow_def['steps']:
                step_id = step.get('id', f"step_{step.get('name', 'unknown')}")
                step_state = dag_run.add_step(step_id=step_id)
                # Set step metadata
                step_state.metadata['name'] = step.get('name', step_id)
                # Mark step as complete based on overall run status
                if dag_run.status == DAGRunStatus.SUCCESS:
                    step_state.status = DAGStepStatus.SUCCESS
                    step_state.start()
                    step_state.complete()
                else:
                    step_state.status = DAGStepStatus.FAILED
                    step_state.start()
                    step_state.fail("Workflow failed")
        
        store.create(dag_run)
        
        return {
            "run_id": result.run_id,
            "status": result.status.value,
            "workflow_name": result.workflow_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dag-runs")
async def list_dag_runs(limit: int = 20, offset: int = 0):
    try:
        runs = store.list_runs(limit=limit)
        # Convert DAGRun objects to dicts with expected format
        items = []
        for run in runs:
            run_dict = run.to_dict() if hasattr(run, 'to_dict') else run
            # Map to expected frontend format
            items.append({
                "id": run_dict.get("run_id"),
                "workflow_name": run_dict.get("dag_id"),
                "status": run_dict.get("status"),
                "started_at": run_dict.get("created_at"),  # Map created_at to started_at
                "completed_at": run_dict.get("updated_at"),
            })
        return {"items": items, "total": len(items), "limit": limit, "offset": offset}
    except Exception as e:
        # If store fails, return empty list
        print(f"Error listing runs: {e}")
        return {"items": [], "total": 0, "limit": limit, "offset": offset}

@router.get("/dag-runs/{run_id}")
async def get_dag_run(run_id: str):
    run = store.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run.to_dict()

@router.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    # Save file
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Run workflow
    result = await run_workflow(
        path="workflows/sample_ingestion_digest.yaml",
        initial_input={"pdf_path": file_path}
    )

    return {"run_id": result.run_id, "status": "started"}

# Triggers (stubs)
@router.post("/workflows/from-url")
def from_url():
    return {"message": "URL ingestion not implemented"}

@router.post("/workflows/from-email")
def from_email():
    return {"message": "Email webhook not implemented"} 