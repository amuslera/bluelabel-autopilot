#!/bin/bash
# update_progress.sh - Synchronize task progress from all agents to .sprint/progress.json

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

echo -e "${CYAN}=== Updating Sprint Progress ===${NC}"
echo -e "Synchronizing task status from all agents..."
echo ""

# Ensure .sprint directory exists
mkdir -p "$PROJECT_ROOT/.sprint"

# Initialize progress file if it doesn't exist
PROGRESS_FILE="$PROJECT_ROOT/.sprint/progress.json"
if [ ! -f "$PROGRESS_FILE" ]; then
    echo '{
  "sprint": "current",
  "last_updated": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "tasks": []
}' > "$PROGRESS_FILE"
    echo -e "${GREEN}✓ Created new progress.json${NC}"
fi

# Create temporary file for building new progress
TEMP_PROGRESS=$(mktemp)

# Start building the JSON structure
echo '{
  "sprint": "current",
  "last_updated": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
  "tasks": [' > "$TEMP_PROGRESS"

# Track if we've added any tasks
first_task=true

# Collect tasks from all agent outboxes
for outbox in "$PROJECT_ROOT"/postbox/*/outbox.json; do
    if [ -f "$outbox" ]; then
        agent_id=$(basename $(dirname "$outbox"))
        echo -e "Processing agent ${YELLOW}$agent_id${NC}..."
        
        # Extract tasks from outbox
        tasks=$(jq -c '.tasks[]' "$outbox" 2>/dev/null || true)
        
        if [ -n "$tasks" ]; then
            while IFS= read -r task; do
                # Add comma if not first task
                if [ "$first_task" = false ]; then
                    echo "," >> "$TEMP_PROGRESS"
                else
                    first_task=false
                fi
                
                # Extract task details
                task_id=$(echo "$task" | jq -r '.task_id')
                title=$(echo "$task" | jq -r '.title')
                status=$(echo "$task" | jq -r '.status')
                priority=$(echo "$task" | jq -r '.priority // "MEDIUM"')
                created_at=$(echo "$task" | jq -r '.created_at // ""')
                completed_at=$(echo "$task" | jq -r '.completed_at // ""')
                estimated_hours=$(echo "$task" | jq -r '.estimated_hours // 0')
                
                # Build task entry
                cat >> "$TEMP_PROGRESS" << EOF
    {
      "id": "$task_id",
      "title": "$title",
      "status": "$status",
      "priority": "$priority",
      "assigned_to": "$agent_id",
      "estimated_hours": $estimated_hours
EOF
                
                # Add optional fields if they exist
                if [ -n "$created_at" ] && [ "$created_at" != "null" ]; then
                    echo ',' >> "$TEMP_PROGRESS"
                    echo "      \"created_at\": \"$created_at\"" >> "$TEMP_PROGRESS"
                fi
                
                if [ -n "$completed_at" ] && [ "$completed_at" != "null" ]; then
                    echo ',' >> "$TEMP_PROGRESS"
                    echo "      \"completed_at\": \"$completed_at\"" >> "$TEMP_PROGRESS"
                    echo ',' >> "$TEMP_PROGRESS"
                    echo "      \"completed_by\": \"$agent_id\"" >> "$TEMP_PROGRESS"
                fi
                
                echo -n "    }" >> "$TEMP_PROGRESS"
                
                echo -e "  ${GREEN}✓${NC} Added task: $task_id ($status)"
            done <<< "$tasks"
        fi
    fi
done

# Close the JSON structure
echo '
  ]
}' >> "$TEMP_PROGRESS"

# Validate the JSON
if jq . "$TEMP_PROGRESS" > /dev/null 2>&1; then
    # Format and save the progress file
    jq . "$TEMP_PROGRESS" > "$PROGRESS_FILE"
    echo -e "\n${GREEN}✓ Successfully updated progress.json${NC}"
    
    # Show summary
    total_tasks=$(jq '.tasks | length' "$PROGRESS_FILE")
    completed_tasks=$(jq '.tasks | map(select(.status == "completed")) | length' "$PROGRESS_FILE")
    in_progress_tasks=$(jq '.tasks | map(select(.status == "in_progress")) | length' "$PROGRESS_FILE")
    pending_tasks=$(jq '.tasks | map(select(.status == "pending")) | length' "$PROGRESS_FILE")
    
    echo ""
    echo -e "${CYAN}=== Progress Summary ===${NC}"
    echo -e "Total Tasks: ${YELLOW}$total_tasks${NC}"
    echo -e "Completed: ${GREEN}$completed_tasks${NC}"
    echo -e "In Progress: ${YELLOW}$in_progress_tasks${NC}"
    echo -e "Pending: ${BLUE}$pending_tasks${NC}"
    
    # Calculate completion percentage
    if [ $total_tasks -gt 0 ]; then
        completion_pct=$((completed_tasks * 100 / total_tasks))
        echo -e "Completion: ${GREEN}$completion_pct%${NC}"
    fi
else
    echo -e "${RED}✗ Error: Failed to create valid JSON${NC}"
    rm -f "$TEMP_PROGRESS"
    exit 1
fi

# Clean up
rm -f "$TEMP_PROGRESS"

# Optionally create a backup
BACKUP_DIR="$PROJECT_ROOT/.sprint/backups"
mkdir -p "$BACKUP_DIR"
BACKUP_FILE="$BACKUP_DIR/progress_$(date +%Y%m%d_%H%M%S).json"
cp "$PROGRESS_FILE" "$BACKUP_FILE"
echo -e "\n${BLUE}Backup saved to: $BACKUP_FILE${NC}"