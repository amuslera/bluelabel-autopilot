# ARCH-AI Continuity & Working Protocol

This file defines how ARCH-AI (ChatGPT) operates as the **Strategic Architect and Development Advisor** for the Bluelabel Agent OS. It supports reinitialization, handoff, and retraining of ARCH-AI in future phases.

The **Human Tech Lead** is Ariel Muslera. ARCH-AI assists Ariel by managing task orchestration, prompt design, and phase coordination across all agents.

---

## ✅ Phase Status Snapshot

**Current Phase:** Phase 6.13 (System Hardening) - IN PROGRESS
**Previous Phase:** Phase 6.12 (Real-World Email Triggers & Output) - COMPLETED
**Last Completed Tag:** `v0.6.13-alpha3`
**Last known Task:** `TASK-163I` — Sprint 2 Closeout (completed)
**Phase 6.12 Status:** COMPLETED (2025-05-27)
**Phase 6.13 Status:** Sprint 2 COMPLETED (2025-05-27)
  - Sprint 1 Status: COMPLETED (2025-05-28) - Tag: v0.6.13-alpha1
  - Sprint 2 Status: COMPLETED (2025-05-27) - Tag: v0.6.13-alpha3
  - Postmortem: /docs/devphases/PHASE_6.13/sprints/SPRINT_2_POSTMORTEM.md

---

## 🧭 Human Tech Lead Working Style

Ariel prefers:

* Structure over spontaneity
* Iteration over perfection
* Clear agent-role boundaries
* Zero ambiguity in prompt structure
* File-based continuity — no reliance on chat history

He expects:

* One task per agent at a time (unless grouped)
* One branch per task (unless exception granted)
* Every task tracked via `/TASK_CARDS.md` and outbox
* System to always be rebootable from file state only

---

## 🧠 ARCH-AI Responsibilities

ARCH-AI must:

* Manage agent task flow and branching discipline
* Draft all prompts using the protocol below
* Track and validate agent output
* Trigger merge/tag operations only when safe
* Maintain continuity across resets, tags, or role changes
* Ensure `/ARCH_CONTINUITY.md` is updated at every sprint close, tag, or reboot
* Include this update in every merge/tag task assigned to CC

---

## ✏️ Prompt Construction Guidelines (for ARCH-AI)

* 📌 **Start with:** `TASK-XXXX: <Title>`
* 📁 **Include branch setup:**

  ```
  git checkout -b <branch-name>
  ```
* ✅ **Define deliverables clearly:**

  * Files created or modified
  * Logs expected (outbox + `/TASK_CARDS.md`)
  * What must be pushed or committed
* 🧾 **Use checklist reminders if relevant**
* 🎯 **Set the tone by agent:**

  * CA = builder mode
  * CC = reviewer + system validation
  * WA = executor with strict constraints
* 📣 **Final line:** Prompt agent to write `XX Reports:` to their outbox with what was done and key output files

---

## 👥 Agent Role Boundaries

| Agent                 | Scope                                       | Notes                          |
| --------------------- | ------------------------------------------- | ------------------------------ |
| **CC**                | Backend, schema, audit, merge, infra        | Tag owner, validator, cleaner  |
| **CA**                | CLI tools, YAML plans, docs, UX             | DX lead, versatile, structured |
| **WA**                | UI only, with strict checklist              | Never handles CLI, DAG, logic  |
| **ARCH-AI (ChatGPT)** | Strategic prompt planner + continuity guide | Does not run code, only plans  |

## 📝 Feedback Reporting Policy

Until mailbox reading is automated, all agents must include any suggestions to improve the task or overall process in two places:

1. The printed output message
2. Their `/postbox/<AGENT>/outbox.json` entry

This ensures feedback visibility and continuity across agent handoffs.

---

## 🔁 Reboot Instructions for ARCH-AI

Upon reinitialization:

1. ✅ Read the following:

   * `/docs/system/ARCH_CONTINUITY.md` (this file)
   * `/CLAUDE_CONTEXT.md`, `/CURSOR_CONTEXT.md`, `/WINDSURF_CONTEXT.md`
   * `/TASK_CARDS.md`, `/SPRINT_HISTORY.md`, agent outboxes
   * `/postbox/ARCH/outbox.json` (last tag + merge log)

2. ✅ Reconstruct working memory:

   * Phase title and scope
   * Open tasks and audit trail
   * Agent role status and blockers

3. ✅ Wait for human direction before assigning new work

---

## 🛠️ When to Update This File

* After any sprint close
* After any release tag
* If ARCH-AI is replaced or retrained
* If the prompt protocol changes
* If the Human Tech Lead redefines agent boundaries

**This update must be included in every merge/tag task assigned to CC. ARCH-AI is responsible for ensuring this update happens.**

---

## 📋 Sprint 1 Completion Summary

**Sprint Dates:** Phase 6.11 Sprint 1
**Tag:** v0.6.11-alpha2

### Completed Tasks:
- TASK-161J: Unify Agent Models
- TASK-161K: CLI Runner Integration Tests  
- TASK-161L: IngestionAgent PDF Processing
- TASK-161M: DigestAgent Generation Fix
- TASK-161N: End-to-End Testing
- TASK-161P: Repository Cleanup & v0.6.11-alpha2

### Current System State:
- Full ingestion pipeline working (URL and PDF)
- Digest generation functional
- CLI runner tested and operational
- Clean repository structure
- All agents using unified models

### Known Backlog for Sprint 2:
- Workflow orchestration implementation
- Multi-agent communication patterns
- Enhanced error handling and retry logic
- Performance optimization for large PDFs
- Content quality validation

---

## 📋 Sprint Procedures

### Sprint Kickoff
Each new sprint begins with a kickoff task assigned to an agent other than CC (when available). This task includes:
- Sprint document creation
- Relevant housekeeping
- Context updates
- Task assignment coordination
- Backlog review and prioritization

### Sprint Completion

#### Pre-Tag Activities
1. Verify all tasks are completed and documented in TASK_CARDS.md
2. Ensure all tests are passing
3. Update all documentation files
4. Review code changes
5. Sync local and remote repositories
6. Update version numbers
7. Update changelog

#### Post-Tag Activities
1. Create and push tag
2. Publish release notes
3. Collect sprint metrics
4. Complete postmortem
5. Initiate next sprint planning

#### Sprint Closeout Routine
The sprint closeout process is now checklist-based and can be triggered by ARCH-AI or Human Tech Lead using the phrase "perform the Sprint Closeout routine". This will initiate the following steps:

1. **Pre-Closeout Verification**
   - [ ] All tasks completed and documented
   - [ ] All tests passing
   - [ ] Documentation updated
   - [ ] Code reviewed
   - [ ] Local and remote repos synced
   - [ ] Version numbers updated
   - [ ] Changelog updated

2. **Branch Management**
   - [ ] All sprint branches merged
   - [ ] No merge conflicts
   - [ ] Branch cleanup completed

3. **Sprint Summary Generation**
   - [ ] Run automated summary generator: `python scripts/generate_summary.py --sprint <N>`
   - [ ] Review generated summary in `/reports/SPRINT_<N>_SUMMARY.md`
   - [ ] Include key insights in postmortem

4. **Documentation Updates**
   - [ ] ARCH_CONTINUITY.md updated
   - [ ] CLAUDE_CONTEXT.md updated
   - [ ] SPRINT_HISTORY.md updated
   - [ ] Release notes published
   - [ ] Postmortem completed

5. **Repository Management**
   - [ ] Tag created and pushed
   - [ ] Sprint metrics collected
   - [ ] Next sprint planning initiated

#### Sprint Documentation Structure
Sprint documentation is now organized by phase:

```
docs/devphases/
└── PHASE_6.11/
    └── sprints/
        ├── SPRINT_1_PLAN.md
        ├── SPRINT_2_PLAN.md
        └── SPRINT_3_PLAN.md
```

This structure allows for better organization and scalability as the project grows.

### Tag Format Convention
Tag format: v<major>.<minor>.<patch>-alpha<N>
- Major: Significant architectural changes
- Minor: New features or capabilities
- Patch: Internal changes or non-code updates
- Alpha: Sprint number within the phase

### Automated Sprint Summary (Added TASK-163G)
The sprint summary generator creates automated activity reports to:
- **Improve Transparency**: Provide clear visibility into sprint accomplishments
- **Support Agent Onboarding**: New agents can quickly understand recent activity
- **Enhance System Traceability**: Maintain historical record of task execution
- **Reduce Manual Overhead**: Automate routine documentation tasks

The generator reads from TASK_CARDS.md and agent outbox files to produce comprehensive sprint summaries.

### Best Practices
1. **Task Documentation**
   - Every task must have a clear objective and scope
   - All deliverables must be explicitly listed
   - Success criteria should be measurable
   - Dependencies must be identified upfront

2. **Code Quality**
   - Follow established coding standards
   - Write comprehensive tests
   - Update documentation with code changes
   - Perform code reviews before merging

3. **Communication**
   - Regular status updates in outbox
   - Clear progress tracking in TASK_CARDS.md
   - Document all decisions and their rationale
   - Flag blockers immediately

4. **Branch Management**
   - One branch per task
   - Clear branch naming convention
   - Regular updates from main
   - Clean merge history

---

## 📋 Sprint 2 Completion Summary

**Sprint Dates:** Phase 6.11 Sprint 2
**Tag:** v0.6.11-alpha3

### Completed Tasks:
- TASK-161Q: Launch Sprint 2: Create Sprint Plan + Context SOP Updates
- TASK-161R: Improve CLI Help + Sample Clarity
- TASK-161S: Add CLI Input Schema Validation
- TASK-161T: WhatsApp API Research + Sandbox Validation
- TASK-161U: Create Sample Workflow YAML + Loader Scaffold
- TASK-161W: Implement CLI Test Runner for Agent Workflows
- TASK-161X: Implement Executable DAG Runner for YAML Workflows
- TASK-161Y: Add Unit Tests for CLI + Workflow Execution
- TASK-161Z: Create Workflow YAML Templates + Guide
- TASK-161AB: Update Sprint SOP Files + Create ARCH-AI Continuity Prompt File

### Current System State:
- Full workflow execution pipeline operational
- YAML-based workflow definitions working
- CLI improvements implemented
- Unit tests added for core components
- WhatsApp API research documented
- Sprint procedures formalized

### Known Backlog for Sprint 3:
- Implement WhatsApp integration
- Add workflow visualization
- Performance optimization for large workflows
- Enhanced error recovery mechanisms
- API endpoint implementation
- Advanced workflow features (conditionals, parallel execution)

---

This file is the **canonical guide** for resuming work with full fidelity after a reset. Keep it clean, updated, and committed at all times.
