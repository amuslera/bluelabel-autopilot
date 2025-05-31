# TASK-173A: ROI Report Automation - Frontend Implementation

**Phase:** 6.17 Sprint 2 - Production MVP
**Priority:** CRITICAL
**Agent:** CA (Frontend Specialist)
**Estimated Hours:** 3-4

## Context
We need to implement the ROI Report Automation workflow end-to-end to demonstrate our production MVP with a real use case. This task focuses on creating the frontend interface for audio upload and results display.

## Use Case Reference
Read the full requirements in: `/bluelabel-AIOS-V2/ROI_Report_Automation_Workflow.md`

## Working Directory
Work in: `/Users/arielmuslera/Development/Projects/bluelabel-autopilot/bluelabel-AIOS-V2`

## Branch Setup
```bash
cd /Users/arielmuslera/Development/Projects/bluelabel-autopilot
git checkout main
git pull origin main
git checkout -b dev/TASK-173A-roi-workflow-frontend
```

## Deliverables

### 1. Audio Upload Interface
- [ ] Create audio file upload component
- [ ] Support common audio formats (mp3, m4a, wav, webm)
- [ ] Add drag-and-drop functionality
- [ ] Show upload progress
- [ ] Display audio file info (duration, size, format)
- [ ] Add audio preview/playback controls

### 2. Workflow Status Display
- [ ] Show processing steps in real-time:
  - "Uploading audio file..."
  - "Transcribing audio (Spanish/English detection)..."
  - "Extracting meeting metadata..."
  - "Generating report..."
- [ ] Add progress indicators
- [ ] Show estimated time remaining
- [ ] Handle error states gracefully

### 3. Results Display
- [ ] Create table view for extracted data:
  - Name
  - Company
  - Position
  - Discussion
  - Contact Type (Prospective/Existing)
  - Priority Level (High/Medium/Low)
  - Action Items
- [ ] Add edit functionality for extracted data
- [ ] Style with consistent UI design

### 4. Export Functionality
- [ ] CSV download button
- [ ] Copy to clipboard option
- [ ] Print-friendly view
- [ ] Save as PDF option (bonus)

### 5. Integration Points
- [ ] Connect to backend upload endpoint
- [ ] WebSocket connection for real-time updates
- [ ] Error handling and retry logic
- [ ] Loading states and user feedback

## Technical Requirements
- Use existing UI components where possible
- Ensure mobile responsiveness
- Add proper TypeScript types
- Include accessibility features
- Maintain terminal-style UI theme

## Component Structure
```
components/
├── ROIWorkflow/
│   ├── AudioUploader.tsx
│   ├── WorkflowProgress.tsx
│   ├── ResultsTable.tsx
│   ├── ExportOptions.tsx
│   └── ROIWorkflowContainer.tsx
```

## API Integration
- POST `/api/workflows/roi-report` (file upload)
- WebSocket `/ws/workflow/{id}` (status updates)
- GET `/api/workflows/roi-report/{id}/results` (final results)

## Success Criteria
- User can upload audio files smoothly
- Real-time progress updates work
- Results display correctly in table format
- CSV export functions properly
- Works on mobile and desktop
- No console errors

## Testing Requirements
- Test with sample audio files
- Verify all file formats work
- Test error scenarios
- Validate mobile responsiveness
- Test accessibility features

## Completion
When complete:
1. Commit all changes to your feature branch
2. Push to remote: `git push -u origin dev/TASK-173A-roi-workflow-frontend`
3. Test with sample audio files
4. Update your outbox.json with status "ready_for_review"
5. Report: "CA Reports: TASK-173A complete - ROI workflow frontend implemented, audio upload and results display operational, ready for backend integration"

Create an amazing user experience for this voice-to-table workflow! 🎤→📊