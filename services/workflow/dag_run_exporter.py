"""
DAGRun Export Utilities.

This module provides functionality to export DAGRun execution results
in various formats (JSON, HTML) for analysis and reporting.
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, Union
from datetime import datetime
import logging
from jinja2 import Environment, FileSystemLoader, select_autoescape

from .dag_run_tracker import DAGRun, DAGRunStatus, DAGStepStatus
from services.workflow.dag_run_store import DAGRunStore

logger = logging.getLogger(__name__)


class ExportFormat(Enum):
    """Supported export formats."""
    JSON = "json"
    HTML = "html"


class ExportValidationError(Exception):
    """Raised when export validation fails."""
    pass


class DAGRunExporter:
    """Export DAGRun execution results in various formats."""

    # Size limit for exports (500KB)
    SIZE_LIMIT = 500 * 1024

    def __init__(self, dag_store: DAGRunStore):
        """Initialize the exporter.
        
        Args:
            dag_store: DAGRunStore instance for accessing DAG runs
        """
        self.dag_store = dag_store
        self.template_env = Environment(
            loader=FileSystemLoader(Path(__file__).parent / "templates"),
            autoescape=True
        )

    def validate_format(self, format_str: str) -> ExportFormat:
        """Validate the requested export format.
        
        Args:
            format_str: Requested format as string
            
        Returns:
            ExportFormat enum value
            
        Raises:
            ExportValidationError: If format is not supported
        """
        try:
            return ExportFormat(format_str.lower())
        except ValueError:
            raise ExportValidationError(
                f"Unsupported export format: {format_str}. "
                f"Supported formats: {', '.join(f.value for f in ExportFormat)}"
            )

    def _check_size(self, content: Union[str, bytes]) -> Optional[str]:
        """Check if content exceeds size limit.
        
        Args:
            content: Content to check
            
        Returns:
            Warning message if size limit exceeded, None otherwise
        """
        size = len(content.encode() if isinstance(content, str) else content)
        if size > self.SIZE_LIMIT:
            return (
                f"Warning: Export size ({size/1024:.1f}KB) exceeds recommended limit "
                f"({self.SIZE_LIMIT/1024:.1f}KB). Consider filtering results."
            )
        return None

    def export(self, run_id: str, format_str: str = "json") -> Dict:
        """Export a DAGRun in the specified format.
        
        Args:
            run_id: ID of the DAGRun to export
            format_str: Export format (json or html)
            
        Returns:
            Dict containing:
                - content: Export content
                - format: Used format
                - warning: Optional size warning
                
        Raises:
            ExportValidationError: If format is invalid
            ValueError: If DAGRun not found
        """
        # Validate format
        export_format = self.validate_format(format_str)
        
        # Get DAGRun
        dag_run = self.dag_store.get(run_id)
        if not dag_run:
            raise ValueError(f"DAGRun not found: {run_id}")
        
        # Generate content
        if export_format == ExportFormat.JSON:
            content = json.dumps(dag_run.to_dict(), indent=2)
        else:  # HTML
            template = self.template_env.get_template("dag_run_report.html")
            content = template.render(dag_run=dag_run)
        
        # Check size
        warning = self._check_size(content)
        
        return {
            "content": content,
            "format": export_format.value,
            "warning": warning
        }

    def export_json(self, dag_run: DAGRun, output_path: Union[str, Path]) -> Path:
        """
        Export DAGRun results to JSON format.
        
        Args:
            dag_run: DAGRun instance to export
            output_path: Path to save the JSON file
            
        Returns:
            Path to the exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get full DAGRun data
        data = dag_run.to_dict()
        
        # Add execution summary
        data['summary'] = dag_run.get_execution_summary()
        
        # Write to file
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported DAGRun {dag_run.run_id} to JSON: {output_path}")
        return output_path

    def export_html(self, dag_run: DAGRun, output_path: Union[str, Path]) -> Path:
        """
        Export DAGRun results to HTML format.
        
        Args:
            dag_run: DAGRun instance to export
            output_path: Path to save the HTML file
            
        Returns:
            Path to the exported file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get template
        template = self.template_env.get_template('dag_run_report.html')
        
        # Prepare data for template
        data = {
            'dag_run': dag_run.to_dict(),
            'summary': dag_run.get_execution_summary(),
            'steps': [
                {
                    'id': step_id,
                    'data': step.to_dict(),
                    'status_class': self._get_status_class(step.status),
                    'duration': self._format_duration(step.duration_seconds)
                }
                for step_id, step in dag_run.steps.items()
            ],
            'total_duration': self._format_duration(dag_run.duration_seconds),
            'export_time': datetime.utcnow().isoformat()
        }
        
        # Render template
        html_content = template.render(**data)
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"Exported DAGRun {dag_run.run_id} to HTML: {output_path}")
        return output_path

    def _get_status_class(self, status: DAGStepStatus) -> str:
        """Get CSS class for step status."""
        status_classes = {
            DAGStepStatus.SUCCESS: 'success',
            DAGStepStatus.FAILED: 'danger',
            DAGStepStatus.RUNNING: 'info',
            DAGStepStatus.PENDING: 'secondary',
            DAGStepStatus.RETRY: 'warning',
            DAGStepStatus.SKIPPED: 'light',
            DAGStepStatus.CANCELLED: 'dark'
        }
        return status_classes.get(status, 'secondary')

    def _format_duration(self, seconds: Optional[float]) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds is None:
            return 'N/A'
        
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h" 