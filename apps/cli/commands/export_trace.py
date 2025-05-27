"""
CLI command for exporting DAG run traces.
"""

import click
import sys
from pathlib import Path

from services.workflow.dag_trace_exporter import DAGTraceExporter

@click.command()
@click.argument('run_id')
@click.option('--format', '-f', default='html', help='Output format (html)')
@click.option('--output', '-o', help='Output file path (default: stdout)')
def export_trace(run_id: str, format: str, output: str):
    """
    Export a DAG run trace in the specified format.
    
    RUN_ID: ID of the DAG run to export
    """
    try:
        # Create exporter
        exporter = DAGTraceExporter()
        
        # Export trace
        content = exporter.export_trace(run_id, format)
        
        # Write output
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content)
            click.echo(f"Trace exported to: {output_path}")
        else:
            click.echo(content)
            
    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1) 