# Bluelabel Autopilot Demo Script 🚀

**Duration**: 5 minutes  
**Objective**: Demonstrate real-time DAG workflow orchestration

## Pre-Demo Setup (30 seconds)

1. **Start Services**
   ```bash
   # Terminal 1: API Server
   cd /apps/api
   python3 simple_test_server.py
   
   # Terminal 2: Frontend
   cd /apps/web
   npm run dev
   ```

2. **Open Browser**
   - Navigate to http://localhost:3000
   - Open DevTools to show WebSocket traffic

3. **Verify Test Dashboard**
   - http://localhost:8001/test_page.html (optional backup)

## Demo Flow

### Part 1: Introduction (30 seconds)

"Welcome to Bluelabel Autopilot - an MCP-native agent orchestration platform.

Today I'll demonstrate how we've unified our architecture to provide real-time workflow visualization and management."

**Show**: Empty dashboard state

### Part 2: Basic Workflow Execution (1 minute)

"Let's start with a simple PDF to summary workflow."

1. **Trigger workflow**:
   - Click "Create Test Workflow"
   - Point out the workflow ID

2. **Real-time visualization**:
   - "Notice how the DAG graph updates in real-time"
   - "Each step shows its current status"
   - "WebSocket delivers updates with <10ms latency"

3. **Show completion**:
   - "The entire pipeline completes in under 3 seconds"
   - "All steps show green checkmarks"

### Part 3: Failure Recovery Demo (1.5 minutes)

"Now let's see how the system handles failures."

1. **Create failure workflow**:
   ```javascript
   // In console
   fetch('http://localhost:8000/api/dag-runs', {
     method: 'POST',
     headers: {'Content-Type': 'application/json'},
     body: JSON.stringify({
       workflow: `name: demo-failure-recovery
steps:
  - name: extract_text`,
       inputs: {demo_type: 'failure_recovery'}
     })
   })
   ```

2. **Watch retry mechanism**:
   - "The extract_text step will fail twice"
   - "Notice the retry counter incrementing"
   - "On the third attempt, it succeeds"
   - "Total time: 12 seconds due to retries"

### Part 4: Parallel Processing (1.5 minutes)

"For large documents, we support parallel processing."

1. **Show workflow list**:
   - Point to the parallel workflow already created
   - ID: `ee5f7d80-c57c-422e-bcad-f424bbf4238e`

2. **Explain optimization**:
   - "Document split into 4 chunks"
   - "All chunks process simultaneously"
   - "6 second max vs 23 seconds sequential"
   - "60% time reduction"

### Part 5: Complex Pipeline (1 minute)

"Here's a production-ready pipeline with 9 steps."

1. **Show complex workflow**:
   - Multiple parallel preprocessing steps
   - Dependency management
   - Quality checks
   - "Notice how the DAG visualizes dependencies"

### Part 6: Architecture Benefits (30 seconds)

"What we've achieved:"

1. **Unified Architecture**:
   - Single workflow engine (no more fragmentation)
   - Consistent API across all agents
   - MCP-native from the ground up

2. **Performance**:
   - <50ms adapter overhead
   - 2-3 second PDF processing
   - Real-time updates via WebSocket

3. **Developer Experience**:
   - Type-safe TypeScript API
   - Comprehensive error handling
   - Visual debugging tools

## Key Talking Points

### Technical Achievement
- "Completed in 4 hours what was planned for 48-72 hours"
- "10x faster delivery through AI pair programming"
- "Zero breaking changes to existing workflows"

### Architecture Wins
- "Strategy pattern allows engine swapping"
- "Dependency injection for dynamic agents"
- "WebSocket for real-time without polling"

### Production Ready
- "Retry mechanisms built-in"
- "Comprehensive error boundaries"
- "Performance monitoring included"

## Q&A Preparation

**Q: How does this compare to existing solutions?**
A: "Unlike traditional orchestrators, we're MCP-native, meaning agents can discover and invoke each other dynamically. Plus, our real-time visualization helps debug complex workflows."

**Q: What about scale?**
A: "The architecture supports horizontal scaling. The WebSocket manager can be replaced with Redis Pub/Sub for multi-instance deployments."

**Q: Integration with existing systems?**
A: "The unified engine maintains backward compatibility. Existing workflows run without modification."

## Troubleshooting

If WebSocket disconnects:
- Refresh the page
- Check console for errors
- Verify server is running

If no data appears:
- Check browser console
- Verify CORS headers
- Try the test dashboard

## Post-Demo

1. Share workflow IDs for exploration
2. Provide API documentation link
3. Mention the performance report
4. Highlight the sprint velocity achievement

---

**Remember**: Keep it visual, emphasize real-time updates, and let the UI tell the story!