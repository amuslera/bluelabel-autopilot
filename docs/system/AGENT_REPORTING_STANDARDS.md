# Agent Reporting Standards

## Task Completion Report Format

When completing a task, all agents MUST report using this standardized format:

### 1. Summary Line
```
✅ TASK-[ID] completed: [Brief one-line summary]
```

### 2. Deliverables Section
List each deliverable with status:
```
DELIVERABLES:
✓ Created tools/morning_kickoff.sh
✓ Updated .sprint/progress.json structure
✓ Documented workflow in README
✗ Pending: Integration tests (blocked by X)
```

### 3. Key Changes
```
KEY CHANGES:
- Added 3 new files in /tools/
- Modified outbox format to include 'status' field
- Refactored task distribution logic
```

### 4. Testing Summary
```
TESTING:
- Ran manual test with 5 sample tasks ✓
- Verified JSON validation ✓
- Edge cases tested: empty tasks, malformed JSON ✓
```

### 5. Next Steps (if any)
```
NEXT STEPS:
- Other agents can now use the standardized format
- Ready for integration with morning routine
```

## Example Complete Report

```
✅ TASK-165B completed: Standardized outbox format across all agents

DELIVERABLES:
✓ Created /docs/system/OUTBOX_SCHEMA.md with complete schema
✓ Created /tools/validate_outbox.py validation script  
✓ Updated all 4 agent outbox files to new format
✓ Added JSON schema validation

KEY CHANGES:
- Standardized on 'tasks' array structure
- Added required fields: agent_id, agent_name, version
- Made status field mandatory for all tasks
- Added optional 'history' array for completed tasks

TESTING:
- Validated all existing outbox files ✓
- Tested validation script with malformed JSON ✓
- Verified backwards compatibility ✓

NEXT STEPS:
- All agents should use validate_outbox.py before updates
- Morning kickoff script can rely on standard format
```

## Reporting Location

1. **Update your outbox.json** - Mark task as completed
2. **Post summary in response** - Use the format above
3. **Update .sprint/progress.json** - If you have access

## DO NOT:
- Ask "Should I proceed with X?"
- Report after every small step
- Wait for confirmation to continue
- Leave tasks partially complete

## DO:
- Complete the entire task autonomously
- Make implementation decisions confidently
- Report only when fully complete
- Include all relevant details in one report