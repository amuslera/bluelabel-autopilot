# TASK-163N: Implement Real API Layer for Frontend

**Priority**: CRITICAL - Frontend is ready but has no real backend API
**Estimated Time**: 2-3 hours
**Dependencies**: None - CC will handle backend integration separately

## Context
The DAG visualization UI is working beautifully with mock data. Now we need the real API layer to connect it to actual workflows. The frontend expects these endpoints but they don't exist yet.

## Your Tasks

### 1. Create FastAPI Backend (`/apps/api/api.py`)
```python
# Key endpoints needed:
POST /api/workflows/run          # Start a new workflow
GET  /api/dag-runs              # List all DAG runs  
GET  /api/dag-runs/{id}         # Get specific run details
WS   /ws/dag-updates            # WebSocket for real-time updates
```

### 2. Connect to Existing DAGRunner
- Import from `services.workflow.dag_runner`
- Use `DAGRunTracker` for state management
- Map DAGRun models to API responses

### 3. WebSocket Implementation
- Real-time status updates as workflows execute
- Send updates for: status changes, step completions, errors
- Use existing event patterns from test server

### 4. Add Workflow Triggers
```python
# Enable these input methods:
- POST /api/workflows/upload-pdf     # PDF file upload
- POST /api/workflows/from-url       # URL ingestion  
- POST /api/workflows/from-email     # Email webhook
```

### 5. Frontend API Client Updates
- Update `/apps/web/lib/api/client.ts` to use real endpoints
- Remove mock data dependencies
- Ensure proper error handling

## Success Criteria
- [ ] Can start a workflow from the UI
- [ ] See real-time updates as it executes
- [ ] List all past workflow runs
- [ ] Click into any run to see details

## Files to Create/Modify
- `/apps/api/api.py` - Main API server
- `/apps/api/routes/workflows.py` - Workflow endpoints
- `/apps/api/routes/websocket.py` - WebSocket handler
- `/apps/web/lib/api/client.ts` - Update to real endpoints

## Testing
```bash
# Start the API server
cd apps/api && python api.py

# Test workflow trigger
curl -X POST http://localhost:8000/api/workflows/run \
  -H "Content-Type: application/json" \
  -d '{"workflow": "sample_ingestion_digest", "input": {"url": "https://example.com"}}'
```

Start immediately - CC is handling the backend integration in parallel!