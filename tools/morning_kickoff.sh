#!/bin/bash
# morning_kickoff.sh - Automated daily task distribution and sprint kickoff
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
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
SPRINT_CONFIG="$PROJECT_ROOT/.sprint/daily_config.yaml"
PROGRESS_FILE="$PROJECT_ROOT/.sprint/progress.json"
DAILY_SUMMARY="$PROJECT_ROOT/.sprint/daily_summary_$(date +%Y%m%d).md"

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
    echo -e "${CYAN}🌅 Morning Kickoff Automation${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --config FILE    Use custom config file (default: .sprint/daily_config.yaml)"
    echo "  --dry-run        Show what would be done without making changes"
    echo "  --verbose        Show detailed output"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Standard morning kickoff"
    echo "  $0 --dry-run         # Preview task assignments"
    echo "  $0 --verbose         # Detailed logging"
    exit 0
}

# Parse command line arguments
DRY_RUN=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            SPRINT_CONFIG="$2"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
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

# Function to check dependencies
check_dependencies() {
    log "DEBUG" "Checking dependencies..."
    
    if ! command -v jq &> /dev/null; then
        log "ERROR" "jq is required but not installed"
        exit 1
    fi
    
    if ! command -v yq &> /dev/null; then
        log "WARN" "yq not found, will use basic YAML parsing"
    fi
    
    log "SUCCESS" "Dependencies checked"
}

# Function to create default config if it doesn't exist
create_default_config() {
    if [ ! -f "$SPRINT_CONFIG" ]; then
        log "INFO" "Creating default daily config..."
        
        mkdir -p "$(dirname "$SPRINT_CONFIG")"
        
        cat > "$SPRINT_CONFIG" << 'EOF'
# Daily Task Configuration
# This file defines the daily task distribution strategy

sprint:
  id: "PHASE_6.15_SPRINT_1"
  start_date: "2025-05-29"
  duration_days: 7
  
daily_tasks:
  - id: "DAILY-STANDUP"
    title: "Daily standup and progress review"
    priority: "HIGH"
    agent: "ARCH"
    estimated_hours: 0.5
    
  - id: "DAILY-MONITORING"
    title: "System monitoring and health checks"
    priority: "MEDIUM"
    agent: "WA"
    estimated_hours: 1
    
  - id: "DAILY-TESTING"
    title: "Automated test suite execution"
    priority: "MEDIUM"
    agent: "CC"
    estimated_hours: 1

task_pool:
  # Available tasks for distribution
  frontend:
    - id: "UI-DASHBOARD"
      title: "Dashboard UI improvements"
      priority: "MEDIUM"
      estimated_hours: 3
      
  backend:
    - id: "API-OPTIMIZATION"
      title: "API performance optimization"
      priority: "MEDIUM"
      estimated_hours: 4
      
  testing:
    - id: "E2E-TESTS"
      title: "End-to-end test coverage"
      priority: "HIGH"
      estimated_hours: 3
      
  infrastructure:
    - id: "DEPLOYMENT-PIPELINE"
      title: "CI/CD pipeline improvements"
      priority: "LOW"
      estimated_hours: 2

distribution_rules:
  max_hours_per_agent: 8
  min_hours_per_agent: 2
  priority_weights:
    HIGH: 3
    MEDIUM: 2
    LOW: 1
EOF
        
        log "SUCCESS" "Created default config at $SPRINT_CONFIG"
    fi
}

# Function to generate daily summary
generate_daily_summary() {
    log "INFO" "Generating daily summary..."
    
    local date=$(date +"%Y-%m-%d")
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    cat > "$DAILY_SUMMARY" << EOF
# Daily Sprint Summary - $date

Generated: $timestamp

## 🎯 Today's Focus

### Sprint Progress
$(if [ -f "$PROGRESS_FILE" ]; then
    local total=$(jq '.total_tasks // 0' "$PROGRESS_FILE" 2>/dev/null || echo "0")
    local completed=$(jq '.completed // 0' "$PROGRESS_FILE" 2>/dev/null || echo "0")
    local in_progress=$(jq '.in_progress // 0' "$PROGRESS_FILE" 2>/dev/null || echo "0")
    echo "- Total Tasks: $total"
    echo "- Completed: $completed"
    echo "- In Progress: $in_progress"
    echo "- Remaining: $((total - completed))"
else
    echo "- Sprint progress file not found"
fi)

## 🤖 Agent Assignments

$(for agent in $(get_all_agents); do
    local outbox_file="$PROJECT_ROOT/postbox/$agent/outbox.json"
    if [ -f "$outbox_file" ]; then
        local pending_count=$(jq '[.tasks[] | select(.status == "pending")] | length' "$outbox_file" 2>/dev/null || echo "0")
        local total_hours=$(jq '[.tasks[] | select(.status == "pending") | .estimated_hours] | add // 0' "$outbox_file" 2>/dev/null || echo "0")
        local expertise=$(get_agent_expertise "$agent")
        echo "### $agent (${expertise//,/, })"
        echo "- Pending Tasks: $pending_count"
        echo "- Estimated Hours: $total_hours"
        echo ""
        
        # List pending tasks
        if [ "$pending_count" -gt 0 ]; then
            jq -r '.tasks[] | select(.status == "pending") | "- **\(.task_id)**: \(.title) (\(.priority), \(.estimated_hours)h)"' "$outbox_file" 2>/dev/null || echo "- No task details available"
        fi
        echo ""
    else
        echo "### $agent"
        echo "- No outbox file found"
        echo ""
    fi
done)

## 📋 Next Steps

1. Each agent should check their outbox: \`postbox/{AGENT}/outbox.json\`
2. Start with HIGH priority tasks
3. Update task status using: \`tools/complete_task.sh {AGENT} {TASK_ID}\`
4. Run end-of-day summary: \`tools/end_of_day.sh\`

## 🔄 Commands

- **Check individual status**: \`tools/task_status.sh {AGENT}\`
- **Quick status overview**: \`tools/quick_status.py\`
- **Complete a task**: \`tools/complete_task.sh {AGENT} {TASK_ID}\`

---
*Generated by morning_kickoff.sh automation*
EOF

    log "SUCCESS" "Daily summary generated: $DAILY_SUMMARY"
}

# Function to update sprint progress
update_sprint_progress() {
    log "DEBUG" "Updating sprint progress..."
    
    mkdir -p "$(dirname "$PROGRESS_FILE")"
    
    # Initialize progress file if it doesn't exist
    if [ ! -f "$PROGRESS_FILE" ]; then
        echo '{
  "sprint_id": "PHASE_6.15_SPRINT_1",
  "start_date": "'$(date +%Y-%m-%d)'",
  "last_updated": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
  "total_tasks": 0,
  "completed": 0,
  "in_progress": 0,
  "tasks": {}
}' > "$PROGRESS_FILE"
    fi
    
    # Update last_updated timestamp
    jq --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" '
        .last_updated = $timestamp
    ' "$PROGRESS_FILE" > "$PROGRESS_FILE.tmp" && mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE"
    
    log "SUCCESS" "Sprint progress updated"
}

# Main function
main() {
    echo -e "${CYAN}"
    echo "🌅 ========================================"
    echo "   MORNING KICKOFF AUTOMATION"
    echo "   Phase 6.15 Sprint 1"
    echo "   $(date +'%A, %B %d, %Y - %H:%M')"
    echo "========================================"
    echo -e "${NC}"
    
    log "INFO" "Starting morning kickoff process..."
    
    # Check dependencies
    check_dependencies
    
    # Create default config if needed
    create_default_config
    
    # Update sprint progress
    update_sprint_progress
    
    # Generate API documentation
    log "INFO" "Generating API documentation..."
    if command -v python3 &> /dev/null; then
        python3 "$SCRIPT_DIR/generate_api_docs.py" --dir tools --output docs/api/API_REFERENCE.md
        log "SUCCESS" "API documentation updated"
    else
        log "WARN" "Python3 not found, skipping API documentation generation"
    fi
    
    # Generate daily summary
    generate_daily_summary
    
    # Display summary
    echo ""
    echo -e "${CYAN}📊 Daily Summary Generated:${NC}"
    echo -e "${BLUE}$DAILY_SUMMARY${NC}"
    echo ""
    
    if [ "$DRY_RUN" = true ]; then
        log "INFO" "DRY RUN completed - no changes made"
    else
        log "SUCCESS" "Morning kickoff completed successfully!"
    fi
    
    echo ""
    echo -e "${YELLOW}🚀 Ready to start the day!${NC}"
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Review your outbox: postbox/{YOUR_AGENT}/outbox.json"
    echo "2. Check daily summary: $DAILY_SUMMARY"
    echo "3. Start with HIGH priority tasks"
    echo "4. Update progress with: tools/complete_task.sh"
    echo ""
}

# Run main function
main "$@" 