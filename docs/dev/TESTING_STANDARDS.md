# Testing Standards for Bluelabel Autopilot

## Overview
This document defines the testing standards and best practices for the Bluelabel Autopilot project. All tests must follow these guidelines to ensure consistency, maintainability, and comprehensive coverage.

## Test File Organization

### Naming Conventions
- Test files must be named `test_<module_name>.py`
- Test classes must be named `Test<ClassName>`
- Test functions must be named `test_<scenario_description>`
- Fixture files must be named `conftest.py` or `fixtures_<module_name>.py`

Example:
```python
# test_workflow_storage.py
class TestWorkflowStorage:
    def test_create_run_directory_with_timestamp():
        pass
    
    def test_save_step_output_with_metadata():
        pass
```

### Directory Structure
```
tests/
├── conftest.py              # Global fixtures
├── test_cli_runner.py       # CLI tests
├── test_workflow_engine.py  # Workflow tests
├── fixtures/                # Test data
│   ├── sample_workflows/    # Workflow examples
│   └── sample_inputs/       # Input examples
└── integration/             # Integration tests
    └── test_agent_flows.py  # End-to-end tests
```

## Input/Output JSON Standards

### Required Structure
1. **Input Files**:
```json
{
    "task_id": "string",
    "task_type": "string",
    "source": "string",
    "content": {
        // Agent-specific content
    },
    "metadata": {
        // Optional metadata
    },
    "context": {
        // Optional context
    }
}
```

2. **Output Files**:
```json
{
    "status": "success|error",
    "timestamp": "ISO8601",
    "result": {
        // Agent-specific result
    },
    "metadata": {
        // Optional metadata
    }
}
```

### Validation Rules
- All JSON must be validated using Pydantic models
- Required fields must be explicitly marked
- Optional fields must have default values
- Timestamps must be ISO8601 format
- Enums must be used for fixed values

Example:
```python
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

class TaskType(str, Enum):
    URL = "url"
    PDF = "pdf"

class AgentInput(BaseModel):
    task_id: str
    task_type: TaskType
    source: str = "cli"
    content: dict
    metadata: dict = Field(default_factory=dict)
    context: dict = Field(default_factory=dict)
```

## Testing Approaches

### Unit Tests
1. **Mock Usage**:
   - Mock external dependencies (HTTP, filesystem)
   - Use `unittest.mock` or `pytest-mock`
   - Document mock behavior in test docstrings

Example:
```python
def test_workflow_execution(mocker):
    """Test workflow execution with mocked agent responses."""
    mock_agent = mocker.patch("agents.ingestion_agent.IngestionAgent")
    mock_agent.return_value.process.return_value = {
        "status": "success",
        "content_id": "test_123"
    }
    # Test implementation
```

2. **Fixtures**:
   - Use `@pytest.fixture` for reusable test data
   - Keep fixtures in `conftest.py` or module-specific files
   - Document fixture purpose and usage

Example:
```python
@pytest.fixture
def sample_workflow_yaml():
    """Provide a sample workflow YAML for testing."""
    return """
    workflow:
      name: "Test Workflow"
      steps:
        - id: step1
          agent: ingestion
    """
```

### CLI Testing
1. **Command Testing**:
   - Test all CLI commands and options
   - Verify help messages and examples
   - Check error handling and exit codes

Example:
```python
def test_cli_help(capsys):
    """Test CLI help message formatting."""
    with pytest.raises(SystemExit):
        cli_runner.main(["--help"])
    captured = capsys.readouterr()
    assert "Usage:" in captured.out
    assert "Options:" in captured.out
```

2. **Input Validation**:
   - Test invalid input handling
   - Verify error messages
   - Check file path validation

Example:
```python
def test_invalid_json_input(capsys):
    """Test handling of invalid JSON input."""
    with pytest.raises(SystemExit):
        cli_runner.main(["run", "ingestion", "{invalid json}"])
    captured = capsys.readouterr()
    assert "Invalid JSON" in captured.err
```

### Async Testing
1. **Async Test Structure**:
   - Use `pytest.mark.asyncio`
   - Properly handle async fixtures
   - Test both success and error cases

Example:
```python
@pytest.mark.asyncio
async def test_async_workflow_execution():
    """Test async workflow execution."""
    engine = WorkflowEngine()
    result = await engine.run_workflow("test_workflow.yaml")
    assert result.status == "success"
```

2. **Error Handling**:
   - Test async error propagation
   - Verify timeout handling
   - Check cancellation behavior

Example:
```python
@pytest.mark.asyncio
async def test_workflow_timeout():
    """Test workflow timeout handling."""
    engine = WorkflowEngine(timeout=1)
    with pytest.raises(TimeoutError):
        await engine.run_workflow("long_running_workflow.yaml")
```

## Best Practices

### Test Coverage
- Aim for 100% coverage of core functionality
- Document any excluded code paths
- Use `pytest-cov` for coverage reporting

### Test Data
- Use realistic test data
- Include edge cases
- Document data sources and assumptions

### Error Cases
- Test all error conditions
- Verify error messages
- Check error recovery

### Performance
- Test with realistic data sizes
- Monitor test execution time
- Document performance requirements

## Example Test Suite

```python
# test_workflow_storage.py
import pytest
from datetime import datetime
from runner.workflow_storage import WorkflowStorage

@pytest.fixture
def storage(tmp_path):
    """Create a WorkflowStorage instance with temporary path."""
    return WorkflowStorage(base_path=str(tmp_path))

@pytest.fixture
def sample_workflow_yaml():
    """Provide sample workflow YAML."""
    return """
    workflow:
      name: "Test Workflow"
      steps:
        - id: step1
          agent: ingestion
    """

def test_create_run_directory(storage):
    """Test run directory creation with timestamp."""
    run_path = storage.create_run_directory("test_workflow")
    assert run_path.exists()
    assert run_path.name.startswith("202")  # Timestamp format

@pytest.mark.asyncio
async def test_save_step_output(storage):
    """Test async step output saving."""
    run_path = storage.create_run_directory("test_workflow")
    output = {
        "status": "success",
        "result": {"content_id": "test_123"}
    }
    await storage.save_step_output(run_path, "step1", output)
    assert (run_path / "step1_output.json").exists()
```

## Additional Resources
- [pytest Documentation](https://docs.pytest.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/) 