# Bluelabel Autopilot API

FastAPI-based REST API with WebSocket support for DAG workflow management.

## Quick Start

```bash
cd apps/api
pip install -r requirements.txt
python main.py
```

API will be available at:
- REST API: http://localhost:8000
- WebSocket: ws://localhost:8000/ws
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing the API

```bash
# Run the local test script
python test_api_local.py

# Or use curl
curl http://localhost:8000/health
```

## API Endpoints

### Health & Monitoring
- `GET /health` - Health check
- `GET /metrics` - Performance metrics

### DAG Runs
- `GET /api/dag-runs` - List all DAG runs (with pagination)
- `GET /api/dag-runs/{id}` - Get specific DAG run details
- `POST /api/dag-runs` - Create new DAG run
- `PATCH /api/dag-runs/{id}/status` - Update run status (e.g., cancel)

### WebSocket Events
Connect to `ws://localhost:8000/ws` to receive real-time updates:
- `dag.run.created` - New DAG run created
- `dag.run.status.updated` - Status changed
- `dag.step.status.updated` - Step progress
- `dag.run.completed` - Run finished

## Request Examples

### Create DAG Run
```bash
curl -X POST http://localhost:8000/api/dag-runs \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_path": "workflows/sample_ingestion_digest.yaml",
    "engine_type": "sequential",
    "persist": true
  }'
```

### List DAG Runs with Pagination
```bash
curl "http://localhost:8000/api/dag-runs?limit=10&offset=0&status=running"
```

### Get Metrics
```bash
curl http://localhost:8000/metrics
```

## WebSocket Example

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(`Event: ${data.event}`, data.data);
};

// Send ping to keep alive
setInterval(() => ws.send('ping'), 30000);
```

## Configuration

### Environment Variables
- `WORKFLOW_ENGINE_TYPE` - Engine to use (`sequential` or `stateful_dag`)
- `LOG_LEVEL` - Logging level (default: INFO)

### CORS
Currently configured for:
- http://localhost:3000
- http://localhost:3001

Update in `main.py` for production domains.

## Architecture

```
apps/api/
├── main.py           # FastAPI application
├── models.py         # Request/response models
├── middleware.py     # Logging, errors, metrics
├── websocket_manager.py  # WebSocket handling
└── routes/           # Additional route modules
```

## Integration with UnifiedWorkflowEngine

The API uses the UnifiedWorkflowEngine to execute workflows:
1. Supports both sequential and stateful DAG engines
2. Integrates with AgentRegistry for dynamic agent discovery
3. Provides real-time updates via WebSocket

## Monitoring

The API includes built-in monitoring:
- Request/response logging
- Performance metrics per endpoint
- Error tracking
- WebSocket connection monitoring

Access metrics at `/metrics` endpoint.

## Error Handling

All errors return standardized JSON:
```json
{
  "error": "Error type",
  "message": "Detailed message",
  "path": "/api/endpoint",
  "timestamp": "2025-05-28T..."
}
```

## Development

### Running Tests
```bash
cd ../..
pytest tests/integration/test_api_workflow_integration.py -v
```

### Adding New Endpoints
1. Add route in `main.py` or create new file in `routes/`
2. Add request/response models in `models.py`
3. Update this README with examples
4. Add integration tests

## Production Considerations

1. **Database**: Currently uses in-memory storage. Add PostgreSQL for production.
2. **Authentication**: Add JWT or OAuth2 authentication
3. **Rate Limiting**: Add rate limiting middleware
4. **Caching**: Consider Redis for caching
5. **Load Balancing**: Use multiple workers with Gunicorn

---

CC: API ready for frontend integration!