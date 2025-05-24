#!/usr/bin/env python3
"""
Workflow Loader for Bluelabel Autopilot
Parses YAML workflow definitions and validates the DAG structure.

Usage:
    python runner/workflow_loader.py --workflow workflows/sample_ingestion_digest.yaml
"""

import yaml
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class WorkflowStep:
    """Represents a single step in the workflow."""
    
    def __init__(self, step_data: Dict[str, Any]):
        self.id = step_data.get('id')
        self.name = step_data.get('name', self.id)
        self.agent = step_data.get('agent')
        self.input_file = step_data.get('input_file')
        self.input_from = step_data.get('input_from')
        self.description = step_data.get('description', '')
        self.config = step_data.get('config', {})
        self.outputs = step_data.get('outputs', [])
        
        # Validate required fields
        if not self.id:
            raise ValueError("Step must have an 'id' field")
        if not self.agent:
            raise ValueError(f"Step '{self.id}' must have an 'agent' field")
        if not self.input_file and not self.input_from:
            raise ValueError(f"Step '{self.id}' must have either 'input_file' or 'input_from'")
            

class WorkflowLoader:
    """Loads and validates workflow definitions from YAML files."""
    
    def __init__(self, workflow_path: Path):
        """Initialize the workflow loader.
        
        Args:
            workflow_path: Path to the YAML workflow file
        """
        self.workflow_path = workflow_path
        self.workflow_data = None
        self.steps = []
        self.step_map = {}
        
    def load(self) -> Dict[str, Any]:
        """Load the workflow from YAML file.
        
        Returns:
            The loaded workflow data
            
        Raises:
            FileNotFoundError: If the workflow file doesn't exist
            yaml.YAMLError: If the YAML is invalid
        """
        if not self.workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {self.workflow_path}")
            
        with open(self.workflow_path, 'r') as f:
            self.workflow_data = yaml.safe_load(f)
            
        if not self.workflow_data:
            raise ValueError("Empty workflow file")
            
        if 'workflow' not in self.workflow_data:
            raise ValueError("Workflow file must contain a 'workflow' section")
            
        if 'steps' not in self.workflow_data:
            raise ValueError("Workflow file must contain a 'steps' section")
            
        return self.workflow_data
        
    def parse_steps(self) -> List[WorkflowStep]:
        """Parse and validate workflow steps.
        
        Returns:
            List of WorkflowStep objects
            
        Raises:
            ValueError: If step validation fails
        """
        if not self.workflow_data:
            raise ValueError("No workflow data loaded. Call load() first.")
            
        steps_data = self.workflow_data.get('steps', [])
        if not steps_data:
            raise ValueError("Workflow must contain at least one step")
            
        # Parse all steps
        for step_data in steps_data:
            step = WorkflowStep(step_data)
            self.steps.append(step)
            self.step_map[step.id] = step
            
        # Validate references
        for step in self.steps:
            if step.input_from:
                if step.input_from not in self.step_map:
                    raise ValueError(
                        f"Step '{step.id}' references unknown step '{step.input_from}'"
                    )
                    
                # Check for circular dependencies
                if self._has_circular_dependency(step.id):
                    raise ValueError(
                        f"Circular dependency detected starting from step '{step.id}'"
                    )
                    
        return self.steps
        
    def _has_circular_dependency(self, start_id: str, visited: Optional[set] = None) -> bool:
        """Check if there's a circular dependency starting from the given step.
        
        Args:
            start_id: The step ID to start checking from
            visited: Set of already visited step IDs
            
        Returns:
            True if circular dependency exists, False otherwise
        """
        if visited is None:
            visited = set()
            
        if start_id in visited:
            return True
            
        visited.add(start_id)
        
        step = self.step_map.get(start_id)
        if step and step.input_from:
            return self._has_circular_dependency(step.input_from, visited.copy())
            
        return False
        
    def get_execution_order(self) -> List[str]:
        """Get the order in which steps should be executed.
        
        Returns:
            List of step IDs in execution order
        """
        # Simple topological sort
        executed = set()
        order = []
        
        while len(executed) < len(self.steps):
            for step in self.steps:
                if step.id in executed:
                    continue
                    
                # Check if all dependencies are satisfied
                if not step.input_from or step.input_from in executed:
                    executed.add(step.id)
                    order.append(step.id)
                    break
            else:
                # No progress made - shouldn't happen if validation passed
                raise RuntimeError("Unable to determine execution order")
                
        return order
        
    def print_workflow(self):
        """Print the workflow structure in a readable format."""
        if not self.workflow_data:
            print("No workflow loaded")
            return
            
        workflow_info = self.workflow_data.get('workflow', {})
        print("\n=== Workflow Information ===")
        print(f"Name: {workflow_info.get('name', 'Unnamed')}")
        print(f"Description: {workflow_info.get('description', 'No description')}")
        print(f"Version: {workflow_info.get('version', 'No version')}")
        
        if not self.steps:
            print("\nNo steps parsed")
            return
            
        print(f"\n=== Workflow Steps ({len(self.steps)}) ===")
        
        execution_order = self.get_execution_order()
        
        for i, step_id in enumerate(execution_order):
            step = self.step_map[step_id]
            print(f"\nStep {i+1}: {step.name} (id: {step.id})")
            print(f"  Agent: {step.agent}")
            
            if step.input_file:
                print(f"  Input: {step.input_file}")
            elif step.input_from:
                print(f"  Input from: {step.input_from}")
                
            if step.description:
                print(f"  Description: {step.description}")
                
            if step.config:
                print(f"  Config: {step.config}")
                
            if step.outputs:
                print(f"  Outputs: {', '.join(step.outputs)}")
                
        # Print metadata if available
        metadata = self.workflow_data.get('metadata', {})
        if metadata:
            print("\n=== Metadata ===")
            for key, value in metadata.items():
                print(f"{key}: {value}")


def main():
    """Main entry point for the workflow loader CLI."""
    parser = argparse.ArgumentParser(
        description='Load and validate workflow YAML files'
    )
    parser.add_argument(
        '--workflow',
        type=Path,
        required=True,
        help='Path to the workflow YAML file'
    )
    
    args = parser.parse_args()
    
    try:
        # Create loader
        loader = WorkflowLoader(args.workflow)
        
        # Load workflow
        print(f"Loading workflow from: {args.workflow}")
        loader.load()
        
        # Parse and validate steps
        print("Parsing and validating steps...")
        loader.parse_steps()
        
        # Print the workflow
        loader.print_workflow()
        
        print("\n✅ Workflow loaded and validated successfully!")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except (ValueError, yaml.YAMLError) as e:
        print(f"❌ Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()