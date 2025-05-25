#!/usr/bin/env python3
"""
CLI command for running and managing DAG executions.
Supports running new DAGs, checking status, and retrying failed steps.
"""

import argparse
import sys
from typing import Optional
from pathlib import Path

from ..utils.dag_run_printer import print_dag_status
from core.workflow_engine import WorkflowEngine
from interfaces.run_models import DAGRun, DAGRunStatus

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run and manage DAG executions")
    
    # Main command group
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("workflow", nargs="?", help="Path to workflow YAML file")
    group.add_argument("--status", metavar="RUN_ID", help="Check status of a DAG run")
    group.add_argument("--retry", metavar="RUN_ID", help="Retry failed steps in a DAG run")
    
    # Optional arguments
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    parser.add_argument("--output-dir", help="Directory for workflow outputs")
    
    return parser.parse_args()

def get_dag_run(run_id: str) -> Optional[DAGRun]:
    """Load DAG run from tracker."""
    # TODO: Implement actual tracker integration
    # For now, return a mock DAG run
    return DAGRun(
        run_id=run_id,
        workflow_id="test_workflow",
        status=DAGRunStatus.RUNNING,
        steps=[
            {"id": "step1", "status": "completed", "retries": 0},
            {"id": "step2", "status": "failed", "retries": 1}
        ]
    )

def run_dag(workflow_path: str, output_dir: Optional[str] = None) -> None:
    """Execute a new DAG run."""
    engine = WorkflowEngine()
    run_id = engine.execute_workflow(workflow_path, output_dir)
    print(f"DAG execution started with run_id: {run_id}")

def check_status(run_id: str, verbose: bool = False) -> None:
    """Check status of a DAG run."""
    dag_run = get_dag_run(run_id)
    if not dag_run:
        print(f"Error: No DAG run found with ID {run_id}")
        sys.exit(1)
    
    print_dag_status(dag_run, verbose)

def retry_failed(run_id: str) -> None:
    """Retry failed steps in a DAG run."""
    dag_run = get_dag_run(run_id)
    if not dag_run:
        print(f"Error: No DAG run found with ID {run_id}")
        sys.exit(1)
    
    engine = WorkflowEngine()
    new_run_id = engine.retry_failed_steps(dag_run)
    print(f"Retry started with new run_id: {new_run_id}")

def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    try:
        if args.status:
            check_status(args.status, args.verbose)
        elif args.retry:
            retry_failed(args.retry)
        else:
            run_dag(args.workflow, args.output_dir)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 