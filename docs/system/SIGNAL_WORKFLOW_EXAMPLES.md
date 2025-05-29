# Signal Workflow Examples
## TASK-165I Agent Communication Protocol

> 📋 **Common signal flow patterns and real-world communication scenarios**

## Overview

This document provides practical examples of how agents use the communication protocol to coordinate work, resolve dependencies, and handle various scenarios in the multi-agent system.

## 🔄 Workflow Patterns

### 1. Task Dependency Chain

**Scenario**: Frontend task needs backend API, which needs database setup

```bash
# Step 1: CB signals blocked waiting for infrastructure
AGENT_ID=CB python3 tools/send_signal.py \
  --type BLOCKED \
  --to WA \
  --message "Cannot proceed with API development until database is ready" \
  --context '{"blocked_task": "TASK-API-001", "waiting_for": "database_setup", "urgency": "HIGH"}'

# Step 2: WA signals ready to help
AGENT_ID=WA python3 tools/send_signal.py \
  --type READY \
  --to CB \
  --message "Database infrastructure ready, can assist with setup" \
  --context '{"available_for": ["database", "infrastructure"], "estimated_time": "2 hours"}'

# Step 3: WA signals completion
AGENT_ID=WA python3 tools/send_signal.py \
  --type COMPLETED \
  --message "Database setup complete, API development can proceed" \
  --context '{"completed_task": "database_setup", "deliverables": ["database_schema", "connection_config"]}'

# Step 4: CB signals API completion and requests frontend handoff
AGENT_ID=CB python3 tools/send_signal.py \
  --type HANDOFF_REQUEST \
  --to CA \
  --message "API endpoints ready for frontend integration" \
  --context '{"task_id": "TASK-API-001", "endpoints": ["/api/auth", "/api/data"], "documentation": "api_docs.md"}'

# Step 5: CA accepts handoff
AGENT_ID=CA python3 tools/send_signal.py \
  --type HANDOFF_ACCEPT \
  --to CB \
  --message "Frontend integration accepted, starting UI development" \
  --context '{"task_id": "TASK-UI-001", "estimated_completion": "2025-05-30T16:00:00Z"}'
```

### 2. Emergency Help Request

**Scenario**: Production issue requiring immediate assistance

```bash
# Step 1: Critical help request
AGENT_ID=WA python3 tools/send_signal.py \
  --type NEEDS_HELP \
  --message "Production deployment failing - critical issue" \
  --context '{
    "issue": "kubernetes_pods_failing",
    "urgency": "CRITICAL", 
    "impact": "production_down",
    "expertise_needed": ["kubernetes", "networking"],
    "logs": "deployment_error.log"
  }' \
  --priority CRITICAL

# Step 2: Multiple agents respond
AGENT_ID=ARCH python3 tools/send_signal.py \
  --type READY \
  --to WA \
  --message "Available to coordinate emergency response" \
  --context '{"role": "incident_commander", "available_immediately": true}'

AGENT_ID=CB python3 tools/send_signal.py \
  --type READY \
  --to WA \
  --message "Can assist with backend debugging" \
  --context '{"expertise": ["backend", "api_debugging"], "available_for": "2 hours"}'

# Step 3: Issue resolution
AGENT_ID=WA python3 tools/send_signal.py \
  --type COMPLETED \
  --message "Production issue resolved with team assistance" \
  --context '{
    "issue_resolved": "kubernetes_pods_failing",
    "resolution": "network_policy_fix",
    "assistance_from": ["ARCH", "CB"],
    "downtime": "15 minutes"
  }'
```

### 3. Resource Coordination

**Scenario**: Multiple agents need access to shared test environment

```bash
# Step 1: CC claims test environment
AGENT_ID=CC python3 tools/send_signal.py \
  --type RESOURCE_CLAIM \
  --message "Claiming test environment for integration testing" \
  --context '{
    "resource": "staging_environment",
    "duration": "30 minutes",
    "operation": "integration_tests",
    "exclusive": true
  }'

# Step 2: CB tries to claim same resource (conflict)
AGENT_ID=CB python3 tools/send_signal.py \
  --type RESOURCE_CLAIM \
  --message "Need staging environment for API testing" \
  --context '{
    "resource": "staging_environment",
    "duration": "45 minutes",
    "operation": "api_load_tests"
  }'

# Step 3: CC offers coordination
AGENT_ID=CC python3 tools/send_signal.py \
  --type READY \
  --to CB \
  --message "Can coordinate shared environment usage" \
  --context '{
    "proposal": "sequential_testing",
    "integration_tests_eta": "20 minutes",
    "can_share_after": "2025-05-29T15:30:00Z"
  }'

# Step 4: CC releases resource
AGENT_ID=CC python3 tools/send_signal.py \
  --type RESOURCE_RELEASE \
  --message "Test environment released, all tests passed" \
  --context '{
    "resource": "staging_environment",
    "status": "clean",
    "test_results": "all_passed",
    "available_for": "CB"
  }'
```

### 4. Sprint Planning and Coordination

**Scenario**: Agents coordinating work for new sprint

```bash
# Step 1: ARCH initiates sprint planning
AGENT_ID=ARCH python3 tools/send_signal.py \
  --type READY \
  --message "Sprint 6.15 planning ready, task assignments available" \
  --context '{
    "sprint": "SPRINT_6_15",
    "total_tasks": 12,
    "assignments": {
      "CA": ["TASK-170A", "TASK-170B"],
      "CB": ["TASK-170C", "TASK-170D"],
      "CC": ["TASK-170E"]
    }
  }'

# Step 2: Agents confirm readiness
AGENT_ID=CA python3 tools/send_signal.py \
  --type READY \
  --message "Ready for frontend tasks in sprint 6.15" \
  --context '{
    "capacity": "40 hours",
    "specializations": ["ui", "frontend"],
    "dependencies": ["design_mockups"]
  }'

AGENT_ID=CB python3 tools/send_signal.py \
  --type BLOCKED \
  --message "Backend tasks dependent on infrastructure changes" \
  --context '{
    "blocked_tasks": ["TASK-170C", "TASK-170D"],
    "waiting_for": "database_migration",
    "estimated_delay": "1 day"
  }'

# Step 3: Dependencies resolved
AGENT_ID=WA python3 tools/send_signal.py \
  --type COMPLETED \
  --message "Infrastructure updates complete for sprint 6.15" \
  --context '{
    "completed": "database_migration",
    "unblocks": ["TASK-170C", "TASK-170D"],
    "ready_for": "CB"
  }'
```

### 5. Quality Assurance Workflow

**Scenario**: Testing workflow with multiple validation stages

```bash
# Step 1: Developer completes feature
AGENT_ID=CA python3 tools/send_signal.py \
  --type COMPLETED \
  --message "User authentication feature complete" \
  --context '{
    "completed_task": "TASK-AUTH-UI",
    "deliverables": ["login_component", "signup_component", "auth_context"],
    "testing_needed": true,
    "branch": "feature/auth-ui"
  }'

# Step 2: Request QA handoff
AGENT_ID=CA python3 tools/send_signal.py \
  --type HANDOFF_REQUEST \
  --to CC \
  --message "Authentication UI ready for testing" \
  --context '{
    "task_id": "TASK-AUTH-UI",
    "test_scenarios": ["login_flow", "signup_flow", "password_reset"],
    "acceptance_criteria": "auth_acceptance_tests.md",
    "deployment_url": "https://staging.app.com/auth"
  }'

# Step 3: QA accepts and starts testing
AGENT_ID=CC python3 tools/send_signal.py \
  --type HANDOFF_ACCEPT \
  --to CA \
  --message "QA testing started for authentication UI" \
  --context '{
    "estimated_duration": "4 hours",
    "test_plan": "auth_test_plan.md",
    "target_completion": "2025-05-29T18:00:00Z"
  }'

# Step 4: QA finds issues
AGENT_ID=CC python3 tools/send_signal.py \
  --type BLOCKED \
  --to CA \
  --message "Authentication testing blocked by validation errors" \
  --context '{
    "issues_found": [
      "Password validation not working",
      "Signup form allows invalid emails"
    ],
    "severity": "HIGH",
    "test_report": "auth_test_report.md"
  }'

# Step 5: Developer fixes and signals completion
AGENT_ID=CA python3 tools/send_signal.py \
  --type COMPLETED \
  --message "Authentication issues fixed, ready for re-testing" \
  --context '{
    "fixes_applied": ["password_validation", "email_validation"],
    "updated_branch": "feature/auth-ui",
    "ready_for_retest": true
  }'

# Step 6: QA completes testing
AGENT_ID=CC python3 tools/send_signal.py \
  --type COMPLETED \
  --message "Authentication UI testing complete - all tests passed" \
  --context '{
    "test_results": "all_passed",
    "test_coverage": "95%",
    "approved_for": "production_deployment"
  }'
```

## 🚀 Advanced Scenarios

### Cross-Project Coordination

```bash
# Project A needs shared component from Project B
AGENT_ID=CA python3 tools/send_signal.py \
  --type NEEDS_HELP \
  --message "Need shared UI component library for Project Alpha" \
  --context '{
    "project": "Project_Alpha",
    "component_needed": "data_visualization_charts",
    "usage": "dashboard_implementation",
    "timeline": "2025-05-30"
  }'

# Project B agent responds
AGENT_ID=BLUE python3 tools/send_signal.py \
  --type READY \
  --to CA \
  --message "Chart component library available for reuse" \
  --context '{
    "component": "chart_library_v2",
    "location": "components/charts/",
    "documentation": "chart_api_docs.md",
    "integration_support": true
  }'
```

### Maintenance Window Coordination

```bash
# Schedule maintenance window
AGENT_ID=WA python3 tools/send_signal.py \
  --type RESOURCE_CLAIM \
  --message "Scheduled maintenance window for database upgrade" \
  --context '{
    "resource": "production_database",
    "scheduled_time": "2025-05-30T02:00:00Z",
    "duration": "2 hours",
    "impact": "full_system_downtime",
    "rollback_plan": "database_rollback_procedure.md"
  }' \
  --priority CRITICAL

# All agents acknowledge
AGENT_ID=CA python3 tools/send_signal.py \
  --type READY \
  --message "Frontend team ready for maintenance window" \
  --context '{"no_deployments_scheduled": true, "support_available": true}'

AGENT_ID=CB python3 tools/send_signal.py \
  --type READY \
  --message "Backend team standing by for maintenance support" \
  --context '{"monitoring_active": true, "rollback_ready": true}'
```

### Performance Optimization Collaboration

```bash
# Performance issue detected
AGENT_ID=CB python3 tools/send_signal.py \
  --type NEEDS_HELP \
  --message "API response times degrading, need optimization assistance" \
  --context '{
    "issue": "slow_database_queries",
    "endpoints_affected": ["/api/users", "/api/dashboard"],
    "response_time": "3.5 seconds",
    "target": "< 500ms",
    "expertise_needed": ["database_optimization", "caching"]
  }' \
  --priority HIGH

# Database expert responds
AGENT_ID=WA python3 tools/send_signal.py \
  --type READY \
  --to CB \
  --message "Available for database optimization" \
  --context '{
    "expertise": ["query_optimization", "indexing", "caching_strategies"],
    "availability": "immediate",
    "tools": ["query_analyzer", "performance_profiler"]
  }'

# Collaboration result
AGENT_ID=CB python3 tools/send_signal.py \
  --type COMPLETED \
  --message "API performance optimization complete" \
  --context '{
    "improvements": {
      "response_time": "< 200ms",
      "improvement": "94%",
      "techniques_used": ["query_optimization", "redis_caching", "connection_pooling"]
    },
    "assistance_from": "WA",
    "documentation": "performance_optimization_report.md"
  }'
```

## 📊 Monitoring and Analytics

### Signal Pattern Analysis

```bash
# Check communication patterns
python3 tools/check_signals.py --stats

# Monitor specific agent communication
python3 tools/check_signals.py --from CB --days 3

# Watch for help requests
python3 tools/check_signals.py --type NEEDS_HELP --priority HIGH
```

### Real-time Coordination

```bash
# Monitor active signals requiring response
python3 tools/check_signals.py --active --monitor

# Set up signal monitoring for coordination
python3 tools/check_signals.py --monitor --interval 10
```

## 🔧 Signal Integration Examples

### Enhanced Task Completion

```bash
# Complete task with automatic signaling
tools/complete_task_with_signals.sh \
  -m "Dashboard implementation complete" \
  -d "UI components,API endpoints,Documentation" \
  -f \
  --priority HIGH \
  TASK-165G

# Complete with handoff to testing
tools/complete_task_with_signals.sh \
  -h CC \
  -m "Feature ready for QA testing" \
  TASK-AUTH-001

# Complete and signal ready for new work
tools/complete_task_with_signals.sh \
  -r \
  --priority MEDIUM \
  TASK-BUG-FIX-42
```

### Morning Kickoff Integration

```bash
# Enhanced morning kickoff with signal checking
tools/morning_kickoff.sh --check-signals --resolve-blocks

# Process overnight signals
python3 tools/check_signals.py --active --days 1
```

## 🎯 Best Practices

### Signal Timing
- **READY signals**: Send when genuinely available with capacity
- **BLOCKED signals**: Send immediately when dependency identified
- **HELP requests**: Include specific expertise needed and urgency
- **COMPLETED signals**: Send with detailed deliverables and context

### Context Information
- Always include relevant task IDs and dependencies
- Specify expertise areas and time estimates
- Include links to deliverables and documentation
- Add urgency and impact information for critical issues

### Response Patterns
- Acknowledge HELP requests within 15 minutes
- Respond to HANDOFF requests within 1 hour
- Provide status updates for long-running assistance
- Close signal loops with completion confirmations

### Error Recovery
- Use BLOCKED signals proactively when issues arise
- Request help early rather than struggling alone
- Provide detailed error context and attempted solutions
- Follow up with resolution details for knowledge sharing

---

**Examples Created**: May 29, 2025  
**Version**: 1.0  
**TASK ID**: TASK-165I  
**Status**: ✅ EXAMPLE FLOWS COMPLETE  

*🎯 Signal workflows documented with practical examples for all common scenarios* 