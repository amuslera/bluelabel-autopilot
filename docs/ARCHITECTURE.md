# Bluelabel Autopilot Architecture

## Overview

Bluelabel Autopilot is an MCP-native agent orchestration platform that processes emails with PDF attachments to generate executive summaries in real-time.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/Next.js)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  DAGGraph   │  │ DAGRunStatus │  │  Email Upload UI   │    │
│  │  Component  │  │   Component  │  │    Component       │    │
│  └──────┬──────┘  └───────┬──────┘  └─────────┬──────────┘    │
│         │                  │                    │               │
│         └──────────────────┴────────────────────┘               │
│                            │                                     │
│                     API Client Layer                             │
│                  (Axios + WebSocket)                             │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                              │ HTTP/WebSocket
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                      FastAPI Backend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │   REST API   │  │  WebSocket   │  │ Email Processor    │   │
│  │  Endpoints   │  │   Server     │  │    Endpoint        │   │
│  └──────┬───────┘  └───────┬──────┘  └─────────┬──────────┘   │
│         │                   │                    │              │
│         └───────────────────┴────────────────────┘              │
│                            │                                     │
│                   UnifiedWorkflowEngine                          │
│              (Adapter Pattern - Strategy)                        │
└─────────────────────────────┬───────────────────────────────────┘
                              │
         ┌────────────────────┴────────────────────┐
         │                                         │
┌────────┴───────────┐                ┌───────────┴──────────────┐
│  WorkflowEngine    │                │  StatefulDAGRunner       │
│   (Sequential)     │                │  (Resumable/Parallel)    │
└────────┬───────────┘                └───────────┬──────────────┘
         │                                         │
         └────────────────────┬────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────────┐
│                        Agent Registry                            │
│           (Dynamic Agent Discovery & Management)                 │
│  ┌──────────────┐                      ┌───────────────────┐   │
│  │ Ingestion    │                      │  Digest Agent     │   │
│  │   Agent      │                      │ (Summary Gen)     │   │
│  │ (PDF/URL)    │                      └───────────────────┘   │
│  └──────────────┘                                               │
└──────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. UnifiedWorkflowEngine
- **Location**: `/core/unified_workflow_engine.py`
- **Purpose**: Adapter that unifies two workflow execution engines
- **Pattern**: Strategy Pattern
- **Features**:
  - Environment-based engine selection
  - Performance monitoring (<100ms overhead)
  - Caching support
  - Backward compatibility

### 2. Agent Registry
- **Location**: `/core/agent_registry.py`
- **Purpose**: Dynamic agent registration and discovery
- **Pattern**: Singleton with Dependency Injection
- **Features**:
  - Thread-safe registration
  - Health monitoring
  - Capability-based discovery
  - Observer pattern for status updates

### 3. FastAPI Backend
- **Location**: `/apps/api/main.py`
- **Endpoints**:
  - `GET /api/dag-runs` - List workflow runs
  - `GET /api/dag-runs/{id}` - Get specific run
  - `POST /api/dag-runs` - Create new run
  - `PATCH /api/dag-runs/{id}/status` - Update status
  - `POST /api/process-email` - Process email with PDF
  - `WS /ws` - WebSocket for real-time updates

### 4. Workflow Processing

#### Email → PDF → Summary Flow
1. Email arrives with PDF attachment (base64 encoded)
2. PDF extracted and saved temporarily
3. Dynamic workflow created with ingestion + digest steps
4. UnifiedWorkflowEngine executes workflow
5. Real-time updates via WebSocket
6. Summary returned to client

### 5. Performance Optimizations
- **Caching**: 5-minute TTL for repeat workflows
- **Connection Pooling**: Resource management
- **Performance Monitoring**: Metrics tracking
- **Async Processing**: Non-blocking execution

## Data Flow

```
Email Request
    │
    ▼
FastAPI Endpoint ──────► WebSocket Event: "email.processing.started"
    │
    ▼
Create Temp Workflow
    │
    ▼
UnifiedWorkflowEngine
    │
    ├─► IngestionAgent ──► WebSocket Event: "email.processing.progress"
    │        │
    │        ▼
    │   Extract PDF Text
    │        │
    │        ▼
    └─► DigestAgent ────► WebSocket Event: "email.processing.progress"
             │
             ▼
        Generate Summary
             │
             ▼
    Return Response ────► WebSocket Event: "email.processing.completed"
```

## Key Design Decisions

### 1. Unified Architecture
- Merged two competing workflow engines
- Zero breaking changes
- Performance overhead <100ms

### 2. Real-time Updates
- WebSocket for live progress
- Event-driven architecture
- Client reconnection support

### 3. Scalability
- File-based storage (ready for DB)
- Stateless API design
- Horizontal scaling ready

### 4. Security
- CORS configured
- Input validation
- Error sanitization
- Future: JWT auth ready

## Performance Characteristics

- **PDF Processing**: 2-3 seconds for 10-page document
- **API Response**: <100ms for most endpoints
- **WebSocket Latency**: <5ms
- **Concurrent Support**: 10+ simultaneous workflows
- **Memory Usage**: ~50MB baseline + workflow data

## Deployment Considerations

### Development
```bash
# Start API
cd apps/api
python main.py

# Start Frontend
cd apps/web
npm run dev
```

### Production
- Use Gunicorn with multiple workers
- PostgreSQL for persistence
- Redis for caching
- Nginx for reverse proxy
- Docker containerization

## Future Enhancements

1. **Parallel Execution**: Leverage StatefulDAGRunner
2. **Agent Marketplace**: Plugin architecture
3. **Workflow Designer**: Visual workflow builder
4. **Advanced Monitoring**: Prometheus/Grafana
5. **Multi-tenant**: Organization support

## Testing

- **Unit Tests**: Component-level testing
- **Integration Tests**: Full pipeline validation
- **Performance Tests**: Load and stress testing
- **E2E Tests**: UI to backend flow

---

Architecture designed for extensibility, performance, and real-time collaboration.