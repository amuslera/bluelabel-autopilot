#!/bin/bash
# task_status.sh - Display status of tasks across all agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -a <agent_id>  - Show tasks for specific agent only"
    echo "  -s <status>    - Filter by status (pending, assigned, in_progress, completed)"
    echo "  -t <task_id>   - Show details for specific task"
    echo "  -p             - Show progress summary"
    echo "  -h             - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Show all tasks"
    echo "  $0 -a CC              # Show tasks for agent CC"
    echo "  $0 -s pending         # Show only pending tasks"
    echo "  $0 -t TASK-165C       # Show details for TASK-165C"
    echo "  $0 -p                 # Show progress summary"
    exit 1
}

# Parse options
FILTER_AGENT=""
FILTER_STATUS=""
FILTER_TASK=""
SHOW_PROGRESS=false

while getopts "a:s:t:ph" opt; do
    case $opt in
        a) FILTER_AGENT="$OPTARG" ;;
        s) FILTER_STATUS="$OPTARG" ;;
        t) FILTER_TASK="$OPTARG" ;;
        p) SHOW_PROGRESS=true ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Function to get status color
get_status_color() {
    case "$1" in
        "completed") echo "$GREEN" ;;
        "in_progress") echo "$YELLOW" ;;
        "assigned") echo "$CYAN" ;;
        "pending") echo "$MAGENTA" ;;
        "failed") echo "$RED" ;;
        *) echo "$NC" ;;
    esac
}

# Function to display task details
show_task_details() {
    local agent_id="$1"
    local task_data="$2"
    
    local task_id=$(echo "$task_data" | jq -r '.task_id')
    local title=$(echo "$task_data" | jq -r '.title')
    local status=$(echo "$task_data" | jq -r '.status')
    local priority=$(echo "$task_data" | jq -r '.priority')
    local created_at=$(echo "$task_data" | jq -r '.created_at // "N/A"')
    local estimated_hours=$(echo "$task_data" | jq -r '.estimated_hours // "N/A"')
    
    local status_color=$(get_status_color "$status")
    
    echo -e "${BLUE}[$agent_id]${NC} ${YELLOW}$task_id${NC} - $title"
    echo -e "  Status: ${status_color}$status${NC} | Priority: $priority | Hours: $estimated_hours"
    if [ "$created_at" != "N/A" ]; then
        echo -e "  Created: $created_at"
    fi
}

# Function to show progress summary
show_progress_summary() {
    echo -e "${CYAN}=== Task Progress Summary ===${NC}"
    echo ""
    
    local total_tasks=0
    local completed_tasks=0
    local in_progress_tasks=0
    local pending_tasks=0
    local assigned_tasks=0
    
    # Count tasks from all agent outboxes
    for outbox in "$PROJECT_ROOT"/postbox/*/outbox.json; do
        if [ -f "$outbox" ]; then
            local counts=$(jq '
                .tasks | {
                    total: length,
                    completed: [.[] | select(.status == "completed")] | length,
                    in_progress: [.[] | select(.status == "in_progress")] | length,
                    pending: [.[] | select(.status == "pending")] | length,
                    assigned: [.[] | select(.status == "assigned")] | length
                }
            ' "$outbox")
            
            total_tasks=$((total_tasks + $(echo "$counts" | jq -r '.total')))
            completed_tasks=$((completed_tasks + $(echo "$counts" | jq -r '.completed')))
            in_progress_tasks=$((in_progress_tasks + $(echo "$counts" | jq -r '.in_progress')))
            pending_tasks=$((pending_tasks + $(echo "$counts" | jq -r '.pending')))
            assigned_tasks=$((assigned_tasks + $(echo "$counts" | jq -r '.assigned')))
        fi
    done
    
    # Calculate completion percentage
    local completion_pct=0
    if [ $total_tasks -gt 0 ]; then
        completion_pct=$((completed_tasks * 100 / total_tasks))
    fi
    
    # Display summary
    echo -e "Total Tasks: ${YELLOW}$total_tasks${NC}"
    echo -e "Completed: ${GREEN}$completed_tasks${NC} ($completion_pct%)"
    echo -e "In Progress: ${YELLOW}$in_progress_tasks${NC}"
    echo -e "Assigned: ${CYAN}$assigned_tasks${NC}"
    echo -e "Pending: ${MAGENTA}$pending_tasks${NC}"
    
    # Progress bar
    echo ""
    echo -n "Progress: ["
    local bar_length=30
    local filled=$((completion_pct * bar_length / 100))
    for ((i=0; i<filled; i++)); do echo -n "="; done
    for ((i=filled; i<bar_length; i++)); do echo -n " "; done
    echo -e "] ${GREEN}$completion_pct%${NC}"
    echo ""
}

# Main execution
if [ "$SHOW_PROGRESS" = true ]; then
    show_progress_summary
    exit 0
fi

echo -e "${CYAN}=== Task Status Report ===${NC}"
echo -e "Generated: $(date)"
echo ""

# Check specific task
if [ -n "$FILTER_TASK" ]; then
    echo -e "Searching for task: ${YELLOW}$FILTER_TASK${NC}"
    echo ""
    
    found=false
    for outbox in "$PROJECT_ROOT"/postbox/*/outbox.json; do
        if [ -f "$outbox" ]; then
            agent_id=$(basename $(dirname "$outbox"))
            task_data=$(jq --arg task_id "$FILTER_TASK" '.tasks[] | select(.task_id == $task_id)' "$outbox" 2>/dev/null)
            
            if [ -n "$task_data" ]; then
                found=true
                show_task_details "$agent_id" "$task_data"
                
                # Show full details
                echo ""
                echo "Full Details:"
                echo "$task_data" | jq '.'
                break
            fi
        fi
    done
    
    if [ "$found" = false ]; then
        echo -e "${RED}Task $FILTER_TASK not found${NC}"
    fi
    exit 0
fi

# Show tasks for all agents or specific agent
task_count=0

for outbox in "$PROJECT_ROOT"/postbox/*/outbox.json; do
    if [ -f "$outbox" ]; then
        agent_id=$(basename $(dirname "$outbox"))
        
        # Skip if filtering by agent
        if [ -n "$FILTER_AGENT" ] && [ "$agent_id" != "$FILTER_AGENT" ]; then
            continue
        fi
        
        # Get agent info
        agent_name=$(jq -r '.agent_name // .agent_id' "$outbox")
        
        # Get tasks with optional status filter
        if [ -n "$FILTER_STATUS" ]; then
            tasks=$(jq --arg status "$FILTER_STATUS" '.tasks[] | select(.status == $status)' "$outbox" 2>/dev/null)
        else
            tasks=$(jq '.tasks[]' "$outbox" 2>/dev/null)
        fi
        
        if [ -n "$tasks" ]; then
            echo -e "\n${BLUE}=== Agent: $agent_id ($agent_name) ===${NC}"
            
            # Process each task
            echo "$tasks" | jq -s '.' | jq -c '.[]' | while IFS= read -r task; do
                show_task_details "$agent_id" "$task"
                task_count=$((task_count + 1))
                echo ""
            done
        fi
    fi
done

# Summary
echo -e "\n${CYAN}=== Summary ===${NC}"
if [ -n "$FILTER_AGENT" ]; then
    echo -e "Agent Filter: ${YELLOW}$FILTER_AGENT${NC}"
fi
if [ -n "$FILTER_STATUS" ]; then
    echo -e "Status Filter: ${YELLOW}$FILTER_STATUS${NC}"
fi

# Show quick progress if no specific filters
if [ -z "$FILTER_AGENT" ] && [ -z "$FILTER_STATUS" ]; then
    echo ""
    show_progress_summary
fi