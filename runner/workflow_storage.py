import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class WorkflowStorage:
    """Handles persistence of workflow outputs and metadata."""
    
    def __init__(self, base_path: str = "data/workflows"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def _generate_run_id(self, use_uuid: bool = False) -> str:
        """Generate a unique run ID."""
        if use_uuid:
            return str(uuid.uuid4())
        return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%SZ")
    
    def create_run_directory(self, workflow_id: str, use_uuid: bool = False) -> Path:
        """Create a directory for a new workflow run."""
        run_id = self._generate_run_id(use_uuid)
        run_path = self.base_path / workflow_id / run_id
        run_path.mkdir(parents=True, exist_ok=True)
        return run_path
    
    def save_workflow_definition(self, run_path: Path, workflow_yaml: str) -> None:
        """Save the workflow YAML definition."""
        with open(run_path / "workflow.yaml", "w") as f:
            f.write(workflow_yaml)
    
    def save_run_metadata(self, run_path: Path, metadata: Dict[str, Any]) -> None:
        """Save run metadata including timestamps and configuration."""
        metadata["timestamp"] = datetime.utcnow().isoformat()
        with open(run_path / "run_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    
    def save_step_output(self, run_path: Path, step_id: str, output: Dict[str, Any]) -> None:
        """Save a step's output to a JSON file."""
        output["timestamp"] = datetime.utcnow().isoformat()
        with open(run_path / f"{step_id}_output.json", "w") as f:
            json.dump(output, f, indent=2)
    
    def get_run_path(self, workflow_id: str, run_id: str) -> Path:
        """Get the path for a specific workflow run."""
        return self.base_path / workflow_id / run_id
    
    def list_runs(self, workflow_id: str) -> list[str]:
        """List all run IDs for a workflow."""
        workflow_path = self.base_path / workflow_id
        if not workflow_path.exists():
            return []
        return [d.name for d in workflow_path.iterdir() if d.is_dir()]
    
    def get_run_metadata(self, workflow_id: str, run_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific run."""
        metadata_path = self.get_run_path(workflow_id, run_id) / "run_metadata.json"
        if not metadata_path.exists():
            return None
        with open(metadata_path) as f:
            return json.load(f)
    
    def get_step_output(self, workflow_id: str, run_id: str, step_id: str) -> Optional[Dict[str, Any]]:
        """Get output for a specific step in a run."""
        output_path = self.get_run_path(workflow_id, run_id) / f"{step_id}_output.json"
        if not output_path.exists():
            return None
        with open(output_path) as f:
            return json.load(f) 