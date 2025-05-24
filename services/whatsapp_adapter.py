"""
WhatsApp Webhook Adapter for Bluelabel Autopilot

This module handles incoming WhatsApp webhook events and triggers the appropriate workflow.
"""

import os
import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("whatsapp_adapter")

# Constants
WORKFLOW_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "workflows", "templates")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "whatsapp_logs")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

class WhatsAppAdapter:
    """Handles WhatsApp webhook events and triggers appropriate workflows."""
    
    def __init__(self, workflow_runner=None):
        """Initialize the WhatsApp adapter.
        
        Args:
            workflow_runner: Optional workflow runner instance. If not provided,
                          the adapter will use the default CLI runner.
        """
        self.workflow_runner = workflow_runner
        self.setup_logging()
    
    def setup_logging(self):
        """Configure file logging for WhatsApp events."""
        log_file = os.path.join(LOG_DIR, f"whatsapp_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    def get_workflow_path(self, content_type: str) -> Optional[str]:
        """Get the path to the workflow template based on content type.
        
        Args:
            content_type: Type of content ('url' or 'pdf')
            
        Returns:
            Path to the workflow template or None if not found
        """
        workflow_map = {
            'url': 'url_to_digest.yaml',
            'pdf': 'pdf_to_digest.yaml'
        }
        
        if content_type not in workflow_map:
            logger.error(f"Unsupported content type: {content_type}")
            return None
            
        workflow_path = os.path.join(WORKFLOW_BASE_DIR, workflow_map[content_type])
        if not os.path.exists(workflow_path):
            logger.error(f"Workflow template not found: {workflow_path}")
            return None
            
        return workflow_path
    
    async def trigger_workflow(self, workflow_path: str, input_data: Dict[str, Any]) -> Tuple[str, str]:
        """Trigger a workflow with the given input data.
        
        Args:
            workflow_path: Path to the workflow template
            input_data: Input data for the workflow
            
        Returns:
            Tuple of (run_id, status)
        """
        run_id = str(uuid.uuid4())
        logger.info(f"Triggering workflow: {workflow_path} (Run ID: {run_id})")
        
        try:
            if self.workflow_runner:
                # Use provided workflow runner if available
                result = await self.workflow_runner.run_workflow(workflow_path, input_data)
                status = "completed" if result.get("success", False) else "failed"
            else:
                # Fallback to CLI runner
                import subprocess
                import shlex
                
                # Convert input data to CLI arguments
                args = ["python", "runner/cli_runner.py", "run_workflow", workflow_path]
                for key, value in input_data.items():
                    args.append(f"--input.{key}")
                    args.append(shlex.quote(str(value)))
                
                logger.info(f"Executing: {' '.join(args)}")
                process = await asyncio.create_subprocess_exec(
                    *args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                status = "completed" if process.returncode == 0 else "failed"
                
                if stderr:
                    logger.error(f"Workflow error: {stderr.decode()}")
                
                logger.info(f"Workflow completed with status: {status}")
                
            return run_id, status
            
        except Exception as e:
            logger.exception(f"Error triggering workflow: {e}")
            return run_id, "error"
    
    async def process_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Process an incoming WhatsApp webhook payload.
        
        Args:
            payload: The webhook payload
            
        Returns:
            Dict containing the processing result
        """
        logger.info(f"Processing webhook: {json.dumps(payload, indent=2)}")
        
        # Extract content type and value
        content_type = payload.get('type')
        content_value = payload.get('value')
        
        if not content_type or not content_value:
            error_msg = "Missing required fields: 'type' and 'value' are required"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        # Get the appropriate workflow
        workflow_path = self.get_workflow_path(content_type)
        if not workflow_path:
            error_msg = f"No workflow found for type: {content_type}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
        
        # Prepare workflow input
        input_data = {content_type: content_value}
        
        # Trigger the workflow
        run_id, status = await self.trigger_workflow(workflow_path, input_data)
        
        # Log the execution
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": run_id,
            "workflow": os.path.basename(workflow_path),
            "status": status,
            "input": payload
        }
        
        log_file = os.path.join(LOG_DIR, f"{run_id}.json")
        with open(log_file, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        return {
            "status": "success",
            "run_id": run_id,
            "workflow": os.path.basename(workflow_path),
            "log_file": log_file
        }

# For testing without asyncio
async def process_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for testing without instantiating the class."""
    adapter = WhatsAppAdapter()
    return await adapter.process_webhook(payload)
