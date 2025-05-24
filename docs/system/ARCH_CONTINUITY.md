# ARCH_CONTINUITY.md

## Current Sprint Phase
- **Phase:** 6.10 (Sprint 10)
- **Status:** In Progress

## Last Completed Tasks
- TASK-150H: YAML Plan Dry-Run Execution Preview (CA)
- TASK-150G: YAML Plan Template Generator (CA)
- TASK-150F-B: WA Checklist Enforcement in Planning (CC)
- TASK-150P: Postmortem Integration for Phase 6.9 (CA)

## Pending Tasks
- TASK-150J: ARCH Continuity & Agent Scorecard Infrastructure (CA, current)
- TASK-151A: Next sprint planning (pending)

## Known Agent Behavior
- **WA:** Under review for UI/plan compliance; must follow WA checklist; no backend/CLI changes
- **CC:** Handles merges, backend infra, schema validation; high reliability
- **CA:** CLI, docs, plans; fast, versatile, needs structured scope
- **ARCH:** Orchestrates, assigns one task per agent, enforces branch discipline, manual prompt delivery

## ARCH Preferences
- One-task-per-agent policy
- Manual prompt delivery (no auto-escalation)
- No early merges; all work reviewed before merge
- Strict branch discipline (no direct commits to main/dev)
- Explicit agent-task mapping and reporting
- Use of /TASK_CARDS.md and /postbox/ for state

## Current Agent-Task Map
| Agent | Current Task(s)                | Notes                                 |
|-------|--------------------------------|---------------------------------------|
| ARCH  | Orchestration, review, routing | One-task-per-agent, manual delivery   |
| CC    | Merge, backend, infra          | Handles merges, schema, infra         |
| CA    | CLI, docs, plan tools          | Fast, versatile, needs clear scope    |
| WA    | UI, plan compliance            | Under review, checklist enforcement   |

## Final Phase 6.10 Summary
- **Tag:** v0.6.10-final
- **Tasks Completed:** 19
- **Key Upgrades:**
  - MCP compliance (message schema, validation)
  - Structured trace logging and execution trace files
  - Enhanced task validation and prompt structure
  - WA checklist enforcement and audit
  - CLI lint output improvements (grouping, severity, actionable suggestions)
- **WA Audit & TASK-150E:**
  - WA was incorrectly assigned CLI lint improvements (TASK-150E); work was not merged
  - CA completed TASK-150E with correct CLI grouping, severity, and help text
  - WA score lowered for CLI ownership; CA score increased for clarity and speed

## Transition to Phase 6.11
- **New Focus:** Content Intelligence Workflow MVP
- **Planned Input/Output:** WhatsApp + Web UI → Summarization agents → Daily digest
- **Key Architectural Question:** Audit and extract from bluelabel-AIOS-V2, avoid tech debt
- **Audit in Progress:** TASK-160A (CC)
- **Postmortem in Queue:** TASK-150X (CA, next task)

## Continuity Guidance
- **What to Read to Catch Up:**
  - /TASK_CARDS.md (task status, history)
  - /SPRINT_HISTORY.md (phase summaries)
  - /postbox/ (agent outboxes for reports)
  - This file (/docs/system/ARCH_CONTINUITY.md)
- **Where Context Lives:**
  - /docs/system/ (CLAUDE, CURSOR, WINDSURF, ARCH_AI context files)
- **Prompt Protocol:**
  - One task per agent per cycle
  - Prompt must include: scope, branch, deliverables, checklist
  - Use explicit agent-task mapping and reporting

---

*This file should be updated at the start and end of each sprint, and whenever ARCH is reassigned or agent roles change.* 