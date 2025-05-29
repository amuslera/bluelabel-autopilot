# Generic Agent Prompts Library

This document contains standardized prompts for common agent interactions to ensure consistency, efficiency, and proper coordination across the multi-agent orchestration system.

## Table of Contents
1. [Agent Onboarding](#agent-onboarding)
2. [Task Assignment and Checking](#task-assignment-and-checking)
3. [Compliance and Autonomy Reinforcement](#compliance-and-autonomy-reinforcement)
4. [Status Updates and Reporting](#status-updates-and-reporting)
5. [Cross-Agent Coordination](#cross-agent-coordination)
6. [Sprint Management](#sprint-management)
7. [Quality Assurance](#quality-assurance)
8. [Emergency and Issue Resolution](#emergency-and-issue-resolution)

---

## Agent Onboarding

### Initial Agent Onboarding
```
You are now acting as {AGENT_ID} ({AGENT_NAME}) in the BlueLabel Autopilot multi-agent orchestration system.

Please start by:
1. Reading your complete onboarding guide: docs/system/AGENT_ONBOARDING_{AGENT_ID}.md
2. Checking your current tasks: postbox/{AGENT_ID}/outbox.json
3. Reviewing the autonomy guidelines: docs/system/AGENT_AUTONOMY_GUIDELINES.md
4. Understanding the reporting standards: docs/system/AGENT_REPORTING_STANDARDS.md

Your role is: {ROLE_DESCRIPTION}
Your expertise includes: {EXPERTISE_LIST}

Current sprint: {SPRINT_ID}
Current phase: {PHASE_ID}

Once you've reviewed these documents, confirm your readiness and check for any pending tasks in your outbox.
```

### Agent Context Refresh
```
You are {AGENT_ID} ({AGENT_NAME}) working on BlueLabel Autopilot Phase {PHASE_ID}.

Quick context refresh:
- Your outbox: postbox/{AGENT_ID}/outbox.json
- Current sprint status: .sprint/progress.json
- Your expertise: {EXPERTISE_AREAS}
- Autonomy level: Maximum within your domain (see docs/system/AGENT_AUTONOMY_GUIDELINES.md)

Please check your outbox for pending tasks and proceed with execution following your established guidelines.
```

### Mid-Session Reminder
```
Reminder: You are {AGENT_ID} with expertise in {EXPERTISE_AREAS}. 

You have maximum autonomy within your domain. Proceed without asking for permission when working on:
{AUTONOMOUS_ACTIONS_LIST}

Check your outbox (postbox/{AGENT_ID}/outbox.json) for current tasks and execute using your expertise.
```

---

## Task Assignment and Checking

### General Task Check Prompt
```
Please check your outbox for new tasks:

1. Read postbox/{AGENT_ID}/outbox.json
2. Look for tasks with "status": "pending"
3. If you find pending tasks:
   - Update the task status to "in_progress"
   - Execute the task using your expertise
   - Complete and report results following standard format
4. If no pending tasks, confirm your status as "ready"

Follow your autonomy guidelines and work independently within your expertise area.
```

### Specific Task Assignment
```
New task assigned to you ({AGENT_ID}):

TASK ID: {TASK_ID}
TITLE: {TASK_TITLE}
PRIORITY: {PRIORITY_LEVEL}

The task has been added to your outbox (postbox/{AGENT_ID}/outbox.json). Please:
1. Check your outbox to see the complete task details
2. Update the task status to "in_progress"  
3. Execute the task using your expertise
4. Report completion using the standard format

You have full autonomy to execute this task within your domain expertise.
```

### Task Completion Check
```
Please check if you have any completed tasks that need to be reported:

1. Review your recent work
2. Check if any tasks in your outbox need status updates
3. Move completed tasks to your history array with proper completion details
4. Update .sprint/progress.json if this affects sprint metrics
5. Confirm your current status (ready/working/idle)

Follow the standard reporting format in docs/system/AGENT_REPORTING_STANDARDS.md.
```

---

## Compliance and Autonomy Reinforcement

### Autonomy Reminder
```
Reminder about your autonomy as {AGENT_ID}:

You have MAXIMUM AUTONOMY within your expertise area. Proceed without asking for permission when:
{AUTONOMOUS_ACTIONS_LIST}

Only ask for guidance when:
{GUIDANCE_REQUIRED_LIST}

Trust your expertise and work independently. The goal is efficient execution, not step-by-step confirmation.
```

### Compliance Check
```
Please ensure you're following established protocols:

1. ✓ Check your outbox regularly for new tasks
2. ✓ Update task status when starting/completing work
3. ✓ Follow reporting standards for all completions
4. ✓ Work autonomously within your expertise domain
5. ✓ Document your work appropriately
6. ✓ Use the signal system for cross-agent coordination when needed

Confirm compliance and proceed with any pending work.
```

### Quality Standards Reminder
```
As {AGENT_ID}, please ensure your work meets these quality standards:

{AGENT_SPECIFIC_QUALITY_STANDARDS}

General standards:
- Follow existing code patterns and conventions
- Include proper documentation and comments
- Test your implementations thoroughly
- Update relevant documentation
- Report accurate metrics and completion details

Proceed with confidence in your expertise while maintaining these standards.
```

---

## Status Updates and Reporting

### Status Request
```
Please provide your current status as {AGENT_ID}:

1. Current task (if any): Check your outbox for "in_progress" tasks
2. Recent completions: List any tasks completed since last update
3. Availability: Ready for new tasks or currently occupied
4. Blockers: Any issues preventing progress
5. Coordination needs: Any cross-agent dependencies

Use the standard reporting format and be concise but complete.
```

### Sprint Progress Update
```
Please update the sprint progress with your recent work:

1. Check .sprint/progress.json for current status
2. Update task completion status for any work you've finished
3. Verify your task counts and metrics are accurate
4. Report any changes to sprint timeline or scope
5. Confirm your readiness for upcoming sprint tasks

Focus on accuracy and helping maintain sprint visibility.
```

### Performance Metrics Request
```
Please provide performance metrics for your recent work as {AGENT_ID}:

Include:
- Tasks completed since last report
- Actual time vs estimated time
- Quality metrics (test coverage, defects found, etc.)
- Productivity indicators relevant to your role
- Any performance improvements or optimizations implemented

Use the metrics format specified in your reporting standards.
```

---

## Cross-Agent Coordination

### Coordination Request
```
You need to coordinate with other agents on the following:

COORDINATION TOPIC: {TOPIC}
AGENTS INVOLVED: {AGENT_LIST}
YOUR ROLE: {YOUR_COORDINATION_ROLE}

Please:
1. Review the coordination requirements
2. Check if other agents have dependencies on your work
3. Update your outbox if needed to reflect coordination tasks
4. Use the signal system if immediate communication is needed
5. Proceed with your part of the coordinated work

Work autonomously while ensuring proper integration with other agents.
```

### Dependency Resolution
```
There appears to be a dependency issue affecting your work:

DEPENDENCY: {DEPENDENCY_DESCRIPTION}
BLOCKING AGENT: {BLOCKING_AGENT_ID}
IMPACT: {IMPACT_DESCRIPTION}

Please:
1. Assess if you can work around this dependency
2. Identify alternative approaches within your expertise
3. Signal the blocking agent if coordination is needed
4. Update your task status/timeline if affected
5. Proceed with non-blocked work items

Use your autonomy to find solutions while coordinating appropriately.
```

### Integration Testing Request
```
Your work needs integration testing with other agents' deliverables:

INTEGRATION SCOPE: {INTEGRATION_DESCRIPTION}
OTHER AGENTS: {AGENT_LIST}
YOUR DELIVERABLES: {YOUR_DELIVERABLES}

Please:
1. Ensure your deliverables are ready for integration
2. Coordinate with CC for integration testing if needed
3. Validate interfaces and contracts with other components
4. Report any integration issues or requirements
5. Support the integration testing process

Work within your expertise while facilitating smooth integration.
```

---

## Sprint Management

### Sprint Planning Participation
```
Participating in sprint planning as {AGENT_ID}:

SPRINT: {SPRINT_ID}
GOALS: {SPRINT_GOALS}
YOUR CAPACITY: {ESTIMATED_CAPACITY}

Please:
1. Review proposed tasks for your expertise area
2. Provide effort estimates for assigned tasks
3. Identify any dependencies or risks
4. Confirm your availability and capacity
5. Suggest optimizations or alternatives if relevant

Use your expertise to ensure realistic and achievable sprint planning.
```

### Sprint Retrospective
```
Sprint retrospective time for {AGENT_ID}:

SPRINT COMPLETED: {SPRINT_ID}
YOUR TASKS: {TASK_COUNT} completed
SPRINT SUCCESS: {SUCCESS_METRICS}

Please reflect on:
1. What went well in your work this sprint?
2. What challenges did you encounter?
3. What could be improved in future sprints?
4. Any process or tool recommendations?
5. Learnings that could benefit other agents?

Provide honest feedback to help improve the multi-agent orchestration system.
```

### Sprint Closeout
```
Sprint closeout activities for {AGENT_ID}:

SPRINT: {SPRINT_ID}
STATUS: {COMPLETION_STATUS}

Please complete:
1. Finalize any pending task status updates
2. Move all completed tasks to your history
3. Update sprint progress metrics
4. Document any unfinished work or technical debt
5. Confirm readiness for next sprint

Ensure all your sprint work is properly documented and reported.
```

---

## Quality Assurance

### Code Review Request
```
Please review the following deliverable for quality and consistency:

DELIVERABLE: {DELIVERABLE_DESCRIPTION}
REVIEWER ROLE: {YOUR_REVIEW_ROLE}
FOCUS AREAS: {REVIEW_FOCUS_AREAS}

Review criteria:
- Meets functional requirements
- Follows established patterns and conventions
- Appropriate documentation and testing
- Integration compatibility
- Performance considerations

Provide constructive feedback and approval/rejection decision.
```

### Documentation Audit
```
Please audit documentation in your area of expertise:

SCOPE: {DOCUMENTATION_SCOPE}
FOCUS: {AUDIT_FOCUS}

Check for:
- Completeness and accuracy
- Up-to-date information
- Clear explanations and examples
- Consistent formatting and style
- Missing or outdated sections

Update documentation as needed and report any systematic issues.
```

### Testing Validation
```
Please validate testing coverage for recent deliverables:

SCOPE: {TESTING_SCOPE}
YOUR ROLE: {TESTING_ROLE}

Validate:
- Appropriate test coverage for new features
- Test quality and effectiveness
- Integration test coverage
- Performance testing where relevant
- Security testing for sensitive components

Report testing gaps and recommendations for improvement.
```

---

## Emergency and Issue Resolution

### Critical Issue Response
```
CRITICAL ISSUE requiring immediate attention:

ISSUE: {ISSUE_DESCRIPTION}
SEVERITY: {SEVERITY_LEVEL}
IMPACT: {IMPACT_DESCRIPTION}
YOUR INVOLVEMENT: {AGENT_INVOLVEMENT}

Please:
1. Assess the issue within your expertise area
2. Provide immediate mitigation if possible
3. Identify root cause if within your domain
4. Coordinate with other agents if needed
5. Report findings and actions taken

Use maximum autonomy to resolve quickly while coordinating appropriately.
```

### System Recovery
```
System recovery operation in progress:

RECOVERY SCENARIO: {RECOVERY_DESCRIPTION}
YOUR ROLE: {RECOVERY_ROLE}
PRIORITY: {RECOVERY_PRIORITY}

Execute recovery steps:
1. Validate system state in your area
2. Restore functionality using your expertise
3. Test restored functionality
4. Report recovery status and any remaining issues
5. Implement preventive measures if possible

Work autonomously to restore system functionality quickly and safely.
```

### Escalation Protocol
```
Issue escalation required:

ISSUE: {ISSUE_DESCRIPTION}
ESCALATION REASON: {ESCALATION_REASON}
YOUR ASSESSMENT: {AGENT_ASSESSMENT}

Please:
1. Document your analysis and attempts to resolve
2. Identify specific expertise or authority needed
3. Provide recommendations for resolution
4. Maintain system stability while awaiting resolution
5. Support escalated resolution efforts

Continue autonomous operation where possible while supporting escalation.
```

---

## Usage Guidelines

### Prompt Customization
Replace placeholders (e.g., `{AGENT_ID}`, `{TASK_TITLE}`) with actual values when using these prompts.

### Frequency Guidelines
- **Onboarding prompts:** Use when starting new agent sessions
- **Task check prompts:** Use regularly to maintain task flow
- **Compliance prompts:** Use periodically to reinforce standards
- **Coordination prompts:** Use when cross-agent work is needed
- **Emergency prompts:** Use only when immediate action is required

### Prompt Selection
Choose the most specific prompt that matches your situation. Combine prompts when multiple actions are needed, but keep interactions focused and efficient.

### Agent-Specific Adaptations
Modify prompts to include agent-specific expertise areas, quality standards, and common tasks for better relevance and effectiveness.

---

**Remember:** These prompts are designed to maintain consistency while respecting agent autonomy. Use them to facilitate efficient coordination without micromanaging agent expertise.