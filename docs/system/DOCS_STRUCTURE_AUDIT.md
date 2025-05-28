# 📚 Documentation Audit – Phase 6.13

## ✅ Objective
Propose a unified structure for all technical, agent, sprint, and system documents to improve clarity, maintainability, and onboarding experience.

## 🗂 Current Structure (Audited)

| File | Purpose | Issues Found | Recommendation |
|------|---------|--------------|----------------|
| `/docs/system/ARCH_CONTINUITY.md` | Agent SOP | Redundant with CLAUDE_CONTEXT.md | Keep, merge with CLAUDE_CONTEXT.md |
| `/docs/system/ROLES_AND_RESPONSIBILITIES.md` | Team roles | Well-structured, current | Keep as is |
| `/docs/system/SPRINT_HISTORY.md` | Sprint tracking | Outdated format | Update to match new structure |
| `/docs/system/CLAUDE_CONTEXT.md` | Agent context | Contains duplicate info | Merge with ARCH_CONTINUITY.md |
| `/docs/system/CURSOR_CONTEXT.md` | IDE context | Well-structured | Keep as is |
| `/docs/system/AGENT_ORCHESTRATION_GUIDE.md` | Agent workflow | Needs updating | Update with new structure |
| `/docs/system/ARCH_SIGNOFF_V*.md` | Architecture reviews | Scattered across system/ | Move to phases/architecture/ |
| `/docs/system/WINDSURF_CONTEXT.md` | Project context | Outdated | Archive, create new overview |
| `/docs/system/WA_CHECKLIST.md` | Agent checklist | Should be in agents/ | Move to agents/wa/ |
| `/docs/system/YAML_WORKFLOW_TEMPLATES.md` | Templates | Well-structured | Keep as is |
| `/docs/system/CLI_TEST_RUNNER.md` | Testing guide | Should be in dev/ | Move to dev/testing/ |
| `/docs/system/TASK_161G_CONTEXT_AUDIT.md` | Task audit | Historical | Archive to phases/6.13/audits/ |

## 🧱 Proposed Structure

```plaintext
/docs/
├── system/                    # Core system documentation
│   ├── ROLES_AND_RESPONSIBILITIES.md
│   ├── AGENT_ORCHESTRATION_GUIDE.md
│   ├── YAML_WORKFLOW_TEMPLATES.md
│   └── templates/            # System-wide templates
│
├── phases/                    # Phase-specific documentation
│   ├── current/              # Symlink to current phase
│   └── PHASE_6.13/
│       ├── plan.md
│       ├── sprints/
│       │   ├── SPRINT_1/
│       │   └── SPRINT_2/
│       ├── features/
│       └── architecture/
│           └── signoffs/
│
├── agents/                    # Agent-specific documentation
│   ├── ca/
│   │   ├── onboarding.md
│   │   └── checklist.md
│   ├── cc/
│   └── wa/
│
├── dev/                       # Development documentation
│   ├── testing/
│   ├── architecture/
│   └── guidelines/
│
└── security/                  # Security documentation
    ├── best_practices.md
    └── audit_reports/
```

## 📝 Suggested Fix Tasks

1. **TASK-162I: Restructure Documentation**
   - Create new directory structure
   - Move files to appropriate locations
   - Update cross-references
   - Create symlinks for current phase

2. **TASK-162J: Agent Documentation**
   - Create agent-specific directories
   - Move WA_CHECKLIST.md to agents/wa/
   - Create onboarding guides for each agent
   - Update AGENT_ORCHESTRATION_GUIDE.md

3. **TASK-162K: System Documentation Cleanup**
   - Merge ARCH_CONTINUITY.md and CLAUDE_CONTEXT.md
   - Archive outdated documents
   - Update templates to match new structure
   - Create documentation style guide

4. **TASK-162L: Phase Documentation**
   - Move architecture signoffs to phases/architecture/
   - Create feature documentation structure
   - Update sprint documentation format
   - Create phase transition guide

## 🔄 Hand-off Note

The proposed structure aims to:
1. Reduce duplication and fragmentation
2. Improve navigation and discovery
3. Separate concerns (system, phases, agents)
4. Make maintenance easier
5. Support better onboarding

Final structure proposal must be reviewed by CC during sprint close. Implementation should be phased to minimize disruption.

## 📊 Implementation Plan

1. **Phase 1: Structure Creation**
   - Create new directory structure
   - Set up symlinks
   - Create placeholder files

2. **Phase 2: Content Migration**
   - Move existing files
   - Update cross-references
   - Archive outdated content

3. **Phase 3: Documentation Updates**
   - Create new guides
   - Update templates
   - Add navigation aids

4. **Phase 4: Review & Cleanup**
   - CC review
   - Final adjustments
   - Documentation of new structure 