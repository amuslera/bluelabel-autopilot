# YAML Workflow Templates Guide

## Overview
This document provides guidance on creating and using YAML workflow templates for the Bluelabel Autopilot system. Workflow templates define the sequence of operations that agents will perform to accomplish specific tasks.

## Table of Contents
1. [YAML Format Basics](#yaml-format-basics)
2. [Workflow Structure](#workflow-structure)
3. [Input Parameters](#input-parameters)
4. [Tasks and Agents](#tasks-and-agents)
5. [Using `input_from`](#using-input_from)
6. [Conditional Execution](#conditional-execution)
7. [Output Configuration](#output-configuration)
8. [Error Handling](#error-handling)
9. [Testing Workflows](#testing-workflows)
10. [Template Examples](#template-examples)

## YAML Format Basics

YAML (YAML Ain't Markup Language) is a human-readable data serialization format. Key points:

- Uses indentation to denote structure (spaces, not tabs)
- Key-value pairs are separated by a colon and space
- Lists are denoted with hyphens
- Comments start with `#`

## Workflow Structure

A workflow YAML file has these main sections:

```yaml
workflow:
  name: "workflow_name"
  description: "Description of what this workflow does"
  version: "1.0.0"

input:
  # Input parameters go here

tasks:
  # List of tasks to execute

output:
  # Output configuration

metadata:
  # Additional metadata
```

## Input Parameters

Define input parameters that can be passed to the workflow:

```yaml
input:
  url:
    type: string
    required: true
    description: "URL to process"
    example: "https://example.com"
  
  max_length:
    type: integer
    required: false
    default: 1000
    description: "Maximum length of the output"
```

## Tasks and Agents

Tasks define the individual steps in your workflow. Each task is executed by an agent:

```yaml
tasks:
  - name: "ingest_content"
    agent: "ingestion"
    type: "url"
    parameters:
      url: "{{ input.url }}"
    output: "ingested_content"
    description: "Fetch content from URL"
```

## Using `input_from`

The `input_from` field allows you to pass data between tasks. It references the output of a previous task:

```yaml
tasks:
  - name: "fetch_data"
    agent: "fetcher"
    output: "raw_data"
    # ...

  - name: "process_data"
    agent: "processor"
    input_from: "raw_data"  # Uses output from fetch_data
    # ...
```

## Conditional Execution

Use the `when` clause to conditionally execute tasks:

```yaml
tasks:
  - name: "generate_detailed_report"
    agent: "reporting"
    when: "input.report_type == 'detailed'"
    # ...

  - name: "generate_summary_report"
    agent: "reporting"
    when: "input.report_type == 'summary'"
    # ...
```

## Output Configuration

Define how the workflow output should be formatted and stored:

```yaml
output:
  format: "markdown"  # or json, html, etc.
  file: "output/result.md"
  fields:
    - name: "title"
      path: "processed_data.title"
    - name: "content"
      path: "processed_data.content"
```

## Error Handling

Define how the workflow should handle errors:

```yaml
error_handling:
  max_retries: 3
  retry_delay: 5s
  on_failure:
    - log_error: true
    - notify: "team@example.com"
```

## Testing Workflows

### Running from CLI

```bash
# Basic usage
python runner/cli_runner.py run_workflow path/to/workflow.yaml

# With input parameters
python runner/cli_runner.py run_workflow path/to/workflow.yaml \
  --input.param1 value1 \
  --input.param2 value2

# Save output to file
python runner/cli_runner.py run_workflow path/to/workflow.yaml > output.txt
```

### Debugging

Add the `--debug` flag for verbose output:

```bash
python runner/cli_runner.py run_workflow path/to/workflow.yaml --debug
```

## Template Examples

### 1. URL to Digest

```yaml
# workflows/templates/url_to_digest.yaml
workflow:
  name: "url_to_digest"
  description: "Process a URL and generate a digest"

tasks:
  - name: "ingest_url"
    agent: "ingestion"
    type: "url"
    parameters:
      url: "{{ input.url }}"
    output: "ingested_content"

  - name: "generate_digest"
    agent: "digest"
    type: "generate"
    input_from: "ingested_content"
    output: "digest_output"
```

### 2. PDF Processing

```yaml
# workflows/templates/pdf_processor.yaml
workflow:
  name: "pdf_processor"
  description: "Process a PDF and extract key information"

tasks:
  - name: "extract_text"
    agent: "ingestion"
    type: "pdf"
    parameters:
      file_path: "{{ input.file_path }}"
    output: "extracted_text"

  - name: "analyze_content"
    agent: "analysis"
    input_from: "extracted_text"
    output: "analysis_results"
```

## Best Practices

1. **Keep it DRY**: Use YAML anchors and aliases for repeated structures
2. **Validate Early**: Test workflows with sample data
3. **Document Thoroughly**: Include descriptions and examples for all parameters
4. **Handle Errors**: Define clear error handling strategies
5. **Version Control**: Include version numbers in your workflow files

## Troubleshooting

### Common Issues

1. **Indentation Errors**: Ensure consistent use of spaces (no tabs)
2. **Missing Dependencies**: Check that all required agents are available
3. **Type Mismatches**: Verify input parameter types match expected values
4. **Permission Issues**: Ensure the workflow has necessary file system permissions

### Getting Help

For additional assistance, refer to:
- [YAML Specification](https://yaml.org/spec/)
- [Workflow Engine Documentation](docs/WORKFLOW_ENGINE.md)
- [Agent Development Guide](docs/AGENT_DEVELOPMENT.md)
