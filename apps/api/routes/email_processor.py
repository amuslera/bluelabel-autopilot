"""
Email processing pipeline endpoint.

Handles email with PDF attachments through the complete workflow:
1. Extract PDF from email
2. Run ingestion agent
3. Generate digest
4. Return summary with real-time updates
"""

import os
import base64
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
import json
import asyncio
from email import message_from_string
from email.mime.multipart import MIMEMultipart

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel, Field

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType
from apps.api.websocket_manager import WebSocketManager
from apps.api.models import WebSocketMessage


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["email"])

# WebSocket manager and active runs will be injected
ws_manager = None
active_runs = None

def init_router(websocket_manager, runs_dict):
    """Initialize router with dependencies."""
    global ws_manager, active_runs
    ws_manager = websocket_manager
    active_runs = runs_dict


class EmailProcessRequest(BaseModel):
    """Request model for email processing."""
    subject: str = Field(..., description="Email subject")
    sender: str = Field(..., description="Sender email address")
    body: str = Field(..., description="Email body text")
    attachments: List[Dict[str, str]] = Field(
        default_factory=list, 
        description="List of attachments with name and base64 content"
    )
    workflow_type: str = Field(
        default="pdf_to_digest", 
        description="Workflow to execute"
    )


class EmailProcessResponse(BaseModel):
    """Response model for email processing."""
    run_id: str = Field(..., description="Workflow run ID")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    summary: Optional[str] = Field(None, description="Generated summary (when complete)")
    processing_time_ms: Optional[int] = Field(None, description="Total processing time")


@router.post("/process-email", response_model=EmailProcessResponse)
async def process_email(
    request: EmailProcessRequest,
    background_tasks: BackgroundTasks
) -> EmailProcessResponse:
    """
    Process an email with PDF attachment through the workflow pipeline.
    
    Extracts PDF, runs ingestion, generates digest, and returns summary.
    Real-time progress updates are sent via WebSocket.
    """
    start_time = datetime.utcnow()
    run_id = f"email-{start_time.timestamp()}"
    
    logger.info(f"Processing email from {request.sender}: {request.subject}")
    
    # Validate we have PDF attachment
    pdf_attachments = [
        att for att in request.attachments 
        if att.get('name', '').lower().endswith('.pdf')
    ]
    
    if not pdf_attachments:
        raise HTTPException(
            status_code=400,
            detail="No PDF attachment found in email"
        )
    
    # Use first PDF attachment
    pdf_attachment = pdf_attachments[0]
    
    # Create temporary workflow for this email
    temp_dir = Path(tempfile.mkdtemp())
    pdf_path = temp_dir / pdf_attachment['name']
    
    try:
        # Decode and save PDF
        pdf_content = base64.b64decode(pdf_attachment['content'])
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        logger.info(f"Saved PDF: {pdf_path} ({len(pdf_content)} bytes)")
        
        # Create workflow YAML
        workflow_yaml = f"""
workflow:
  name: Email PDF Processing
  version: 1.0.0
  description: Process PDF from email {request.sender}

steps:
  - id: ingest_pdf
    name: Extract PDF Content
    agent: ingestion_agent
    input_file: {temp_dir}/pdf_input.json
    
  - id: create_digest
    name: Generate Summary
    agent: digest_agent
    input_from: ingest_pdf
    config:
      max_length: 500
      style: executive_summary
"""
        
        workflow_path = temp_dir / "email_workflow.yaml"
        with open(workflow_path, 'w') as f:
            f.write(workflow_yaml)
        
        # Create input JSON for ingestion
        input_data = {
            "task_id": run_id,
            "source": "email",
            "content": {
                "type": "pdf",
                "file_path": str(pdf_path),
                "metadata": {
                    "email_subject": request.subject,
                    "email_sender": request.sender,
                    "attachment_name": pdf_attachment['name']
                }
            },
            "metadata": {
                "email_received": start_time.isoformat(),
                "workflow_type": request.workflow_type
            }
        }
        
        input_path = temp_dir / "pdf_input.json"
        with open(input_path, 'w') as f:
            json.dump(input_data, f)
        
        # Send initial WebSocket update
        await ws_manager.broadcast(WebSocketMessage(
            event="email.processing.started",
            data={
                "run_id": run_id,
                "subject": request.subject,
                "sender": request.sender,
                "pdf_name": pdf_attachment['name'],
                "pdf_size": len(pdf_content)
            }
        ))
        
        # Execute workflow asynchronously
        background_tasks.add_task(
            execute_email_workflow,
            run_id=run_id,
            workflow_path=workflow_path,
            temp_dir=temp_dir,
            email_data=request.dict()
        )
        
        return EmailProcessResponse(
            run_id=run_id,
            status="processing",
            message=f"Processing PDF '{pdf_attachment['name']}' from email"
        )
        
    except Exception as e:
        logger.error(f"Error processing email: {e}")
        # Clean up temp files
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir)
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process email: {str(e)}"
        )


async def execute_email_workflow(
    run_id: str,
    workflow_path: Path,
    temp_dir: Path,
    email_data: Dict[str, Any]
):
    """Execute the email workflow in the background."""
    try:
        # Create workflow engine
        engine = UnifiedWorkflowEngine(
            engine_type=EngineType.SEQUENTIAL,
            storage_path=temp_dir / "storage"
        )
        
        # Track progress via callback
        async def on_progress(result):
            """Send progress updates via WebSocket."""
            completed_steps = len([
                s for s in result.step_outputs.values() 
                if s.status == "success"
            ])
            total_steps = len(result.step_outputs)
            
            await ws_manager.broadcast(WebSocketMessage(
                event="email.processing.progress",
                data={
                    "run_id": run_id,
                    "status": result.status.value,
                    "progress": f"{completed_steps}/{total_steps} steps",
                    "current_step": list(result.step_outputs.keys())[-1] if result.step_outputs else None
                }
            ))
        
        # Execute workflow
        result = await engine.execute_workflow(
            workflow_path=workflow_path,
            persist=True,
            on_complete=on_progress
        )
        
        # Store result
        active_runs[run_id] = result
        
        # Extract summary from digest step
        summary = None
        if result.status.value == "success":
            digest_result = result.step_outputs.get("create_digest")
            if digest_result and digest_result.result:
                summary = digest_result.result.get("digest", "")
        
        # Calculate processing time
        processing_time = int(
            (datetime.utcnow() - datetime.fromisoformat(email_data['subject']))
            .total_seconds() * 1000
        ) if 'subject' in email_data else 0
        
        # Send completion update
        await ws_manager.broadcast(WebSocketMessage(
            event="email.processing.completed",
            data={
                "run_id": run_id,
                "status": result.status.value,
                "summary": summary,
                "processing_time_ms": result.duration_ms,
                "email_subject": email_data.get('subject'),
                "workflow_url": f"/api/dag-runs/{result.run_id}"
            }
        ))
        
        logger.info(f"Email workflow completed: {run_id} - {result.status.value}")
        
    except Exception as e:
        logger.error(f"Error executing email workflow: {e}")
        
        # Send error update
        await ws_manager.broadcast(WebSocketMessage(
            event="email.processing.error",
            data={
                "run_id": run_id,
                "error": str(e),
                "email_subject": email_data.get('subject')
            }
        ))
    
    finally:
        # Clean up temp directory
        if temp_dir.exists():
            import shutil
            try:
                shutil.rmtree(temp_dir)
                logger.info(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                logger.error(f"Failed to clean up temp directory: {e}")


@router.get("/email-status/{run_id}")
async def get_email_status(run_id: str) -> EmailProcessResponse:
    """Get the status of an email processing job."""
    if run_id not in active_runs:
        raise HTTPException(
            status_code=404,
            detail=f"Email processing job {run_id} not found"
        )
    
    result = active_runs[run_id]
    
    # Extract summary if available
    summary = None
    if result.status.value == "success":
        digest_step = result.step_outputs.get("create_digest")
        if digest_step and digest_step.result:
            summary = digest_step.result.get("digest", "")
    
    return EmailProcessResponse(
        run_id=run_id,
        status=result.status.value,
        message=f"Workflow {result.status.value}",
        summary=summary,
        processing_time_ms=result.duration_ms
    )


@router.post("/process-email-form")
async def process_email_form(
    subject: str = Form(...),
    sender: str = Form(...),
    body: str = Form(...),
    pdf_file: UploadFile = File(...)
) -> EmailProcessResponse:
    """
    Process email via form upload (for testing).
    
    Accepts multipart form data with PDF file.
    """
    # Read PDF content
    pdf_content = await pdf_file.read()
    pdf_base64 = base64.b64encode(pdf_content).decode()
    
    # Create request
    request = EmailProcessRequest(
        subject=subject,
        sender=sender,
        body=body,
        attachments=[{
            "name": pdf_file.filename,
            "content": pdf_base64
        }]
    )
    
    # Process using main endpoint
    background_tasks = BackgroundTasks()
    return await process_email(request, background_tasks)