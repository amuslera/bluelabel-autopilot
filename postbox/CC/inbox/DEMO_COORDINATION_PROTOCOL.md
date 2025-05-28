# Demo Coordination Protocol 🎬

## Your Role (CC - Backend Controller)
You control the backend and trigger workflows on CA's cues.

## Coordination Signals

### CA Will Signal You Via:
- **File creation**: `/data/demo_signals/ready_for_recording.txt` 
- **File content**: The scenario number they want (1, 2, 3, or 4)

### Your Response:
1. **Monitor** the `/data/demo_signals/` folder
2. **When you see `ready_for_recording.txt`**:
   - Read the scenario number
   - Trigger the corresponding test scenario
   - Create `/data/demo_signals/scenario_triggered.txt` with status

### Scenarios to Trigger:
- **Scenario 1**: Success path (5-page PDF)
- **Scenario 2**: Large file (200-page PDF) 
- **Scenario 3**: Error recovery (corrupted file)
- **Scenario 4**: Your choice demo

### Demo Flow:
1. CA starts recording
2. CA creates `ready_for_recording.txt` with scenario number
3. You trigger the workflow immediately
4. You monitor and create status updates
5. Repeat for multiple scenarios if needed

Ready? Wait for CA's signal files!