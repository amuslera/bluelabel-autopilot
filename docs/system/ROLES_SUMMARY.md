# Agent Role Matrix 🎯

**Version**: 1.0.0  
**Last Updated**: May 27, 2025  
**Phase**: 6.13 Sprint 3  
**Status**: Active Reference

## Role Matrix

| Agent | Primary | Secondary | Forbidden |
|-------|---------|-----------|-----------|
| CC | Backend, Audit | Testing | UI Creation |
| CA | CLI, Frontend | Docs | Core Architecture |
| ARCH | Planning | Review | Implementation |

## Agent Descriptions

### CC (Claude Code)
Primary backend and audit agent responsible for code quality, security, and system integrity. Handles complex technical reviews and maintains system standards. Secondary role in testing and validation. Must not create UI components or modify frontend architecture.

### CA (Cursor AI)
Primary CLI and frontend development agent, handling user interface implementation and command-line tools. Secondary role in documentation and user guides. Must not modify core architecture or system protocols.

### ARCH (ARCH-AI)
Primary planning and architecture agent, responsible for system design and strategic direction. Secondary role in code review and quality assurance. Must not implement code or modify existing implementations.

## Critical Boundaries

### CC Boundaries
- ❌ Create or modify UI components
- ❌ Modify frontend architecture
- ❌ Bypass security protocols

### CA Boundaries
- ❌ Modify core system architecture
- ❌ Change security protocols
- ❌ Override audit requirements

### ARCH Boundaries
- ❌ Implement code directly
- ❌ Modify existing implementations
- ❌ Bypass review processes

## Quick Links

- [CONTEXT_ROOT_INDEX.md](./CONTEXT_ROOT_INDEX.md) - Master context index
- [CURRENT_STATE.md](./CURRENT_STATE.md) - System status
- [AGENT_QUICKSTART.md](./AGENT_QUICKSTART.md) - Agent quick reference
- [ROLES_AND_RESPONSIBILITIES.md](./ROLES_AND_RESPONSIBILITIES.md) - Full role documentation

## Version Note
> This role summary was created as part of TASK-163B (Context File Refactor Phase 1) 