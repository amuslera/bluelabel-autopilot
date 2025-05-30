# UI-Backend Mapping - AIOS v2

This document comprehensively maps all UI components to their corresponding API endpoints and WebSocket events based on actual component audit.

## Overview

This mapping covers all AIOS v2 UI components across four main areas:
1. **File Processing & Upload** - Document/audio/URL processing workflows
2. **Agent Management** - AI agent monitoring and status tracking  
3. **Knowledge Repository** - Search and browse processed knowledge
4. **Analytics & Dashboard** - Metrics, insights, and system monitoring
5. **DAG Operations** - Legacy DAG visualization and monitoring

## File Processing Components

### UploadZone Component (`/pages/index.tsx`)

**Purpose**: Main file upload interface with drag-and-drop support

#### API Endpoints
- **POST /api/workflows/upload-pdf**
  - Used for PDF file uploads with multipart/form-data
  - Parameters: `file`, `extract_text`, `generate_summary`
  - Returns: `{ run_id, status, message }`
  
- **POST /api/workflows/upload-audio**
  - Used for audio file uploads
  - Parameters: `file`, `transcribe`, `summarize`
  - Returns: `{ run_id, status, message }`
  
- **POST /api/workflows/from-url**
  - Used for URL content processing
  - Parameters: `url`, `full_content`, `generate_summary`
  - Returns: `{ run_id, status, message }`

#### WebSocket Events
- **processing_job_status** - Updates upload progress and status
- **processing_job_completed** - Notifies when processing finishes
- **processing_job_failed** - Handles processing errors

#### State Management
```typescript
interface UploadZoneState {
  uploadedFiles: ProcessingJob[];
  isUploading: boolean;
  currentProgress: { [jobId: string]: number };
}
```

### ProcessingJobsList Component (`/pages/index.tsx`)

**Purpose**: Displays list of active/completed processing jobs

#### API Endpoints
- **GET /api/workflows/dag-runs**
  - Fetches paginated list of processing jobs
  - Parameters: `limit`, `offset`, `status`, `type`
  - Used for initial load and pagination

- **GET /api/workflows/dag-runs/{runId}**
  - Fetches detailed job information
  - Used when clicking on individual jobs
  - Returns full job details with steps and results

#### WebSocket Events
- **processing_job_status** - Real-time status updates
- **processing_job_completed** - Job completion notifications
- **processing_job_failed** - Error notifications

#### Implementation Pattern
```typescript
// Initial fetch
useEffect(() => {
  const fetchJobs = async () => {
    const response = await aiosClient.listProcessingJobs();
    setJobs(response);
  };
  fetchJobs();
}, []);

// WebSocket updates
useEffect(() => {
  const ws = aiosClient.connectWebSocket((data) => {
    if (data.event === 'processing_job_status') {
      updateJobInList(data.data);
    }
  });
  return () => ws.close();
}, []);
```

## Agent Management Components

### AgentConsole Component (`/pages/index.tsx`)

**Purpose**: Displays AI agent status and performance metrics

#### API Endpoints
- **GET /api/agents**
  - Fetches list of all available agents
  - Returns agent status, performance metrics, current tasks
  - Called on component mount and every 5 seconds for updates

- **GET /api/agents/{agentId}**
  - Fetches detailed information about specific agent
  - Used for agent detail views or debugging

#### WebSocket Events
- **agent_status_update** - Real-time agent status changes
- **agent_task_completed** - Task completion notifications
- **agent_error** - Agent error notifications

#### State Management
```typescript
interface AgentConsoleState {
  agents: Agent[];
  loading: boolean;
  selectedAgent: Agent | null;
  error: string | null;
}
```

#### Performance Considerations
- Polling every 5 seconds for agent status
- WebSocket updates for real-time status changes
- Optimistic UI updates for better responsiveness

## Knowledge Repository Components

### KnowledgeBrowser Component (`/pages/index.tsx`)

**Purpose**: Search and browse processed knowledge items

#### API Endpoints
- **GET /api/knowledge/search**
  - Primary search endpoint for knowledge repository
  - Parameters: `q` (query), `type`, `tags`, `limit`, `offset`
  - Supports filtering by type and tags
  - Used for both search and browsing

- **GET /api/knowledge/{itemId}**
  - Fetches detailed knowledge item content
  - Used when user clicks on knowledge item
  - Returns full content and metadata

#### WebSocket Events
- **knowledge_item_created** - New knowledge item notifications
- **knowledge_item_updated** - Knowledge item update notifications

#### Search Implementation
```typescript
const searchKnowledge = async (query: string) => {
  setLoading(true);
  try {
    const results = await aiosClient.searchKnowledge(query, {
      type: selectedType === 'all' ? undefined : selectedType
    });
    setKnowledgeItems(results);
  } catch (error) {
    console.error('Search failed:', error);
  } finally {
    setLoading(false);
  }
};

// Debounced search
useEffect(() => {
  const timeoutId = setTimeout(() => {
    if (searchQuery) {
      searchKnowledge(searchQuery);
    }
  }, 300);
  return () => clearTimeout(timeoutId);
}, [searchQuery, selectedType]);
```

## Analytics & Dashboard Components

### AnalyticsDashboard Component (`/pages/index.tsx`)

**Purpose**: Display system metrics, insights, and recent activity

#### API Endpoints
- **GET /api/analytics/dashboard**
  - Fetches key dashboard metrics
  - Returns: `total_processed`, `processing_time`, `success_rate`, `active_agents`, `knowledge_items`, `recent_activity`
  - Called on component mount

- **GET /api/analytics/insights**
  - Fetches AI-generated insights and recommendations
  - Parameters: `type`, `limit`
  - Returns array of insights with confidence scores

#### WebSocket Events
- **dashboard_metrics_update** - Real-time metrics updates
- **insight_generated** - New insight notifications

#### Metrics Display
```typescript
interface DashboardMetrics {
  totalProcessed: number;
  processingTime: number;
  successRate: number;
  activeAgents: number;
  knowledgeItems: number;
  recentActivity: RecentActivity[];
}
```

## DAG Operations (Legacy Support)

### DAGGraph Component (`/components/DAGGraph.tsx`)

**Purpose**: Visualizes DAG run execution with real-time updates

#### API Endpoints
- **GET /api/v1/dags/{dagId}/runs/{runId}** (Legacy)
  - Fetches complete DAG run data with steps
  - Used for initial graph rendering
  - Called when component mounts or runId changes

- **GET /api/v1/dags/{dagId}/runs/{runId}/steps** (Legacy)
  - Fetches detailed step information
  - Used for step-level details and debugging

#### WebSocket Events
- **dag_run_status** - Overall DAG run status updates
- **step_status** - Individual step status changes  
- **dag_run_progress** - Progress metrics updates

#### Real-time Updates
```typescript
// WebSocket integration
const { 
  status: currentStatus,
  steps: updatedSteps,
  progress: currentProgress,
  error: wsError,
  isConnected: wsConnected
} = useDAGRunUpdates('', runId);

// Update graph nodes when steps change
useEffect(() => {
  if (updatedSteps && updatedSteps.length > 0 && nodes.length > 0) {
    const stepsById = updatedSteps.reduce((acc, step) => {
      acc[step.id] = step;
      return acc;
    }, {} as Record<string, any>);
    
    const updatedNodes = nodes.map(node => {
      const step = stepsById[node.id];
      if (step) {
        return {
          ...node,
          data: { ...node.data, ...step, lastUpdate: Date.now() }
        };
      }
      return node;
    });
    setNodes(updatedNodes);
  }
}, [updatedSteps, nodes, setNodes]);
```

### DAGRunPage (`/pages/dag/[runId].tsx`)

**Purpose**: Full-page DAG run visualization

#### API Endpoints
- Uses same endpoints as DAGGraph component
- Implements error boundaries and retry logic

#### Error Handling
```typescript
<ErrorBoundary
  key={graphKey}
  onReset={handleGraphReset}
  fallback={<RetryableError onRetry={handleGraphReset} />}
>
  <DAGGraph runId={runId as string} />
</ErrorBoundary>
```

## Missing API Methods

Based on component audit, these methods are referenced but missing from current client:

### In `hooks.ts` but missing from `client.ts`:
1. **`apiClient.getDAGRun(dagId, runId)`** - Used by `useDAGRun` hook
2. **`apiClient.listDAGRuns(dagId, limit)`** - Used by `useDAGRuns` hook  
3. **`apiClient.getDAGRunSteps(dagId, runId)`** - Used by `useDAGRunSteps` hook
4. **`apiClient.subscribeToDAGRun(runId)`** - Used by WebSocket integration
5. **`apiClient.runWorkflow(workflowPath, inputs)`** - Used by `useRunWorkflow` hook

### Required Implementation:
```typescript
// Add to AIOSAPIClient class
async getDAGRun(dagId: string, runId: string): Promise<DAGRun> {
  const response = await this.client.get(`/api/workflows/dag-runs/${runId}`);
  return response.data;
}

async listDAGRuns(dagId: string, limit: number = 20): Promise<DAGRun[]> {
  const response = await this.client.get(`/api/workflows/dag-runs?limit=${limit}`);
  return response.data.items;
}

async getDAGRunSteps(dagId: string, runId: string): Promise<DAGStep[]> {
  const response = await this.client.get(`/api/workflows/dag-runs/${runId}`);
  return response.data.steps || [];
}

subscribeToDAGRun(runId: string): void {
  if (this.wsClient) {
    this.wsClient.send(JSON.stringify({
      event: 'subscribe_dag_run',
      data: { run_id: runId }
    }));
  }
}

async runWorkflow(workflowPath: string, inputs: Record<string, any>): Promise<{run_id: string; status: string}> {
  const response = await this.client.post('/api/workflows/run', {
    workflow_path: workflowPath,
    inputs
  });
  return response.data;
}
```

## Cross-Component Integration

### File Upload → Agent Console → Knowledge Browser Flow
1. User uploads file via **UploadZone**
2. **AgentConsole** shows agents processing the file
3. **KnowledgeBrowser** displays new knowledge items created
4. **AnalyticsDashboard** updates metrics and generates insights

### WebSocket Event Coordination
All components should subscribe to relevant events:
```typescript
// Central WebSocket manager
class AIOSEventManager {
  subscribe(component: string, events: string[]) {
    // Subscribe component to specific events
  }
  
  broadcast(event: any) {
    // Distribute events to subscribed components
  }
}
```

## Performance Optimization

### Pagination Strategy
- **Processing Jobs**: 20 items per page, infinite scroll
- **Knowledge Items**: 20 items per page, search-based pagination
- **Insights**: 10 items per page, type-based filtering

### Caching Strategy
- **Agent Status**: Cache for 30 seconds, update via WebSocket
- **Dashboard Metrics**: Cache for 60 seconds, background refresh
- **Knowledge Search**: Cache search results for 5 minutes

### WebSocket Optimization
- **Selective Subscription**: Only subscribe to events needed by active components
- **Event Batching**: Batch rapid updates to avoid UI thrashing
- **Connection Pooling**: Single WebSocket connection shared across components

## Error Handling Patterns

### API Error Handling
```typescript
try {
  const data = await apiCall();
  return data;
} catch (error) {
  if (error instanceof APIError) {
    showUserFriendlyError(error.message);
  } else {
    logError(error);
    showGenericError();
  }
}
```

### WebSocket Error Recovery
```typescript
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  // Implement exponential backoff reconnection
  setTimeout(() => reconnect(), Math.min(1000 * Math.pow(2, retryCount), 30000));
};
```

### Component Error Boundaries
All major components wrapped in ErrorBoundary with retry functionality.

## Testing Strategy

### API Integration Tests
- Mock all API endpoints with realistic data
- Test error scenarios and edge cases
- Validate WebSocket event handling

### Component Integration Tests
- Test component behavior with real API responses
- Verify WebSocket event processing
- Test error states and recovery

### End-to-End Tests
- Full file upload and processing workflow
- Agent status monitoring during processing
- Knowledge item creation and search
- Dashboard metrics updates 