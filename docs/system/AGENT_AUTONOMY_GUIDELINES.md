# Agent Autonomy Guidelines

## Core Principle: Maximum Autonomy

Agents should operate with maximum autonomy within their defined scope. Only seek confirmation for:
1. **Destructive operations** (deleting files, overwriting critical code)
2. **Scope expansion** (working outside assigned files/directories)
3. **Architectural decisions** (changing core design patterns)

## Decision Framework

### ✅ PROCEED WITHOUT ASKING:
- Creating new files within your task scope
- Writing code that implements the requirements
- Running tests and fixing errors
- Making implementation choices within established patterns
- Updating documentation for your changes
- Committing to your feature branch

### ❌ ASK BEFORE:
- Modifying files outside your task assignment
- Changing established architectural patterns
- Deleting or moving existing files
- Making breaking API changes
- Modifying another agent's work

## Implementation Guidelines

1. **Read the full task description** - All information needed is in your outbox
2. **Make decisions based on context** - Use existing patterns in the codebase
3. **Complete the full task** - Don't stop at each step for confirmation
4. **Test your work** - Run relevant tests before marking complete
5. **Document your changes** - Update relevant docs as you go

## Error Handling

When you encounter errors:
1. **First attempt**: Try to fix it yourself
2. **Second attempt**: Try an alternative approach
3. **Third attempt**: Document the blocker and ask for help

## Task Execution Flow

```
1. Read task from outbox
2. Update task status to "in_progress" in outbox.json
3. Plan implementation (internally)
4. Execute full implementation
5. Test the implementation
6. Fix any issues found
7. Update documentation
8. Update task status to "ready_for_review" with timestamp
9. Wait for ARCH review and promotion to "completed" status
10. ARCH moves completed task to history array with summary
```

## Required Status Updates

### When Starting a Task:
```json
{
  "task_id": "TASK-XXX",
  "status": "in_progress",
  "started_at": "2025-05-29T15:45:00Z"
}
```

### When Ready for Review:
```json
{
  "task_id": "TASK-XXX", 
  "status": "ready_for_review",
  "completed_at": "2025-05-29T16:30:00Z"
}
```

### ARCH Review Process:
```json
{
  "task_id": "TASK-XXX", 
  "status": "completed",
  "reviewed_by": "ARCH",
  "completed_at": "2025-05-29T16:45:00Z"
}
```

### Move to History:
```json
{
  "task_id": "TASK-XXX",
  "timestamp": "2025-05-29T16:30:00Z", 
  "status": "completed",
  "summary": "Brief description of what was accomplished",
  "completion_message": "Detailed completion message"
}
```

## Reporting Standards

See AGENT_REPORTING_STANDARDS.md for completion report format.

## Remember

- You have full autonomy within your task scope
- The human wants results, not step-by-step confirmations
- Be confident in your implementation decisions
- Complete the entire task before reporting back