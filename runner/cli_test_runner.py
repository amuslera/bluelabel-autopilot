#!/usr/bin/env python3
"""
CLI Test Runner for Bluelabel Autopilot Workflows
A command-line tool for executing and testing agent workflows defined in YAML files.

Examples:
    # Run a workflow from a YAML file
    python cli_test_runner.py run workflows/sample_ingestion_digest.yaml

    # Run with verbose logging
    python cli_test_runner.py run workflows/sample_ingestion_digest.yaml --verbose

    # Run with custom log file
    python cli_test_runner.py run workflows/sample_ingestion_digest.yaml --log-file test_run.log
"""

import asyncio
import json
import sys
import yaml
import logging
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


class WorkflowTestRunner:
    """Test runner for executing agent workflows defined in YAML files."""
    
    def __init__(self, storage_path: Optional[Path] = None, temp_path: Optional[Path] = None):
        """Initialize the test runner.
        
        Args:
            storage_path: Path to content storage directory
            temp_path: Path to temporary files directory
        """
        self.storage_path = storage_path or Path("./data/knowledge")
        self.temp_path = temp_path or Path("./data/temp")
        
        # Initialize agents
        self.agents = {
            'ingestion_agent': IngestionAgent(
                storage_path=self.storage_path,
                temp_path=self.temp_path
            ),
            'digest_agent': DigestAgent()
        }
        
        # Setup logging
        self.logger = logging.getLogger('workflow_test_runner')
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
    
    def load_workflow(self, workflow_file: Path) -> Dict[str, Any]:
        """Load and validate workflow definition from YAML file.
        
        Args:
            workflow_file: Path to workflow YAML file
            
        Returns:
            Workflow definition dictionary
            
        Raises:
            ValueError: If workflow file is invalid
        """
        try:
            with open(workflow_file) as f:
                workflow = yaml.safe_load(f)
            
            # Validate workflow structure
            required_fields = ['workflow', 'steps']
            for field in required_fields:
                if field not in workflow:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate workflow metadata
            workflow_info = workflow['workflow']
            for field in ['name', 'description', 'version']:
                if field not in workflow_info:
                    raise ValueError(f"Missing required workflow field: {field}")
            
            # Validate steps
            for step in workflow['steps']:
                required_step_fields = ['id', 'name', 'agent']
                for field in required_step_fields:
                    if field not in step:
                        raise ValueError(f"Missing required step field: {field}")
                
                if step['agent'] not in self.agents:
                    raise ValueError(f"Unknown agent: {step['agent']}")
            
            return workflow
            
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file: {e}")
        except FileNotFoundError:
            raise ValueError(f"Workflow file not found: {workflow_file}")
    
    def load_step_input(self, step: Dict[str, Any], step_outputs: Dict[str, Any]) -> Dict[str, Any]:
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
        if 'input_file' in step:
            input_file = Path(step['input_file'])
            if not input_file.exists():
                raise ValueError(f"Input file not found: {input_file}")
            
            with open(input_file) as f:
                return json.load(f)
        
        # Check for input from previous step
        elif 'input_from' in step:
            source_step = step['input_from']
            if source_step not in step_outputs:
                raise ValueError(f"Source step output not found: {source_step}")
            
            # Create input from previous step's output
            source_output = step_outputs[source_step]
            input_data = {
                'task_id': f"workflow-{step['id']}",
                'source': 'workflow',
                'content': source_output.get('result', {}),
                'metadata': source_output.get('metadata', {})
            }
            
            # Add any additional configuration
            if 'config' in step:
                input_data['content'].update(step['config'])
            
            return input_data
        
        else:
            raise ValueError("Step must specify either input_file or input_from")
    
    async def execute_step(self, step: Dict[str, Any], step_outputs: Dict[str, Any]) -> AgentOutput:
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
            input_data = self.load_step_input(step, step_outputs)
            
            # Get agent
            agent = self.agents[step['agent']]
            
            # Create agent input
            agent_input = AgentInput.parse_obj(input_data)
            
            # Execute step
            self.logger.info(f"Executing step: {step['name']} ({step['id']})")
            result = await agent.process(agent_input)
            
            # Log result
            if result.status == "success":
                self.logger.info(f"Step completed successfully: {step['name']}")
            else:
                self.logger.error(f"Step failed: {step['name']} - {result.error}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing step {step['id']}: {e}")
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
            # Load workflow
            workflow = self.load_workflow(workflow_file)
            workflow_info = workflow['workflow']
            
            self.logger.info(f"Running workflow: {workflow_info['name']} (v{workflow_info['version']})")
            self.logger.info(f"Description: {workflow_info['description']}")
            
            # Execute steps
            step_outputs = {}
            for step in workflow['steps']:
                result = await self.execute_step(step, step_outputs)
                step_outputs[step['id']] = {
                    'status': result.status,
                    'result': result.result,
                    'metadata': result.metadata,
                    'error': result.error,
                    'duration_ms': result.duration_ms
                }
            
            # Print summary
            self.logger.info("\nWorkflow Execution Summary:")
            self.logger.info("-------------------------")
            for step in workflow['steps']:
                output = step_outputs[step['id']]
                self.logger.info(f"\nStep: {step['name']} ({step['id']})")
                self.logger.info(f"Status: {output['status']}")
                self.logger.info(f"Duration: {output['duration_ms']}ms")
                
                if output['status'] == "success":
                    if 'outputs' in step:
                        for output_field in step['outputs']:
                            if output_field in output['result']:
                                self.logger.info(f"{output_field}: {output['result'][output_field]}")
                else:
                    self.logger.error(f"Error: {output['error']}")
            
            return step_outputs
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise ValueError(f"Workflow execution failed: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Bluelabel Autopilot Workflow Test Runner',
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
    
    # Create test runner
    runner = WorkflowTestRunner(
        storage_path=args.storage_path,
        temp_path=args.temp_path
    )
    
    # Setup logging
    runner.setup_logging(
        log_file=args.log_file,
        verbose=args.verbose
    )
    
    # Run workflow
    try:
        asyncio.run(runner.run_workflow(args.workflow_file))
    except ValueError as e:
        print(f"\nError: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nWorkflow execution interrupted")
        sys.exit(1)


if __name__ == '__main__':
    main() 