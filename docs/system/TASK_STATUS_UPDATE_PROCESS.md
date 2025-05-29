# Task Status Update Process

**CRITICAL:** All agents must update their outbox.json status when starting and completing tasks.

## 🚨 Mandatory Process

### Step 1: When Starting a Task
**Before doing any work**, update your outbox.json:

```json
{
  "task_id": "TASK-XXX",
  "status": "in_progress",
  "started_at": "2025-05-29T15:45:00Z"
}
```

### Step 2: Execute the Task
- Do your work autonomously
- Use your expertise to complete all deliverables
- Test and validate your implementation

### Step 3: When Ready for Review
**After finishing all work**, update your outbox.json:

1. **Update task status to ready_for_review:**
```json
{
  "task_id": "TASK-XXX", 
  "status": "ready_for_review",
  "completed_at": "2025-05-29T16:30:00Z"
}
```

### Step 4: ARCH Review Process (ARCH Agent Only)
**ARCH reviews work and promotes to completed:**

1. **Review deliverables and mark as completed:**
```json
{
  "task_id": "TASK-XXX", 
  "status": "completed",
  "reviewed_by": "ARCH",
  "completed_at": "2025-05-29T16:45:00Z"
}
```

2. **Move to history array:**
```json
{
  "task_id": "TASK-XXX",
  "timestamp": "2025-05-29T16:30:00Z", 
  "status": "completed",
  "summary": "Brief description of what was accomplished",
  "completion_message": "Detailed completion message"
}
```

3. **Remove from tasks array:**
Remove the completed task from the "tasks" array

## 📋 Complete Example

### Before Starting (outbox.json):
```json
{
  "tasks": [
    {
      "task_id": "TASK-167X",
      "title": "Example Task",
      "status": "pending",
      "created_at": "2025-05-29T15:00:00Z"
    }
  ],
  "history": []
}
```

### When Starting Work:
```json
{
  "tasks": [
    {
      "task_id": "TASK-167X",
      "title": "Example Task", 
      "status": "in_progress",
      "created_at": "2025-05-29T15:00:00Z",
      "started_at": "2025-05-29T15:45:00Z"
    }
  ],
  "history": []
}
```

### When Ready for Review:
```json
{
  "tasks": [
    {
      "task_id": "TASK-167X",
      "title": "Example Task", 
      "status": "ready_for_review",
      "created_at": "2025-05-29T15:00:00Z",
      "started_at": "2025-05-29T15:45:00Z",
      "completed_at": "2025-05-29T16:30:00Z"
    }
  ],
  "history": []
}
```

### After ARCH Review & Completion:
```json
{
  "tasks": [],
  "history": [
    {
      "task_id": "TASK-167X",
      "timestamp": "2025-05-29T16:45:00Z",
      "status": "completed", 
      "reviewed_by": "ARCH",
      "summary": "Successfully implemented example functionality",
      "completion_message": "All deliverables completed successfully"
    }
  ]
}
```

## 🔄 Monitor Integration

This process ensures:
- ✅ Monitor shows accurate "Working" status when agents are active
- ✅ Monitor shows accurate "Idle" status when agents complete tasks
- ✅ Sprint progress updates automatically
- ✅ Recent activity reflects real-time completions
- ✅ No manual intervention required for status tracking

## ❌ Common Mistakes to Avoid

- Don't forget to update status to "in_progress" when starting
- Don't forget to move completed tasks to history
- Don't leave completed tasks in the "tasks" array
- Don't forget to add timestamps for tracking

## ✅ Success Criteria

**The monitor should show:**
- Agent as "Working" when status is "in_progress"
- Agent as "Idle" when tasks array is empty
- Recent activity updates when tasks move to history
- Accurate sprint progress percentages

---

**Remember: Status updates are not optional - they're required for system coordination!**