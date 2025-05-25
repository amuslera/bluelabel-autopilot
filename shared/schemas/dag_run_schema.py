"""
JSONSchema definitions for DAGRun serialization and validation.

This module provides schema definitions for validating DAGRun data structures
during serialization and deserialization.
"""

from typing import Dict, Any

# JSONSchema for DAGStepState
DAG_STEP_STATE_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["step_id", "status"],
    "properties": {
        "step_id": {
            "type": "string",
            "description": "Unique identifier for the step"
        },
        "status": {
            "type": "string",
            "enum": ["pending", "running", "success", "failed", "retry", "skipped", "cancelled"],
            "description": "Current execution status of the step"
        },
        "start_time": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "ISO format timestamp when step started"
        },
        "end_time": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "ISO format timestamp when step completed"
        },
        "retry_count": {
            "type": "integer",
            "minimum": 0,
            "default": 0,
            "description": "Number of retry attempts"
        },
        "max_retries": {
            "type": "integer",
            "minimum": 0,
            "default": 3,
            "description": "Maximum number of retries allowed"
        },
        "error": {
            "type": ["string", "null"],
            "description": "Error message if step failed"
        },
        "result": {
            "type": ["object", "null"],
            "description": "Step execution result data"
        },
        "metadata": {
            "type": "object",
            "default": {},
            "description": "Additional step metadata"
        },
        "duration_seconds": {
            "type": ["number", "null"],
            "minimum": 0,
            "description": "Execution duration in seconds"
        }
    }
}

# JSONSchema for DAGRun
DAG_RUN_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["dag_id", "run_id", "status"],
    "properties": {
        "dag_id": {
            "type": "string",
            "description": "Identifier of the DAG being executed"
        },
        "run_id": {
            "type": "string",
            "format": "uuid",
            "description": "Unique identifier for this run"
        },
        "status": {
            "type": "string",
            "enum": ["created", "running", "success", "failed", "retry", "cancelled", "partial_success"],
            "description": "Overall execution status"
        },
        "steps": {
            "type": "object",
            "patternProperties": {
                "^.*$": DAG_STEP_STATE_SCHEMA
            },
            "default": {},
            "description": "Map of step IDs to step states"
        },
        "start_time": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "ISO format timestamp when run started"
        },
        "end_time": {
            "type": ["string", "null"],
            "format": "date-time",
            "description": "ISO format timestamp when run completed"
        },
        "total_retries": {
            "type": "integer",
            "minimum": 0,
            "default": 0,
            "description": "Total number of retries across all steps"
        },
        "error": {
            "type": ["string", "null"],
            "description": "Overall error message if run failed"
        },
        "metadata": {
            "type": "object",
            "default": {},
            "description": "Additional run metadata"
        },
        "duration_seconds": {
            "type": ["number", "null"],
            "minimum": 0,
            "description": "Total execution duration in seconds"
        }
    }
}

# JSONSchema for DAGRun summary (used in listings)
DAG_RUN_SUMMARY_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["run_id", "dag_id", "status"],
    "properties": {
        "run_id": {
            "type": "string",
            "format": "uuid"
        },
        "dag_id": {
            "type": "string"
        },
        "status": {
            "type": "string",
            "enum": ["created", "running", "success", "failed", "retry", "cancelled", "partial_success"]
        },
        "created_at": {
            "type": ["string", "null"],
            "format": "date-time"
        },
        "updated_at": {
            "type": ["string", "null"],
            "format": "date-time"
        }
    }
}

# JSONSchema for execution statistics
DAG_STATISTICS_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["total_runs", "by_status", "success_rate"],
    "properties": {
        "total_runs": {
            "type": "integer",
            "minimum": 0
        },
        "by_status": {
            "type": "object",
            "patternProperties": {
                "^(created|running|success|failed|retry|cancelled|partial_success)$": {
                    "type": "integer",
                    "minimum": 0
                }
            }
        },
        "success_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 100
        }
    }
}


def validate_dag_run(data: Dict[str, Any]) -> bool:
    """
    Validate DAGRun data against schema.
    
    Args:
        data: Dictionary to validate
        
    Returns:
        True if valid, raises jsonschema.ValidationError if invalid
    """
    try:
        import jsonschema
        jsonschema.validate(data, DAG_RUN_SCHEMA)
        return True
    except ImportError:
        # If jsonschema not installed, skip validation
        return True


def validate_dag_step_state(data: Dict[str, Any]) -> bool:
    """
    Validate DAGStepState data against schema.
    
    Args:
        data: Dictionary to validate
        
    Returns:
        True if valid, raises jsonschema.ValidationError if invalid
    """
    try:
        import jsonschema
        jsonschema.validate(data, DAG_STEP_STATE_SCHEMA)
        return True
    except ImportError:
        # If jsonschema not installed, skip validation
        return True