#!/bin/bash
# assign_task.sh - Assign a new task to an agent

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display usage
usage() {
    echo "Usage: $0 <agent_id> <task_id> <title> <priority> [estimated_hours]"
    echo ""
    echo "Arguments:"
    echo "  agent_id         - Agent ID (e.g., CA, CB, CC)"
    echo "  task_id          - Task ID (e.g., TASK-165D)"
    echo "  title            - Task title (in quotes)"
    echo "  priority         - Priority level (HIGH, MEDIUM, LOW)"
    echo "  estimated_hours  - Optional estimated hours (default: 2)"
    echo ""
    echo "Example:"
    echo "  $0 CA TASK-165D \"Implement new feature\" HIGH 4"
    exit 1
}

# Check arguments
if [ $# -lt 4 ]; then
    usage
fi

AGENT_ID="$1"
TASK_ID="$2"
TITLE="$3"
PRIORITY="$4"
ESTIMATED_HOURS="${5:-2}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Validate priority
if [[ ! "$PRIORITY" =~ ^(HIGH|MEDIUM|LOW)$ ]]; then
    echo -e "${RED}Error: Priority must be HIGH, MEDIUM, or LOW${NC}"
    exit 1
fi

echo -e "${YELLOW}Assigning task $TASK_ID to agent $AGENT_ID...${NC}"

# Ensure postbox directory exists
mkdir -p "$PROJECT_ROOT/postbox/$AGENT_ID/inbox"

# Create or update outbox.json
OUTBOX_FILE="$PROJECT_ROOT/postbox/$AGENT_ID/outbox.json"
if [ ! -f "$OUTBOX_FILE" ]; then
    echo "Creating new outbox.json for agent $AGENT_ID..."
    echo '{
  "agent_id": "'$AGENT_ID'",
  "agent_name": "Agent '$AGENT_ID'",
  "expertise": [],
  "tasks": []
}' > "$OUTBOX_FILE"
fi

# Add task to outbox.json
echo "Adding task to outbox.json..."
jq --arg task_id "$TASK_ID" \
   --arg title "$TITLE" \
   --arg priority "$PRIORITY" \
   --arg timestamp "$TIMESTAMP" \
   --argjson hours "$ESTIMATED_HOURS" '
    .tasks += [{
        "task_id": $task_id,
        "title": $title,
        "priority": $priority,
        "status": "pending",
        "created_at": $timestamp,
        "estimated_hours": $hours,
        "description": "Task assigned via assign_task.sh script",
        "deliverables": [],
        "dependencies": []
    }]
' "$OUTBOX_FILE" > "$OUTBOX_FILE.tmp" && mv "$OUTBOX_FILE.tmp" "$OUTBOX_FILE"

echo -e "${GREEN}✓ Added task to outbox.json${NC}"

# Create task assignment file in inbox
TASK_FILE="$PROJECT_ROOT/postbox/$AGENT_ID/inbox/${TASK_ID}.md"
cat > "$TASK_FILE" << EOF
# Task Assignment: $TASK_ID

## Task Details
- **Task ID**: $TASK_ID
- **Title**: $TITLE
- **Priority**: $PRIORITY
- **Estimated Hours**: $ESTIMATED_HOURS
- **Assigned**: $TIMESTAMP
- **Agent**: $AGENT_ID

## Description
This task has been assigned via the automated task assignment system.

## Instructions
1. Review the task requirements
2. Complete the deliverables
3. Update status using: \`tools/complete_task.sh $AGENT_ID $TASK_ID\`

## Status
Current Status: **PENDING**

---
*This task was assigned using the assign_task.sh script*
EOF

echo -e "${GREEN}✓ Created task assignment in inbox${NC}"

# Update .sprint/progress.json
PROGRESS_FILE="$PROJECT_ROOT/.sprint/progress.json"
if [ ! -f "$PROGRESS_FILE" ]; then
    mkdir -p "$PROJECT_ROOT/.sprint"
    echo '{
  "sprint": "current",
  "tasks": []
}' > "$PROGRESS_FILE"
fi

# Add task to progress.json
jq --arg task_id "$TASK_ID" \
   --arg agent "$AGENT_ID" \
   --arg timestamp "$TIMESTAMP" \
   --arg title "$TITLE" \
   --arg priority "$PRIORITY" '
    .tasks += [{
        "id": $task_id,
        "title": $title,
        "priority": $priority,
        "status": "assigned",
        "assigned_to": $agent,
        "assigned_at": $timestamp
    }]
' "$PROGRESS_FILE" > "$PROGRESS_FILE.tmp" && mv "$PROGRESS_FILE.tmp" "$PROGRESS_FILE"

echo -e "${GREEN}✓ Updated progress.json${NC}"

# Create notification flag for agent monitoring
NOTIFICATION_FLAG="$PROJECT_ROOT/postbox/$AGENT_ID/inbox/NEW_TASK_${TASK_ID}.flag"
echo "$TIMESTAMP" > "$NOTIFICATION_FLAG"

echo -e "${GREEN}✓ Created notification flag${NC}"

# Summary
echo ""
echo -e "${GREEN}=== Task Assignment Summary ===${NC}"
echo -e "Task ID: ${YELLOW}$TASK_ID${NC}"
echo -e "Title: ${BLUE}$TITLE${NC}"
echo -e "Agent: ${YELLOW}$AGENT_ID${NC}"
echo -e "Priority: ${YELLOW}$PRIORITY${NC}"
echo -e "Estimated Hours: $ESTIMATED_HOURS"
echo -e "Status: ${YELLOW}ASSIGNED${NC}"
echo -e "Time: $TIMESTAMP"
echo -e "${GREEN}===============================${NC}"
echo ""
echo -e "Task file created at: ${BLUE}$TASK_FILE${NC}"