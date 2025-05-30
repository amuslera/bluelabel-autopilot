# WebSocket Events Documentation - AIOS v2

## Overview

This document describes all WebSocket events used by AIOS v2 for real-time updates across file processing, agent management, knowledge repository, analytics, and DAG operations.

## Connection

Connect to the WebSocket endpoint:
```
ws://localhost:8000/ws
```

## Authentication

Send authentication message immediately after connection:
```json
{
  "event": "auth",
  "data": {
    "token": "your-auth-token"
  }
}
```

## Client-to-Server Messages

### Subscribe to Updates
Subscribe to specific types of updates:
```json
{
  "event": "subscribe",
  "data": {
    "types": ["processing_jobs", "agents", "knowledge", "insights"],
    "filters": {
      "run_id": "specific-run-id",  // Optional: subscribe to specific job
      "agent_ids": ["agent1", "agent2"]  // Optional: specific agents
    }
  }
}
```

### Unsubscribe
```json
{
  "event": "unsubscribe",
  "data": {
    "types": ["processing_jobs"]
  }
}
```

### Subscribe to DAG Run (Legacy)
For backward compatibility with DAG components:
```json
{
  "event": "subscribe_dag_run",
  "data": {
    "run_id": "manual__2023-01-01T00:00:00+00:00"
  }
}
```

## Server-to-Client Events

### Connection Events

#### Connected
Sent when WebSocket connection is established:
```json
{
  "event": "connected",
  "data": {
    "client_id": "client-123",
    "server_time": "2023-01-01T00:00:00Z"
  }
}
```

#### Ping/Heartbeat
Server sends heartbeat every 30 seconds:
```json
{
  "event": "ping",
  "data": {
    "timestamp": "2023-01-01T00:00:00Z"
  }
}
```

### File Processing Events

#### Processing Job Status Update
Sent when a processing job status changes:
```json
{
  "event": "processing_job_status",
  "data": {
    "job_id": "job-12345",
    "run_id": "run-67890",
    "type": "pdf",
    "status": "processing",
    "progress": 45,
    "filename": "document.pdf",
    "started_at": "2023-01-01T00:00:00Z",
    "estimated_completion": "2023-01-01T00:05:00Z",
    "current_step": "text_extraction",
    "timestamp": "2023-01-01T00:02:30Z"
  }
}
```

#### Processing Job Completed
Sent when a processing job completes:
```json
{
  "event": "processing_job_completed",
  "data": {
    "job_id": "job-12345",
    "run_id": "run-67890",
    "type": "pdf",
    "status": "completed",
    "progress": 100,
    "completed_at": "2023-01-01T00:05:00Z",
    "result": {
      "extracted_text": "Document content...",
      "summary": "Brief summary...",
      "entities": ["entity1", "entity2"],
      "insights": ["insight1", "insight2"]
    },
    "timestamp": "2023-01-01T00:05:00Z"
  }
}
```

#### Processing Job Failed
Sent when a processing job fails:
```json
{
  "event": "processing_job_failed",
  "data": {
    "job_id": "job-12345",
    "run_id": "run-67890",
    "type": "pdf",
    "status": "failed",
    "error": "Failed to extract text: Invalid PDF format",
    "failed_at": "2023-01-01T00:03:00Z",
    "retry_count": 2,
    "can_retry": true,
    "timestamp": "2023-01-01T00:03:00Z"
  }
}
```

### Agent Management Events

#### Agent Status Update
Sent when an agent's status changes:
```json
{
  "event": "agent_status_update",
  "data": {
    "agent_id": "content_mind_01",
    "name": "Content Mind",
    "type": "analysis",
    "status": "working",
    "current_task": "Analyzing PDF document for key insights",
    "progress": 75,
    "performance": {
      "tasks_completed": 145,
      "average_processing_time": 2.3,
      "success_rate": 98.5
    },
    "timestamp": "2023-01-01T00:00:00Z"
  }
}
```

#### Agent Task Completed
Sent when an agent completes a task:
```json
{
  "event": "agent_task_completed",
  "data": {
    "agent_id": "digest_agent_02",
    "task_id": "task-789",
    "job_id": "job-12345",
    "task_type": "text_summarization",
    "duration": 45.2,
    "result": {
      "summary": "Generated summary...",
      "confidence": 0.94
    },
    "timestamp": "2023-01-01T00:02:45Z"
  }
}
```

#### Agent Error
Sent when an agent encounters an error:
```json
{
  "event": "agent_error",
  "data": {
    "agent_id": "summary_agent_03",
    "error": "Connection timeout to language model",
    "severity": "warning",
    "can_retry": true,
    "affected_jobs": ["job-12345", "job-12346"],
    "timestamp": "2023-01-01T00:01:30Z"
  }
}
```

### Knowledge Repository Events

#### Knowledge Item Created
Sent when a new knowledge item is created:
```json
{
  "event": "knowledge_item_created",
  "data": {
    "item_id": "kb-item-456",
    "title": "Q4 Financial Analysis Report",
    "type": "analysis",
    "source_job": "job-12345",
    "tags": ["finance", "quarterly", "analysis"],
    "created_at": "2023-01-01T00:05:00Z",
    "timestamp": "2023-01-01T00:05:00Z"
  }
}
```

#### Knowledge Item Updated
Sent when a knowledge item is updated:
```json
{
  "event": "knowledge_item_updated",
  "data": {
    "item_id": "kb-item-456",
    "updated_fields": ["content", "tags"],
    "updated_at": "2023-01-01T00:06:00Z",
    "timestamp": "2023-01-01T00:06:00Z"
  }
}
```

### Analytics & Insights Events

#### New Insight Generated
Sent when AI generates a new insight:
```json
{
  "event": "insight_generated",
  "data": {
    "insight_id": "insight-789",
    "title": "Processing Volume Increase Detected",
    "description": "Document processing volume has increased by 45% this week",
    "type": "trend",
    "confidence": 0.92,
    "metadata": {
      "metric": "volume",
      "change": "+45%",
      "period": "week",
      "affected_categories": ["pdf", "audio"]
    },
    "created_at": "2023-01-01T00:07:00Z",
    "timestamp": "2023-01-01T00:07:00Z"
  }
}
```

#### Dashboard Metrics Update
Sent periodically with updated dashboard metrics:
```json
{
  "event": "dashboard_metrics_update",
  "data": {
    "total_processed": 1247,
    "processing_time": 2.8,
    "success_rate": 97.3,
    "active_agents": 3,
    "knowledge_items": 892,
    "changes": {
      "total_processed": "+5",
      "success_rate": "+0.2"
    },
    "timestamp": "2023-01-01T00:08:00Z"
  }
}
```

### DAG Operation Events (Legacy Compatibility)

#### DAG Run Status Update
Sent when a DAG run's status changes:
```json
{
  "event": "dag_run_status",
  "data": {
    "dag_id": "example_dag",
    "run_id": "manual__2023-01-01T00:00:00+00:00",
    "status": "running",
    "started_at": "2023-01-01T00:00:00Z",
    "timestamp": "2023-01-01T00:00:00Z"
  }
}
```

#### Step Status Update
Sent when a DAG step's status changes:
```json
{
  "event": "step_status",
  "data": {
    "dag_id": "example_dag",
    "run_id": "manual__2023-01-01T00:00:00+00:00",
    "step_id": "extract_data",
    "status": "success",
    "start_time": "2023-01-01T00:00:00Z",
    "end_time": "2023-01-01T00:05:00Z",
    "duration": 300000,
    "retry_count": 0,
    "error": null,
    "timestamp": "2023-01-01T00:05:00Z"
  }
}
```

#### DAG Run Progress
Sent with overall DAG run progress:
```json
{
  "event": "dag_run_progress",
  "data": {
    "dag_id": "example_dag",
    "run_id": "manual__2023-01-01T00:00:00+00:00",
    "total_steps": 4,
    "completed_steps": 2,
    "running_steps": 1,
    "failed_steps": 0,
    "pending_steps": 1,
    "completion_percentage": 50.0,
    "timestamp": "2023-01-01T00:05:00Z"
  }
}
```

### Error Events

#### General Error
Sent when a general error occurs:
```json
{
  "event": "error",
  "data": {
    "code": "processing_error",
    "message": "Failed to process document",
    "details": {
      "job_id": "job-12345",
      "error_type": "validation_error",
      "retry_available": true
    },
    "timestamp": "2023-01-01T00:02:00Z"
  }
}
```

#### Connection Error
Sent when there's a connection-related error:
```json
{
  "event": "connection_error",
  "data": {
    "code": "websocket_error",
    "message": "Connection unstable, reconnecting...",
    "timestamp": "2023-01-01T00:01:00Z"
  }
}
```

## Event Flow Examples

### File Upload and Processing Flow
1. Client uploads file via REST API
2. Server responds with `job_id` and `run_id`
3. Client subscribes to WebSocket updates for that `run_id`
4. Server sends periodic `processing_job_status` events
5. Agents send `agent_status_update` events as they work
6. Server sends `processing_job_completed` when done
7. Server sends `knowledge_item_created` if new knowledge is generated
8. Server sends `insight_generated` if patterns are detected

### Real-time Dashboard Updates
1. Client subscribes to `["processing_jobs", "agents", "insights"]`
2. Server sends `dashboard_metrics_update` every 30 seconds
3. Server sends `agent_status_update` when agents change status
4. Server sends `insight_generated` when new insights are created
5. Server sends `processing_job_status` for active jobs

## Client Implementation Notes

### WebSocket Connection Management
```typescript
class AIOSWebSocketClient {
  private ws: WebSocket;
  private subscriptions: Set<string> = new Set();
  
  connect() {
    this.ws = new WebSocket('ws://localhost:8000/ws');
    
    this.ws.onopen = () => {
      this.authenticate();
      this.resubscribe();
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleEvent(data);
    };
    
    this.ws.onclose = () => {
      setTimeout(() => this.reconnect(), 1000);
    };
  }
  
  subscribe(types: string[], filters?: any) {
    this.ws.send(JSON.stringify({
      event: 'subscribe',
      data: { types, filters }
    }));
    types.forEach(type => this.subscriptions.add(type));
  }
  
  private handleEvent(data: any) {
    switch (data.event) {
      case 'processing_job_status':
        this.updateJobStatus(data.data);
        break;
      case 'agent_status_update':
        this.updateAgentStatus(data.data);
        break;
      case 'insight_generated':
        this.addInsight(data.data);
        break;
      // ... handle other events
    }
  }
}
```

### Reconnection Strategy
1. Exponential backoff starting at 1 second
2. Maximum retry interval: 30 seconds
3. After successful reconnection:
   - Resend authentication
   - Resubscribe to previous subscriptions
   - Request missed updates since last connection

### Performance Considerations
1. **Event Filtering**: Subscribe only to relevant events
2. **Batching**: UI updates can be batched to avoid excessive re-renders
3. **Debouncing**: Debounce rapid status updates
4. **Connection Health**: Monitor ping/pong for connection health
5. **Offline Support**: Cache events when connection is lost

## Error Handling

### Connection Failures
- Implement exponential backoff for reconnection
- Show connection status in UI
- Queue important actions when offline

### Event Processing Errors
- Log malformed events
- Continue processing other events
- Request resynchronization if needed

### Authentication Errors
- Redirect to login when authentication fails
- Refresh tokens automatically when possible 