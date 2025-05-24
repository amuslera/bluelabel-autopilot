# Windsurf AI (WA) Task Execution Checklist

This checklist governs how Windsurf AI (WA) must execute every task in Phase 6.11 and beyond. It must be complete, unambiguous, and enforceable.

## Pre-Implementation Checklist
- [ ] Read and understand task prompt completely
- [ ] Verify task is explicitly assigned by ARCH-AI or Ariel
- [ ] Check for any dependencies or prerequisites
- [ ] Review existing UI patterns in `/apps/web/src/components/`

## Branch Management
- [ ] Create feature branch using format: `ui/feature-TASK-XXXX`
- [ ] Branch must be created from `main`
- [ ] Branch name must match task ID exactly

## Development Standards
- [ ] Use TypeScript with proper type definitions
- [ ] Follow React functional component patterns
- [ ] Implement with Tailwind CSS for styling
- [ ] Ensure accessibility compliance
- [ ] Only modify files explicitly listed in task prompt
- [ ] No experimental or partial implementations

## Testing Protocol
- [ ] Start dev server: `npm run dev`
- [ ] Test all modified routes and components
- [ ] Verify responsive design at all breakpoints
- [ ] Test accessibility features
- [ ] Ensure no console errors or warnings
- [ ] Verify all props and types are correct

## Visual Documentation
- [ ] Take at least one screenshot of working UI
- [ ] Screenshot must show the implemented feature
- [ ] Save screenshot in `/apps/web/screenshots/`
- [ ] Include screenshot path in outbox report

## Git Compliance
- [ ] Check status: `git status`
- [ ] Review diff: `git diff`
- [ ] Verify only assigned files are modified
- [ ] Write clear, descriptive commit messages
- [ ] No CLI tools, core logic, or backend changes

## Documentation Updates
- [ ] Update `/TASK_CARDS.md` with:
  - Task summary
  - Implementation details
  - Status
  - Time spent
  - Files modified
- [ ] Document component props
- [ ] Update any relevant README files

## Reporting Requirements
Write structured report to `/postbox/WA/outbox.json`:
```json
{
  "task_id": "TASK-XXXX",
  "agent": "WA",
  "status": "completed",
  "summary": "Brief description",
  "files_modified": ["list", "of", "files"],
  "screenshot_path": "/path/to/screenshot.png",
  "dev_server_tested": true,
  "checklist_complete": true,
  "timestamp": "ISO-8601"
}
```

## Quality Gates
Before marking task complete:
- [ ] Dev server runs without errors
- [ ] All routes tested and functional
- [ ] Screenshot captured and saved
- [ ] TASK_CARDS.md updated
- [ ] Outbox report written
- [ ] Git branch properly named
- [ ] Only assigned files modified

## Prohibited Actions
- ❌ Modify CLI tools
- ❌ Change core logic
- ❌ Alter backend infrastructure
- ❌ Skip documentation
- ❌ Omit screenshots
- ❌ Commit unverified code

## Consequences for Non-Compliance
⚠️ **WARNING**: ARCH reviews all WA output for checklist compliance. Violations result in:
1. Task rejection and rework required
2. Possible reassignment to CA or CC
3. Additional oversight requirements
4. Documented in agent scorecard

## Reference
- [WA Operating Protocol – WA_BOOT.md](/postbox/WA/WA_BOOT.md)
- [Windsurf Context – WINDSURF_CONTEXT.md](/docs/system/WINDSURF_CONTEXT.md) 