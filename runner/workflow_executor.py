#!/usr/bin/env python3
"""
Workflow Executor for Bluelabel Autopilot
Executes agent workflows defined in YAML files, with proper output storage and error handling.

Usage:
    python runner/workflow_executor.py --workflow workflows/sample_ingestion_digest.yaml
"""

import asyncio
import json
import sys
import yaml
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import models and agents
from interfaces.agent_models import AgentInput, AgentOutput
from agents.digest_agent import DigestAgent
from agents.ingestion_agent import IngestionAgent
from runner.workflow_loader import WorkflowLoader, WorkflowStep


class WorkflowExecutor:
    """Executes agent workflows defined in YAML files."""
    
    def __init__(self, storage_path: Optional[Path] = None, temp_path: Optional[Path] = None):
        """Initialize the workflow executor.
        
        Args:
            storage_path: Path to content storage directory
            temp_path: Path to temporary files directory
        """
        self.storage_path = storage_path or Path("./data/knowledge")
        self.temp_path = temp_path or Path("./data/temp")
        self.workflow_output_path = Path("./data/workflows")
        
        # Initialize agents
        self.agents = {
            'ingestion_agent': IngestionAgent(
                storage_path=self.storage_path,
                temp_path=self.temp_path
            ),
            'digest_agent': DigestAgent()
        }
        
        # Setup logging
        self.logger = logging.getLogger('workflow_executor')
        self.logger.setLevel(logging.INFO)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(console_handler)
    
    def setup_logging(self, log_file: Optional[Path] = None, verbose: bool = False):
        """Setup logging configuration.
        
        Args:
            log_file: Path to log file
            verbose: Enable verbose logging
        """
        if verbose:
            self.logger.setLevel(logging.DEBUG)
        
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            self.logger.addHandler(file_handler)
    
    def _create_workflow_dir(self, workflow_id: str) -> Path:
        """Create directory for workflow outputs.
        
        Args:
            workflow_id: Unique workflow identifier
            
        Returns:
            Path to workflow output directory
        """
        workflow_dir = self.workflow_output_path / workflow_id
        workflow_dir.mkdir(parents=True, exist_ok=True)
        return workflow_dir
    
    def _save_step_output(self, workflow_dir: Path, step_id: str, output: Dict[str, Any]):
        """Save step output to file.
        
        Args:
            workflow_dir: Path to workflow output directory
            step_id: Step identifier
            output: Step output data
        """
        output_file = workflow_dir / f"{step_id}.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
    
    def _load_step_input(self, step: WorkflowStep, step_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Load input data for a workflow step.
        
        Args:
            step: Step definition
            step_outputs: Outputs from previous steps
            
        Returns:
            Input data dictionary
            
        Raises:
            ValueError: If input data is invalid
        """
        # Check for input file
        if step.input_file:
            input_file = Path(step.input_file)
            if not input_file.exists():
                raise ValueError(f"Input file not found: {input_file}")
            
            with open(input_file) as f:
                input_data = json.load(f)
                
            # Special handling for PDF inputs
            if step.agent == 'ingestion_agent' and input_data.get('task_type') == 'pdf':
                pdf_path = input_data.get('content', {}).get('file_path')
                if pdf_path and Path(pdf_path).exists():
                    with open(pdf_path, 'rb') as pdf_file:
                        input_data['content']['pdf_data'] = pdf_file.read()
                        input_data['content']['filename'] = Path(pdf_path).name
                        
            return input_data
        
        # Check for input from previous step
        elif step.input_from:
            source_step = step.input_from
            if source_step not in step_outputs:
                raise ValueError(f"Source step output not found: {source_step}")
            
            # Create input from previous step's output
            source_output = step_outputs[source_step]
            input_data = {
                'task_id': f"workflow-{step.id}",
                'source': 'workflow',
                'content': source_output.get('result', {}),
                'metadata': source_output.get('metadata', {})
            }
            
            # Add any additional configuration
            if step.config:
                input_data['content'].update(step.config)
            
            return input_data
        
        else:
            raise ValueError("Step must specify either input_file or input_from")
    
    async def execute_step(self, step: WorkflowStep, step_outputs: Dict[str, Any]) -> AgentOutput:
        """Execute a single workflow step.
        
        Args:
            step: Step definition
            step_outputs: Outputs from previous steps
            
        Returns:
            Agent output
            
        Raises:
            ValueError: If step execution fails
        """
        try:
            # Load input data
            input_data = self._load_step_input(step, step_outputs)
            
            # Get agent
            if step.agent not in self.agents:
                raise ValueError(f"Unknown agent: {step.agent}")
            agent = self.agents[step.agent]
            
            # Create agent input
            agent_input = AgentInput.model_validate(input_data)
            
            # Initialize agent if needed
            if hasattr(agent, 'initialize') and not getattr(agent, '_initialized', False):
                await agent.initialize()
            
            # Execute step
            self.logger.info(f"Executing step: {step.name} ({step.id})")
            result = await agent.process(agent_input)
            
            # Log result
            if result.status == "success":
                self.logger.info(f"Step completed successfully: {step.name}")
            else:
                self.logger.error(f"Step failed: {step.name} - {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing step {step.id}: {e}")
            raise ValueError(f"Step execution failed: {e}")
    
    async def run_workflow(self, workflow_file: Path) -> Dict[str, Any]:
        """Run a complete workflow.
        
        Args:
            workflow_file: Path to workflow YAML file
            
        Returns:
            Dictionary of step outputs
            
        Raises:
            ValueError: If workflow execution fails
        """
        try:
            # Load and validate workflow
            loader = WorkflowLoader(workflow_file)
            workflow_data = loader.load()
            steps = loader.parse_steps()
            
            # Get workflow info
            workflow_info = workflow_data['workflow']
            workflow_id = str(uuid.uuid4())
            
            # Create workflow output directory
            workflow_dir = self._create_workflow_dir(workflow_id)
            
            # Save workflow definition
            with open(workflow_dir / "workflow.yaml", 'w') as f:
                yaml.dump(workflow_data, f)
            
            self.logger.info(f"Running workflow: {workflow_info['name']} (v{workflow_info['version']})")
            self.logger.info(f"Description: {workflow_info['description']}")
            self.logger.info(f"Workflow ID: {workflow_id}")
            
            # Get execution order
            execution_order = loader.get_execution_order()
            
            # Execute steps in order
            step_outputs = {}
            for step_id in execution_order:
                step = loader.step_map[step_id]
                result = await self.execute_step(step, step_outputs)
                
                # Save step output
                output_data = {
                    'status': result.status,
                    'result': result.result,
                    'metadata': result.metadata,
                    'error': result.error,
                    'duration_ms': result.duration_ms,
                    'timestamp': datetime.utcnow().isoformat()
                }
                self._save_step_output(workflow_dir, step_id, output_data)
                step_outputs[step_id] = output_data
            
            # Print summary
            self.logger.info("\nWorkflow Execution Summary:")
            self.logger.info("-------------------------")
            for step_id in execution_order:
                step = loader.step_map[step_id]
                output = step_outputs[step_id]
                self.logger.info(f"\nStep: {step.name} ({step.id})")
                self.logger.info(f"Status: {output['status']}")
                self.logger.info(f"Duration: {output['duration_ms']}ms")
                
                if output['status'] == "success":
                    if step.outputs:
                        for output_field in step.outputs:
                            if output_field in output['result']:
                                self.logger.info(f"{output_field}: {output['result'][output_field]}")
                else:
                    self.logger.error(f"Error: {output['error']}")
            
            # Save workflow summary
            summary = {
                'workflow_id': workflow_id,
                'name': workflow_info['name'],
                'version': workflow_info['version'],
                'description': workflow_info['description'],
                'status': 'success' if all(o['status'] == 'success' for o in step_outputs.values()) else 'failed',
                'steps': {
                    step_id: {
                        'name': loader.step_map[step_id].name,
                        'status': output['status'],
                        'duration_ms': output['duration_ms']
                    }
                    for step_id, output in step_outputs.items()
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            with open(workflow_dir / "summary.json", 'w') as f:
                json.dump(summary, f, indent=2)
            
            return step_outputs
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise ValueError(f"Workflow execution failed: {e}")


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
    
    # Create executor
    executor = WorkflowExecutor(
        storage_path=args.storage_path,
        temp_path=args.temp_path
    )
    
    # Setup logging
    executor.setup_logging(
        log_file=args.log_file,
        verbose=args.verbose
    )
    
    # Run workflow
    try:
        asyncio.run(executor.run_workflow(args.workflow_file))
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nWorkflow execution interrupted")
        sys.exit(1)


if __name__ == '__main__':
    main() 