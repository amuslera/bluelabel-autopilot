"""
CLI command for exporting DAGRun execution results.

This module provides a command-line interface for exporting DAGRun execution
results in various formats (JSON, HTML) for analysis and reporting.
"""

import click
from pathlib import Path
from services.workflow.dag_run_exporter import DAGRunExporter, ExportValidationError
from services.workflow.dag_run_store import DAGRunStore


@click.command()
@click.argument('run_id')
@click.option(
    '--format', '-f',
    default='json',
    help='Export format (json or html)'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output file path (default: {run_id}.{format})'
)
def export_dag_run(run_id: str, format: str, output: str):
    """Export a DAGRun execution result in the specified format.
    
    RUN_ID: ID of the DAGRun to export
    """
    try:
        # Initialize exporter
        dag_store = DAGRunStore()
        exporter = DAGRunExporter(dag_store)
        
        # Export DAGRun
        result = exporter.export(run_id, format)
        
        # Determine output path
        if not output:
            output = f"{run_id}.{format}"
        output_path = Path(output)
        
        # Write content
        output_path.write_text(result['content'])
        
        # Print status
        click.echo(f"Exported DAGRun {run_id} to {output_path}")
        
        # Show warning if any
        if result['warning']:
            click.echo(click.style(result['warning'], fg='yellow'))
            
    except ExportValidationError as e:
        click.echo(click.style(str(e), fg='red'), err=True)
        raise click.Abort()
    except ValueError as e:
        click.echo(click.style(str(e), fg='red'), err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(click.style(f"Export failed: {str(e)}", fg='red'), err=True)
        raise click.Abort() 