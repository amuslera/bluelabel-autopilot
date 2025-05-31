# TASK-173B: ROI Report Automation - Backend Implementation

**Phase:** 6.17 Sprint 2 - Production MVP
**Priority:** CRITICAL
**Agent:** CB (Backend Specialist)
**Estimated Hours:** 4-5

## Context
Implement the complete backend for the ROI Report Automation workflow, including agent orchestration, AI integrations, and data processing. This demonstrates our production MVP with a real business use case.

## Use Case Reference
Read the full requirements in: `/bluelabel-AIOS-V2/ROI_Report_Automation_Workflow.md`

## Working Directory
Work in: `/Users/arielmuslera/Development/Projects/bluelabel-autopilot/bluelabel-AIOS-V2`

## Branch Setup
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-autopilot
git checkout main
git pull origin main
git checkout -b dev/TASK-173B-roi-workflow-backend
```

## Deliverables

### 1. Audio Processing Pipeline
- [ ] Create audio upload endpoint `/api/workflows/roi-report`
- [ ] Support multiple audio formats (mp3, m4a, wav, webm)
- [ ] Validate file size and format
- [ ] Store uploaded files securely
- [ ] Generate unique workflow IDs

### 2. Transcription Agent
- [ ] Integrate OpenAI Whisper API
- [ ] Auto-detect Spanish/English language
- [ ] Handle audio format conversion if needed
- [ ] Return transcription with confidence scores
- [ ] Add error handling for API failures

### 3. Data Extraction Agent
- [ ] Create LLM-based parsing agent
- [ ] Extract structured data from transcripts:
  - Name
  - Company
  - Position
  - Discussion
  - Contact Type (Prospective/Existing)
  - Priority Level (High/Medium/Low)
  - Action Items
- [ ] Support both Spanish and English templates
- [ ] Handle partial or missing data gracefully

### 4. Workflow Orchestration
- [ ] Create workflow state machine
- [ ] Coordinate between agents
- [ ] Track processing progress
- [ ] Send real-time updates via WebSocket
- [ ] Handle failures and retries

### 5. Results API
- [ ] Store extracted data in database
- [ ] Create results retrieval endpoint
- [ ] Generate CSV export functionality
- [ ] Add data validation and cleanup

## Implementation Details

### Database Schema
```sql
CREATE TABLE roi_workflows (
    id UUID PRIMARY KEY,
    status VARCHAR(50),
    audio_file_path VARCHAR(255),
    transcription TEXT,
    extracted_data JSONB,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### Workflow Steps
1. **Upload** → Store file, create workflow record
2. **Transcription** → Send to Whisper API
3. **Extraction** → Parse with LLM
4. **Storage** → Save results to database
5. **Notification** → Send completion via WebSocket

### API Endpoints
```python
POST   /api/workflows/roi-report          # Upload audio
GET    /api/workflows/roi-report/{id}     # Get status
GET    /api/workflows/roi-report/{id}/results # Get results
GET    /api/workflows/roi-report/{id}/csv # Download CSV
```

### LLM Prompt Template
```python
EXTRACTION_PROMPT = """
Extract the following information from this meeting transcript:
- Name: Person's name
- Company: Company name
- Position: Their role/title
- Discussion: Summary of what was discussed
- Contact Type: "Prospective" or "Existing"
- Priority: "High", "Medium", or "Low"
- Action Items: List of follow-up actions

Transcript: {transcript}

Return as JSON with exact field names.
"""
```

## Technical Requirements
- Use async/await for all API calls
- Implement proper error handling
- Add comprehensive logging
- Use background tasks for long operations
- Ensure data security and privacy
- Add rate limiting for API calls

## Testing Requirements
- Unit tests for each agent
- Integration tests for workflow
- Test with sample Spanish/English audio
- Error scenario testing
- Performance testing with large files

## Success Criteria
- Audio uploads process correctly
- Transcription works for both languages
- Data extraction is >85% accurate
- Workflow completes end-to-end
- Real-time updates function properly
- CSV export works correctly

## Sample Test Data
Create test audio files with:
1. English meeting memo
2. Spanish meeting memo
3. Mixed language memo
4. Low quality audio (edge case)

## Completion
When complete:
1. Commit all changes to your feature branch
2. Push to remote: `git push -u origin dev/TASK-173B-roi-workflow-backend`
3. Test with sample audio files
4. Create API documentation
5. Update your outbox.json with status "ready_for_review"
6. Report: "CB Reports: TASK-173B complete - ROI workflow backend operational, transcription and extraction agents working, ready for frontend integration"

Build a robust AI-powered workflow system! 🎤🤖📊