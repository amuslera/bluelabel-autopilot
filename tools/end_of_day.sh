#!/bin/bash
# end_of_day.sh - Session wrap-up and daily summary generation
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
PROGRESS_FILE="$PROJECT_ROOT/.sprint/progress.json"
EOD_SUMMARY="$PROJECT_ROOT/.sprint/eod_summary_$(date +%Y%m%d).md"
ARCHIVE_DIR="$PROJECT_ROOT/.sprint/archive"

# Function to display usage
usage() {
    echo -e "${CYAN}🌙 End of Day Wrap-up${NC}"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --archive        Archive completed tasks"
    echo "  --metrics        Generate detailed performance metrics"
    echo "  --verbose        Show detailed output"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Standard end-of-day wrap-up"
    echo "  $0 --archive         # Include task archiving"
    echo "  $0 --metrics         # Include performance metrics"
    exit 0
}

# Parse command line arguments
ARCHIVE=false
METRICS=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --archive)
            ARCHIVE=true
            shift
            ;;
        --metrics)
            METRICS=true
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

# Function to collect agent statistics
collect_agent_stats() {
    log "DEBUG" "Collecting agent statistics..."
    
    declare -A agent_stats
    local total_completed=0
    local total_pending=0
    local total_hours_completed=0
    local total_hours_pending=0
    
    for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
        if [ -d "$agent_dir" ]; then
            local agent=$(basename "$agent_dir")
            local outbox_file="$agent_dir/outbox.json"
            
            if [ -f "$outbox_file" ]; then
                local completed=$(jq '[.tasks[] | select(.status == "completed")] | length' "$outbox_file" 2>/dev/null || echo "0")
                local pending=$(jq '[.tasks[] | select(.status == "pending")] | length' "$outbox_file" 2>/dev/null || echo "0")
                local in_progress=$(jq '[.tasks[] | select(.status == "in_progress")] | length' "$outbox_file" 2>/dev/null || echo "0")
                local hours_completed=$(jq '[.tasks[] | select(.status == "completed") | .estimated_hours] | add // 0' "$outbox_file" 2>/dev/null || echo "0")
                local hours_pending=$(jq '[.tasks[] | select(.status == "pending") | .estimated_hours] | add // 0' "$outbox_file" 2>/dev/null || echo "0")
                
                agent_stats["$agent"]="$completed,$pending,$in_progress,$hours_completed,$hours_pending"
                total_completed=$((total_completed + completed))
                total_pending=$((total_pending + pending))
                total_hours_completed=$((total_hours_completed + hours_completed))
                total_hours_pending=$((total_hours_pending + hours_pending))
            fi
        fi
    done
    
    echo "$total_completed,$total_pending,$total_hours_completed,$total_hours_pending"
}

# Function to generate performance metrics
generate_performance_metrics() {
    log "INFO" "Generating performance metrics..."
    
    local date=$(date +"%Y-%m-%d")
    local week_num=$(date +"%W")
    
    cat << EOF

## 📊 Performance Metrics

### Daily Statistics
- Date: $date
- Week: $week_num
- Session Duration: $(if [ -f "/tmp/session_start_time" ]; then
    local start_time=$(cat /tmp/session_start_time 2>/dev/null || echo "unknown")
    if [ "$start_time" != "unknown" ]; then
        local duration=$(($(date +%s) - start_time))
        echo "${duration}s ($(($duration / 3600))h $(($duration % 3600 / 60))m)"
    else
        echo "unknown"
    fi
else
    echo "unknown"
fi)

### Velocity Tracking
$(local stats=$(collect_agent_stats)
IFS=',' read -r total_completed total_pending total_hours_completed total_hours_pending <<< "$stats"
echo "- Tasks Completed Today: $total_completed"
echo "- Tasks Remaining: $total_pending"
echo "- Hours Delivered: $total_hours_completed"
echo "- Hours Planned: $total_hours_pending"
echo "- Completion Rate: $(if [ "$total_completed" -gt 0 ] && [ "$total_pending" -gt 0 ]; then
    echo "scale=1; $total_completed * 100 / ($total_completed + $total_pending)" | bc 2>/dev/null || echo "N/A"
else
    echo "N/A"
fi)%")

### Team Productivity
$(for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
    if [ -d "$agent_dir" ]; then
        local agent=$(basename "$agent_dir")
        local outbox_file="$agent_dir/outbox.json"
        
        if [ -f "$outbox_file" ]; then
            local completed=$(jq '[.tasks[] | select(.status == "completed")] | length' "$outbox_file" 2>/dev/null || echo "0")
            local pending=$(jq '[.tasks[] | select(.status == "pending")] | length' "$outbox_file" 2>/dev/null || echo "0")
            local hours_completed=$(jq '[.tasks[] | select(.status == "completed") | .estimated_hours] | add // 0' "$outbox_file" 2>/dev/null || echo "0")
            
            echo "- **$agent**: $completed completed, $pending pending ($hours_completed hours delivered)"
        fi
    fi
done)

EOF
}

# Function to identify blockers and risks
identify_blockers() {
    log "DEBUG" "Identifying blockers and risks..."
    
    cat << EOF

## 🚧 Blockers & Risks

### High Priority Overdue
$(for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
    if [ -d "$agent_dir" ]; then
        local agent=$(basename "$agent_dir")
        local outbox_file="$agent_dir/outbox.json"
        
        if [ -f "$outbox_file" ]; then
            # Find high priority pending tasks
            local high_priority_pending=$(jq -r '.tasks[] | select(.status == "pending" and .priority == "HIGH") | "- **\(.task_id)** (\(.agent_id // "'$agent'")): \(.title)"' "$outbox_file" 2>/dev/null || echo "")
            
            if [ -n "$high_priority_pending" ]; then
                echo "$high_priority_pending"
            fi
        fi
    fi
done | head -10)

### Agents with Heavy Load
$(for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
    if [ -d "$agent_dir" ]; then
        local agent=$(basename "$agent_dir")
        local outbox_file="$agent_dir/outbox.json"
        
        if [ -f "$outbox_file" ]; then
            local hours_pending=$(jq '[.tasks[] | select(.status == "pending") | .estimated_hours] | add // 0' "$outbox_file" 2>/dev/null || echo "0")
            
            # Flag agents with more than 6 hours of pending work
            if [ "$hours_pending" -gt 6 ]; then
                echo "- **$agent**: $hours_pending hours pending (consider load balancing)"
            fi
        fi
    fi
done)

### Dependencies Waiting
$(for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
    if [ -d "$agent_dir" ]; then
        local agent=$(basename "$agent_dir")
        local outbox_file="$agent_dir/outbox.json"
        
        if [ -f "$outbox_file" ]; then
            # Find tasks with dependencies
            local blocked_tasks=$(jq -r '.tasks[] | select(.status == "pending" and (.dependencies | length) > 0) | "- **\(.task_id)** (\(.agent_id // "'$agent'")): waiting on \(.dependencies | join(", "))"' "$outbox_file" 2>/dev/null || echo "")
            
            if [ -n "$blocked_tasks" ]; then
                echo "$blocked_tasks"
            fi
        fi
    fi
done | head -5)

EOF
}

# Function to generate tomorrow's preparation
generate_tomorrow_prep() {
    log "DEBUG" "Generating tomorrow's preparation..."
    
    cat << EOF

## 🌅 Tomorrow's Preparation

### Priority Focus Areas
$(# Identify high priority pending tasks
for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
    if [ -d "$agent_dir" ]; then
        local agent=$(basename "$agent_dir")
        local outbox_file="$agent_dir/outbox.json"
        
        if [ -f "$outbox_file" ]; then
            local high_priority=$(jq -r '.tasks[] | select(.status == "pending" and .priority == "HIGH") | .title' "$outbox_file" 2>/dev/null | head -3)
            
            if [ -n "$high_priority" ]; then
                echo "**$agent Focus:**"
                echo "$high_priority" | sed 's/^/- /'
                echo ""
            fi
        fi
    fi
done)

### Recommended Actions
1. **Morning Kickoff**: Run \`tools/morning_kickoff.sh\` to start the day
2. **Priority Review**: Focus on HIGH priority tasks first
3. **Dependency Check**: Review blocked tasks and resolve dependencies
4. **Load Balancing**: Consider redistributing heavy workloads

### Quick Commands for Tomorrow
\`\`\`bash
# Start the day
tools/morning_kickoff.sh

# Check team status
tools/quick_status.py

# Monitor individual agent
tools/task_status.sh {AGENT_ID}

# Complete tasks as you go
tools/complete_task.sh {AGENT_ID} {TASK_ID}
\`\`\`

EOF
}

# Function to archive completed tasks
archive_completed_tasks() {
    if [ "$ARCHIVE" = false ]; then
        return 0
    fi
    
    log "INFO" "Archiving completed tasks..."
    
    mkdir -p "$ARCHIVE_DIR"
    local archive_file="$ARCHIVE_DIR/completed_$(date +%Y%m%d).json"
    local archived_count=0
    
    # Collect all completed tasks
    echo "{" > "$archive_file"
    echo "  \"archive_date\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"," >> "$archive_file"
    echo "  \"completed_tasks\": [" >> "$archive_file"
    
    local first_task=true
    for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
        if [ -d "$agent_dir" ]; then
            local agent=$(basename "$agent_dir")
            local outbox_file="$agent_dir/outbox.json"
            
            if [ -f "$outbox_file" ]; then
                # Extract completed tasks
                local completed_tasks=$(jq -c '.tasks[] | select(.status == "completed")' "$outbox_file" 2>/dev/null || echo "")
                
                while IFS= read -r task; do
                    if [ -n "$task" ]; then
                        if [ "$first_task" = false ]; then
                            echo "," >> "$archive_file"
                        fi
                        echo "    $task" >> "$archive_file"
                        first_task=false
                        archived_count=$((archived_count + 1))
                    fi
                done <<< "$completed_tasks"
                
                # Remove completed tasks from outbox
                jq '.tasks = [.tasks[] | select(.status != "completed")]' "$outbox_file" > "$outbox_file.tmp" && mv "$outbox_file.tmp" "$outbox_file"
            fi
        fi
    done
    
    echo "" >> "$archive_file"
    echo "  ]" >> "$archive_file"
    echo "}" >> "$archive_file"
    
    log "SUCCESS" "Archived $archived_count completed tasks to $archive_file"
}

# Function to update sprint progress
update_final_progress() {
    log "DEBUG" "Updating final sprint progress..."
    
    if [ -f "$PROGRESS_FILE" ]; then
        # Update final statistics
        local stats=$(collect_agent_stats)
        IFS=',' read -r total_completed total_pending total_hours_completed total_hours_pending <<< "$stats"
        
        jq --arg timestamp "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
           --argjson completed "$total_completed" \
           --argjson pending "$total_pending" \
           --argjson hours_completed "$total_hours_completed" \
           --argjson hours_pending "$total_hours_pending" '
            .last_updated = $timestamp |
            .completed = $completed |
            .in_progress = $pending |
            .total_tasks = ($completed + $pending) |
            .daily_stats.hours_completed = $hours_completed |
            .daily_stats.hours_pending = $hours_pending
        ' "$PROGRESS_FILE" > "$PROGRESS_FILE.tmp" && mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE"
    fi
}

# Function to generate end-of-day summary
generate_eod_summary() {
    log "INFO" "Generating end-of-day summary..."
    
    local date=$(date +"%Y-%m-%d")
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    cat > "$EOD_SUMMARY" << EOF
# End of Day Summary - $date

Generated: $timestamp

## 🎯 Daily Accomplishments

### Tasks Completed Today
$(for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
    if [ -d "$agent_dir" ]; then
        local agent=$(basename "$agent_dir")
        local outbox_file="$agent_dir/outbox.json"
        
        if [ -f "$outbox_file" ]; then
            # Get completed tasks from today
            local today_completed=$(jq -r '.tasks[] | select(.status == "completed" and (.completed_at // .created_at) | startswith("'$(date +%Y-%m-%d)'")) | "- **\(.task_id)**: \(.title) (\(.estimated_hours)h) - \(.agent_id // "'$agent'")"' "$outbox_file" 2>/dev/null || echo "")
            
            if [ -n "$today_completed" ]; then
                echo "$today_completed"
            fi
        fi
    fi
done)

$(if [ "$METRICS" = true ]; then
    generate_performance_metrics
fi)

$(identify_blockers)

$(generate_tomorrow_prep)

## 📋 Team Status Overview

$(for agent_dir in "$PROJECT_ROOT/postbox"/*/; do
    if [ -d "$agent_dir" ]; then
        local agent=$(basename "$agent_dir")
        local outbox_file="$agent_dir/outbox.json"
        
        if [ -f "$outbox_file" ]; then
            local completed=$(jq '[.tasks[] | select(.status == "completed")] | length' "$outbox_file" 2>/dev/null || echo "0")
            local pending=$(jq '[.tasks[] | select(.status == "pending")] | length' "$outbox_file" 2>/dev/null || echo "0")
            local in_progress=$(jq '[.tasks[] | select(.status == "in_progress")] | length' "$outbox_file" 2>/dev/null || echo "0")
            local hours_pending=$(jq '[.tasks[] | select(.status == "pending") | .estimated_hours] | add // 0' "$outbox_file" 2>/dev/null || echo "0")
            
            echo "### $agent"
            echo "- ✅ Completed: $completed"
            echo "- ⏳ Pending: $pending ($hours_pending hours)"
            echo "- 🔄 In Progress: $in_progress"
            echo ""
        fi
    fi
done)

## 🔄 Session Wrap-up

- **Total session time**: $(if [ -f "/tmp/session_start_time" ]; then
    local start_time=$(cat /tmp/session_start_time 2>/dev/null || echo "unknown")
    if [ "$start_time" != "unknown" ]; then
        local duration=$(($(date +%s) - start_time))
        echo "${duration}s ($(($duration / 3600))h $(($duration % 3600 / 60))m)"
    else
        echo "unknown"
    fi
else
    echo "unknown"
fi)
- **Archive status**: $(if [ "$ARCHIVE" = true ]; then echo "Completed tasks archived"; else echo "No archiving performed"; fi)
- **Next session**: Run \`tools/morning_kickoff.sh\` to start tomorrow

---
*Generated by end_of_day.sh automation*
EOF

    log "SUCCESS" "End-of-day summary generated: $EOD_SUMMARY"
}

# Main function
main() {
    echo -e "${CYAN}"
    echo "🌙 ========================================"
    echo "   END OF DAY WRAP-UP"
    echo "   Phase 6.15 Sprint 1"
    echo "   $(date +'%A, %B %d, %Y - %H:%M')"
    echo "========================================"
    echo -e "${NC}"
    
    log "INFO" "Starting end-of-day wrap-up..."
    
    # Record session end time if start time exists
    if [ -f "/tmp/session_start_time" ]; then
        echo "$(date +%s)" > "/tmp/session_end_time"
    fi
    
    # Archive completed tasks if requested
    archive_completed_tasks
    
    # Update final progress
    update_final_progress
    
    # Generate end-of-day summary
    generate_eod_summary
    
    # Display summary
    echo ""
    echo -e "${CYAN}📊 End-of-Day Summary Generated:${NC}"
    echo -e "${BLUE}$EOD_SUMMARY${NC}"
    echo ""
    
    log "SUCCESS" "End-of-day wrap-up completed successfully!"
    
    echo ""
    echo -e "${YELLOW}🌙 Session Complete!${NC}"
    echo -e "${BLUE}Summary available at:${NC} $EOD_SUMMARY"
    echo -e "${BLUE}Tomorrow's kickoff:${NC} tools/morning_kickoff.sh"
    
    if [ "$ARCHIVE" = true ]; then
        echo -e "${BLUE}Archived tasks:${NC} $ARCHIVE_DIR/"
    fi
    
    echo ""
    echo -e "${GREEN}Sweet dreams! 😴${NC}"
}

# Run main function
main "$@" 