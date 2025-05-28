# UI-Backend Mapping

This document maps UI components to their corresponding API endpoints and WebSocket events.

## DAGGraph Component

### API Endpoints
- **GET /api/v1/dags/{dagId}/runs/{runId}**
  - Used to fetch initial DAG run data
  - Provides complete DAG structure and step information
  - Called when component mounts or DAG ID changes

### WebSocket Events
- **dag_run_status**
  - Updates overall DAG run status
  - Triggers re-render of status indicators
- **step_status**
  - Updates individual step status
  - Triggers re-render of step nodes
- **dag_run_progress**
  - Updates progress metrics
  - Triggers re-render of progress indicators

### State Management
```typescript
interface DAGGraphState {
  dagRun: DAGRun;
  metrics: {
    totalSteps: number;
    completedSteps: number;
    runningSteps: number;
    failedSteps: number;
    completionPercentage: number;
  };
}
```

## DAGRunStatus Component

### API Endpoints
- **GET /api/v1/dags/{dagId}/runs/{runId}**
  - Fetches detailed run information
  - Called when component mounts
- **GET /api/v1/dags/{dagId}/runs/{runId}/steps**
  - Fetches detailed step information
  - Called when steps need to be refreshed

### WebSocket Events
- **step_status**
  - Updates individual step status
  - Triggers re-render of step rows
- **error**
  - Displays error messages in UI
  - Updates error state for affected steps

### State Management
```typescript
interface DAGRunStatusState {
  dagRun: DAGRun;
  steps: DAGStep[];
  error: string | null;
  loading: boolean;
}
```

## Common Patterns

### Error Handling
1. API errors are caught and displayed in UI
2. WebSocket connection errors trigger reconnection
3. Failed API calls are retried with exponential backoff

### Loading States
1. Initial data fetch shows loading spinner
2. WebSocket updates show optimistic UI updates
3. Error states are clearly indicated

### Real-time Updates
1. WebSocket connection is established on component mount
2. Subscription to specific DAG updates is sent
3. UI is updated in real-time as events arrive

## Implementation Notes

### DAGGraph Component
```typescript
// Initial data fetch
useEffect(() => {
  const fetchDAGRun = async () => {
    const response = await api.get(`/dags/${dagId}/runs/${runId}`);
    setDAGRun(response.data);
  };
  fetchDAGRun();
}, [dagId, runId]);

// WebSocket subscription
useEffect(() => {
  const ws = new WebSocket('ws://localhost:3000/api/v1/ws');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch (data.type) {
      case 'dag_run_status':
        updateDAGRunStatus(data.data);
        break;
      case 'step_status':
        updateStepStatus(data.data);
        break;
      case 'dag_run_progress':
        updateProgress(data.data);
        break;
    }
  };
  return () => ws.close();
}, [dagId, runId]);
```

### DAGRunStatus Component
```typescript
// Initial data fetch
useEffect(() => {
  const fetchData = async () => {
    const [runResponse, stepsResponse] = await Promise.all([
      api.get(`/dags/${dagId}/runs/${runId}`),
      api.get(`/dags/${dagId}/runs/${runId}/steps`)
    ]);
    setDAGRun(runResponse.data);
    setSteps(stepsResponse.data);
  };
  fetchData();
}, [dagId, runId]);

// WebSocket subscription
useEffect(() => {
  const ws = new WebSocket('ws://localhost:3000/api/v1/ws');
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'step_status') {
      updateStepStatus(data.data);
    }
  };
  return () => ws.close();
}, [dagId, runId]);
```

## Performance Considerations

1. **Pagination**
   - DAG runs list is paginated
   - Step list is paginated for large DAGs
   - Infinite scroll implementation for better UX

2. **Caching**
   - DAG run data is cached
   - Step data is cached with TTL
   - WebSocket updates invalidate cache

3. **Optimistic Updates**
   - UI updates immediately on WebSocket events
   - Fallback to API data if WebSocket fails
   - Background refresh to ensure consistency 