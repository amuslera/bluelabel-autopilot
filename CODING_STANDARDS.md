# Coding Standards & Best Practices - Bluelabel Autopilot

**Version:** 1.0  
**Last Updated:** November 27, 2024

## Python Coding Standards

### Code Style

1. **Formatting**
   - Use Black with default settings (line length 88)
   - Run `black .` before committing
   - Configure your IDE to format on save

2. **Linting**
   - Use flake8 with these settings:
   ```ini
   # .flake8
   [flake8]
   max-line-length = 88
   extend-ignore = E203, W503
   exclude = .git,__pycache__,docs/,build/,dist/
   ```

3. **Type Hints**
   - Always use type hints for function parameters and returns
   - Use `Optional[]` for nullable types
   - Use `Union[]` sparingly, prefer specific types

### Code Examples

#### Good Practice
```python
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

async def process_workflow(
    workflow_id: str,
    config: Dict[str, Any],
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """Process a workflow with the given configuration.
    
    Args:
        workflow_id: Unique identifier for the workflow
        config: Workflow configuration dictionary
        timeout: Optional timeout in seconds
        
    Returns:
        Dictionary containing workflow results
        
    Raises:
        WorkflowError: If workflow processing fails
        TimeoutError: If workflow exceeds timeout
    """
    try:
        logger.info(f"Processing workflow {workflow_id}")
        # Implementation here
        return {"status": "success", "workflow_id": workflow_id}
    except Exception as e:
        logger.error(f"Workflow {workflow_id} failed: {str(e)}")
        raise WorkflowError(f"Failed to process workflow: {str(e)}") from e
```

#### Bad Practice
```python
# No type hints, poor error handling, no logging
def process_workflow(id, config, timeout=None):
    try:
        # Implementation
        return {"status": "success"}
    except:  # Bare except
        return None  # Silent failure
```

## Project Structure Standards

### Module Organization

```
module/
├── __init__.py          # Public API exports
├── models.py           # Pydantic models
├── service.py          # Business logic
├── adapters.py         # External integrations
├── exceptions.py       # Custom exceptions
└── utils.py           # Helper functions
```

### Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import os
import sys
from datetime import datetime

# Third-party
import asyncio
from pydantic import BaseModel

# Local
from services.email import EmailService
from interfaces.agent_models import AgentInput
```

## Error Handling Standards

### Exception Hierarchy

```python
# exceptions.py
class AutopilotError(Exception):
    """Base exception for all Autopilot errors."""
    pass

class ValidationError(AutopilotError):
    """Raised when input validation fails."""
    pass

class WorkflowError(AutopilotError):
    """Raised when workflow execution fails."""
    pass

class ConfigurationError(AutopilotError):
    """Raised when configuration is invalid."""
    pass
```

### Error Handling Pattern

```python
# Always catch specific exceptions
try:
    result = await process_workflow(workflow_id)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")
    return {"error": "Invalid input", "details": str(e)}
except WorkflowError as e:
    logger.error(f"Workflow error: {e}")
    return {"error": "Processing failed", "details": str(e)}
except Exception as e:
    logger.exception("Unexpected error")
    raise  # Re-raise unexpected errors
```

## Async/Await Best Practices

### Resource Management

```python
# Good: Proper async context manager
async def read_file(path: str) -> str:
    async with aiofiles.open(path, 'r') as f:
        return await f.read()

# Good: Proper cleanup
async def process_with_timeout(coro, timeout: int):
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.warning(f"Operation timed out after {timeout}s")
        raise
```

### Concurrent Operations

```python
# Good: Concurrent execution
async def process_multiple(items: List[str]) -> List[Dict]:
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Bad: Sequential execution
async def process_multiple_bad(items: List[str]) -> List[Dict]:
    results = []
    for item in items:
        results.append(await process_item(item))  # Sequential!
    return results
```

## Security Standards

### Input Validation

```python
from pydantic import BaseModel, validator, constr

class WorkflowInput(BaseModel):
    workflow_id: constr(regex=r'^[a-zA-Z0-9_-]+$', max_length=100)
    email: constr(regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
    @validator('workflow_id')
    def validate_workflow_id(cls, v):
        if '..' in v or '/' in v:
            raise ValueError('Invalid characters in workflow_id')
        return v
```

### Secrets Management

```python
# Good: Use environment variables or secret manager
import os
from typing import Optional

def get_secret(key: str) -> Optional[str]:
    """Get secret from environment or secret manager."""
    # First try environment
    value = os.environ.get(key)
    if value:
        return value
    
    # Then try secret manager (example)
    # return secret_manager.get_secret(key)
    
    return None

# Bad: Hardcoded secrets
API_KEY = "sk-1234567890"  # NEVER DO THIS
```

## Testing Standards

### Test Structure

```python
# test_workflow_engine.py
import pytest
from unittest.mock import Mock, patch

class TestWorkflowEngine:
    """Test cases for WorkflowEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a test engine instance."""
        return WorkflowEngine(test_mode=True)
    
    @pytest.fixture
    def mock_workflow(self):
        """Create a mock workflow for testing."""
        return {
            "id": "test-workflow",
            "steps": [{"agent": "test", "action": "process"}]
        }
    
    async def test_successful_execution(self, engine, mock_workflow):
        """Test successful workflow execution."""
        result = await engine.execute(mock_workflow)
        assert result["status"] == "success"
        assert result["workflow_id"] == "test-workflow"
    
    async def test_validation_error(self, engine):
        """Test workflow validation error handling."""
        with pytest.raises(ValidationError):
            await engine.execute({"invalid": "workflow"})
```

### Test Naming

- Test files: `test_<module_name>.py`
- Test classes: `Test<ClassName>`
- Test methods: `test_<what_is_being_tested>`

## Documentation Standards

### Docstring Format (Google Style)

```python
def complex_function(
    param1: str,
    param2: Dict[str, Any],
    param3: Optional[int] = None
) -> Tuple[str, int]:
    """Brief description of function.
    
    Longer description if needed, explaining the purpose
    and any important details about the function.
    
    Args:
        param1: Description of param1
        param2: Description of param2, can be multi-line
            if needed for clarity
        param3: Optional parameter description
        
    Returns:
        Tuple containing:
            - Processed string result
            - Count of operations performed
            
    Raises:
        ValueError: If param1 is empty
        KeyError: If required keys missing from param2
        
    Example:
        >>> result, count = complex_function(
        ...     "test",
        ...     {"key": "value"},
        ...     timeout=30
        ... )
        >>> print(result)
        'processed: test'
    """
    pass
```

### README Structure

1. Project Title and Description
2. Installation Instructions
3. Quick Start Guide
4. Configuration
5. Usage Examples
6. API Documentation
7. Contributing Guidelines
8. License

## Git Commit Standards

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes

### Examples

```bash
feat(email): Add OAuth 2.0 authentication support

- Implement proper redirect flow for Gmail OAuth
- Add token refresh logic
- Encrypt stored credentials

Closes #123

---

fix(workflow): Prevent memory leak in PDF processing

Stream PDF content instead of loading entire file into memory.
This fixes OOM errors with files larger than 100MB.

Fixes #456
```

## Code Review Checklist

Before submitting a PR, ensure:

- [ ] All tests pass (`make test`)
- [ ] Code is formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Type checking passes (`mypy .`)
- [ ] Documentation is updated
- [ ] Commit messages follow standards
- [ ] No hardcoded secrets
- [ ] Error handling is appropriate
- [ ] Logging is adequate
- [ ] Performance impact considered

## Performance Guidelines

1. **Avoid Premature Optimization**
   - Profile before optimizing
   - Focus on algorithmic improvements

2. **Memory Management**
   - Stream large files
   - Use generators for large datasets
   - Clean up resources properly

3. **Async Best Practices**
   - Don't block the event loop
   - Use connection pooling
   - Batch operations when possible

## Monitoring Standards

### Logging Levels

- `DEBUG`: Detailed information for diagnosing problems
- `INFO`: General informational messages
- `WARNING`: Warning messages for potentially harmful situations
- `ERROR`: Error events that might still allow the application to continue
- `CRITICAL`: Critical events that will probably cause the application to abort

### Logging Format

```python
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Good: Structured logging
logger.info(
    "Workflow completed",
    extra={
        "workflow_id": workflow_id,
        "duration_ms": duration,
        "status": "success"
    }
)
```

---

*These standards are living documents and should be updated as the project evolves.*