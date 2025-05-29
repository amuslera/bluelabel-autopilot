#!/bin/bash
"""
Enhanced Task Completion Script with Signal Integration
Part of TASK-165I: Agent Communication Protocol
Automatically sends completion signals when tasks are finished
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AGENT_ID=${AGENT_ID:-"CA"}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Usage function
usage() {
    echo "Enhanced Task Completion with Signal Integration"
    echo ""
    echo "Usage: $0 [OPTIONS] <task_id>"
    echo ""
    echo "Options:"
    echo "  -a, --agent AGENT_ID    Agent completing the task (default: \$AGENT_ID or CA)"
    echo "  -m, --message MESSAGE   Custom completion message"
    echo "  -d, --deliverables LIST Comma-separated list of deliverables"
    echo "  -f, --follow-up         Indicate follow-up work is available"
    echo "  -h, --handoff AGENT     Request handoff to specific agent"
    echo "  -p, --priority PRIORITY Signal priority (LOW, MEDIUM, HIGH, CRITICAL)"
    echo "  -s, --skip-signal       Skip sending completion signal"
    echo "  -r, --ready             Also send READY signal after completion"
    echo "  --help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 TASK-165I"
    echo "  $0 -m \"Dashboard implemented successfully\" -d \"UI,API,docs\" TASK-165G"
    echo "  $0 -h CB -f TASK-165J"
    echo "  $0 -r --priority HIGH TASK-165K"
    echo ""
    echo "Environment Variables:"
    echo "  AGENT_ID                Current agent identifier"
}

# Parse command line arguments
TASK_ID=""
MESSAGE=""
DELIVERABLES=""
FOLLOW_UP=false
HANDOFF_AGENT=""
PRIORITY="LOW"
SKIP_SIGNAL=false
SEND_READY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--agent)
            AGENT_ID="$2"
            shift 2
            ;;
        -m|--message)
            MESSAGE="$2"
            shift 2
            ;;
        -d|--deliverables)
            DELIVERABLES="$2"
            shift 2
            ;;
        -f|--follow-up)
            FOLLOW_UP=true
            shift
            ;;
        -h|--handoff)
            HANDOFF_AGENT="$2"
            shift 2
            ;;
        -p|--priority)
            PRIORITY="$2"
            shift 2
            ;;
        -s|--skip-signal)
            SKIP_SIGNAL=true
            shift
            ;;
        -r|--ready)
            SEND_READY=true
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        -*)
            echo -e "${RED}Error: Unknown option $1${NC}" >&2
            usage
            exit 1
            ;;
        *)
            if [[ -z "$TASK_ID" ]]; then
                TASK_ID="$1"
            else
                echo -e "${RED}Error: Multiple task IDs provided${NC}" >&2
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

# Validate required arguments
if [[ -z "$TASK_ID" ]]; then
    echo -e "${RED}Error: Task ID is required${NC}" >&2
    usage
    exit 1
fi

# Validate agent ID
VALID_AGENTS=("CA" "CB" "CC" "WA" "ARCH" "BLUE")
if [[ ! " ${VALID_AGENTS[@]} " =~ " ${AGENT_ID} " ]]; then
    echo -e "${RED}Error: Invalid agent ID: $AGENT_ID${NC}" >&2
    echo "Valid agents: ${VALID_AGENTS[*]}"
    exit 1
fi

# Validate priority
VALID_PRIORITIES=("LOW" "MEDIUM" "HIGH" "CRITICAL")
if [[ ! " ${VALID_PRIORITIES[@]} " =~ " ${PRIORITY} " ]]; then
    echo -e "${RED}Error: Invalid priority: $PRIORITY${NC}" >&2
    echo "Valid priorities: ${VALID_PRIORITIES[*]}"
    exit 1
fi

# Set default message if not provided
if [[ -z "$MESSAGE" ]]; then
    MESSAGE="Task $TASK_ID completed successfully"
fi

echo -e "${BLUE}🚀 Completing Task: $TASK_ID${NC}"
echo -e "${BLUE}Agent: $AGENT_ID${NC}"
echo -e "${BLUE}Message: $MESSAGE${NC}"

# Update agent outbox with task completion
update_outbox() {
    local outbox_file="$PROJECT_ROOT/postbox/$AGENT_ID/outbox.json"
    
    if [[ -f "$outbox_file" ]]; then
        echo -e "${YELLOW}📝 Updating agent outbox...${NC}"
        
        # Create a temporary Python script to update the outbox
        python3 -c "
import json
import sys
from datetime import datetime

outbox_file = '$outbox_file'
task_id = '$TASK_ID'
message = '''$MESSAGE'''

try:
    with open(outbox_file, 'r') as f:
        outbox = json.load(f)
except:
    outbox = {
        'agent_id': '$AGENT_ID',
        'tasks': [],
        'history': [],
        'metadata': {}
    }

# Find and update the task
task_found = False
for task in outbox.get('tasks', []):
    if task.get('task_id') == task_id:
        task['status'] = 'completed'
        task['completed_at'] = datetime.utcnow().isoformat() + 'Z'
        task_found = True
        break

# Add to history
history_entry = {
    'task_id': task_id,
    'timestamp': datetime.utcnow().isoformat() + 'Z',
    'status': 'completed',
    'summary': message,
    'completion_message': message
}

if 'history' not in outbox:
    outbox['history'] = []
outbox['history'].append(history_entry)

# Update metadata
if 'metadata' not in outbox:
    outbox['metadata'] = {}
outbox['metadata']['last_updated'] = datetime.utcnow().isoformat() + 'Z'
outbox['metadata']['total_tasks_completed'] = outbox['metadata'].get('total_tasks_completed', 0) + 1

# Save updated outbox
with open(outbox_file, 'w') as f:
    json.dump(outbox, f, indent=2)

if task_found:
    print('✓ Task updated in outbox')
else:
    print('! Task not found in outbox - added to history only')
"
    else
        echo -e "${YELLOW}⚠️  Outbox file not found: $outbox_file${NC}"
    fi
}

# Send completion signal
send_completion_signal() {
    if [[ "$SKIP_SIGNAL" == true ]]; then
        echo -e "${YELLOW}⏭️  Skipping completion signal${NC}"
        return
    fi
    
    echo -e "${YELLOW}📡 Sending completion signal...${NC}"
    
    # Build deliverables array
    local deliverables_json="[]"
    if [[ -n "$DELIVERABLES" ]]; then
        # Convert comma-separated list to JSON array
        deliverables_json=$(echo "[$DELIVERABLES]" | sed 's/,/","/g' | sed 's/\[/["/' | sed 's/\]/"]/')
    fi
    
    # Build context JSON
    local context_json="{
        \"completed_task\": \"$TASK_ID\",
        \"deliverables\": $deliverables_json,
        \"follow_up_available\": $FOLLOW_UP
    }"
    
    # Send signal
    export AGENT_ID="$AGENT_ID"
    python3 "$SCRIPT_DIR/send_signal.py" \
        --type COMPLETED \
        --message "$MESSAGE" \
        --context "$context_json" \
        --priority "$PRIORITY"
    
    echo -e "${GREEN}✓ Completion signal sent${NC}"
}

# Send handoff request
send_handoff_request() {
    if [[ -z "$HANDOFF_AGENT" ]]; then
        return
    fi
    
    echo -e "${YELLOW}🤝 Sending handoff request to $HANDOFF_AGENT...${NC}"
    
    local handoff_message="Task $TASK_ID ready for handoff to $HANDOFF_AGENT"
    local context_json="{
        \"task_id\": \"$TASK_ID\",
        \"from_agent\": \"$AGENT_ID\",
        \"handoff_artifacts\": [\"Task completion\", \"Deliverables\"],
        \"acceptance_criteria\": [\"Review deliverables\", \"Continue implementation\"]
    }"
    
    export AGENT_ID="$AGENT_ID"
    python3 "$SCRIPT_DIR/send_signal.py" \
        --type HANDOFF_REQUEST \
        --to "$HANDOFF_AGENT" \
        --message "$handoff_message" \
        --context "$context_json" \
        --priority "HIGH"
    
    echo -e "${GREEN}✓ Handoff request sent to $HANDOFF_AGENT${NC}"
}

# Send ready signal
send_ready_signal() {
    if [[ "$SEND_READY" != true ]]; then
        return
    fi
    
    echo -e "${YELLOW}✅ Sending ready signal...${NC}"
    
    local ready_message="Available for new tasks after completing $TASK_ID"
    local context_json="{
        \"completed_task\": \"$TASK_ID\",
        \"available_for\": [\"frontend\", \"ui\", \"integration\"],
        \"estimated_capacity\": \"6 hours\"
    }"
    
    export AGENT_ID="$AGENT_ID"
    python3 "$SCRIPT_DIR/send_signal.py" \
        --type READY \
        --message "$ready_message" \
        --context "$context_json" \
        --priority "MEDIUM"
    
    echo -e "${GREEN}✓ Ready signal sent${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}🎯 Starting task completion process...${NC}"
    
    # Update outbox
    update_outbox
    
    # Send completion signal
    send_completion_signal
    
    # Send handoff request if specified
    send_handoff_request
    
    # Send ready signal if specified
    send_ready_signal
    
    echo -e "${GREEN}✅ Task $TASK_ID completed successfully!${NC}"
    
    # Show active signals
    echo -e "${BLUE}📡 Checking for active signals...${NC}"
    python3 "$SCRIPT_DIR/check_signals.py" --active
}

# Error handling
trap 'echo -e "${RED}❌ Error occurred during task completion${NC}" >&2; exit 1' ERR

# Run main function
main 