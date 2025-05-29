# Agent Performance Metrics System

## Overview

The Agent Performance Metrics System tracks and reports on agent task execution performance, providing insights into:
- Task completion times
- Success/failure rates
- Agent efficiency scores
- Historical performance trends

## Architecture

```
.metrics/
├── agents/         # Per-agent metric files
├── tasks/          # Individual task tracking files
└── reports/        # Generated performance reports
```

## Usage

### Command Line Interface

```bash
# Collect metrics from all agents
python tools/agent_metrics.py collect

# Collect metrics for a specific agent
python tools/agent_metrics.py collect --agent CA

# Generate performance report
python tools/agent_metrics.py report

# Track task start
python tools/agent_metrics.py track-start --agent CB --task TASK-165E

# Track task completion
python tools/agent_metrics.py track-complete --agent CB --task TASK-165E --status completed
```

### Python API

```python
from tools.agent_metrics import AgentMetrics, TaskMetric

# Initialize metrics system
metrics = AgentMetrics()

# Collect metrics from an agent's outbox
agent_metrics = metrics.collect_metrics_from_outbox("CB")
metrics.save_agent_metrics("CB", agent_metrics)

# Track task execution
metrics.track_task_start("CB", "TASK-165E")
# ... task execution ...
metrics.track_task_complete("CB", "TASK-165E", "completed")

# Generate performance report
report = metrics.generate_performance_report()
metrics.print_summary_report(report)
```

## Metrics Collected

### Task Metrics
- **task_id**: Unique task identifier
- **agent_id**: Agent who executed the task
- **status**: Task completion status (completed, failed, blocked)
- **created_at**: Task creation timestamp
- **started_at**: Task start timestamp
- **completed_at**: Task completion timestamp
- **estimated_hours**: Original time estimate
- **actual_hours**: Actual execution time
- **deliverables_completed**: Number of deliverables completed
- **deliverables_total**: Total number of deliverables

### Calculated Metrics
- **execution_time**: Time from start to completion in hours
- **efficiency_score**: 0-100 score based on:
  - Time efficiency (50%): How close actual time was to estimate
  - Deliverable completion (50%): Percentage of deliverables completed

### Agent Summary Metrics
- **total_tasks**: Total number of tasks assigned
- **completed_tasks**: Successfully completed tasks
- **failed_tasks**: Failed or blocked tasks
- **success_rate**: Percentage of successful completions
- **avg_execution_time_hours**: Average task execution time
- **avg_efficiency_score**: Average efficiency across all tasks

## Performance Report Structure

```json
{
  "generated_at": "2025-05-29T12:00:00Z",
  "agents": {
    "CB": {
      "total_tasks": 10,
      "completed_tasks": 9,
      "failed_tasks": 1,
      "success_rate": 90.0,
      "avg_execution_time_hours": 2.5,
      "avg_efficiency_score": 85.5
    }
  },
  "overall": {
    "total_tasks": 50,
    "completed_tasks": 45,
    "failed_tasks": 5,
    "success_rate": 90.0,
    "avg_execution_time_hours": 3.2,
    "avg_efficiency_score": 82.3
  }
}
```

## Integration with Orchestration

### Automatic Tracking

The metrics system can be integrated with the agent autopilot system to automatically track task execution:

1. When a task is assigned, call `track_task_start()`
2. When a task is completed, call `track_task_complete()`
3. Metrics are automatically collected from outbox files

### Morning Kickoff Integration

```bash
# In morning_kickoff.sh
python tools/agent_metrics.py collect
python tools/agent_metrics.py report
```

### End of Day Integration

```bash
# In end_of_day.sh
python tools/agent_metrics.py collect
python tools/agent_metrics.py report > daily_performance_summary.txt
```

## Best Practices

1. **Regular Collection**: Run metrics collection at least daily
2. **Track All Tasks**: Use the tracking API for accurate timing
3. **Review Reports**: Check performance trends weekly
4. **Update Estimates**: Use historical data to improve time estimates

## Efficiency Score Calculation

The efficiency score is calculated as:

```python
time_score = min(estimated_hours / actual_hours, 2.0) * 50
deliverable_score = (deliverables_completed / deliverables_total) * 50
efficiency_score = min(time_score + deliverable_score, 100)
```

This rewards:
- Completing tasks close to or faster than estimates (up to 2x)
- Completing all deliverables
- Maximum score is 100

## Troubleshooting

### Missing Metrics
- Ensure outbox files follow the standard schema
- Check that history entries have required fields
- Run validation: `python orchestration/validate_outbox.py --all`

### Zero Efficiency Scores
- Historical tasks may lack time estimates
- Add `actual_hours` to task history entries
- Update deliverable counts in outbox files

### Performance Issues
- Metrics are cached in `.metrics/` directory
- Clear cache by removing old metric files
- Run collection with specific agents to isolate issues