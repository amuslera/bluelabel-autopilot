# CLI Test Runner Documentation

The CLI Test Runner is a command-line tool for executing and testing agent workflows defined in YAML files. It provides a structured way to run multi-step agent workflows and validate their execution.

## Usage

```bash
# Basic usage
python runner/cli_test_runner.py workflows/sample_ingestion_digest.yaml

# With verbose logging
python runner/cli_test_runner.py workflows/sample_ingestion_digest.yaml --verbose

# With custom log file
python runner/cli_test_runner.py workflows/sample_ingestion_digest.yaml --log-file test_run.log

# With custom storage paths
python runner/cli_test_runner.py workflows/sample_ingestion_digest.yaml \
    --storage-path ./custom/knowledge \
    --temp-path ./custom/temp
```

## Workflow YAML Format

Workflows are defined in YAML files with the following structure:

```yaml
workflow:
  name: "Workflow Name"
  description: "Workflow description"
  version: "1.0.0"

steps:
  - id: step1
    name: "Step Name"
    agent: agent_name
    input_file: path/to/input.json
    description: "Step description"
    outputs:
      - output_field1
      - output_field2

  - id: step2
    name: "Next Step"
    agent: another_agent
    input_from: step1
    config:
      key: value
    outputs:
      - output_field3
```

### Required Fields

- `workflow`:
  - `name`: Workflow name
  - `description`: Workflow description
  - `version`: Workflow version

- `steps`:
  - `id`: Unique step identifier
  - `name`: Step name
  - `agent`: Agent to execute (must be registered)
  - Either `input_file` or `input_from` must be specified
  - `outputs`: List of output fields to display

### Optional Fields

- `config`: Additional configuration for the step
- `description`: Step description
- `metadata`: Workflow metadata

## Input Sources

Steps can get their input from two sources:

1. Input File:
```yaml
steps:
  - id: step1
    agent: ingestion_agent
    input_file: tests/sample_input.json
```

2. Previous Step Output:
```yaml
steps:
  - id: step2
    agent: digest_agent
    input_from: step1
    config:
      format: markdown
```

## Output Format

The test runner provides detailed output for each step:

```
Running workflow: PDF Ingestion and Digest (v1.0.0)
Description: Process a PDF file and generate a formatted digest

Executing step: Ingest PDF (ingest)
Step completed successfully: Ingest PDF

Executing step: Generate Digest (digest)
Step completed successfully: Generate Digest

Workflow Execution Summary:
-------------------------

Step: Ingest PDF (ingest)
Status: success
Duration: 1234ms
content_id: pdf_abc123
content_type: pdf
content_length: 5678

Step: Generate Digest (digest)
Status: success
Duration: 567ms
digest: # Sample Digest\n\n- Point 1\n- Point 2
summary_count: 2
format: markdown
```

## Error Handling

The test runner provides clear error messages for common issues:

1. Invalid YAML:
```
Error: Invalid YAML file: mapping values are not allowed here
```

2. Missing Required Fields:
```
Error: Missing required field: steps
```

3. Unknown Agent:
```
Error: Unknown agent: unknown_agent
```

4. Missing Input File:
```
Error: Input file not found: tests/missing.json
```

5. Step Execution Failure:
```
Error: Step execution failed: Invalid input format
```

## Troubleshooting

1. **Workflow Fails to Load**
   - Check YAML syntax
   - Verify all required fields are present
   - Ensure agent names are correct

2. **Step Execution Fails**
   - Check input file format
   - Verify file paths exist
   - Check agent configuration

3. **Output Fields Missing**
   - Verify output fields exist in agent result
   - Check step configuration
   - Enable verbose logging for details

4. **Performance Issues**
   - Use custom storage paths
   - Check file system permissions
   - Monitor log file for bottlenecks

## Best Practices

1. **Workflow Design**
   - Keep workflows focused and simple
   - Use descriptive step names
   - Document expected outputs

2. **Input Files**
   - Use sample files for testing
   - Validate input format
   - Keep paths relative to workspace

3. **Logging**
   - Use verbose mode for debugging
   - Save logs for analysis
   - Monitor execution times

4. **Error Handling**
   - Test error conditions
   - Provide clear error messages
   - Handle cleanup on failure 