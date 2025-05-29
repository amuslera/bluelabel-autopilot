# Phase 6.15: Practical Agent Orchestration

## Sprint Theme: "Streamlined Multi-Agent Workflow"

### Objective
Optimize the existing outbox-based orchestration system to maximize single developer productivity with multiple AI agents working in parallel.

## Core Principles
1. **Keep It Simple** - Use existing messaging system, no over-engineering
2. **Human in the Loop** - Developer triggers agents, maintains quality control
3. **Progressive Enhancement** - Start manual, automate only proven patterns
4. **Real Work Focus** - Measure success by actual features delivered

## Sprint Goals

### 1. Messaging System Optimization
- Standardize task format across all agents
- Implement task dependencies and signals
- Create templates for common task types
- Add progress tracking to outbox.json

### 2. Developer Experience
- One-command agent status check: `./tools/agent_monitor.py`
- Standardized prompts: "Check your outbox at postbox/[AGENT]/outbox.json"
- Quick complete command: `./tools/complete_task.sh TASK-ID`
- Morning kickoff script to distribute tasks

### 3. Sprint Workflow
```
ARCH Planning → Task Creation → Agent Assignment → Manual Trigger → Execution → Completion
     ↑                                                    │                          │
     └────────────────────── Sprint Progress ────────────┴──────────────────────────┘
```

## Task Distribution Strategy

### Agent Specializations
- **CA (Cursor)**: Frontend, UI/UX, React components
- **CB (Claude Code)**: Backend, APIs, business logic
- **CC (Claude Code)**: Testing, integration, quality
- **WA (Windsurf)**: Infrastructure, DevOps, tooling
- **ARCH (You)**: Planning, coordination, code review

### Task Format
```json
{
  "task_id": "TASK-165A",
  "title": "Implement user dashboard",
  "agent": "CA",
  "priority": "HIGH",
  "dependencies": [],
  "signals_when_done": "Dashboard routes available at /dashboard",
  "context": {
    "previous_work": ["TASK-164B", "TASK-164C"],
    "key_files": ["apps/web/pages/dashboard.tsx"],
    "requirements": "Show user stats, recent activity, quick actions"
  },
  "estimated_hours": 2,
  "deliverables": [
    "Dashboard component with responsive design",
    "Integration with existing auth",
    "Basic unit tests"
  ]
}
```

## Implementation Phases

### Week 1: Foundation
- [ ] Create `.sprint/` directory structure
- [ ] Implement agent_monitor.py (DONE!)
- [ ] Standardize outbox.json format
- [ ] Create task distribution scripts
- [ ] Document agent prompt templates

### Week 2: Workflow Optimization
- [ ] Build sprint progress tracker
- [ ] Add task dependency resolver
- [ ] Create batch task operations
- [ ] Implement completion notifications

### Week 3: Progressive Automation
- [ ] Browser bookmarks for quick prompts
- [ ] CLI shortcuts for common operations
- [ ] Explore safe automation options
- [ ] Performance metrics dashboard

## Success Metrics
- Tasks completed per day (target: 8-12)
- Parallel work efficiency (target: 2-3 agents active)
- Context switch time (target: < 2 minutes)
- Sprint velocity increase (target: 30%+)

## Risk Mitigation
- **Git conflicts**: Branch-per-agent strategy
- **Quality issues**: Mandatory code review checkpoints
- **Context loss**: Automatic work session saving
- **Agent confusion**: Clear task boundaries and dependencies

## Daily Workflow

### Morning (5 min)
```bash
./tools/morning_kickoff.sh
# Updates all outboxes with day's tasks
# Shows sprint progress
# Identifies blockers
```

### During Day
1. Check agent monitor for status
2. Prompt idle agents: "Check your outbox"
3. Agents work independently
4. Complete tasks as they finish
5. Monitor handles progress tracking

### Evening (5 min)
```bash
./tools/end_of_day.sh
# Saves all work states
# Updates sprint progress
# Prepares next day's tasks
```

## Next Immediate Steps

1. **Create Sprint Infrastructure**
```bash
mkdir -p .sprint
touch .sprint/progress.json
touch .sprint/checkpoint.yaml
```

2. **First Task Wave**
- TASK-165A: Sprint infrastructure setup (ARCH)
- TASK-165B: Outbox format standardization (CB) 
- TASK-165C: Task completion scripts (CC)
- TASK-165D: Morning kickoff automation (WA)

3. **Launch Protocol**
- Distribute tasks to agent outboxes
- Start agent monitor in dedicated terminal
- Begin with CA on frontend task
- Scale to parallel execution

Ready to start distributing the first wave of tasks?