# GitHub Workflows

## Currently Active Workflows
None - All autonomous orchestration has been moved to the file-based system using outbox.json

## Disabled Workflows
- `autonomous_sprint.yml.disabled` - Old autonomous orchestrator that used live status files
  - This was causing errors by checking for files that no longer exist
  - Replaced by the new file-based orchestration system in Phase 6.15

## Notes
The autonomous orchestration system now operates through:
- Agent outboxes in `/postbox/[AGENT]/outbox.json`
- Manual coordination and task assignment
- Local monitoring tools (agent_monitor_v2.py)

No GitHub Actions are needed for agent orchestration anymore.