#!/bin/bash
# complete_task_with_recovery.sh - Enhanced task completion with retry logic and error recovery

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Import file locking
PYTHON_CMD="python3"

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Retry configuration
MAX_RETRIES=3
RETRY_DELAY=2

# Function to display usage
usage() {
    echo "Usage: $0 <agent_id> <task_id> [completion_message]"
    echo ""
    echo "Arguments:"
    echo "  agent_id         - Agent ID (e.g., CA, CB, CC)"
    echo "  task_id          - Task ID (e.g., TASK-165C)"
    echo "  completion_message - Optional completion message"
    echo ""
    echo "Features:"
    echo "  - Automatic retry on failure (max $MAX_RETRIES attempts)"
    echo "  - File locking to prevent concurrent updates"
    echo "  - Checkpoint creation for recovery"
    echo "  - Rollback on critical failures"
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

# Checkpoint functions
create_checkpoint() {
    local checkpoint_file="$PROJECT_ROOT/data/checkpoints/${TASK_ID}_completion.json"
    mkdir -p "$(dirname "$checkpoint_file")"
    
    cat > "$checkpoint_file" << EOF
{
  "task_id": "$TASK_ID",
  "agent_id": "$AGENT_ID",
  "timestamp": "$TIMESTAMP",
  "status": "$1",
  "data": {
    "outbox_updated": ${2:-false},
    "progress_updated": ${3:-false},
    "completion_record_created": ${4:-false}
  }
}
EOF
}

# Rollback function
rollback_changes() {
    echo -e "${YELLOW}Rolling back changes for $TASK_ID...${NC}"
    
    # Restore outbox backup if exists
    OUTBOX_BACKUP="$PROJECT_ROOT/postbox/$AGENT_ID/outbox.json.backup_$TASK_ID"
    if [ -f "$OUTBOX_BACKUP" ]; then
        cp "$OUTBOX_BACKUP" "$PROJECT_ROOT/postbox/$AGENT_ID/outbox.json"
        rm "$OUTBOX_BACKUP"
        echo -e "${GREEN}✓ Restored outbox.json from backup${NC}"
    fi
    
    # Restore progress backup if exists
    PROGRESS_BACKUP="$PROJECT_ROOT/.sprint/progress.json.backup_$TASK_ID"
    if [ -f "$PROGRESS_BACKUP" ]; then
        cp "$PROGRESS_BACKUP" "$PROJECT_ROOT/.sprint/progress.json"
        rm "$PROGRESS_BACKUP"
        echo -e "${GREEN}✓ Restored progress.json from backup${NC}"
    fi
    
    # Remove incomplete completion record
    COMPLETION_RECORD="$PROJECT_ROOT/postbox/$AGENT_ID/completed/${TASK_ID}_completion.json"
    if [ -f "$COMPLETION_RECORD" ]; then
        rm "$COMPLETION_RECORD"
        echo -e "${GREEN}✓ Removed incomplete completion record${NC}"
    fi
}

# Function to update file with retry
update_with_retry() {
    local file_path="$1"
    local update_function="$2"
    local description="$3"
    local attempt=0
    
    while [ $attempt -lt $MAX_RETRIES ]; do
        attempt=$((attempt + 1))
        
        echo -e "${BLUE}Attempt $attempt/$MAX_RETRIES: $description${NC}"
        
        # Try to acquire lock and update
        if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from file_lock import file_transaction
import json
import time

def update_file():
    with file_transaction('$file_path', backup=True) as f:
        time.sleep(0.1)  # Simulate some processing
        $update_function
        return True

try:
    result = update_file()
    sys.exit(0)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
"; then
            echo -e "${GREEN}✓ $description succeeded${NC}"
            return 0
        else
            if [ $attempt -lt $MAX_RETRIES ]; then
                echo -e "${YELLOW}⚠ $description failed, retrying in ${RETRY_DELAY}s...${NC}"
                sleep $RETRY_DELAY
            else
                echo -e "${RED}✗ $description failed after $MAX_RETRIES attempts${NC}"
                return 1
            fi
        fi
    done
}

echo -e "${YELLOW}Marking task $TASK_ID as complete for agent $AGENT_ID...${NC}"

# Initialize checkpoint
create_checkpoint "started" false false false

# Create backups
OUTBOX_FILE="$PROJECT_ROOT/postbox/$AGENT_ID/outbox.json"
PROGRESS_FILE="$PROJECT_ROOT/.sprint/progress.json"

if [ -f "$OUTBOX_FILE" ]; then
    cp "$OUTBOX_FILE" "$OUTBOX_FILE.backup_$TASK_ID"
fi

if [ -f "$PROGRESS_FILE" ]; then
    cp "$PROGRESS_FILE" "$PROGRESS_FILE.backup_$TASK_ID"
fi

# Track success
OUTBOX_UPDATED=false
PROGRESS_UPDATED=false
COMPLETION_CREATED=false

# Update outbox.json with retry
if [ -f "$OUTBOX_FILE" ]; then
    UPDATE_OUTBOX_FUNC="
with open('$OUTBOX_FILE', 'r') as f:
    data = json.load(f)

# Update task status
for task in data.get('tasks', []):
    if task.get('task_id') == '$TASK_ID':
        task['status'] = 'completed'
        task['completed_at'] = '$TIMESTAMP'
        task['completion_message'] = '''$COMPLETION_MESSAGE'''
        break

with open('$OUTBOX_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    
    if update_with_retry "$OUTBOX_FILE" "$UPDATE_OUTBOX_FUNC" "Updating outbox.json"; then
        OUTBOX_UPDATED=true
        create_checkpoint "outbox_updated" true false false
    else
        rollback_changes
        exit 1
    fi
else
    echo -e "${RED}✗ Outbox file not found: $OUTBOX_FILE${NC}"
fi

# Update .sprint/progress.json with retry
if [ -f "$PROGRESS_FILE" ]; then
    UPDATE_PROGRESS_FUNC="
with open('$PROGRESS_FILE', 'r') as f:
    data = json.load(f)

# Handle both object and array formats for tasks
tasks = data.get('tasks', {})

if isinstance(tasks, dict):
    # Object format
    if '$TASK_ID' in tasks:
        tasks['$TASK_ID']['status'] = 'completed'
        tasks['$TASK_ID']['completed_at'] = '$TIMESTAMP'
        tasks['$TASK_ID']['completed_by'] = '$AGENT_ID'
elif isinstance(tasks, list):
    # Array format
    for task in tasks:
        if task.get('id') == '$TASK_ID':
            task['status'] = 'completed'
            task['completed_at'] = '$TIMESTAMP'
            task['completed_by'] = '$AGENT_ID'
            break
    else:
        # Add new task if not found
        tasks.append({
            'id': '$TASK_ID',
            'status': 'completed',
            'assigned_to': '$AGENT_ID',
            'completed_at': '$TIMESTAMP',
            'completed_by': '$AGENT_ID'
        })

# Update completed count
if 'completed' in data:
    data['completed'] = data.get('completed', 0) + 1

with open('$PROGRESS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"
    
    if update_with_retry "$PROGRESS_FILE" "$UPDATE_PROGRESS_FUNC" "Updating progress.json"; then
        PROGRESS_UPDATED=true
        create_checkpoint "progress_updated" true true false
    else
        echo -e "${YELLOW}⚠ Progress file update failed, continuing...${NC}"
    fi
else
    echo -e "${YELLOW}⚠ Progress file not found, creating .sprint directory...${NC}"
    mkdir -p "$PROJECT_ROOT/.sprint"
    echo '{
  "sprint": "current",
  "tasks": {
    "'$TASK_ID'": {
      "status": "completed",
      "agent": "'$AGENT_ID'",
      "completed_at": "'$TIMESTAMP'"
    }
  }
}' > "$PROGRESS_FILE"
    PROGRESS_UPDATED=true
fi

# Create completion record with retry
COMPLETION_RECORD="$PROJECT_ROOT/postbox/$AGENT_ID/completed/${TASK_ID}_completion.json"
mkdir -p "$PROJECT_ROOT/postbox/$AGENT_ID/completed"

CREATE_COMPLETION_FUNC="
completion_data = {
    'task_id': '$TASK_ID',
    'agent_id': '$AGENT_ID',
    'status': 'completed',
    'completed_at': '$TIMESTAMP',
    'completion_message': '''$COMPLETION_MESSAGE'''
}

with open('$COMPLETION_RECORD', 'w') as f:
    json.dump(completion_data, f, indent=2)
"

if $PYTHON_CMD -c "
import json
$CREATE_COMPLETION_FUNC
"; then
    echo -e "${GREEN}✓ Created completion record${NC}"
    COMPLETION_CREATED=true
    create_checkpoint "completed" true true true
else
    echo -e "${YELLOW}⚠ Failed to create completion record${NC}"
fi

# Clean up backups if everything succeeded
if [ "$OUTBOX_UPDATED" = true ] && [ "$PROGRESS_UPDATED" = true ]; then
    rm -f "$OUTBOX_FILE.backup_$TASK_ID"
    rm -f "$PROGRESS_FILE.backup_$TASK_ID"
fi

# Summary
echo ""
echo -e "${GREEN}=== Task Completion Summary ===${NC}"
echo -e "Task ID: ${YELLOW}$TASK_ID${NC}"
echo -e "Agent: ${YELLOW}$AGENT_ID${NC}"
echo -e "Status: ${GREEN}COMPLETED${NC}"
echo -e "Time: $TIMESTAMP"
echo -e "Message: $COMPLETION_MESSAGE"
echo ""
echo -e "Updates:"
echo -e "  Outbox: $([ "$OUTBOX_UPDATED" = true ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}")"
echo -e "  Progress: $([ "$PROGRESS_UPDATED" = true ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}")"
echo -e "  Completion Record: $([ "$COMPLETION_CREATED" = true ] && echo -e "${GREEN}✓${NC}" || echo -e "${RED}✗${NC}")"
echo -e "${GREEN}===============================${NC}"