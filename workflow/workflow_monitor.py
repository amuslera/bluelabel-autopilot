#!/usr/bin/env python3
"""
Workflow Monitoring and Health Checking System

Monitors workflow execution, health status, and provides real-time insights
into workflow performance and issues.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import statistics


@dataclass
class WorkflowHealth:
    """Workflow health status"""
    workflow_id: str
    name: str
    status: str
    health_score: float  # 0-100
    issues: List[str]
    metrics: Dict[str, Any]
    last_check: datetime


@dataclass
class TaskHealth:
    """Individual task health status"""
    task_id: str
    workflow_id: str
    status: str
    health_score: float
    execution_time: Optional[float]
    retry_count: int
    issues: List[str]


class WorkflowMonitor:
    """Monitors workflow execution and health"""
    
    def __init__(self, base_path: str = "/Users/arielmuslera/Development/Projects/bluelabel-autopilot"):
        self.base_path = Path(base_path)
        self.workflows_dir = self.base_path / "workflow" / "instances"
        self.monitoring_dir = self.base_path / "workflow" / "monitoring"
        self.monitoring_dir.mkdir(parents=True, exist_ok=True)
        
        # Health thresholds
        self.thresholds = {
            "task_timeout_warning": 3600,  # 1 hour
            "task_timeout_critical": 7200,  # 2 hours
            "workflow_timeout_warning": 14400,  # 4 hours
            "workflow_timeout_critical": 28800,  # 8 hours
            "retry_warning": 2,
            "retry_critical": 4,
            "health_score_warning": 70,
            "health_score_critical": 50
        }
        
        # Historical data
        self.health_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.performance_metrics: Dict[str, List[float]] = defaultdict(list)
        
        # Monitoring state
        self.monitoring_active = False
        self.last_scan = None
        
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous workflow monitoring"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                await self.scan_workflows()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
                
    def stop_monitoring(self):
        """Stop workflow monitoring"""
        self.monitoring_active = False
        
    async def scan_workflows(self) -> Dict[str, WorkflowHealth]:
        """Scan all workflows and assess health"""
        workflow_health = {}
        
        for workflow_file in self.workflows_dir.glob("*.json"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = json.load(f)
                    
                health = await self._assess_workflow_health(workflow_data)
                workflow_health[health.workflow_id] = health
                
                # Store in history
                self.health_history[health.workflow_id].append(health)
                
            except Exception as e:
                print(f"Error scanning workflow {workflow_file}: {e}")
                
        self.last_scan = datetime.now()
        
        # Save monitoring report
        await self._save_monitoring_report(workflow_health)
        
        return workflow_health
        
    async def _assess_workflow_health(self, workflow_data: Dict[str, Any]) -> WorkflowHealth:
        """Assess health of individual workflow"""
        workflow_id = workflow_data['id']
        name = workflow_data['name']
        status = workflow_data.get('status', 'unknown')
        
        issues = []
        metrics = {}
        health_components = []
        
        # Check workflow timing
        created_at = datetime.fromisoformat(workflow_data['created_at'])
        started_at = datetime.fromisoformat(workflow_data['started_at']) if workflow_data.get('started_at') else None
        completed_at = datetime.fromisoformat(workflow_data['completed_at']) if workflow_data.get('completed_at') else None
        
        now = datetime.now()
        
        # Workflow duration analysis
        if started_at and not completed_at:
            running_duration = (now - started_at).total_seconds()
            metrics['running_duration_seconds'] = running_duration
            
            if running_duration > self.thresholds['workflow_timeout_critical']:
                issues.append(f"Workflow running for {running_duration/3600:.1f} hours (critical)")
                health_components.append(20)
            elif running_duration > self.thresholds['workflow_timeout_warning']:
                issues.append(f"Workflow running for {running_duration/3600:.1f} hours (warning)")
                health_components.append(60)
            else:
                health_components.append(90)
        elif completed_at and started_at:
            total_duration = (completed_at - started_at).total_seconds()
            metrics['total_duration_seconds'] = total_duration
            health_components.append(95)
        else:
            health_components.append(85)
            
        # Task health analysis
        tasks = workflow_data.get('tasks', {})
        task_health_scores = []
        
        for task_id, task_data in tasks.items():
            task_health = await self._assess_task_health(task_data, workflow_id)
            task_health_scores.append(task_health.health_score)
            
            if task_health.issues:
                issues.extend([f"Task {task_id}: {issue}" for issue in task_health.issues])
                
        if task_health_scores:
            avg_task_health = statistics.mean(task_health_scores)
            metrics['average_task_health'] = avg_task_health
            health_components.append(avg_task_health)
        else:
            health_components.append(50)
            
        # Status-based health
        if status == 'completed':
            health_components.append(100)
        elif status == 'running':
            health_components.append(80)
        elif status == 'failed':
            health_components.append(10)
            issues.append("Workflow has failed")
        elif status == 'cancelled':
            health_components.append(0)
            issues.append("Workflow was cancelled")
        else:
            health_components.append(50)
            
        # Error analysis
        if workflow_data.get('error'):
            issues.append(f"Workflow error: {workflow_data['error']}")
            health_components.append(20)
        else:
            health_components.append(100)
            
        # Calculate overall health score
        health_score = statistics.mean(health_components) if health_components else 50
        
        # Performance metrics
        metrics.update({
            'task_count': len(tasks),
            'completed_tasks': sum(1 for t in tasks.values() if t.get('status') == 'completed'),
            'failed_tasks': sum(1 for t in tasks.values() if t.get('status') == 'failed'),
            'running_tasks': sum(1 for t in tasks.values() if t.get('status') == 'running')
        })
        
        return WorkflowHealth(
            workflow_id=workflow_id,
            name=name,
            status=status,
            health_score=health_score,
            issues=issues,
            metrics=metrics,
            last_check=datetime.now()
        )
        
    async def _assess_task_health(self, task_data: Dict[str, Any], workflow_id: str) -> TaskHealth:
        """Assess health of individual task"""
        task_id = task_data['id']
        status = task_data.get('status', 'unknown')
        
        issues = []
        health_components = []
        
        # Timing analysis
        started_at = task_data.get('started_at')
        completed_at = task_data.get('completed_at')
        execution_time = None
        
        if started_at and completed_at:
            start_time = datetime.fromisoformat(started_at)
            end_time = datetime.fromisoformat(completed_at)
            execution_time = (end_time - start_time).total_seconds()
            
        elif started_at and not completed_at:
            start_time = datetime.fromisoformat(started_at)
            running_time = (datetime.now() - start_time).total_seconds()
            execution_time = running_time
            
            if running_time > self.thresholds['task_timeout_critical']:
                issues.append(f"Task running for {running_time/3600:.1f} hours (critical)")
                health_components.append(10)
            elif running_time > self.thresholds['task_timeout_warning']:
                issues.append(f"Task running for {running_time/3600:.1f} hours (warning)")
                health_components.append(50)
            else:
                health_components.append(80)
        else:
            health_components.append(70)
            
        # Retry analysis
        retry_count = len([h for h in task_data.get('execution_history', []) if h.get('action') == 'error'])
        
        if retry_count >= self.thresholds['retry_critical']:
            issues.append(f"Task has {retry_count} retry attempts (critical)")
            health_components.append(20)
        elif retry_count >= self.thresholds['retry_warning']:
            issues.append(f"Task has {retry_count} retry attempts (warning)")
            health_components.append(60)
        else:
            health_components.append(90)
            
        # Status-based health
        if status == 'completed':
            health_components.append(100)
        elif status == 'running':
            health_components.append(75)
        elif status == 'failed':
            health_components.append(0)
            issues.append("Task has failed")
        elif status == 'blocked':
            health_components.append(40)
            issues.append("Task is blocked")
        else:
            health_components.append(50)
            
        # Error analysis
        if task_data.get('error'):
            issues.append(f"Task error: {task_data['error']}")
            health_components.append(10)
        else:
            health_components.append(100)
            
        health_score = statistics.mean(health_components) if health_components else 50
        
        return TaskHealth(
            task_id=task_id,
            workflow_id=workflow_id,
            status=status,
            health_score=health_score,
            execution_time=execution_time,
            retry_count=retry_count,
            issues=issues
        )
        
    async def _save_monitoring_report(self, workflow_health: Dict[str, WorkflowHealth]):
        """Save monitoring report to file"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_workflows": len(workflow_health),
                "healthy_workflows": sum(1 for h in workflow_health.values() if h.health_score >= self.thresholds['health_score_warning']),
                "warning_workflows": sum(1 for h in workflow_health.values() if self.thresholds['health_score_critical'] <= h.health_score < self.thresholds['health_score_warning']),
                "critical_workflows": sum(1 for h in workflow_health.values() if h.health_score < self.thresholds['health_score_critical']),
                "average_health": statistics.mean([h.health_score for h in workflow_health.values()]) if workflow_health else 0
            },
            "workflows": [asdict(h) for h in workflow_health.values()]
        }
        
        # Save current report
        report_file = self.monitoring_dir / "current_health_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        # Save timestamped report
        timestamp_file = self.monitoring_dir / f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(timestamp_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
    def get_workflow_health(self, workflow_id: str) -> Optional[WorkflowHealth]:
        """Get current health status for specific workflow"""
        if workflow_id in self.health_history:
            history = self.health_history[workflow_id]
            if history:
                return history[-1]
        return None
        
    def get_health_trends(self, workflow_id: str, hours: int = 24) -> List[WorkflowHealth]:
        """Get health trend for workflow over specified time period"""
        if workflow_id not in self.health_history:
            return []
            
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [h for h in self.health_history[workflow_id] if h.last_check >= cutoff_time]
        
    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        current_report_file = self.monitoring_dir / "current_health_report.json"
        
        if current_report_file.exists():
            with open(current_report_file, 'r') as f:
                return json.load(f)
        else:
            return {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "total_workflows": 0,
                    "healthy_workflows": 0,
                    "warning_workflows": 0,
                    "critical_workflows": 0,
                    "average_health": 0
                },
                "workflows": []
            }
            
    async def generate_health_alerts(self) -> List[Dict[str, Any]]:
        """Generate health alerts for critical issues"""
        alerts = []
        
        workflow_health = await self.scan_workflows()
        
        for health in workflow_health.values():
            # Critical health score
            if health.health_score < self.thresholds['health_score_critical']:
                alerts.append({
                    "type": "critical",
                    "workflow_id": health.workflow_id,
                    "message": f"Workflow '{health.name}' has critical health score: {health.health_score:.1f}",
                    "issues": health.issues,
                    "timestamp": datetime.now().isoformat()
                })
                
            # Warning health score
            elif health.health_score < self.thresholds['health_score_warning']:
                alerts.append({
                    "type": "warning",
                    "workflow_id": health.workflow_id,
                    "message": f"Workflow '{health.name}' has low health score: {health.health_score:.1f}",
                    "issues": health.issues,
                    "timestamp": datetime.now().isoformat()
                })
                
            # Long running workflows
            if health.status == 'running' and 'running_duration_seconds' in health.metrics:
                duration_hours = health.metrics['running_duration_seconds'] / 3600
                if duration_hours > self.thresholds['workflow_timeout_critical'] / 3600:
                    alerts.append({
                        "type": "critical",
                        "workflow_id": health.workflow_id,
                        "message": f"Workflow '{health.name}' has been running for {duration_hours:.1f} hours",
                        "timestamp": datetime.now().isoformat()
                    })
                    
        # Save alerts
        if alerts:
            alerts_file = self.monitoring_dir / f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(alerts_file, 'w') as f:
                json.dump(alerts, f, indent=2)
                
        return alerts
        
    def cleanup_old_reports(self, days_to_keep: int = 7):
        """Cleanup old monitoring reports"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        for report_file in self.monitoring_dir.glob("health_report_*.json"):
            try:
                # Extract timestamp from filename
                timestamp_str = report_file.stem.split('_', 2)[2]
                file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                if file_date < cutoff_date:
                    report_file.unlink()
                    
            except (ValueError, IndexError):
                # Skip files with unexpected names
                continue
                
        # Cleanup old alerts
        for alert_file in self.monitoring_dir.glob("alerts_*.json"):
            try:
                timestamp_str = alert_file.stem.split('_', 1)[1]
                file_date = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                
                if file_date < cutoff_date:
                    alert_file.unlink()
                    
            except (ValueError, IndexError):
                continue


async def main():
    """CLI interface for workflow monitoring"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Workflow Monitoring System")
    parser.add_argument("command", choices=["monitor", "health", "alerts", "trends", "cleanup"],
                       help="Command to execute")
    parser.add_argument("--workflow-id", help="Specific workflow ID")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    parser.add_argument("--hours", type=int, default=24, help="Time window for trends in hours")
    parser.add_argument("--days", type=int, default=7, help="Days to keep for cleanup")
    
    args = parser.parse_args()
    
    monitor = WorkflowMonitor()
    
    if args.command == "monitor":
        print(f"Starting workflow monitoring (interval: {args.interval}s)")
        print("Press Ctrl+C to stop...")
        try:
            await monitor.start_monitoring(args.interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped")
            
    elif args.command == "health":
        if args.workflow_id:
            health = monitor.get_workflow_health(args.workflow_id)
            if health:
                print(f"\nWorkflow: {health.name}")
                print(f"Status: {health.status}")
                print(f"Health Score: {health.health_score:.1f}/100")
                if health.issues:
                    print("Issues:")
                    for issue in health.issues:
                        print(f"  - {issue}")
                print(f"Metrics: {health.metrics}")
            else:
                print(f"No health data found for workflow: {args.workflow_id}")
        else:
            summary = monitor.get_system_health_summary()
            print("\nSystem Health Summary:")
            print(f"Total Workflows: {summary['summary']['total_workflows']}")
            print(f"Healthy: {summary['summary']['healthy_workflows']}")
            print(f"Warning: {summary['summary']['warning_workflows']}")
            print(f"Critical: {summary['summary']['critical_workflows']}")
            print(f"Average Health: {summary['summary']['average_health']:.1f}/100")
            
    elif args.command == "alerts":
        alerts = await monitor.generate_health_alerts()
        if alerts:
            print(f"\n{len(alerts)} alerts generated:")
            for alert in alerts:
                print(f"\n[{alert['type'].upper()}] {alert['message']}")
                if 'issues' in alert:
                    for issue in alert['issues']:
                        print(f"  - {issue}")
        else:
            print("No alerts generated")
            
    elif args.command == "trends":
        if not args.workflow_id:
            print("--workflow-id required for trends command")
            return
            
        trends = monitor.get_health_trends(args.workflow_id, args.hours)
        if trends:
            print(f"\nHealth trends for {args.workflow_id} (last {args.hours} hours):")
            for i, health in enumerate(trends[-10:]):  # Show last 10 entries
                print(f"{i+1:2d}. {health.last_check.strftime('%H:%M:%S')} - "
                      f"Health: {health.health_score:.1f} - Status: {health.status}")
        else:
            print(f"No trend data found for workflow: {args.workflow_id}")
            
    elif args.command == "cleanup":
        monitor.cleanup_old_reports(args.days)
        print(f"Cleaned up monitoring reports older than {args.days} days")


if __name__ == "__main__":
    asyncio.run(main())