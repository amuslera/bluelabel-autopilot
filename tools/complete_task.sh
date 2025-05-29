#!/bin/bash
# complete_task.sh - Mark a task as complete and update all relevant files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 <agent_id> <task_id> [completion_message]"
    echo ""
    echo "Arguments:"
    echo "  agent_id         - Agent ID (e.g., CA, CB, CC)"
    echo "  task_id          - Task ID (e.g., TASK-165C)"
    echo "  completion_message - Optional completion message"
    echo ""
    echo "Example:"
    echo "  $0 CC TASK-165C \"Completed all deliverables successfully\""
    exit 1
}

# Check arguments
if [ $# -lt 2 ]; then
    usage
fi

AGENT_ID="$1"
TASK_ID="$2"
COMPLETION_MESSAGE="${3:-Task completed successfully}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo -e "${YELLOW}Marking task $TASK_ID as complete for agent $AGENT_ID...${NC}"

# Update outbox.json
OUTBOX_FILE="$PROJECT_ROOT/postbox/$AGENT_ID/outbox.json"
if [ -f "$OUTBOX_FILE" ]; then
    echo "Updating $OUTBOX_FILE..."
    
    # Create a temporary file with updated status
    jq --arg task_id "$TASK_ID" --arg timestamp "$TIMESTAMP" --arg message "$COMPLETION_MESSAGE" '
        .tasks |= map(
            if .task_id == $task_id then
                .status = "completed" |
                .completed_at = $timestamp |
                .completion_message = $message
            else . end
        )
    ' "$OUTBOX_FILE" > "$OUTBOX_FILE.tmp" && mv "$OUTBOX_FILE.tmp" "$OUTBOX_FILE"
    
    echo -e "${GREEN}✓ Updated outbox.json${NC}"
else
    echo -e "${RED}✗ Outbox file not found: $OUTBOX_FILE${NC}"
fi

# Update .sprint/progress.json if it exists
PROGRESS_FILE="$PROJECT_ROOT/.sprint/progress.json"
if [ -f "$PROGRESS_FILE" ]; then
    echo "Updating $PROGRESS_FILE..."
    
    # Check if task exists in progress.json
    if jq -e --arg task_id "$TASK_ID" '.tasks[] | select(.id == $task_id)' "$PROGRESS_FILE" > /dev/null 2>&1; then
        # Update existing task
        jq --arg task_id "$TASK_ID" --arg timestamp "$TIMESTAMP" --arg agent "$AGENT_ID" '
            .tasks |= map(
                if .id == $task_id then
                    .status = "completed" |
                    .completed_at = $timestamp |
                    .completed_by = $agent
                else . end
            )
        ' "$PROGRESS_FILE" > "$PROGRESS_FILE.tmp" && mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE"
    else
        # Add new completed task
        jq --arg task_id "$TASK_ID" --arg timestamp "$TIMESTAMP" --arg agent "$AGENT_ID" '
            .tasks += [{
                "id": $task_id,
                "status": "completed",
                "assigned_to": $agent,
                "completed_at": $timestamp,
                "completed_by": $agent
            }]
        ' "$PROGRESS_FILE" > "$PROGRESS_FILE.tmp" && mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE"
    fi
    
    echo -e "${GREEN}✓ Updated progress.json${NC}"
else
    echo -e "${YELLOW}⚠ Progress file not found, creating .sprint directory...${NC}"
    mkdir -p "$PROJECT_ROOT/.sprint"
    echo '{
  "sprint": "current",
  "tasks": [
    {
      "id": "'$TASK_ID'",
      "status": "completed",
      "assigned_to": "'$AGENT_ID'",
      "completed_at": "'$TIMESTAMP'",
      "completed_by": "'$AGENT_ID'"
    }
  ]
}' > "$PROGRESS_FILE"
    echo -e "${GREEN}✓ Created progress.json${NC}"
fi

# Create a completion record in postbox
COMPLETION_RECORD="$PROJECT_ROOT/postbox/$AGENT_ID/completed/${TASK_ID}_completion.json"
mkdir -p "$PROJECT_ROOT/postbox/$AGENT_ID/completed"

echo '{
  "task_id": "'$TASK_ID'",
  "agent_id": "'$AGENT_ID'",
  "status": "completed",
  "completed_at": "'$TIMESTAMP'",
  "completion_message": "'$COMPLETION_MESSAGE'"
}' > "$COMPLETION_RECORD"

echo -e "${GREEN}✓ Created completion record${NC}"

# Summary
echo ""
echo -e "${GREEN}=== Task Completion Summary ===${NC}"
echo -e "Task ID: ${YELLOW}$TASK_ID${NC}"
echo -e "Agent: ${YELLOW}$AGENT_ID${NC}"
echo -e "Status: ${GREEN}COMPLETED${NC}"
echo -e "Time: $TIMESTAMP"
echo -e "Message: $COMPLETION_MESSAGE"
echo -e "${GREEN}===============================${NC}"