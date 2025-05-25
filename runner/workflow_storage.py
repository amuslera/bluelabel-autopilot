import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

class WorkflowStorage:
    """Handles persistence of workflow outputs and metadata."""
    
    def __init__(self, base_path: str = "data/workflows"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.archive_file = self.base_path / "run_archive.json"
    
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
    
    def _load_archive(self) -> List[Dict[str, Any]]:
        """Load existing archive or return empty list."""
        if self.archive_file.exists():
            try:
                with open(self.archive_file) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def _save_archive(self, archive: List[Dict[str, Any]]) -> None:
        """Save archive to disk."""
        with open(self.archive_file, 'w') as f:
            json.dump(archive, f, indent=2)
    
    def add_to_archive(self, workflow_id: str, run_id: str, metadata: Dict[str, Any]) -> None:
        """Add a workflow run to the archive."""
        archive = self._load_archive()
        
        # Create archive entry
        entry = {
            "workflow_id": workflow_id,
            "run_id": run_id,
            "timestamp": metadata.get("timestamp", datetime.utcnow().isoformat()),
            "workflow_name": metadata.get("workflow_name", workflow_id),
            "version": metadata.get("version", "1.0.0"),
            "status": metadata.get("status", "completed"),
            "duration_ms": metadata.get("duration_ms", 0),
            "tags": metadata.get("tags", []),
            "summary": metadata.get("summary", ""),
            "source": metadata.get("source", {})
        }
        
        # Add entry and keep only last 100 runs
        archive.append(entry)
        if len(archive) > 100:
            archive = archive[-100:]
        
        self._save_archive(archive)
    
    def get_archive(self) -> List[Dict[str, Any]]:
        """Get the full run archive."""
        return self._load_archive()
    
    def get_recent_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent runs from archive."""
        archive = self._load_archive()
        return archive[-limit:] if archive else [] 