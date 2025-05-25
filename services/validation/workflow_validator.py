"""
Workflow YAML validation to prevent security issues.

This module validates workflow YAML files to ensure they are safe to execute
and don't contain malicious content.
"""

import yaml
import re
from typing import Any, Dict, List, Tuple, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class WorkflowValidationError(Exception):
    """Raised when workflow validation fails."""
    pass


class WorkflowValidator:
    """Validates workflow YAML files for security and correctness."""
    
    # Allowed agents (whitelist approach)
    ALLOWED_AGENTS = {
        'ingestion', 'ingestion_agent', 'IngestionAgent',
        'digest', 'digest_agent', 'DigestAgent',
        'email', 'email_agent', 'EmailAgent',
        'whatsapp', 'whatsapp_agent', 'WhatsAppAgent'
    }
    
    # Disallowed patterns in any string value
    DANGEROUS_PATTERNS = [
        # Command injection patterns
        r'`[^`]+`',  # Backticks
        r'\$\([^)]+\)',  # Command substitution
        r'\$\{[^}]+\}',  # Variable expansion
        # Path traversal
        r'\.\.[/\\]',  # Directory traversal
        # Python code injection
        r'__[^_]+__',  # Dunder methods
        r'exec\s*\(',  # exec calls
        r'eval\s*\(',  # eval calls
        r'compile\s*\(',  # compile calls
        r'open\s*\(',  # file operations
        r'import\s+',  # import statements
        # System calls
        r'os\.',  # os module calls
        r'subprocess\.',  # subprocess calls
        r'sys\.',  # sys module calls
    ]
    
    # Maximum limits to prevent resource exhaustion
    MAX_STEPS = 50
    MAX_STRING_LENGTH = 10000
    MAX_WORKFLOW_SIZE = 1_000_000  # 1MB
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern) for pattern in self.DANGEROUS_PATTERNS]
    
    def validate_workflow_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a workflow YAML file.
        
        Args:
            file_path: Path to the workflow YAML file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(file_path)
            
            # Check file exists
            if not path.exists():
                return False, f"Workflow file not found: {file_path}"
            
            # Check file size
            file_size = path.stat().st_size
            if file_size > self.MAX_WORKFLOW_SIZE:
                return False, f"Workflow file too large: {file_size} bytes (max: {self.MAX_WORKFLOW_SIZE})"
            
            # Load and validate YAML
            with open(file_path, 'r') as f:
                workflow_data = yaml.safe_load(f)
            
            return self.validate_workflow(workflow_data)
            
        except yaml.YAMLError as e:
            return False, f"Invalid YAML syntax: {str(e)}"
        except Exception as e:
            return False, f"Error validating workflow: {str(e)}"
    
    def validate_workflow(self, workflow: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate a workflow dictionary.
        
        Args:
            workflow: Workflow configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required fields
            if not isinstance(workflow, dict):
                return False, "Workflow must be a dictionary"
            
            if 'workflow' not in workflow:
                return False, "Missing 'workflow' section"
            
            if 'steps' not in workflow:
                return False, "Missing 'steps' section"
            
            # Validate workflow metadata
            workflow_meta = workflow['workflow']
            if not isinstance(workflow_meta, dict):
                return False, "'workflow' section must be a dictionary"
            
            # Validate required workflow fields
            if 'name' not in workflow_meta:
                return False, "Missing workflow name"
            
            # Validate steps
            steps = workflow['steps']
            if not isinstance(steps, list):
                return False, "'steps' must be a list"
            
            if len(steps) == 0:
                return False, "Workflow must have at least one step"
            
            if len(steps) > self.MAX_STEPS:
                return False, f"Too many steps: {len(steps)} (max: {self.MAX_STEPS})"
            
            # Validate each step
            step_ids = set()
            for i, step in enumerate(steps):
                is_valid, error = self._validate_step(step, i, step_ids)
                if not is_valid:
                    return False, error
            
            # Validate step references
            for i, step in enumerate(steps):
                if 'input_from' in step:
                    ref_step = step['input_from']
                    if ref_step not in step_ids:
                        return False, f"Step {i} references unknown step: {ref_step}"
            
            # Deep validation for dangerous patterns
            is_safe, error = self._validate_values_recursive(workflow)
            if not is_safe:
                return False, error
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    def _validate_step(self, step: Dict[str, Any], index: int, step_ids: set) -> Tuple[bool, Optional[str]]:
        """Validate a single workflow step."""
        if not isinstance(step, dict):
            return False, f"Step {index} must be a dictionary"
        
        # Required fields
        if 'id' not in step:
            return False, f"Step {index} missing 'id' field"
        
        if 'agent' not in step:
            return False, f"Step {index} missing 'agent' field"
        
        # Validate step ID
        step_id = step['id']
        if not isinstance(step_id, str):
            return False, f"Step {index} id must be a string"
        
        if step_id in step_ids:
            return False, f"Duplicate step id: {step_id}"
        
        step_ids.add(step_id)
        
        # Validate agent
        agent = step['agent']
        if not isinstance(agent, str):
            return False, f"Step {index} agent must be a string"
        
        if agent.lower() not in self.ALLOWED_AGENTS:
            return False, f"Step {index} uses disallowed agent: {agent}"
        
        # Must have either input_file or input_from
        if 'input_file' not in step and 'input_from' not in step:
            return False, f"Step {index} must have either 'input_file' or 'input_from'"
        
        return True, None
    
    def _validate_values_recursive(self, obj: Any, path: str = "") -> Tuple[bool, Optional[str]]:
        """Recursively validate all values for dangerous patterns."""
        if isinstance(obj, str):
            # Check string length
            if len(obj) > self.MAX_STRING_LENGTH:
                return False, f"String too long at {path}: {len(obj)} chars"
            
            # Check for dangerous patterns
            for pattern in self.compiled_patterns:
                if pattern.search(obj):
                    return False, f"Dangerous pattern detected at {path}: {pattern.pattern}"
            
        elif isinstance(obj, dict):
            for key, value in obj.items():
                # Validate key
                if isinstance(key, str):
                    is_valid, error = self._validate_values_recursive(key, f"{path}.{key}")
                    if not is_valid:
                        return False, error
                
                # Validate value
                is_valid, error = self._validate_values_recursive(value, f"{path}.{key}")
                if not is_valid:
                    return False, error
                    
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                is_valid, error = self._validate_values_recursive(item, f"{path}[{i}]")
                if not is_valid:
                    return False, error
        
        return True, None


# Convenience function
def validate_workflow_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate a workflow YAML file.
    
    Args:
        file_path: Path to the workflow YAML file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    validator = WorkflowValidator()
    return validator.validate_workflow_file(file_path)