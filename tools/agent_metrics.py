#!/usr/bin/env python3
"""
Agent Performance Metrics System

Tracks and reports on agent task execution performance metrics including:
- Task completion times
- Success/failure rates
- Agent efficiency metrics
- Historical performance trends
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import statistics


@dataclass
class TaskMetric:
    """Individual task execution metric"""
    task_id: str
    agent_id: str
    status: str  # completed, failed, blocked
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]
    estimated_hours: float
    actual_hours: Optional[float]
    deliverables_completed: int
    deliverables_total: int
    
    @property
    def execution_time(self) -> Optional[float]:
        """Calculate execution time in hours"""
        if not self.started_at or not self.completed_at:
            return None
        start = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
        end = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00'))
        return (end - start).total_seconds() / 3600
    
    @property
    def efficiency_score(self) -> Optional[float]:
        """Calculate efficiency score (0-100)"""
        if not self.actual_hours:
            return None
        # Base score on time efficiency and deliverable completion
        time_score = min(self.estimated_hours / self.actual_hours, 2.0) * 50 if self.estimated_hours > 0 else 50
        deliverable_score = (self.deliverables_completed / self.deliverables_total) * 50 if self.deliverables_total > 0 else 50
        return min(time_score + deliverable_score, 100)


class AgentMetrics:
    """Manages agent performance metrics collection and reporting"""
    
    def __init__(self, base_path: str = "/Users/arielmuslera/Development/Projects/bluelabel-autopilot"):
        self.base_path = Path(base_path)
        self.metrics_dir = self.base_path / ".metrics"
        self.metrics_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.metrics_dir / "agents").mkdir(exist_ok=True)
        (self.metrics_dir / "tasks").mkdir(exist_ok=True)
        (self.metrics_dir / "reports").mkdir(exist_ok=True)
        
    def collect_metrics_from_outbox(self, agent_id: str) -> List[TaskMetric]:
        """Collect metrics from an agent's outbox file"""
        outbox_path = self.base_path / f"postbox/{agent_id}/outbox.json"
        
        if not outbox_path.exists():
            return []
            
        with open(outbox_path, 'r') as f:
            data = json.load(f)
            
        metrics = []
        
        # Process active tasks
        for task in data.get('tasks', []):
            metric = TaskMetric(
                task_id=task['task_id'],
                agent_id=agent_id,
                status=task['status'],
                created_at=task['created_at'],
                started_at=task.get('started_at'),
                completed_at=task.get('completed_at'),
                estimated_hours=task.get('estimated_hours', 0),
                actual_hours=task.get('actual_hours'),
                deliverables_completed=0,  # TODO: Parse from status
                deliverables_total=len(task.get('deliverables', []))
            )
            metrics.append(metric)
            
        # Process historical tasks
        for entry in data.get('history', []):
            # Extract metrics from history entry
            actual_hours = None
            if 'metrics' in entry and 'actual_hours' in entry['metrics']:
                actual_hours = entry['metrics']['actual_hours']
                
            metric = TaskMetric(
                task_id=entry['task_id'],
                agent_id=agent_id,
                status=entry['status'],
                created_at=entry.get('timestamp', ''),  # Approximate
                started_at=entry.get('timestamp', ''),  # Approximate
                completed_at=entry.get('timestamp', ''),
                estimated_hours=0,  # Not available in history
                actual_hours=actual_hours,
                deliverables_completed=len(entry.get('files', {}).get('created', [])) + 
                                     len(entry.get('files', {}).get('modified', [])),
                deliverables_total=0  # Not available in history
            )
            metrics.append(metric)
            
        return metrics
        
    def save_agent_metrics(self, agent_id: str, metrics: List[TaskMetric]):
        """Save metrics for a specific agent"""
        agent_file = self.metrics_dir / f"agents/{agent_id}_metrics.json"
        
        # Load existing metrics
        existing_metrics = []
        if agent_file.exists():
            with open(agent_file, 'r') as f:
                existing_data = json.load(f)
                existing_metrics = [TaskMetric(**m) for m in existing_data.get('metrics', [])]
                
        # Merge metrics (avoid duplicates)
        existing_ids = {m.task_id for m in existing_metrics}
        for metric in metrics:
            if metric.task_id not in existing_ids:
                existing_metrics.append(metric)
                
        # Calculate aggregate stats
        completed_tasks = [m for m in existing_metrics if m.status == 'completed']
        failed_tasks = [m for m in existing_metrics if m.status == 'failed']
        
        success_rate = len(completed_tasks) / (len(completed_tasks) + len(failed_tasks)) * 100 if (completed_tasks or failed_tasks) else 0
        
        execution_times = [m.execution_time for m in completed_tasks if m.execution_time]
        avg_execution_time = statistics.mean(execution_times) if execution_times else 0
        
        efficiency_scores = [m.efficiency_score for m in completed_tasks if m.efficiency_score]
        avg_efficiency = statistics.mean(efficiency_scores) if efficiency_scores else 0
        
        # Save updated metrics
        output_data = {
            "agent_id": agent_id,
            "last_updated": datetime.now().isoformat() + 'Z',
            "summary": {
                "total_tasks": len(existing_metrics),
                "completed_tasks": len(completed_tasks),
                "failed_tasks": len(failed_tasks),
                "success_rate": round(success_rate, 2),
                "avg_execution_time_hours": round(avg_execution_time, 2),
                "avg_efficiency_score": round(avg_efficiency, 2)
            },
            "metrics": [asdict(m) for m in existing_metrics]
        }
        
        with open(agent_file, 'w') as f:
            json.dump(output_data, f, indent=2)
            
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report across all agents"""
        report = {
            "generated_at": datetime.now().isoformat() + 'Z',
            "agents": {},
            "overall": {
                "total_tasks": 0,
                "completed_tasks": 0,
                "failed_tasks": 0,
                "success_rate": 0,
                "avg_execution_time_hours": 0,
                "avg_efficiency_score": 0
            }
        }
        
        # Collect metrics from all agents
        agent_dirs = [d for d in (self.base_path / "postbox").iterdir() if d.is_dir()]
        
        all_execution_times = []
        all_efficiency_scores = []
        
        for agent_dir in agent_dirs:
            agent_id = agent_dir.name
            metrics = self.collect_metrics_from_outbox(agent_id)
            
            if metrics:
                self.save_agent_metrics(agent_id, metrics)
                
                # Load the saved metrics with calculations
                agent_file = self.metrics_dir / f"agents/{agent_id}_metrics.json"
                if agent_file.exists():
                    with open(agent_file, 'r') as f:
                        agent_data = json.load(f)
                        report["agents"][agent_id] = agent_data["summary"]
                        
                        # Collect for overall stats
                        report["overall"]["total_tasks"] += agent_data["summary"]["total_tasks"]
                        report["overall"]["completed_tasks"] += agent_data["summary"]["completed_tasks"]
                        report["overall"]["failed_tasks"] += agent_data["summary"]["failed_tasks"]
                        
                        # Collect execution times and efficiency scores
                        for metric in agent_data["metrics"]:
                            if metric["status"] == "completed":
                                if metric.get("actual_hours"):
                                    all_execution_times.append(metric["actual_hours"])
                                # Recalculate efficiency for overall stats
                                tm = TaskMetric(**metric)
                                if tm.efficiency_score:
                                    all_efficiency_scores.append(tm.efficiency_score)
                                    
        # Calculate overall statistics
        total_completed_failed = report["overall"]["completed_tasks"] + report["overall"]["failed_tasks"]
        if total_completed_failed > 0:
            report["overall"]["success_rate"] = round(
                report["overall"]["completed_tasks"] / total_completed_failed * 100, 2
            )
            
        if all_execution_times:
            report["overall"]["avg_execution_time_hours"] = round(statistics.mean(all_execution_times), 2)
            
        if all_efficiency_scores:
            report["overall"]["avg_efficiency_score"] = round(statistics.mean(all_efficiency_scores), 2)
            
        # Save the report
        report_file = self.metrics_dir / f"reports/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        # Also save as latest report
        latest_file = self.metrics_dir / "reports/latest_performance_report.json"
        with open(latest_file, 'w') as f:
            json.dump(report, f, indent=2)
            
        return report
        
    def print_summary_report(self, report: Dict[str, Any]):
        """Print a human-readable summary of the performance report"""
        print("\n" + "="*60)
        print("AGENT PERFORMANCE METRICS REPORT")
        print(f"Generated: {report['generated_at']}")
        print("="*60)
        
        # Overall statistics
        print("\nOVERALL PERFORMANCE:")
        print(f"  Total Tasks: {report['overall']['total_tasks']}")
        print(f"  Completed: {report['overall']['completed_tasks']}")
        print(f"  Failed: {report['overall']['failed_tasks']}")
        print(f"  Success Rate: {report['overall']['success_rate']}%")
        print(f"  Avg Execution Time: {report['overall']['avg_execution_time_hours']} hours")
        print(f"  Avg Efficiency Score: {report['overall']['avg_efficiency_score']}/100")
        
        # Per-agent statistics
        print("\nPER-AGENT PERFORMANCE:")
        for agent_id, stats in report['agents'].items():
            print(f"\n  {agent_id}:")
            print(f"    Tasks: {stats['total_tasks']} (✓ {stats['completed_tasks']} / ✗ {stats['failed_tasks']})")
            print(f"    Success Rate: {stats['success_rate']}%")
            print(f"    Avg Time: {stats['avg_execution_time_hours']} hrs")
            print(f"    Efficiency: {stats['avg_efficiency_score']}/100")
            
        print("\n" + "="*60)
        
    def track_task_start(self, agent_id: str, task_id: str):
        """Mark a task as started and record the timestamp"""
        timestamp = datetime.now().isoformat() + 'Z'
        task_file = self.metrics_dir / f"tasks/{task_id}_tracking.json"
        
        tracking_data = {
            "task_id": task_id,
            "agent_id": agent_id,
            "started_at": timestamp,
            "status": "in_progress",
            "events": [
                {
                    "timestamp": timestamp,
                    "event": "task_started"
                }
            ]
        }
        
        with open(task_file, 'w') as f:
            json.dump(tracking_data, f, indent=2)
            
    def track_task_complete(self, agent_id: str, task_id: str, status: str = "completed"):
        """Mark a task as completed and record the timestamp"""
        timestamp = datetime.now().isoformat() + 'Z'
        task_file = self.metrics_dir / f"tasks/{task_id}_tracking.json"
        
        # Load existing tracking data
        if task_file.exists():
            with open(task_file, 'r') as f:
                tracking_data = json.load(f)
        else:
            tracking_data = {
                "task_id": task_id,
                "agent_id": agent_id,
                "events": []
            }
            
        tracking_data["completed_at"] = timestamp
        tracking_data["status"] = status
        tracking_data["events"].append({
            "timestamp": timestamp,
            "event": f"task_{status}"
        })
        
        # Calculate actual hours if we have start time
        if "started_at" in tracking_data:
            start = datetime.fromisoformat(tracking_data["started_at"].replace('Z', '+00:00'))
            end = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            tracking_data["actual_hours"] = (end - start).total_seconds() / 3600
            
        with open(task_file, 'w') as f:
            json.dump(tracking_data, f, indent=2)


def main():
    """CLI interface for agent metrics"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agent Performance Metrics System")
    parser.add_argument("command", choices=["collect", "report", "track-start", "track-complete"],
                       help="Command to execute")
    parser.add_argument("--agent", help="Agent ID (for collect or track commands)")
    parser.add_argument("--task", help="Task ID (for track commands)")
    parser.add_argument("--status", default="completed", help="Task completion status")
    
    args = parser.parse_args()
    
    metrics = AgentMetrics()
    
    if args.command == "collect":
        if args.agent:
            # Collect metrics for specific agent
            agent_metrics = metrics.collect_metrics_from_outbox(args.agent)
            metrics.save_agent_metrics(args.agent, agent_metrics)
            print(f"Collected {len(agent_metrics)} metrics for agent {args.agent}")
        else:
            # Collect metrics for all agents
            agent_dirs = [d for d in (metrics.base_path / "postbox").iterdir() if d.is_dir()]
            for agent_dir in agent_dirs:
                agent_id = agent_dir.name
                agent_metrics = metrics.collect_metrics_from_outbox(agent_id)
                if agent_metrics:
                    metrics.save_agent_metrics(agent_id, agent_metrics)
                    print(f"Collected {len(agent_metrics)} metrics for agent {agent_id}")
                    
    elif args.command == "report":
        report = metrics.generate_performance_report()
        metrics.print_summary_report(report)
        print(f"\nDetailed report saved to: .metrics/reports/latest_performance_report.json")
        
    elif args.command == "track-start":
        if not args.agent or not args.task:
            print("Error: --agent and --task required for track-start")
            return
        metrics.track_task_start(args.agent, args.task)
        print(f"Started tracking task {args.task} for agent {args.agent}")
        
    elif args.command == "track-complete":
        if not args.agent or not args.task:
            print("Error: --agent and --task required for track-complete")
            return
        metrics.track_task_complete(args.agent, args.task, args.status)
        print(f"Completed tracking task {args.task} for agent {args.agent} with status: {args.status}")


if __name__ == "__main__":
    main()