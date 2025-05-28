#!/bin/bash
# Quick demo trigger commands for recording

echo "🎬 Bluelabel Autopilot Demo Triggers"
echo "====================================="
echo ""
echo "1. Create Email → PDF → Summary workflow:"
echo "   curl -X POST http://localhost:8000/api/test/create-sample-workflow"
echo ""
echo "2. Trigger retry demo (fails 2x, succeeds 3rd):"
echo "   python3 demo_coordinator.py (then press 2)"
echo ""
echo "3. Show all workflows:"
echo "   curl http://localhost:8000/api/dag-runs | jq '.items[] | {id: .id[0:8], name: .workflow_name, status: .status}'"
echo ""
echo "4. Create fresh workflow for live demo:"
echo "   curl -X POST http://localhost:8000/api/test/create-sample-workflow -s | jq '{id: .id[0:8], status: .status}'"
echo ""

# Function to create workflow and return ID
create_workflow() {
    echo "Creating new test workflow..."
    RESPONSE=$(curl -X POST http://localhost:8000/api/test/create-sample-workflow -s)
    ID=$(echo $RESPONSE | jq -r '.id')
    echo "✅ Created workflow: $ID"
    echo "   Watch it at: http://localhost:3000/dag/$ID"
}

# Check if argument provided
if [ "$1" = "create" ]; then
    create_workflow
elif [ "$1" = "list" ]; then
    echo "Current workflows:"
    curl http://localhost:8000/api/dag-runs -s | jq '.items[] | {id: .id[0:8], name: .workflow_name, status: .status}'
elif [ "$1" = "stats" ]; then
    echo "System statistics:"
    curl http://localhost:8000/api/dag-runs -s | jq '{total: .total, items: .items | length}'
else
    echo ""
    echo "Usage:"
    echo "  ./quick_demo_trigger.sh create  - Create new workflow"
    echo "  ./quick_demo_trigger.sh list    - List all workflows"
    echo "  ./quick_demo_trigger.sh stats   - Show statistics"
fi