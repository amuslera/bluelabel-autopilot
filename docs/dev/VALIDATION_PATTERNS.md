# Validation Patterns

This document outlines the current validation patterns used in the Bluelabel Autopilot system, focusing on WhatsApp inputs and YAML workflow definitions.

## WhatsApp Input Validation

The WhatsApp adapter enforces the following validation rules for incoming webhook payloads:

### Required Fields

- `type`: Must be one of: `url`, `pdf`
- `value`: Must be a non-empty string

### Example Valid Payloads

```json
{
  "type": "url",
  "value": "https://example.com"
}

{
  "type": "pdf",
  "value": "/path/to/document.pdf"
}
```

### Common Validation Errors

1. **Missing Required Fields**
   ```json
   {
     "type": "url"
     // Missing 'value' field
   }
   ```
   Error: `"Missing required fields: 'type' and 'value' are required"`

2. **Invalid Type**
   ```json
   {
     "type": "invalid_type",
     "value": "some value"
   }
   ```
   Error: `"No workflow found for type: invalid_type"`

3. **Empty Value**
   ```json
   {
     "type": "url",
     "value": ""
   }
   ```
   Error: `"Missing required fields: 'type' and 'value' are required"`

## YAML Workflow Validation

Workflow YAML files must adhere to the following structure:

### Required Top-Level Fields

- `workflow`: Contains workflow metadata
  - `name`: Workflow identifier (string)
  - `description`: Brief description (string)
  - `version`: Version string (semver recommended)

- `input`: Defines input parameters
  - Each parameter must have:
    - `type`: Data type (string, number, boolean, etc.)
    - `required`: Boolean indicating if the parameter is required
    - `description`: Brief description of the parameter

- `tasks`: List of tasks to execute
  - Each task must have:
    - `name`: Unique identifier for the task
    - `agent`: The agent responsible for the task
    - `type`: Task type
    - `parameters`: Task-specific parameters
    - `output`: Variable name to store the task's output

### Example Validation Rules

1. **Required Fields**
   ```yaml
   # Invalid - missing required 'workflow' section
   input:
     url:
       type: string
   ```

2. **Task Validation**
   ```yaml
   tasks:
     - name: "ingest_url"
       # Missing required 'agent' field
       type: "url"
   ```

3. **Input Validation**
   ```yaml
   input:
     url:
       type: "invalid_type"  # Must be a valid type
       required: true
   ```

## Current Implementation Notes

The current implementation performs basic validation:

1. **WhatsApp Adapter**
   - Validates presence of required fields
   - Validates content type against supported workflows
   - Logs validation errors with detailed messages

2. **YAML Workflows**
   - Basic structure validation during workflow loading
   - Type checking for input parameters
   - Task dependency resolution

## Future Improvements (Draft)

### JSON Schema Validation

Consider implementing JSON Schema validation for both webhook payloads and workflow definitions:

```json
// Example schema for WhatsApp payloads
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["type", "value"],
  "properties": {
    "type": {
      "type": "string",
      "enum": ["url", "pdf"]
    },
    "value": {
      "type": "string",
      "minLength": 1
    }
  }
}
```

### Enhanced Error Messages

- Include detailed error paths for nested validation errors
- Provide suggestions for fixing common mistakes
- Support for i18n of error messages

### Type-Specific Validation

- URL validation for URL inputs
- File existence checks for file paths
- Content type validation for binary data
- Range validation for numeric inputs

### Workflow-Specific Validation

- Validate task dependencies
- Check for circular references
- Validate input/output types between tasks
- Resource requirement validation

### Integration with CI/CD

- Pre-commit hooks for workflow validation
- Automated testing of example workflows
- Schema validation in CI pipelines
