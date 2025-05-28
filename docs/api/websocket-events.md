# WebSocket Events Documentation

## Connection

Connect to the WebSocket endpoint:
```
ws://localhost:3000/api/v1/ws
```

## Authentication

Send authentication message immediately after connection:
```json
{
  "type": "auth",
  "token": "your-auth-token"
}
```

## Event Types

### 1. DAG Run Status Update
Sent when a DAG run's status changes.

```json
{
  "type": "dag_run_status",
  "data": {
    "dagId": "example_dag",
    "runId": "manual__2023-01-01T00:00:00+00:00",
    "status": "running",
    "timestamp": "2023-01-01T00:00:00Z"
  }
}
```

### 2. Step Status Update
Sent when a step's status changes within a DAG run.

```json
{
  "type": "step_status",
  "data": {
    "dagId": "example_dag",
    "runId": "manual__2023-01-01T00:00:00+00:00",
    "stepId": "extract_data",
    "status": "success",
    "startTime": "2023-01-01T00:00:00Z",
    "endTime": "2023-01-01T00:05:00Z",
    "duration": 300000,
    "retryCount": 0,
    "error": null,
    "timestamp": "2023-01-01T00:05:00Z"
  }
}
```

### 3. DAG Run Progress
Sent periodically with overall progress of a DAG run.

```json
{
  "type": "dag_run_progress",
  "data": {
    "dagId": "example_dag",
    "runId": "manual__2023-01-01T00:00:00+00:00",
    "totalSteps": 4,
    "completedSteps": 2,
    "runningSteps": 1,
    "failedSteps": 0,
    "pendingSteps": 1,
    "completionPercentage": 50.0,
    "timestamp": "2023-01-01T00:05:00Z"
  }
}
```

### 4. Error Event
Sent when an error occurs in the DAG execution.

```json
{
  "type": "error",
  "data": {
    "dagId": "example_dag",
    "runId": "manual__2023-01-01T00:00:00+00:00",
    "stepId": "transform_data",
    "error": "Failed to process data: Invalid format",
    "timestamp": "2023-01-01T00:10:00Z"
  }
}
```

## Subscription

To receive updates for specific DAGs, send a subscription message:

```json
{
  "type": "subscribe",
  "dagIds": ["example_dag", "another_dag"]
}
```

To unsubscribe:

```json
{
  "type": "unsubscribe",
  "dagIds": ["example_dag"]
}
```

## Heartbeat

Server sends heartbeat every 30 seconds:

```json
{
  "type": "heartbeat",
  "timestamp": "2023-01-01T00:00:00Z"
}
```

## Error Handling

If an error occurs in the WebSocket connection:

```json
{
  "type": "error",
  "code": "connection_error",
  "message": "Failed to connect to WebSocket server",
  "timestamp": "2023-01-01T00:00:00Z"
}
```

## Reconnection Strategy

1. Client should attempt to reconnect with exponential backoff
2. Maximum retry interval: 30 seconds
3. After successful reconnection:
   - Resend authentication
   - Resubscribe to previous DAGs
   - Request missed updates since last connection 