# Agent Management Index

This document provides a quick reference for efficiently managing and onboarding agents in the BlueLabel Autopilot multi-agent orchestration system.

## Quick Navigation

### 🚀 Agent Onboarding Guides
- **[CA (Cursor AI Frontend)](AGENT_ONBOARDING_CA.md)** - Frontend, UI/UX, React specialist
- **[CB (Claude Code Backend)](AGENT_ONBOARDING_CB.md)** - Python, API, system architecture specialist  
- **[CC (Claude Code Testing)](AGENT_ONBOARDING_CC.md)** - Testing, QA, security specialist
- **[ARCH (Architecture)](AGENT_ONBOARDING_ARCH.md)** - Coordination, planning, architectural decisions

### 📝 Generic Prompts Library
- **[Generic Agent Prompts](GENERIC_AGENT_PROMPTS.md)** - Standardized prompts for common interactions

### 📋 Supporting Documentation
- **[Agent Autonomy Guidelines](AGENT_AUTONOMY_GUIDELINES.md)** - What agents can do independently
- **[Agent Reporting Standards](AGENT_REPORTING_STANDARDS.md)** - How to report completion and status
- **[Agent Communication Protocol](AGENT_COMMUNICATION_PROTOCOL.md)** - Cross-agent coordination methods

## Quick Start Workflow

### 1. Starting a New Agent Session
```
1. Use appropriate onboarding prompt from Generic_Agent_Prompts.md
2. Agent reads their specific onboarding guide (AGENT_ONBOARDING_{ID}.md)
3. Agent checks their outbox (postbox/{AGENT_ID}/outbox.json)
4. Agent confirms readiness and begins work
```

### 2. Assigning Tasks to Agents
```
1. Update agent's outbox.json with new task
2. Use "Specific Task Assignment" prompt from Generic_Agent_Prompts.md
3. Agent updates status to "in_progress" and executes
4. Agent reports completion using standard format
```

### 3. Checking Agent Status
```
1. Use "Status Request" prompt from Generic_Agent_Prompts.md
2. Review agent's outbox for current task status
3. Check .sprint/progress.json for overall progress
4. Use agent monitor: python tools/agent_monitor_v2.py
```

## Agent Capabilities Summary

| Agent | Primary Skills | Autonomous Actions | Coordination Needs |
|-------|---------------|-------------------|-------------------|
| **CA** | Frontend, UI/UX, React | Component creation, styling, user experience | API contracts, design systems |
| **CB** | Backend, Python, APIs | System architecture, performance optimization | API interfaces, data schemas |
| **CC** | Testing, QA, Security | Test creation, security audits, validation | Integration testing, quality gates |
| **ARCH** | Coordination, Planning | Sprint planning, task distribution, decisions | Strategic direction, resource allocation |

## Common Use Cases

### 🎯 Starting a Sprint
1. **ARCH**: Create sprint plan and distribute tasks
2. **All Agents**: Check outboxes and confirm task assignments
3. **ARCH**: Monitor progress and coordinate dependencies
4. **All Agents**: Execute tasks autonomously within expertise

### 🔄 Daily Coordination
1. **Check Status**: Use agent monitor or status prompts
2. **Resolve Blockers**: Use coordination prompts for dependencies
3. **Update Progress**: Agents update task status and sprint metrics
4. **Address Issues**: Use emergency prompts for critical problems

### ✅ Completing Tasks
1. **Agent**: Complete work and update outbox status
2. **Agent**: Report using standard completion format
3. **ARCH**: Review deliverables and update sprint progress
4. **All**: Coordinate integration and testing as needed

### 📊 Sprint Closeout
1. **All Agents**: Complete final task status updates
2. **ARCH**: Generate sprint summary and metrics
3. **All Agents**: Participate in retrospective
4. **ARCH**: Plan next sprint based on learnings

## Efficiency Tips

### For Human Coordinators
- Use specific prompts from the Generic_Agent_Prompts.md library
- Trust agent autonomy within their expertise areas
- Focus coordination on cross-agent dependencies
- Monitor via agent_monitor_v2.py rather than constant status checks

### For Agent Performance
- Agents should read their onboarding guide completely
- Follow autonomy guidelines to minimize confirmation requests
- Use standard reporting formats for consistency
- Coordinate proactively when dependencies are identified

### For System Optimization
- Keep outbox.json files updated in real-time
- Use sprint progress tracking for visibility
- Leverage agent expertise for independent execution
- Document decisions and learnings for future improvement

## File Locations Quick Reference

### Agent Files
```
postbox/{AGENT_ID}/outbox.json          # Agent tasks and status
docs/system/AGENT_ONBOARDING_{ID}.md    # Agent onboarding guide
```

### System Files
```
.sprint/progress.json                   # Sprint progress tracking
docs/system/GENERIC_AGENT_PROMPTS.md   # Standard prompt library
tools/agent_monitor_v2.py               # Real-time agent monitoring
```

### Documentation
```
docs/system/AGENT_AUTONOMY_GUIDELINES.md
docs/system/AGENT_REPORTING_STANDARDS.md
docs/system/AGENT_COMMUNICATION_PROTOCOL.md
```

## Troubleshooting

### Agent Not Responding Appropriately
1. Use "Autonomy Reminder" prompt
2. Check if agent has current context
3. Provide "Agent Context Refresh" prompt
4. Verify task clarity and requirements

### Cross-Agent Coordination Issues
1. Use "Coordination Request" prompt
2. Check for dependency conflicts in outboxes
3. Update task sequencing if needed
4. Use "Dependency Resolution" prompt

### Sprint Progress Problems
1. Use "Sprint Progress Update" prompt
2. Check individual agent status
3. Identify and resolve blockers
4. Adjust sprint scope if necessary

---

**Quick Access:** Bookmark this index for rapid access to all agent management resources. Use the specific onboarding guides and prompt library to maintain consistent, efficient agent coordination.