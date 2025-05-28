# TASK-163N: Complete Backend Integration & Unification

**Priority**: CRITICAL - Need unified backend for real workflow execution
**Estimated Time**: 2-3 hours  
**Dependencies**: None - CA will handle API layer separately

## Context
We have two workflow systems (WorkflowEngine and DAGRunner) that need unification. The test API works but uses mock data. We need real workflow execution connected to the UI.

## Your Tasks

### 1. Create UnifiedWorkflowAdapter (`/core/unified_workflow_adapter.py`)
```python
class UnifiedWorkflowAdapter:
    """Bridges WorkflowEngine and DAGRunner"""
    def __init__(self):
        self.workflow_engine = WorkflowEngine()
        self.dag_runner = DAGRunner()
    
    async def run_workflow(self, workflow_name: str, inputs: dict):
        # Convert YAML workflow to DAG format
        # Execute via DAGRunner for persistence
        # Return run_id for tracking
```

### 2. Implement Dependency Injection (`/core/agent_registry.py`)
```python
class AgentRegistry:
    """Dynamic agent registration and discovery"""
    _agents = {}
    
    @classmethod
    def register(cls, agent_type: str, agent_class):
        cls._agents[agent_type] = agent_class
    
    @classmethod 
    def get_agent(cls, agent_type: str, **kwargs):
        # Create agent instance with config
```

### 3. Real Workflow Execution
- Connect `IngestionAgent` and `DigestAgent` to UnifiedAdapter
- Ensure file outputs go to correct locations
- Map agent outputs to DAG step results

### 4. Integration Points
```python
# Key integrations needed:
- Email → Workflow trigger (using existing email router)
- PDF processing → Ingestion agent
- Ingestion → Digest pipeline  
- Results → Email delivery
```

### 5. State Persistence
- Ensure all runs are saved to `/data/workflows/`
- Update DAGRunTracker for proper status tracking
- Handle failures gracefully with retry logic

## Success Criteria
- [ ] Single workflow execution path (no dual systems)
- [ ] Real agents processing real data
- [ ] State persisted and resumable
- [ ] Email-triggered workflows working end-to-end

## Files to Create/Modify
- `/core/unified_workflow_adapter.py` - New adapter
- `/core/agent_registry.py` - DI system
- `/services/workflow/dag_runner.py` - Updates for real agents
- `/agents/base_agent.py` - Registry integration

## Testing
```python
# Test unified execution
adapter = UnifiedWorkflowAdapter()
run_id = await adapter.run_workflow(
    "sample_ingestion_digest",
    {"url": "https://example.com"}
)
# Should see real agent execution, not mocks
```

## Parallel Work
While you implement this, CA is building the API layer. Plan for these integration points:
- API will call `UnifiedWorkflowAdapter.run_workflow()`
- WebSocket updates from `DAGRunTracker` events
- Status queries via `get_run_status(run_id)`

Start immediately - we need this for a working MVP!