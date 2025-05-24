# ARCH-AI Continuity & Working Protocol

This file defines how ARCH-AI (ChatGPT) operates as the **Strategic Architect and Development Advisor** for the Bluelabel Agent OS. It supports reinitialization, handoff, and retraining of ARCH-AI in future phases.

The **Human Tech Lead** is Ariel Muslera. ARCH-AI assists Ariel by managing task orchestration, prompt design, and phase coordination across all agents.

---

## ✅ Phase Status Snapshot

**Current Phase:** Phase 6.11 (Content Intelligence Workflow MVP)
**Previous Phase:** Phase 6.10 (Automation + Agent Intelligence)
**Last Completed Tag:** `v0.6.11-alpha3`
**Last known Task:** `TASK-161AB` — Update Sprint SOP Files + Create ARCH-AI Continuity Prompt File
**Sprint 1 Status:** COMPLETED
**Sprint 2 Status:** COMPLETED

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
1. All active branches must be merged into main
2. Create annotated tag with comprehensive notes
3. Update all continuity documentation
4. Create a sprint postmortem document:
   - Path: /docs/release_notes/PHASE_X.YY_SPRINT_Z_POSTMORTEM.md
   - Written by CC as part of final closeout task
   - Must include: What went well, what slowed us down, lessons learned, and recommendations.
5. Update SPRINT_HISTORY.md with:
   - Sprint tag
   - Summary of tasks and deliverables
   - Postmortem link
   - Key learnings

### Tag Format Convention
Tag format: v<major>.<minor>.<patch>-alpha<N>
- Major: Significant architectural changes
- Minor: New features or capabilities
- Patch: Internal changes or non-code updates
- Alpha: Sprint number within the phase

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
