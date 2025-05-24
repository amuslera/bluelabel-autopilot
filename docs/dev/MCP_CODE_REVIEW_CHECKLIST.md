# MCP Code Review Checklist

## Overview
This checklist ensures all code meets Model Context Protocol (MCP) compliance standards and project conventions. Use this when reviewing any agent code, especially cross-agent work.

---

## MCP Input/Output Structure

### Agent Input Validation
- [ ] Uses `AgentInput` from `/interfaces/agent_models.py`
- [ ] Required fields present:
  - [ ] `task_id` (string, can be UUID)
  - [ ] `task_type` (optional but recommended)
  - [ ] `source` (string, origin identifier)
  - [ ] `content` (dict with agent-specific data)
  - [ ] `metadata` (dict, can be empty)
- [ ] Input validation using Pydantic models
- [ ] Proper error handling for invalid inputs

### Agent Output Structure
- [ ] Uses `AgentOutput` from `/interfaces/agent_models.py`
- [ ] Required fields populated:
  - [ ] `status` ("success" or "error")
  - [ ] `result` (dict with output data)
  - [ ] `metadata` (dict with execution details)
  - [ ] `error` (string if status is "error", None otherwise)
  - [ ] `duration_ms` (execution time)
- [ ] Consistent error reporting format
- [ ] Result structure documented

## CLI and Report Formatting

### CLI Implementation
- [ ] Uses Click framework consistently
- [ ] Help messages are clear and include examples
- [ ] Arguments have proper validation
- [ ] Error messages guide users to correct usage
- [ ] Output formatting is consistent
- [ ] JSON input can be provided via file path
- [ ] Verbose/debug flags work correctly

### Report Standards
- [ ] Updates `/TASK_CARDS.md` with:
  - [ ] Task ID and status
  - [ ] Clear deliverables list
  - [ ] Files created/modified
  - [ ] Time spent
- [ ] Writes to `/postbox/{AGENT}/outbox.json`:
  - [ ] Proper JSON structure
  - [ ] Timestamp in ISO format
  - [ ] Comprehensive summary
  - [ ] Status field

## Naming Conventions

### File Naming
- [ ] Python files use snake_case
- [ ] Test files prefixed with `test_`
- [ ] Config files use lowercase with underscores
- [ ] Documentation files use UPPERCASE or Title_Case

### Code Naming
- [ ] Classes use PascalCase
- [ ] Functions/methods use snake_case
- [ ] Constants use UPPERCASE_WITH_UNDERSCORES
- [ ] Private methods prefixed with underscore
- [ ] Descriptive variable names (no single letters except loops)

### Branch Naming
- [ ] Format: `dev/TASK-XXX-{agent}-description`
- [ ] Agent identifier included (cc, ca, wa)
- [ ] Description is hyphenated lowercase
- [ ] Task ID matches assigned task

## Performance and Memory Review

### Efficiency Checks
- [ ] No unnecessary loops or iterations
- [ ] Async/await used appropriately
- [ ] Large files processed in chunks
- [ ] Memory-intensive operations documented
- [ ] Timeouts configured for external calls

### Resource Management
- [ ] Files closed properly (use context managers)
- [ ] No memory leaks in long-running processes
- [ ] Temporary files cleaned up
- [ ] Connection pools managed correctly
- [ ] Large objects freed when no longer needed

## Agent-Specific Review Points

### WA (Windsurf AI) Merges
- [ ] UI components follow established patterns
- [ ] Frontend/backend integration points clear
- [ ] WhatsApp adapter follows rate limits
- [ ] Simulation tools have proper documentation
- [ ] YAML templates are valid and documented

### CA (Cursor AI) Merges
- [ ] Test coverage meets standards
- [ ] Async patterns used correctly
- [ ] Mock objects properly implemented
- [ ] Test data realistic and comprehensive
- [ ] Schema validation in place

## General Code Quality

### Documentation
- [ ] Docstrings for all public methods
- [ ] Complex logic has inline comments
- [ ] README updated if needed
- [ ] API changes documented
- [ ] Breaking changes highlighted

### Error Handling
- [ ] Try/except blocks are specific
- [ ] Errors logged appropriately
- [ ] User-friendly error messages
- [ ] No bare except clauses
- [ ] Graceful degradation implemented

### Testing
- [ ] Unit tests for new functionality
- [ ] Integration tests for workflows
- [ ] Edge cases covered
- [ ] Mocks used appropriately
- [ ] Tests are deterministic

## Security Considerations
- [ ] No hardcoded credentials
- [ ] Input sanitization implemented
- [ ] File paths validated
- [ ] No arbitrary code execution
- [ ] Sensitive data not logged

## Final Checks
- [ ] Code runs without warnings
- [ ] All tests pass
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] Dependencies documented
- [ ] Version compatibility noted

---

## Review Process

1. **Initial Scan**: Check MCP compliance and structure
2. **Deep Review**: Examine logic and implementation
3. **Test Execution**: Run tests and verify behavior
4. **Documentation Check**: Ensure docs are updated
5. **Final Approval**: Confirm all checklist items

## Notes
- This checklist supplements, not replaces, standard code review practices
- Focus extra attention on cross-agent integration points
- When in doubt, err on the side of stricter compliance
- Update this checklist based on patterns observed in reviews