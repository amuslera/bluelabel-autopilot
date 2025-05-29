# Outbox Schema Standard

## Overview

This document defines the standardized schema for `outbox.json` files used across all agents in the BlueLabelAutopilot system. The schema supports both active task tracking and historical record keeping.

## Schema Definition

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["agent_id", "agent_name", "agent_type", "version", "tasks", "history"],
  "properties": {
    "agent_id": {
      "type": "string",
      "description": "Unique identifier for the agent (e.g., CA, CB, CC, WA, ARCH)"
    },
    "agent_name": {
      "type": "string",
      "description": "Human-readable name of the agent"
    },
    "agent_type": {
      "type": "string",
      "enum": ["ai", "human", "hybrid"],
      "description": "Type of agent"
    },
    "version": {
      "type": "string",
      "description": "Schema version (current: 1.0.0)"
    },
    "expertise": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of agent capabilities and expertise areas"
    },
    "tasks": {
      "type": "array",
      "description": "Active and pending tasks",
      "items": {
        "$ref": "#/definitions/task"
      }
    },
    "history": {
      "type": "array",
      "description": "Completed tasks and historical records",
      "items": {
        "$ref": "#/definitions/historyEntry"
      }
    },
    "metadata": {
      "type": "object",
      "description": "Additional agent-specific metadata",
      "properties": {
        "last_updated": {
          "type": "string",
          "format": "date-time"
        },
        "total_tasks_completed": {
          "type": "integer"
        }
      }
    }
  },
  "definitions": {
    "task": {
      "type": "object",
      "required": ["task_id", "title", "status", "priority", "created_at"],
      "properties": {
        "task_id": {
          "type": "string",
          "description": "Unique task identifier"
        },
        "title": {
          "type": "string",
          "description": "Brief task title"
        },
        "description": {
          "type": "string",
          "description": "Detailed task description"
        },
        "status": {
          "type": "string",
          "enum": ["pending", "in_progress", "completed", "failed", "blocked"],
          "description": "Current task status"
        },
        "priority": {
          "type": "string",
          "enum": ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
          "description": "Task priority level"
        },
        "created_at": {
          "type": "string",
          "format": "date-time",
          "description": "Task creation timestamp"
        },
        "started_at": {
          "type": "string",
          "format": "date-time",
          "description": "Task start timestamp"
        },
        "completed_at": {
          "type": "string",
          "format": "date-time",
          "description": "Task completion timestamp"
        },
        "estimated_hours": {
          "type": "number",
          "description": "Estimated hours to complete"
        },
        "actual_hours": {
          "type": "number",
          "description": "Actual hours taken"
        },
        "context": {
          "type": "object",
          "description": "Additional context for the task"
        },
        "deliverables": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Expected deliverables"
        },
        "dependencies": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Task dependencies (other task IDs)"
        },
        "signals_when_done": {
          "type": "string",
          "description": "Completion indicators"
        }
      }
    },
    "historyEntry": {
      "type": "object",
      "required": ["task_id", "timestamp", "status"],
      "properties": {
        "task_id": {
          "type": "string",
          "description": "Task identifier"
        },
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "Entry timestamp"
        },
        "status": {
          "type": "string",
          "description": "Final task status"
        },
        "summary": {
          "type": "string",
          "description": "Brief summary of work completed"
        },
        "report": {
          "type": "string",
          "description": "Detailed completion report"
        },
        "files": {
          "type": "object",
          "properties": {
            "created": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "modified": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        },
        "metrics": {
          "type": "object",
          "description": "Performance metrics for the completed task"
        }
      }
    }
  }
}
```

## Example Outbox File

```json
{
  "agent_id": "CB",
  "agent_name": "Claude Code Backend",
  "agent_type": "ai",
  "version": "1.0.0",
  "expertise": ["python", "backend", "api", "system_design"],
  "tasks": [
    {
      "task_id": "TASK-165B",
      "title": "Outbox format standardization",
      "description": "Standardize the outbox.json format across all agents",
      "status": "in_progress",
      "priority": "HIGH",
      "created_at": "2025-05-29T10:00:00Z",
      "started_at": "2025-05-29T12:30:00Z",
      "estimated_hours": 2,
      "context": {
        "problem": "Inconsistent outbox formats",
        "solution": "Create standard schema"
      },
      "deliverables": [
        "Standard schema definition",
        "Validation script",
        "Updated outbox files",
        "Documentation"
      ],
      "dependencies": [],
      "signals_when_done": "All outbox files follow standard format"
    }
  ],
  "history": [
    {
      "task_id": "TASK-164G",
      "timestamp": "2025-05-28T18:00:00Z",
      "status": "completed",
      "summary": "Implemented agent autopilot system",
      "files": {
        "created": ["orchestration/agent_autopilot.py"],
        "modified": ["orchestration/routing_rules.yaml"]
      }
    }
  ],
  "metadata": {
    "last_updated": "2025-05-29T12:30:00Z",
    "total_tasks_completed": 15
  }
}
```

## Migration Guide

### From Simple Format (BLUE)
1. Add required fields: `agent_id`, `agent_name`, `agent_type`, `version`
2. Convert `messages` to `tasks` array
3. Add empty `history` array

### From Task-Based Format (ARCH, CB, CC, WA)
1. Add `agent_type` and `version` fields
2. Add empty `history` array
3. Ensure all task fields match the schema

### From Historical Format (CA)
1. Add standard header fields
2. Move historical entries to `history` array
3. Create empty `tasks` array for active tasks

## Validation

Use the provided validation script to ensure outbox files conform to this schema:

```bash
python orchestration/validate_outbox.py <path_to_outbox.json>
```

## Version History

- **1.0.0** (2025-05-29): Initial standardized schema