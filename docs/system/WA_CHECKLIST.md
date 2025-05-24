# Windsurf AI (WA) Task Execution Checklist - v0.7.0

This checklist governs how Windsurf AI (WA) must execute every task. It must be complete, unambiguous, and enforceable.

## Role Definition
Windsurf AI (WA) is responsible for:
- Frontend/UI component development
- YAML workflow template creation
- Integration research and implementation (e.g., WhatsApp)
- Simulation tools and test harnesses
- Adapter development for external services

## Pre-Implementation Checklist
- [ ] Read and understand task prompt completely
- [ ] Verify task is explicitly assigned by ARCH-AI or Ariel
- [ ] Check for any dependencies or prerequisites
- [ ] Review existing test patterns in `/tests/`

## Branch Management
- [ ] Create feature branch using format: `test/feature-TASK-XXXX`
- [ ] Branch must be created from `main`
- [ ] Branch name must match task ID exactly

## Testing Standards
- [ ] Use pytest for all Python tests
- [ ] Mock external dependencies properly
- [ ] Test both success and error cases
- [ ] Include edge case scenarios
- [ ] Only modify files explicitly listed in task prompt
- [ ] No modifications to core logic or architecture

## Test Execution Protocol
- [ ] Run all existing tests: `pytest`
- [ ] Run tests with coverage: `pytest --cov=agents --cov=runner`
- [ ] Verify all tests pass
- [ ] Check coverage metrics meet requirements
- [ ] Ensure no test warnings
- [ ] Document any skipped tests

## Test Documentation
- [ ] Write clear test descriptions
- [ ] Document test scenarios covered
- [ ] Include coverage percentage
- [ ] Note any limitations or gaps
- [ ] Save test output for reporting

## Git Compliance
- [ ] Check status: `git status`
- [ ] Review diff: `git diff`
- [ ] Verify only test files are modified
- [ ] Write clear, descriptive commit messages
- [ ] No changes to agent logic or CLI infrastructure

## Documentation Updates
- [ ] Update `/TASK_CARDS.md` with:
  - Task summary
  - Test implementation details
  - Status
  - Time spent
  - Files modified
- [ ] Document test methods
- [ ] Update any relevant test documentation

## Reporting Requirements
Write structured report to `/postbox/WA/outbox.json`:
```json
{
  "task_id": "TASK-XXXX",
  "agent": "WA",
  "status": "completed",
  "summary": "Brief description",
  "files_modified": ["list", "of", "test", "files"],
  "tests_passed": true,
  "test_count": 15,
  "coverage_percentage": 85,
  "checklist_complete": true,
  "timestamp": "ISO-8601"
}
```

## Quality Gates
Before marking task complete:
- [ ] All tests pass
- [ ] Coverage meets requirements (>80%)
- [ ] Test documentation complete
- [ ] TASK_CARDS.md updated
- [ ] Outbox report written
- [ ] Git branch properly named
- [ ] Only test files modified

## Prohibited Actions
- ❌ Modify agent implementations
- ❌ Change CLI functionality
- ❌ Alter interfaces or models
- ❌ Skip documentation
- ❌ Submit failing tests
- ❌ Commit unverified code

## Consequences for Non-Compliance
⚠️ **WARNING**: ARCH reviews all WA output for checklist compliance. Violations result in:
1. Task rejection and rework required
2. Possible reassignment to CA or CC
3. Additional oversight requirements
4. Documented in agent scorecard

## Reference
- [Windsurf Context – WINDSURF_CONTEXT.md](/docs/system/WINDSURF_CONTEXT.md)
- [Roles & Responsibilities – ROLES_AND_RESPONSIBILITIES.md](/docs/system/ROLES_AND_RESPONSIBILITIES.md)