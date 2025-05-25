"""
Utility functions for formatting and printing DAG run status information.
"""

from typing import List, Dict
from datetime import datetime
from tabulate import tabulate

from interfaces.run_models import DAGRun, DAGRunStatus

def format_step_status(step: Dict) -> List[str]:
    """Format a single step's status information."""
    return [
        step["id"],
        step["status"].upper(),
        str(step.get("retries", 0)),
        step.get("started_at", "N/A"),
        step.get("completed_at", "N/A")
    ]

def print_dag_status(dag_run: DAGRun, verbose: bool = False) -> None:
    """Print DAG run status in a formatted table."""
    # Print header information
    print(f"\nDAG Run: {dag_run.run_id}")
    print(f"Workflow: {dag_run.workflow_id}")
    print(f"Status: {dag_run.status.value}")
    print(f"Started: {dag_run.started_at}")
    
    if dag_run.completed_at:
        print(f"Completed: {dag_run.completed_at}")
    
    # Print step status table
    headers = ["Step ID", "Status", "Retries", "Started", "Completed"]
    rows = [format_step_status(step) for step in dag_run.steps]
    
    print("\nStep Status:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Print additional information in verbose mode
    if verbose:
        print("\nAdditional Information:")
        print(f"Total Steps: {len(dag_run.steps)}")
        print(f"Failed Steps: {sum(1 for s in dag_run.steps if s['status'] == 'failed')}")
        print(f"Completed Steps: {sum(1 for s in dag_run.steps if s['status'] == 'completed')}")
        
        if dag_run.error:
            print(f"\nError: {dag_run.error}") 