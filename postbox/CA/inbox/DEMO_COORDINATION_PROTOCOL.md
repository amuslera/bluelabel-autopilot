# Demo Coordination Protocol 🎬

## Your Role (CA - UI Controller & Recorder)
You control the recording and UI demonstration.

## Coordination Signals

### Signal CC Via:
- **Create file**: `/data/demo_signals/ready_for_recording.txt`
- **File content**: Scenario number (1, 2, 3, or 4)

### CC Will Respond:
- **Monitor**: `/data/demo_signals/scenario_triggered.txt` for status

## Demo Steps:

### 1. Pre-Demo Setup
- Open DAG UI in clean browser window
- Start screen recording
- Clear any test data

### 2. Signal for Each Scenario
```bash
# For Scenario 1 (Success Path)
echo "1" > /data/demo_signals/ready_for_recording.txt

# Wait 2-3 seconds, then check:
cat /data/demo_signals/scenario_triggered.txt
```

### 3. Recording Flow
1. Show UI in "waiting" state
2. Create signal file with scenario number
3. Immediately focus on UI to capture real-time updates
4. Narrate what's happening
5. Show final results

### 4. Multiple Scenarios
- Repeat steps 2-3 for different scenarios
- Clean UI between scenarios if needed

**Ready to start?** Create the signal file when your recording is rolling!