# Frontend Integration Debugging Guide

**From**: CC  
**For**: CA  
**Re**: Connecting to the API

## Quick Connection Test

1. **Check API Health**:
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status": "healthy", ...}`

2. **Test WebSocket**:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/ws');
   ws.onopen = () => console.log('Connected!');
   ws.onmessage = (e) => console.log('Event:', JSON.parse(e.data));
   ```

## Common Issues & Solutions

### CORS Errors
If you see CORS errors, the API is already configured for:
- http://localhost:3000
- http://localhost:3001

If using a different port, let me know and I'll add it.

### WebSocket Connection Failed
1. Make sure API is running: `python apps/api/main.py`
2. Check browser console for specific errors
3. Try the connection test above

### API Endpoints Not Working
All endpoints are prefixed with `/api/`:
- GET `/api/dag-runs`
- GET `/api/dag-runs/{id}`
- POST `/api/dag-runs`
- PATCH `/api/dag-runs/{id}/status`

### WebSocket Events
You should receive these events:
```javascript
// DAG run events
{
  event: "dag.run.created",
  data: { run_id, workflow_name, engine_type }
}

{
  event: "dag.step.status.updated", 
  data: { run_id, status, steps_completed, steps_total }
}

{
  event: "dag.run.completed",
  data: { run_id, status, duration_ms }
}

// Email processing events (if using email endpoint)
{
  event: "email.processing.started",
  data: { run_id, subject, sender, pdf_name }
}
```

## Testing the Integration

1. **Create a test DAG run**:
   ```bash
   curl -X POST http://localhost:8000/api/dag-runs \
     -H "Content-Type: application/json" \
     -d '{"workflow_path": "workflows/sample_ingestion_digest.yaml", "persist": false}'
   ```

2. **Watch WebSocket for updates** in your component

3. **Verify in UI** that status updates in real-time

## Need Help?

I'm monitoring this and ready to help debug! Current status:
- API: ✅ Running on port 8000
- WebSocket: ✅ Active
- CORS: ✅ Configured for localhost:3000/3001
- All endpoints: ✅ Tested and working

Post any errors you see and I'll help resolve them immediately!

---
CC