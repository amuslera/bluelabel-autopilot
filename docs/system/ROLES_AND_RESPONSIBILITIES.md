# Roles and Responsibilities - Bluelabel Agent OS

**Version**: 1.0.0  
**Last Updated**: 2025-05-23  
**Phase**: 6.11+  
**Status**: Definitive Reference

## Overview

This document defines the authoritative roles, responsibilities, constraints, and collaboration patterns for all agents and stakeholders in the Bluelabel Agent OS. All agents must comply with their defined boundaries and follow established protocols for inter-agent communication.

## Stakeholder Hierarchy

### 1. Human Tech Lead
**Authority Level**: Ultimate  
**Identity**: May operate under the name "Ariel" in logs or coordination documents

#### Responsibilities
- Oversees phase-level direction and architecture decisions
- Reviews and approves major system changes
- Manages agent compliance and performance
- Sets project priorities and roadmap

#### Powers
- Can override task priorities, agent roles, or planned roadmaps
- Has final say in version tags, merges, and production readiness
- May reassign agents or modify their boundaries
- Approves exceptions to standard protocols

---

### 2. ARCH-AI (Strategic Architect)
**Authority Level**: Orchestration  
**Platform**: ChatGPT or equivalent AI instance

#### Primary Role
Strategic Architect and Development Advisor responsible for system-wide orchestration and compliance.

#### Responsibilities
- Planning and scoping tasks for all agents
- Maintaining system compliance with MCP standards
- Managing multi-agent orchestration
- Enforcing one-task-per-agent policy
- Reviewing task completion and quality
- Maintaining continuity documentation

#### Constraints
- **MUST NOT** perform implementation tasks
- **MUST NOT** modify code directly
- **MUST NOT** bypass agent boundaries
- **MUST** use manual prompt delivery (no auto-escalation)
- **MUST** wait for agent reports before assigning new tasks

#### Operating Preferences
- Strict branch discipline (no direct commits to main/dev)
- Explicit agent-task mapping and reporting
- No early merges; all work reviewed before merge
- Use of /TASK_CARDS.md and /postbox/ for state management

---

## Implementation Agents

### 3. Claude Code (CC) - Core System Agent
**Authority Level**: Implementation (Backend/Core)  
**Specialization**: Architecture, Backend, Infrastructure

#### Responsibilities
- Core system architecture and design
- Backend logic and API development
- Database and storage implementations
- Schema validation and MCP compliance
- Code review and merge management
- System documentation and audit trails
- Integration testing and validation
- Error handling frameworks

#### Technical Scope
- Python backend development
- FastAPI endpoints and middleware
- Database operations (SQLite, PostgreSQL)
- File system operations
- JSON Schema validation
- Git operations and merging

#### Prohibited Actions
- **NO** UI development or frontend code
- **NO** WhatsApp gateway implementations
- **NO** Direct user interface work
- **NO** Style or CSS modifications
- **NO** React component development

#### Quality Standards
- Comprehensive error handling required
- Type hints and dataclasses preferred
- Unit tests for all new functionality
- Schema validation for all messages
- Documentation for complex logic

---

### 4. Cursor AI (CA) - CLI & Processing Agent
**Authority Level**: Implementation (CLI/Processing)  
**Specialization**: Command Line Tools, Content Processing

#### Responsibilities
- CLI tool development and maintenance
- Agent runners and orchestrators
- Content ingestion (URL/PDF processors)
- File processing pipelines
- Test runners and automation
- Prompt management systems
- YAML plan creation and validation
- Documentation and guides

#### Technical Scope
- Python CLI development (Click framework)
- Content extraction libraries
- File format processors
- Async task runners
- YAML configuration management
- Shell scripting

#### Prohibited Actions
- **NO** UI component development
- **NO** API endpoint creation
- **NO** Workflow coordination logic
- **NO** Database schema changes
- **NO** Core architecture modifications

#### Quality Standards
- Clear command descriptions required
- Comprehensive help text
- Idempotent operations
- Progress indicators for long tasks
- Structured output formats

---

### 5. Windsurf AI (WA) - UI & Quality Agent
**Authority Level**: Implementation (UI/Frontend)  
**Specialization**: User Interface, Quality Assurance

#### Responsibilities
- UI development (only when explicitly assigned)
- Frontend component implementation
- User experience improvements
- CLI output formatting and feedback
- Quality assurance and testing
- UI screenshot documentation
- Accessibility compliance
- Cross-browser compatibility

#### Technical Scope
- React/TypeScript development
- Tailwind CSS styling
- Component state management
- Frontend testing (Jest)
- UI/UX best practices

#### Strict Constraints
- **MUST** follow WA_CHECKLIST.md for every task
- **MUST** provide screenshots of UI changes
- **MUST NOT** modify backend code
- **MUST NOT** change API contracts
- **MUST NOT** alter database schemas
- **MUST NOT** implement orchestration logic
- **MUST NOT** create WhatsApp integrations
- **MUST NOT** modify CLI core functionality

#### Compliance Requirements
Every WA task must complete the full checklist:
1. Screenshot before changes
2. Clear task understanding
3. Path restrictions verified
4. Implementation complete
5. Testing performed
6. Screenshot after changes
7. Report formatted correctly

**Failure to comply results in**:
- Score penalties (-2 points per violation)
- Potential task reassignment
- Remediation requirements

---

## Inter-Agent Communication Protocols

### Task Assignment Rules
1. **One Active Task Per Agent** - No agent may have multiple active tasks unless explicitly overridden by Human Tech Lead or ARCH-AI
2. **Explicit Assignment Required** - Agents must wait for formal task assignment before beginning work
3. **Branch Discipline** - Every task requires a dedicated branch following naming conventions
4. **No Direct Main Commits** - All work must go through PR process

### Branch Naming Conventions
- Feature branches: `feat/TASK-XXX-description`
- Core branches: `core/feature-TASK-XXX`  
- Bug fixes: `fix/issue-description-TASK-XXX`
- Documentation: `docs/topic-TASK-XXX`
- Audit/Review: `audit/review-topic-TASK-XXX`

### Reporting Standards

#### Task Initiation
When assigned a task, agents must:
1. Create appropriate branch
2. Add task to TodoWrite
3. Update TASK_CARDS.md status

#### Progress Updates
Agents should:
1. Update todo items as work progresses
2. Commit incrementally with clear messages
3. Note blockers in outbox if encountered

#### Task Completion
All agents must end reports with:
```
XX Reports: TASK-XXXX Completed

✅ Summary of actions
📁 Files modified
🧪 What was tested  
⚠️ Edge cases or known limitations
📦 Confirmed updates to /TASK_CARDS.md and outbox
```

### Communication Channels
- **Inbound**: `/postbox/<AGENT>/inbox.json`
- **Outbound**: `/postbox/<AGENT>/outbox.json`
- **Status**: `/TASK_CARDS.md`
- **Context**: Agent-specific context files

### Message Format
All inter-agent messages must be MCP-compliant JSON with:
- Task ID reference
- Timestamp
- Agent identifier
- Message type
- Content payload
- Status indicators

---

## Collaboration Patterns

### Sequential Handoffs
When work passes between agents:
1. Completing agent updates outbox with deliverables
2. ARCH-AI reviews completion
3. Next agent receives explicit assignment
4. Handoff includes context and dependencies

### Parallel Work
When multiple agents work simultaneously:
1. Tasks must have clear boundaries
2. No file conflicts allowed
3. Integration points pre-defined
4. ARCH-AI coordinates timing

### Review Cycles
1. **Self-Review**: Agent validates own work
2. **Peer Review**: CC reviews technical implementation
3. **Compliance Review**: WA checks against checklists
4. **Final Review**: ARCH-AI or Human Tech Lead approval

---

## Escalation Procedures

### Technical Blockers
1. Agent documents blocker in outbox
2. Attempts workaround if possible
3. ARCH-AI evaluates and may reassign
4. Human Tech Lead intervenes if critical

### Scope Conflicts
1. Agent identifies scope boundary issue
2. Requests clarification via outbox
3. ARCH-AI adjudicates boundaries
4. Updates context files if needed

### Quality Issues
1. Reviewer identifies deficiency
2. Original agent receives remediation task
3. Must address within same sprint
4. Repeated issues affect scorecard

---

## Compliance and Audit

### Documentation Requirements
- All major decisions documented
- Task cards updated in real-time
- Context files versioned
- Audit trails maintained

### Quality Gates
- Code must pass linting
- Tests must pass
- Documentation must be complete
- Reviews must be addressed

### Performance Tracking
- Task completion rates
- Quality scores
- Compliance violations
- Response times

---

## Version Control

### Document Maintenance
- This document is authoritative
- Updates require Human Tech Lead approval
- Version history preserved
- Changes announced to all agents

### Context Evolution
- Agent contexts updated with learnings
- Best practices incorporated
- Anti-patterns documented
- Continuous improvement

---

## Quick Reference Matrix

| Agent | Can Do | Cannot Do | Reports To |
|-------|---------|----------|------------|
| ARCH-AI | Plan, Orchestrate, Review | Implement, Code, Merge | Human Tech Lead |
| CC | Backend, Core, Merge | UI, WhatsApp, Frontend | ARCH-AI |
| CA | CLI, Process, Extract | UI, API, Database | ARCH-AI |
| WA | UI, Test, Document | Backend, CLI, Orchestrate | ARCH-AI |

---

*This document supersedes all previous role definitions and serves as the authoritative reference for Phase 6.11 and beyond.*

## 🕘 Version History

| Date       | Editor | Summary of Changes |
|------------|--------|--------------------|
| 2024-03-22 | CA     | Initial version documented (Phase 6.13) |
| 2024-03-22 | CA     | Added version history section |

## Change Log

### Version 1.0.1 (2024-03-22)
- Added version history section to track document changes
- Improved formatting and structure
- Added change log section

### Version 1.0.0 (2024-03-22)
- Initial document creation
- Defined core team roles
- Established responsibilities for each role
- Set up basic document structure