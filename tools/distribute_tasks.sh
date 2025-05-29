#!/bin/bash
# distribute_tasks.sh - Smart task distribution based on agent expertise
# Part of TASK-165D: Morning kickoff automation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Agent expertise mapping function (compatible with bash 3.2)
get_agent_expertise() {
    local agent="$1"
    case "$agent" in
        "CA") echo "frontend,ui,react,css,user_experience,tooling" ;;
        "CB") echo "python,backend,api,system_design" ;;
        "CC") echo "testing,quality_assurance,integration,performance" ;;
        "WA") echo "infrastructure,devops,tooling,automation" ;;
        "ARCH") echo "architecture,system_design,planning,documentation" ;;
        "BLUE") echo "analysis,optimization,monitoring,reporting" ;;
        *) echo "" ;;
    esac
}

# Get list of all agents
get_all_agents() {
    echo "CA CB CC WA ARCH BLUE"
}

# Function to display usage
usage() {
    echo -e "${CYAN}🎯 Smart Task Distribution${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS] [TASK_FILE]"
    echo ""
    echo "Options:"
    echo "  --dry-run        Show what would be assigned without making changes"
    echo "  --balanced       Try to balance workload across agents"
    echo "  --priority PRIO  Only distribute tasks with specific priority (HIGH, MEDIUM, LOW)"
    echo "  --agent AGENT    Distribute tasks only to specific agent"
    echo "  --verbose        Show detailed output"
    echo "  --help           Show this help message"
    echo ""
    echo "Arguments:"
    echo "  TASK_FILE        JSON file containing tasks to distribute (default: .sprint/task_backlog.json)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Distribute from default backlog"
    echo "  $0 --dry-run                # Preview task distribution"
    echo "  $0 --priority HIGH          # Only distribute high priority tasks"
    echo "  $0 --agent CA custom.json   # Assign all tasks to CA from custom file"
    exit 0
}

# Parse command line arguments
DRY_RUN=false
BALANCED=false
PRIORITY_FILTER=""
AGENT_FILTER=""
VERBOSE=false
TASK_FILE="$PROJECT_ROOT/.sprint/task_backlog.json"

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --balanced)
            BALANCED=true
            shift
            ;;
        --priority)
            PRIORITY_FILTER="$2"
            shift 2
            ;;
        --agent)
            AGENT_FILTER="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            ;;
        -*)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
        *)
            TASK_FILE="$1"
            shift
            ;;
    esac
done

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    
    case $level in
        "INFO")
            echo -e "${GREEN}ℹ $message${NC}"
            ;;
        "WARN")
            echo -e "${YELLOW}⚠ $message${NC}"
            ;;
        "ERROR")
            echo -e "${RED}✗ $message${NC}"
            ;;
        "DEBUG")
            if [ "$VERBOSE" = true ]; then
                echo -e "${BLUE}🔍 $message${NC}"
            fi
            ;;
        "SUCCESS")
            echo -e "${GREEN}✓ $message${NC}"
            ;;
    esac
}

# Function to create sample task backlog if it doesn't exist
create_sample_backlog() {
    if [ ! -f "$TASK_FILE" ]; then
        log "INFO" "Creating sample task backlog..."
        
        mkdir -p "$(dirname "$TASK_FILE")"
        
        cat > "$TASK_FILE" << 'EOF'
{
  "backlog_version": "1.0",
  "created": "2025-05-29T10:00:00Z",
  "description": "Sample task backlog for automated distribution",
  "tasks": [
    {
      "id": "TASK-DASHBOARD-UI",
      "title": "Update dashboard UI components",
      "description": "Modernize the dashboard interface with new design system",
      "priority": "HIGH",
      "estimated_hours": 4,
      "keywords": ["frontend", "ui", "react", "dashboard"],
      "skills_required": ["react", "css", "frontend"],
      "dependencies": []
    },
    {
      "id": "TASK-API-PERFORMANCE",
      "title": "Optimize API performance",
      "description": "Improve response times and reduce database load",
      "priority": "MEDIUM",
      "estimated_hours": 6,
      "keywords": ["backend", "api", "performance", "database"],
      "skills_required": ["python", "backend", "api"],
      "dependencies": []
    },
    {
      "id": "TASK-E2E-COVERAGE",
      "title": "Expand end-to-end test coverage",
      "description": "Add comprehensive E2E tests for critical user flows",
      "priority": "HIGH",
      "estimated_hours": 5,
      "keywords": ["testing", "e2e", "qa", "coverage"],
      "skills_required": ["testing", "quality_assurance"],
      "dependencies": ["TASK-DASHBOARD-UI"]
    },
    {
      "id": "TASK-DEPLOY-PIPELINE",
      "title": "Improve deployment pipeline",
      "description": "Streamline CI/CD process and add automated rollbacks",
      "priority": "MEDIUM",
      "estimated_hours": 3,
      "keywords": ["devops", "ci", "cd", "deployment"],
      "skills_required": ["infrastructure", "devops", "automation"],
      "dependencies": []
    },
    {
      "id": "TASK-ARCH-REVIEW",
      "title": "Architecture documentation review",
      "description": "Update system architecture diagrams and documentation",
      "priority": "LOW",
      "estimated_hours": 2,
      "keywords": ["architecture", "documentation", "planning"],
      "skills_required": ["architecture", "documentation"],
      "dependencies": []
    },
    {
      "id": "TASK-PERF-ANALYSIS",
      "title": "Performance monitoring analysis",
      "description": "Analyze system performance metrics and identify bottlenecks",
      "priority": "MEDIUM",
      "estimated_hours": 3,
      "keywords": ["monitoring", "analysis", "performance"],
      "skills_required": ["analysis", "monitoring", "optimization"],
      "dependencies": []
    }
  ]
}
EOF
        
        log "SUCCESS" "Created sample backlog at $TASK_FILE"
    fi
}

# Function to calculate expertise match score
calculate_expertise_score() {
    local agent="$1"
    local task_keywords="$2"
    local skills_required="$3"
    
    local expertise=$(get_agent_expertise "$agent")
    local score=0
    
    # Score based on required skills (high weight)
    IFS=',' read -ra skills <<< "$skills_required"
    for skill in "${skills[@]}"; do
        skill=$(echo "$skill" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"')
        if [[ "$expertise" == *"$skill"* ]]; then
            score=$((score + 15))
        fi
    done
    
    # Score based on keywords (medium weight)
    IFS=',' read -ra keywords <<< "$task_keywords"
    for keyword in "${keywords[@]}"; do
        keyword=$(echo "$keyword" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | tr -d '"')
        if [[ "$expertise" == *"$keyword"* ]]; then
            score=$((score + 10))
        fi
    done
    
    echo "$score"
}

# Function to get current agent workload
get_agent_workload() {
    local agent="$1"
    local outbox_file="$PROJECT_ROOT/postbox/$agent/outbox.json"
    
    if [ -f "$outbox_file" ]; then
        jq '[.tasks[] | select(.status == "pending") | .estimated_hours] | add // 0' "$outbox_file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Function to find best agent for task
find_best_agent() {
    local task_keywords="$1"
    local skills_required="$2"
    local task_hours="$3"
    
    local best_agent=""
    local best_score=0
    local best_workload=999
    
    for agent in $(get_all_agents); do
        # Skip if agent filter is set and doesn't match
        if [ -n "$AGENT_FILTER" ] && [ "$agent" != "$AGENT_FILTER" ]; then
            continue
        fi
        
        local score=$(calculate_expertise_score "$agent" "$task_keywords" "$skills_required")
        local workload=$(get_agent_workload "$agent")
        
        log "DEBUG" "Agent $agent: score=$score, workload=${workload}h"
        
        # If balanced mode, consider workload in scoring
        if [ "$BALANCED" = true ]; then
            # Prefer agents with lower workload (subtract workload from score)
            score=$((score - workload))
        fi
        
        # Choose agent with highest score, or lowest workload if scores are equal
        if [ $score -gt $best_score ] || ([ $score -eq $best_score ] && [ $workload -lt $best_workload ]); then
            best_score=$score
            best_agent=$agent
            best_workload=$workload
        fi
    done
    
    echo "$best_agent"
}

# Function to assign task to agent
assign_task() {
    local agent="$1"
    local task_id="$2"
    local title="$3"
    local priority="$4"
    local hours="$5"
    local description="$6"
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN: Would assign $task_id to $agent ($hours hours)"
        return 0
    fi
    
    log "DEBUG" "Assigning $task_id to $agent..."
    
    # Use existing assign_task.sh script if available
    if [ -f "$SCRIPT_DIR/assign_task.sh" ]; then
        "$SCRIPT_DIR/assign_task.sh" "$agent" "$task_id" "$title" "$priority" "$hours" >/dev/null 2>&1
    else
        # Fallback manual assignment
        local outbox_file="$PROJECT_ROOT/postbox/$agent/outbox.json"
        local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        
        mkdir -p "$(dirname "$outbox_file")"
        
        if [ ! -f "$outbox_file" ]; then
            local agent_expertise=$(get_agent_expertise "$agent")
            echo '{
  "agent_id": "'$agent'",
  "agent_name": "Agent '$agent'",
  "expertise": ["'${agent_expertise/,/\",\"}"],
  "tasks": []
}' > "$outbox_file"
        fi
        
        # Add task using jq
        jq --arg task_id "$task_id" \
           --arg title "$title" \
           --arg priority "$priority" \
           --arg timestamp "$timestamp" \
           --argjson hours "$hours" \
           --arg description "$description" '
            .tasks += [{
                "task_id": $task_id,
                "title": $title,
                "priority": $priority,
                "status": "pending",
                "created_at": $timestamp,
                "estimated_hours": $hours,
                "description": $description,
                "deliverables": [],
                "dependencies": [],
                "assigned_by": "distribute_tasks"
            }]
        ' "$outbox_file" > "$outbox_file.tmp" && mv "$outbox_file.tmp" "$outbox_file"
    fi
    
    log "SUCCESS" "Assigned $task_id to $agent"
}

# Function to distribute tasks from backlog
distribute_tasks() {
    log "INFO" "Reading tasks from $TASK_FILE..."
    
    if [ ! -f "$TASK_FILE" ]; then
        log "ERROR" "Task file not found: $TASK_FILE"
        return 1
    fi
    
    # Validate JSON format
    if ! jq empty "$TASK_FILE" 2>/dev/null; then
        log "ERROR" "Invalid JSON format in task file"
        return 1
    fi
    
    local total_tasks=$(jq '.tasks | length' "$TASK_FILE")
    log "INFO" "Found $total_tasks tasks in backlog"
    
    local assigned_count=0
    local skipped_count=0
    
    # Process each task
    while IFS= read -r task; do
        local task_id=$(echo "$task" | jq -r '.id')
        local title=$(echo "$task" | jq -r '.title')
        local description=$(echo "$task" | jq -r '.description')
        local priority=$(echo "$task" | jq -r '.priority')
        local hours=$(echo "$task" | jq -r '.estimated_hours')
        local keywords=$(echo "$task" | jq -r '.keywords | join(",")')
        local skills=$(echo "$task" | jq -r '.skills_required | join(",")')
        
        # Apply priority filter if set
        if [ -n "$PRIORITY_FILTER" ] && [ "$priority" != "$PRIORITY_FILTER" ]; then
            log "DEBUG" "Skipping $task_id (priority $priority != $PRIORITY_FILTER)"
            skipped_count=$((skipped_count + 1))
            continue
        fi
        
        # Find best agent for this task
        local best_agent=$(find_best_agent "$keywords" "$skills" "$hours")
        
        if [ -z "$best_agent" ]; then
            log "WARN" "No suitable agent found for $task_id"
            skipped_count=$((skipped_count + 1))
            continue
        fi
        
        # Assign the task
        assign_task "$best_agent" "$task_id" "$title" "$priority" "$hours" "$description"
        assigned_count=$((assigned_count + 1))
        
    done < <(jq -c '.tasks[]' "$TASK_FILE")
    
    echo ""
    log "INFO" "Distribution completed:"
    log "INFO" "  - Assigned: $assigned_count tasks"
    log "INFO" "  - Skipped: $skipped_count tasks"
    
    if [ "$DRY_RUN" = false ]; then
        log "INFO" "  - Check agent outboxes for assignments"
    fi
}

# Function to show distribution summary
show_distribution_summary() {
    echo ""
    echo -e "${CYAN}📊 Current Workload Distribution:${NC}"
    echo ""
    
    for agent in $(get_all_agents); do
        local workload=$(get_agent_workload "$agent")
        local pending_count=0
        
        local outbox_file="$PROJECT_ROOT/postbox/$agent/outbox.json"
        if [ -f "$outbox_file" ]; then
            pending_count=$(jq '[.tasks[] | select(.status == "pending")] | length' "$outbox_file" 2>/dev/null || echo "0")
        fi
        
        echo -e "${BLUE}$agent${NC}: $pending_count tasks, ${workload}h pending"
    done
    echo ""
}

# Main function
main() {
    echo -e "${CYAN}"
    echo "🎯 ========================================"
    echo "   SMART TASK DISTRIBUTION"
    echo "   Phase 6.15 Sprint 1"
    echo "========================================"
    echo -e "${NC}"
    
    log "INFO" "Starting task distribution..."
    
    # Create sample backlog if needed
    create_sample_backlog
    
    # Show current state
    show_distribution_summary
    
    # Distribute tasks
    distribute_tasks
    
    # Show updated state
    show_distribution_summary
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN completed - no changes made"
        echo -e "${YELLOW}Run without --dry-run to apply changes${NC}"
    else
        log "SUCCESS" "Task distribution completed!"
        echo -e "${BLUE}Next steps:${NC}"
        echo "1. Run tools/morning_kickoff.sh for full daily summary"
        echo "2. Agents should check their outboxes"
        echo "3. Start working on assigned tasks"
    fi
    
    echo ""
}

# Run main function
main "$@" 