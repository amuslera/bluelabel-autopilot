#!/usr/bin/env python3
"""
Workflow Executor CLI for Bluelabel Autopilot
CLI wrapper around the core workflow engine service.

Usage:
    python runner/workflow_executor.py --workflow workflows/sample_ingestion_digest.yaml
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from typing import Optional
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the workflow engine service
from core.workflow_engine import run_workflow
from interfaces.run_models import WorkflowStatus


# Setup logging
def setup_logging(log_file: Optional[Path] = None, verbose: bool = False) -> logging.Logger:
    """Setup logging configuration.
    
    Args:
        log_file: Path to log file
        verbose: Enable verbose logging
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger('workflow_executor_cli')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    # Remove existing handlers
    logger.handlers = []
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)
    
    return logger


async def run_workflow_cli(workflow_file: Path, storage_path: Optional[Path] = None, 
                          temp_path: Optional[Path] = None, logger: Optional[logging.Logger] = None) -> None:
    """Run workflow with CLI output formatting.
    
    Args:
        workflow_file: Path to workflow YAML file
        storage_path: Path to content storage directory
        temp_path: Path to temporary files directory
        logger: Logger instance
    """
    if not logger:
        logger = logging.getLogger('workflow_executor_cli')
    
    try:
        # Run workflow using the service
        logger.info(f"Starting workflow execution: {workflow_file}")
        
        result = await run_workflow(
            path=str(workflow_file),
            persist=True,
            storage_path=str(storage_path) if storage_path else None,
            temp_path=str(temp_path) if temp_path else None
        )
        
        # Print execution summary
        logger.info(f"\nWorkflow: {result.workflow_name} (v{result.workflow_version})")
        logger.info(f"Run ID: {result.run_id}")
        logger.info(f"Status: {result.status.value}")
        
        if result.started_at and result.completed_at:
            duration = (result.completed_at - result.started_at).total_seconds()
            logger.info(f"Duration: {duration:.2f}s")
        
        # Print step details
        logger.info("\nStep Results:")
        logger.info("-------------")
        for step_id, step_result in result.step_outputs.items():
            logger.info(f"\nStep: {step_result.step_name} ({step_id})")
            logger.info(f"  Status: {step_result.status}")
            logger.info(f"  Duration: {step_result.duration_ms}ms")
            
            if step_result.status == "failed" and step_result.error:
                logger.error(f"  Error: {step_result.error}")
            elif step_result.status == "success" and step_result.result:
                # Show key outputs if specified
                for key, value in step_result.result.items():
                    if isinstance(value, (str, int, float, bool)):
                        logger.info(f"  {key}: {value}")
        
        # Overall status
        if result.status == WorkflowStatus.SUCCESS:
            logger.info("\nWorkflow completed successfully!")
        else:
            logger.error(f"\nWorkflow failed with status: {result.status.value}")
            if result.errors:
                for error in result.errors:
                    logger.error(f"Error: {error}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"\nWorkflow execution failed: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Bluelabel Autopilot Workflow Executor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example Workflow YAML:
  workflow:
    name: "Sample Workflow"
    description: "Process content through multiple agents"
    version: "1.0.0"
  
  steps:
    - id: step1
      name: "First Step"
      agent: ingestion_agent
      input_file: tests/sample_input.json
    
    - id: step2
      name: "Second Step"
      agent: digest_agent
      input_from: step1
      config:
        format: markdown
"""
    )
    
    parser.add_argument('workflow_file', type=Path,
                       help='Path to workflow YAML file')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--log-file', type=Path,
                       help='Path to log file')
    parser.add_argument('--storage-path', type=Path, default='./data/knowledge',
                       help='Path to content storage directory (default: ./data/knowledge)')
    parser.add_argument('--temp-path', type=Path, default='./data/temp',
                       help='Path to temporary files directory (default: ./data/temp)')
    
    args = parser.parse_args()
    
    # Validate workflow file exists
    if not args.workflow_file.exists():
        print(f"Error: Workflow file not found: {args.workflow_file}")
        sys.exit(1)
    
    # Setup logging
    logger = setup_logging(
        log_file=args.log_file,
        verbose=args.verbose
    )
    
    # Run workflow
    try:
        asyncio.run(run_workflow_cli(
            workflow_file=args.workflow_file,
            storage_path=args.storage_path,
            temp_path=args.temp_path,
            logger=logger
        ))
    except KeyboardInterrupt:
        print("\nWorkflow execution interrupted")
        sys.exit(1)


if __name__ == '__main__':
    main() 