# Agent Roster - Bluelabel Agent OS

**Version**: 2.0.0  
**Last Updated**: May 27, 2025  
**Phase**: 6.13 Sprint 2  
**Status**: Current Reference

## Active Agents (as of Sprint 2)

| Agent | Full Name | Role | Model | Responsibilities | Notes |
|-------|-----------|------|-------|-------------------|-------|
| CA | Cursor AI | Core Agent | GPT-4 via Cursor | Backend, CLI, UI components | Also handles WA's decommissioned scope |
| CC | Claude Code | Core Agent | Claude 3 | Backend audits, merges, review, orchestration | Primary code review agent |
| ARCH | ARCH-AI | System Architect | GPT-4 | Planning, prompting, continuity, phase oversight | Strategic system coordination |

## Decommissioned Agents

> WA (Windsurf AI) was decommissioned in Sprint 2 (see `/docs/agents/WA_LEGACY_REPORT.md`) due to persistent execution and process failures.

## Agent Context Files

The following files contain detailed context and configuration for each agent:

- `/docs/system/CURSOR_CONTEXT.md` - CA's operational parameters and capabilities
- `/docs/system/CLAUDE_CONTEXT.md` - CC's system integration and review protocols
- `/docs/system/ARCH_CONTINUITY.md` - ARCH's strategic planning and oversight framework
- `/docs/agents/WA_LEGACY_REPORT.md` (archived) - Historical record of WA's decommissioning

## System Interaction Flow

```mermaid
graph TD
    ARCH[ARCH-AI]
    CA[CA (Cursor AI)]
    CC[CC (Claude Code)]
    
    %% Strategic Planning Flow
    ARCH -->|Strategic Planning| CA
    ARCH -->|System Architecture| CC
    
    %% Task Execution Flow
    CA -->|Code Implementation| CC
    CA -->|Documentation| ARCH
    
    %% Review Flow
    CC -->|Code Review| CA
    CC -->|Architecture Review| ARCH
    
    %% Legend
    subgraph Legend
        L1[Strategic Planning]
        L2[Implementation]
        L3[Review]
    end
```

## Version Note
> Agent roster last updated during Sprint 2 (May 27, 2025) 