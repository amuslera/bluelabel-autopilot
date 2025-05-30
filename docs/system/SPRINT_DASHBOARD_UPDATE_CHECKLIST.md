# Sprint Dashboard Update Checklist

**Purpose:** Ensure the live agent monitor dashboard is updated whenever a new sprint is launched.

## Files to Update

### 1. `.sprint/progress.json`
Update with new sprint information:
```json
{
  "sprint_id": "PHASE_X.XX_SPRINT_NAME",
  "phase": "Phase X.XX Description",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "total_tasks": X,
  "completed_tasks": 0,
  "tasks": [
    {
      "id": "TASK-XXXX",
      "title": "Task Title",
      "assigned_to": "CA/CB/CC",
      "status": "pending",
      "priority": "HIGH/MEDIUM/LOW"
    }
  ]
}
```

### 2. `agent_monitor_v2.py`
Update the sprint configuration section:
- Sprint ID and phase information
- Task list with new task IDs
- Sprint dates

### 3. `apps/web/pages/collaboration.tsx` (if exists)
Update:
- Agent workloads (reset to 0%)
- Current tasks for each agent
- Chat messages to reflect new sprint

## Update Process

1. **At Sprint Kickoff:**
   ```bash
   # Update progress.json with new sprint data
   # Update agent_monitor_v2.py with sprint info
   # Commit changes
   ```

2. **Verify Dashboard:**
   - Run the monitor to confirm updates
   - Check that all agents show correct tasks
   - Ensure progress shows 0% at start

3. **During Sprint:**
   - Update task statuses as they progress
   - Mark completed_tasks when done
   - Keep progress percentage accurate

## Quick Update Script

Consider creating `update_sprint_dashboard.py`:
```python
def update_dashboard(sprint_id, phase, start_date, end_date, tasks):
    # Update progress.json
    # Update agent_monitor_v2.py
    # Commit changes
```

## Important Notes

- Always update dashboard BEFORE notifying agents
- Keep task IDs consistent across all files
- Reset progress to 0% for new sprints
- Include all active tasks in the update

---

This ensures the live dashboard stays in sync with actual sprint progress!