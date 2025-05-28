# ARCH Q&A Protocol for Autonomous Execution

## How to Get Help from ARCH-Claude

### For Questions:
1. Post your question to `/postbox/ARCH/questions/[agent]-[timestamp].md`
2. ARCH will respond in `/postbox/[agent]/answers/[timestamp]-response.md`
3. Check for responses every 30 minutes

### For Blockers:
1. Post to `/postbox/ARCH/URGENT.md` 
2. ARCH will respond within 15 minutes

### For Code Reviews:
1. Create PR and add file `/postbox/ARCH/reviews/[pr-number].md`
2. ARCH will review and respond with approval or changes needed

## Pre-Answered Common Questions

### Q: Should I use the WorkflowEngine or StatefulDAGRunner as the base?
A: Use WorkflowEngine as the base (it's in production) and adapt StatefulDAGRunner's better features into it.

### Q: What's the API authentication approach?
A: Start with API keys in headers. We'll add OAuth later. Focus on getting data flowing first.

### Q: How should WebSocket events be structured?
A: Use this format:
```json
{
  "event": "dag.status.update",
  "data": {
    "dagRunId": "xxx",
    "status": "running|completed|failed",
    "step": "step-id",
    "timestamp": "ISO-8601"
  }
}
```

### Q: What's the file structure for new API endpoints?
A: Create `/apps/api/routes/dag/[endpoint].py` using FastAPI or similar pattern to existing code.

### Q: Should I worry about database migrations?
A: No. We're using file-based storage for now. Focus on the API contract.

### Q: What about CORS for the frontend?
A: Enable CORS for localhost:3000 initially. We'll tighten in production.

### Q: How do I test integration between CC and CA work?
A: Create integration tests in `/tests/integration/` that both can run.

## Architecture Decisions Already Made

1. **Unified Engine**: Wrap both engines, don't rewrite from scratch
2. **API First**: REST + WebSocket, no GraphQL for now
3. **File Storage**: Keep using current file-based approach
4. **No Breaking Changes**: All existing workflows must continue working
5. **TypeScript**: Frontend stays TypeScript, backend Python
6. **Testing**: Unit tests required, integration tests for connections

## If You're Stuck

1. Try the simplest approach first
2. Working code > perfect code
3. Ask for review early with partial implementation
4. Document assumptions in code comments

Remember: We have 48 hours. Move fast, integrate continuously!