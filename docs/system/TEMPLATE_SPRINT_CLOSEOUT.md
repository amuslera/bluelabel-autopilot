# Sprint Closeout Checklist Template

## Overview
This checklist ensures all required steps are completed when closing a sprint. Follow this template to maintain consistency and avoid missing critical tasks.

---

## Pre-Closeout Verification
- [ ] All assigned tasks marked as completed in `/TASK_CARDS.md`
- [ ] All feature branches have been tested
- [ ] No failing tests in main branch
- [ ] All agent outbox reports submitted

## Branch Merge Checklist
- [ ] Switch to main branch: `git checkout main`
- [ ] Pull latest changes (if remote exists): `git pull origin main`
- [ ] Merge each feature branch:
  ```bash
  git merge dev/TASK-XXX-description --no-ff -m "Merge TASK-XXX: Brief description"
  ```
- [ ] Resolve any merge conflicts
- [ ] Run tests after each merge to ensure stability
- [ ] Delete merged branches: `git branch -d dev/TASK-XXX-description`

## Sprint Summary Generation
- [ ] Run the automated sprint summary generator:
  ```bash
  python scripts/generate_summary.py --sprint <sprint_number>
  ```
- [ ] Verify output is saved to `/reports/SPRINT_<N>_SUMMARY.md`
- [ ] Review generated summary for accuracy and completeness
- [ ] Include key insights from summary in postmortem

## Required Documentation Updates

### 1. ARCH_CONTINUITY.md
- [ ] Mark sprint as complete in current sprint section
- [ ] Add completion date and summary
- [ ] Update "Last Sprint Completed" field
- [ ] Note any architectural decisions made

### 2. CLAUDE_CONTEXT.md
- [ ] Update "Last Known State" section with new tag
- [ ] Add completed sprint tasks to task history
- [ ] Update current architecture if changed
- [ ] Refresh sprint status information

### 3. SPRINT_HISTORY.md
- [ ] Add sprint summary with:
  - Start and end dates
  - Number of tasks completed
  - Key deliverables
  - Agents involved
  - Major achievements

### 4. TASK_CARDS.md
- [ ] Add sprint closeout task entry
- [ ] Verify all sprint tasks are documented
- [ ] Update task statuses to "Completed"
- [ ] Add time spent for each task

### 5. /postbox/CC/outbox.json
- [ ] Submit sprint closeout report with:
  - Tasks completed count
  - Branches merged list
  - Tag created
  - Documentation updated
  - Key metrics

### 6. Agent Context Files
- [ ] Update CURSOR_CONTEXT.md:
  - Current state and capabilities
  - Recent tasks completed by CA
  - Test infrastructure updates
- [ ] Update WINDSURF_CONTEXT.md:
  - UI/frontend developments
  - WhatsApp integration progress
  - Simulation tools status
- [ ] Review WA_CHECKLIST.md:
  - Ensure checklist reflects current practices
  - Update with any new compliance requirements

## Tag Creation
- [ ] Ensure all changes are committed
- [ ] Create annotated tag:
  ```bash
  git tag -a v0.6.11-alphaX -m "Sprint X complete. Brief summary of achievements"
  ```
- [ ] Verify tag was created: `git tag -l`
- [ ] Push tag (if remote exists): `git push origin v0.6.11-alphaX`

## Sprint Postmortem
- [ ] Create postmortem file: `/docs/release_notes/PHASE_6.11_SPRINT_X_POSTMORTEM.md`
- [ ] Include sections:
  - What Went Well
  - What Could Be Improved
  - Key Metrics
  - Lessons Learned
  - Recommendations for Next Sprint
- [ ] Reference postmortem in ARCH_CONTINUITY.md

## Repository Sync
- [ ] Check repository status: `git status`
- [ ] Ensure working directory is clean
- [ ] If remote exists:
  - [ ] Push all changes: `git push origin main`
  - [ ] Verify remote is up to date
- [ ] If local only:
  - [ ] Document in sprint notes that repo is local-only
  - [ ] Consider backup strategy

## Optional: Test Coverage Snapshot
- [ ] Run test coverage report (if available)
- [ ] Document coverage percentage in postmortem
- [ ] Note any areas needing more tests
- [ ] Compare with previous sprint coverage

## Final Verification
- [ ] All checklist items completed
- [ ] No uncommitted changes: `git status`
- [ ] Tag is visible: `git describe --tags`
- [ ] Documentation is current
- [ ] Next sprint can begin cleanly

---

## Notes
- This checklist should be copied for each sprint closeout
- Customize as needed for specific sprint requirements
- Archive completed checklists in sprint documentation
- Review and update template based on lessons learned
- The sprint summary generator (added in TASK-163F) provides automated activity tracking and improves transparency for agent onboarding