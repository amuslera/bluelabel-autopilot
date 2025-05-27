"""
DAG Trace Exporter - Generates human-readable reports from DAG run traces.

This module provides functionality to export DAG run traces in various formats,
with a focus on human-readable HTML reports for debugging and transparency.
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from jinja2 import Environment, FileSystemLoader
from services.workflow.dag_run_store import DAGRunStore
from services.workflow.dag_run_tracker import DAGRunStatus

logger = logging.getLogger(__name__)

class DAGTraceExporter:
    """Exports DAG run traces in various formats."""
    
    def __init__(self, dag_store: Optional[DAGRunStore] = None):
        """
        Initialize the DAG trace exporter.
        
        Args:
            dag_store: DAGRunStore instance for accessing traces
        """
        self.dag_store = dag_store or DAGRunStore()
        
        # Setup Jinja2 environment for HTML templates
        template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True
        )
    
    def export_trace(self, run_id: str, format: str = "html") -> str:
        """
        Export a DAG run trace in the specified format.
        
        Args:
            run_id: ID of the DAG run to export
            format: Output format ("html" supported)
            
        Returns:
            Exported trace content as string
            
        Raises:
            ValueError: If format is not supported
            FileNotFoundError: If trace not found
        """
        # Get DAG run from store
        dag_run = self.dag_store.get(run_id)
        if not dag_run:
            raise FileNotFoundError(f"No DAG run found with ID: {run_id}")
            
        # Export in requested format
        if format == "html":
            return self._export_html(dag_run)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_html(self, dag_run: Any) -> str:
        """
        Export DAG run trace as HTML report.
        
        Args:
            dag_run: DAGRun instance to export
            
        Returns:
            HTML report as string
        """
        # Load HTML template
        template = self.env.get_template("dag_trace_report.html")
        
        # Prepare template data
        data = {
            "dag_id": dag_run.dag_id,
            "run_id": dag_run.run_id,
            "status": dag_run.status.value,
            "created_at": dag_run.created_at.isoformat(),
            "updated_at": dag_run.updated_at.isoformat(),
            "duration": self._format_duration(dag_run.duration),
            "steps": self._prepare_step_data(dag_run.steps),
            "metadata": dag_run.metadata,
            "error": dag_run.error
        }
        
        # Render template
        return template.render(**data)
    
    def _prepare_step_data(self, steps: Dict[str, Any]) -> list:
        """Prepare step data for template rendering."""
        step_list = []
        
        for step_id, step in steps.items():
            step_data = {
                "id": step_id,
                "status": step.status.value,
                "started_at": step.started_at.isoformat() if step.started_at else None,
                "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                "duration": self._format_duration(step.duration),
                "retries": step.retry_count,
                "error": step.error,
                "result": step.result
            }
            step_list.append(step_data)
            
        return step_list
    
    def _format_duration(self, duration: Optional[float]) -> str:
        """Format duration in seconds to human-readable string."""
        if duration is None:
            return "N/A"
            
        if duration < 1:
            return f"{duration*1000:.0f}ms"
        elif duration < 60:
            return f"{duration:.1f}s"
        else:
            minutes = int(duration // 60)
            seconds = duration % 60
            return f"{minutes}m {seconds:.1f}s" 