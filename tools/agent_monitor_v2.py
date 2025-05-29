#!/usr/bin/env python3
"""
Enhanced Agent Status Monitor v2
Shows real-time status with improved UI and features
Now includes: Export, Compact View, Historical View, Notifications, Preferences
"""

import json
import os
import time
import csv
import threading
import subprocess
import pyperclip
from datetime import datetime, timedelta
from pathlib import Path
import shutil
import argparse

class EnhancedAgentMonitor:
    def __init__(self, config_file="tools/monitor_config.json"):
        self.base_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-autopilot")
        self.postbox_path = self.base_path / "postbox"
        self.sprint_file = self.base_path / ".sprint" / "progress.json"
        self.metrics_path = self.base_path / ".metrics"
        self.config_file = self.base_path / config_file
        self.start_times = {}  # Track when tasks started
        self.historical_data = []  # Store 24h history
        self.last_notification_time = {}  # Track notifications
        
        # Load user preferences
        self.config = self.load_config()
        
        # Initialize metrics directory
        self.metrics_path.mkdir(exist_ok=True)
        (self.metrics_path / "agents").mkdir(exist_ok=True)
        (self.metrics_path / "exports").mkdir(exist_ok=True)
    
    def parse_iso_datetime(self, datetime_str):
        """Parse ISO datetime string, handling 'Z' suffix"""
        if datetime_str.endswith('Z'):
            datetime_str = datetime_str[:-1] + '+00:00'
        return datetime.fromisoformat(datetime_str)
        
    def load_config(self):
        """Load user configuration preferences"""
        default_config = {
            "view_mode": "normal",  # normal, compact, historical
            "auto_export": False,
            "notifications_enabled": True,
            "refresh_interval": 5,
            "show_performance": True,
            "max_history_hours": 24,
            "export_format": "csv",
            "notification_sound": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except:
                pass
        else:
            self.save_config(default_config)
        
        return default_config
    
    def save_config(self, config=None):
        """Save user configuration"""
        if config is None:
            config = self.config
        
        self.config_file.parent.mkdir(exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_terminal_width(self):
        """Get terminal width for responsive display"""
        return shutil.get_terminal_size().columns
    
    def format_duration(self, start_time):
        """Format duration from start time"""
        if not start_time:
            return ""
        duration = datetime.now() - self.parse_iso_datetime(start_time)
        hours = int(duration.total_seconds() // 3600)
        minutes = int((duration.total_seconds() % 3600) // 60)
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    def record_historical_data(self):
        """Record current status for historical view"""
        timestamp = datetime.now()
        agents_status = {}
        
        for agent in ["CA", "CB", "CC", "ARCH"]:
            status = self.get_agent_status(agent)
            agents_status[agent] = {
                "status": status["status"],
                "task": status["current_task"]["task_id"] if status["current_task"] else None,
                "pending_count": len(status["pending_tasks"])
            }
        
        sprint_progress = self.get_sprint_progress()
        
        historical_entry = {
            "timestamp": timestamp.isoformat(),
            "agents": agents_status,
            "sprint": {
                "total": sprint_progress.get("total_tasks", 0),
                "completed": sprint_progress.get("completed", 0),
                "in_progress": sprint_progress.get("in_progress", 0)
            }
        }
        
        self.historical_data.append(historical_entry)
        
        # Keep only last 24 hours
        cutoff = timestamp - timedelta(hours=self.config["max_history_hours"])
        self.historical_data = [
            entry for entry in self.historical_data 
            if self.parse_iso_datetime(entry["timestamp"]) > cutoff
        ]
    
    def send_desktop_notification(self, title, message):
        """Send desktop notification for task completions"""
        if not self.config["notifications_enabled"]:
            return
        
        try:
            # macOS notification
            script = f'''
            display notification "{message}" with title "{title}"
            '''
            subprocess.run(["osascript", "-e", script], check=False)
            
        except:
            # Fallback - print to console
            print(f"\n🔔 {title}: {message}")
    
    def check_for_completions(self):
        """Check for new task completions and send notifications"""
        for agent in ["CA", "CB", "CC", "ARCH"]:
            status = self.get_agent_status(agent)
            
            if status["history"]:
                latest_task = status["history"][-1]
                task_id = latest_task.get("task_id")
                timestamp = latest_task.get("timestamp")
                
                if task_id and timestamp:
                    notification_key = f"{agent}:{task_id}"
                    if notification_key not in self.last_notification_time:
                        # New completion
                        self.last_notification_time[notification_key] = timestamp
                        task_title = latest_task.get("summary", task_id)
                        hours = latest_task.get("metrics", {}).get("actual_hours", "?")
                        
                        self.send_desktop_notification(
                            f"Task Completed - {agent}",
                            f"{task_title} (Duration: {hours}h)"
                        )
    
    def export_metrics_to_csv(self, filename=None):
        """Export current metrics and status to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_metrics_{timestamp}.csv"
        
        export_path = self.metrics_path / "exports" / filename
        export_path.parent.mkdir(exist_ok=True)
        
        # Prepare data for export
        export_data = []
        
        for agent in ["CA", "CB", "CC", "ARCH", "WA"]:
            status = self.get_agent_status(agent)
            metrics = self.get_agent_metrics(agent)
            
            row = {
                "Agent": agent,
                "Status": status["status"],
                "Current_Task": status["current_task"]["task_id"] if status["current_task"] else "",
                "Pending_Tasks": len(status["pending_tasks"]),
                "Completed_Tasks": len(status["history"]),
                "Success_Rate": metrics.get("success_rate", 0) if metrics else 0,
                "Avg_Duration": metrics.get("average_completion_time", 0) if metrics else 0,
                "Last_Active": status["history"][-1]["timestamp"] if status["history"] else "",
                "Export_Time": datetime.now().isoformat()
            }
            
            # Add current task details if working
            if status["current_task"]:
                task = status["current_task"]
                row.update({
                    "Current_Task_Title": task.get("title", ""),
                    "Current_Task_Priority": task.get("priority", ""),
                    "Task_Duration": self.format_duration(self.start_times.get(agent))
                })
            
            export_data.append(row)
        
        # Write to CSV
        with open(export_path, 'w', newline='') as csvfile:
            if export_data:
                fieldnames = export_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(export_data)
        
        return export_path
    
    def copy_status_to_clipboard(self):
        """Copy current status report to clipboard"""
        status_report = []
        status_report.append(f"Agent Status Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        status_report.append("=" * 50)
        
        for agent in ["CA", "CB", "CC", "ARCH"]:
            status = self.get_agent_status(agent)
            
            if status["status"] == "working":
                task = status["current_task"]
                duration = self.format_duration(self.start_times.get(agent))
                status_report.append(f"{agent}: Working on {task['task_id']} - {task['title']} ({duration})")
            elif status["status"] == "ready":
                pending = len(status["pending_tasks"])
                status_report.append(f"{agent}: Ready ({pending} pending tasks)")
            elif status["status"] == "idle":
                status_report.append(f"{agent}: Idle")
            else:
                status_report.append(f"{agent}: {status['status']}")
        
        # Sprint progress
        progress = self.get_sprint_progress()
        if progress.get("total_tasks", 0) > 0:
            completed = progress.get("completed", 0)
            total = progress.get("total_tasks", 0)
            percent = int((completed / total) * 100)
            status_report.append(f"\nSprint Progress: {completed}/{total} ({percent}%)")
        
        report_text = "\n".join(status_report)
        
        try:
            pyperclip.copy(report_text)
            return True
        except:
            return False
    
    def get_agent_metrics(self, agent_id):
        """Get performance metrics for agent"""
        metrics_file = self.metrics_path / "agents" / f"{agent_id}_metrics.json"
        if not metrics_file.exists():
            return None
        try:
            with open(metrics_file) as f:
                return json.load(f)
        except:
            return None
    
    def get_agent_status(self, agent_id):
        """Check agent's current task from outbox"""
        outbox_file = self.postbox_path / agent_id / "outbox.json"
        
        if not outbox_file.exists():
            return {"status": "no_outbox", "current_task": None, "pending_tasks": [], "history": []}
            
        try:
            with open(outbox_file) as f:
                outbox = json.load(f)
                
            # Check if agent is decommissioned
            if outbox.get("status") == "DECOMMISSIONED - No longer active":
                return {"status": "inactive", "current_task": None, "pending_tasks": [], "history": []}
                
            tasks = outbox.get("tasks", [])
            history = outbox.get("history", [])
            
            # Find active and pending tasks
            active_task = None
            pending_tasks = []
            
            for task in tasks:
                if task.get("status") == "in_progress":
                    active_task = task
                    # Track start time
                    if agent_id not in self.start_times:
                        self.start_times[agent_id] = task.get("created_at", datetime.now().isoformat())
                elif task.get("status") == "pending":
                    pending_tasks.append(task)
                    
            if active_task:
                return {
                    "status": "working",
                    "current_task": active_task,
                    "pending_tasks": pending_tasks,
                    "history": history[-3:]  # Last 3 completed tasks
                }
            elif pending_tasks:
                # Clear start time if not working
                self.start_times.pop(agent_id, None)
                return {
                    "status": "ready",
                    "current_task": None,
                    "pending_tasks": pending_tasks,
                    "history": history[-3:]
                }
                
            self.start_times.pop(agent_id, None)
            return {"status": "idle", "current_task": None, "pending_tasks": [], "history": history[-3:]}
            
        except Exception as e:
            return {"status": "error", "current_task": None, "pending_tasks": [], "history": [], "error": str(e)}
    
    def get_sprint_progress(self):
        """Load sprint progress from file"""
        if not self.sprint_file.exists():
            return {"total_tasks": 0, "completed": 0, "in_progress": 0, "tasks": {}}
            
        try:
            with open(self.sprint_file) as f:
                return json.load(f)
        except:
            return {"total_tasks": 0, "completed": 0, "in_progress": 0, "tasks": {}}
    
    def get_next_planned_tasks(self):
        """Return list of next planned tasks"""
        return [
            "TASK-165M: Security audit tools",
            "TASK-165N: Batch task processing", 
            "TASK-165O: Agent health monitoring",
            "TASK-165P: Workflow visualization",
            "TASK-165Q: Sprint automation tools"
        ]
    
    def get_priority_icon(self, priority):
        """Get icon for priority level"""
        return {
            "HIGH": "🔴",
            "MEDIUM": "🟡", 
            "LOW": "🟢"
        }.get(priority, "⚪")
    
    def get_agent_efficiency_stars(self, metrics):
        """Calculate efficiency stars"""
        if not metrics:
            return "⭐☆☆☆☆"
        
        success_rate = metrics.get("success_rate", 0)
        if success_rate >= 95:
            return "⭐⭐⭐⭐⭐"
        elif success_rate >= 90:
            return "⭐⭐⭐⭐☆"
        elif success_rate >= 80:
            return "⭐⭐⭐☆☆"
        elif success_rate >= 70:
            return "⭐⭐☆☆☆"
        else:
            return "⭐☆☆☆☆"
    
    def display_compact_view(self):
        """Display compact/minimal view"""
        width = self.get_terminal_width()
        
        print("=" * width)
        print(f"🚀 AGENT MONITOR (Compact) - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * width)
        
        # One-line status for each agent
        agents = ["CA", "CB", "CC", "ARCH"]
        for agent in agents:
            status = self.get_agent_status(agent)
            
            if status["status"] == "working":
                task = status["current_task"]
                duration = self.format_duration(self.start_times.get(agent))
                print(f"{agent}: ⚡ {task['task_id']} ({duration})")
            elif status["status"] == "ready":
                pending = len(status["pending_tasks"])
                print(f"{agent}: ✓ Ready ({pending} pending)")
            elif status["status"] == "idle":
                print(f"{agent}: 💤 Idle")
            else:
                print(f"{agent}: ❌ {status['status']}")
        
        # Sprint progress (one line)
        progress = self.get_sprint_progress()
        if progress.get("total_tasks", 0) > 0:
            completed = progress.get("completed", 0)
            total = progress.get("total_tasks", 0)
            percent = int((completed / total) * 100)
            print(f"\nSprint: {completed}/{total} ({percent}%)")
        
        print(f"\n[c]opy [e]xport [n]ormal [h]istory [q]uit | Refresh: {self.config['refresh_interval']}s")
    
    def display_historical_view(self):
        """Display 24-hour historical view"""
        width = self.get_terminal_width()
        
        print("=" * width)
        print(f"📊 AGENT MONITOR (24h History) - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * width)
        
        if not self.historical_data:
            print("No historical data available yet. Monitor needs to run to collect data.")
            print("\n[n]ormal [c]ompact [q]uit")
            return
        
        # Show hourly activity summary
        print("HOURLY ACTIVITY (Last 24h):")
        print("-" * width)
        
        # Group data by hour
        hourly_data = {}
        for entry in self.historical_data:
            hour = self.parse_iso_datetime(entry["timestamp"]).strftime("%H:00")
            if hour not in hourly_data:
                hourly_data[hour] = {"total_active": 0, "task_changes": 0}
            
            active_count = sum(1 for agent_status in entry["agents"].values() 
                             if agent_status["status"] == "working")
            hourly_data[hour]["total_active"] += active_count
        
        # Display last 12 hours
        for i in range(12):
            hour_time = datetime.now() - timedelta(hours=i)
            hour_key = hour_time.strftime("%H:00")
            
            if hour_key in hourly_data:
                avg_active = hourly_data[hour_key]["total_active"] / len([
                    e for e in self.historical_data 
                    if self.parse_iso_datetime(e["timestamp"]).strftime("%H:00") == hour_key
                ])
                activity_bar = "█" * int(avg_active) + "░" * (4 - int(avg_active))
                print(f"{hour_key}: [{activity_bar}] Avg {avg_active:.1f} agents active")
            else:
                print(f"{hour_key}: [░░░░] No data")
        
        # Recent significant events
        print(f"\nRECENT EVENTS:")
        print("-" * width)
        
        # Look for status changes in recent data
        if len(self.historical_data) >= 2:
            latest = self.historical_data[-1]
            previous = self.historical_data[-2]
            
            for agent in ["CA", "CB", "CC", "ARCH"]:
                latest_status = latest["agents"].get(agent, {})
                previous_status = previous["agents"].get(agent, {})
                
                if latest_status.get("status") != previous_status.get("status"):
                    time_str = self.parse_iso_datetime(latest["timestamp"]).strftime("%H:%M")
                    print(f"[{time_str}] {agent} changed from {previous_status.get('status', 'unknown')} to {latest_status.get('status', 'unknown')}")
        
        print(f"\n[n]ormal [c]ompact [e]xport [q]uit")
    
    def display_normal_view(self):
        """Display normal detailed view"""
        width = self.get_terminal_width()
        
        # Header
        print("=" * width)
        print(f"🚀 ENHANCED AGENT STATUS MONITOR v2 - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * width)
        print()
        
        # Agent statuses with time tracking
        agents = ["CA", "CB", "CC", "ARCH"]
        
        print("AGENT STATUS & PERFORMANCE:")
        print("-" * width)
        
        for agent in agents:
            status = self.get_agent_status(agent)
            metrics = self.get_agent_metrics(agent)
            
            # Status line with time tracking
            if status["status"] == "working":
                task = status["current_task"]
                duration = self.format_duration(self.start_times.get(agent))
                priority_icon = self.get_priority_icon(task.get("priority", "MEDIUM"))
                print(f"{agent} [Working]: {task['task_id']} - {task['title']} {priority_icon} ⚡ ({duration})")
            elif status["status"] == "ready":
                pending = status["pending_tasks"]
                last_task = status["history"][-1] if status["history"] else None
                last_info = f" Last: {last_task['task_id']} ✅" if last_task else ""
                print(f"{agent} [Ready]: {len(pending)} task(s) pending ✓{last_info}")
                if pending:
                    priority_icon = self.get_priority_icon(pending[0].get("priority", "MEDIUM"))
                    print(f"      Next: {pending[0]['task_id']} - {pending[0]['title']} {priority_icon}")
            elif status["status"] == "idle":
                last_task = status["history"][-1] if status["history"] else None
                last_info = f" Last: {last_task['task_id']} ({last_task.get('metrics', {}).get('actual_hours', '?')}h)" if last_task else ""
                print(f"{agent} [Idle]: No tasks 💤{last_info}")
            elif status["status"] == "inactive":
                print(f"{agent} [Inactive]: Decommissioned ❌")
            else:
                print(f"{agent} [Error]: {status.get('error', 'Unknown error')} ⚠️")
            
            # Performance metrics
            if metrics and self.config["show_performance"]:
                stars = self.get_agent_efficiency_stars(metrics)
                avg_time = metrics.get("average_completion_time", 0)
                success_rate = metrics.get("success_rate", 0)
                print(f"      Performance: {stars} | Avg: {avg_time:.1f}h | Success: {success_rate:.0f}%")
        
        # WA status (always inactive)
        print("WA [Inactive]: Decommissioned ❌")
        
        print()
        
        # Recent Activity
        print("RECENT ACTIVITY:")
        print("-" * width)
        
        recent_activities = []
        for agent in agents:
            status = self.get_agent_status(agent)
            for task in status.get("history", [])[-1:]:
                if "timestamp" in task:
                    recent_activities.append({
                        "time": task["timestamp"],
                        "agent": agent,
                        "task": task["task_id"],
                        "summary": task.get("summary", "Completed"),
                        "hours": task.get("metrics", {}).get("actual_hours", "?")
                    })
        
        # Sort by time and show last 3
        recent_activities.sort(key=lambda x: x["time"], reverse=True)
        for activity in recent_activities[:3]:
            time_str = self.parse_iso_datetime(activity["time"]).strftime("%H:%M")
            try:
                hours_val = float(activity["hours"])
                emoji = "🚀" if hours_val < 0.5 else "✅"
            except (ValueError, TypeError):
                emoji = "⏱️"  # Unknown duration
            print(f"[{time_str}] {activity['agent']} completed {activity['task']} in {activity['hours']}h {emoji}")
        
        print()
        
        # Sprint progress with visual bar
        print("SPRINT PROGRESS:")
        print("-" * width)
        
        progress = self.get_sprint_progress()
        total = progress.get("total_tasks", 0)
        completed = progress.get("completed", 0)
        in_progress = progress.get("in_progress", 0)
        
        if total > 0:
            percent = int((completed / total) * 100)
            bar_length = min(40, width - 20)
            filled = int(bar_length * completed / total)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"Progress: [{bar}] {percent}%")
            print(f"Tasks: {completed}/{total} complete, {in_progress} in progress")
            
            # Sprint velocity
            sprint_start = progress.get("start_date")
            if sprint_start:
                days_elapsed = (datetime.now() - self.parse_iso_datetime(sprint_start)).days + 1
                daily_rate = completed / days_elapsed
                print(f"Velocity: {daily_rate:.1f} tasks/day")
        else:
            print("No sprint tasks defined")
        
        print()
        
        # Alerts
        alerts = []
        for agent in agents:
            status = self.get_agent_status(agent)
            if status["status"] == "idle" and agent != "ARCH":
                alerts.append(f"• {agent} idle - assign new task?")
        
        if alerts:
            print("⚠️  ALERTS:")
            print("-" * width)
            for alert in alerts:
                print(alert)
            print()
        
        # Next planned tasks
        print("NEXT 5 PLANNED TASKS:")
        print("-" * width)
        next_tasks = self.get_next_planned_tasks()
        for i, task in enumerate(next_tasks, 1):
            print(f"{i}. {task}")
        
        print()
        print("Commands: [c]opy [e]xport [h]istory [C]ompact [n]otifications [q]uit")
        print(f"Auto-refresh: {self.config['refresh_interval']}s | Notifications: {'ON' if self.config['notifications_enabled'] else 'OFF'}")
    
    def display_status(self):
        """Display status based on current view mode"""
        os.system('clear')
        
        if self.config["view_mode"] == "compact":
            self.display_compact_view()
        elif self.config["view_mode"] == "historical":
            self.display_historical_view()
        else:
            self.display_normal_view()
    
    def handle_user_input(self):
        """Handle user keyboard input for interactive features"""
        import select
        import sys
        import tty
        import termios
        
        if select.select([sys.stdin], [], [], 0.1)[0]:
            # Save terminal settings
            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())
                key = sys.stdin.read(1)
            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            
            if key == 'c':
                # Copy status to clipboard
                if self.copy_status_to_clipboard():
                    print("\n✅ Status copied to clipboard!")
                else:
                    print("\n❌ Failed to copy to clipboard")
                time.sleep(1)
            
            elif key == 'e':
                # Export metrics
                export_path = self.export_metrics_to_csv()
                print(f"\n✅ Metrics exported to: {export_path}")
                time.sleep(1)
            
            elif key == 'h':
                # Switch to historical view
                self.config["view_mode"] = "historical"
                self.save_config()
            
            elif key == 'C':
                # Switch to compact view
                self.config["view_mode"] = "compact"
                self.save_config()
            
            elif key == 'n':
                # Toggle notifications
                self.config["notifications_enabled"] = not self.config["notifications_enabled"]
                self.save_config()
                status = "enabled" if self.config["notifications_enabled"] else "disabled"
                print(f"\n🔔 Notifications {status}")
                time.sleep(1)
            
            elif key in ['1', '2', '3', '4']:
                # Switch view mode by number
                modes = ["normal", "compact", "historical"]
                mode_index = int(key) - 1
                if mode_index < len(modes):
                    self.config["view_mode"] = modes[mode_index]
                    self.save_config()
            
            elif key == 'q':
                return False
        
        return True
    
    def run(self, interactive=True):
        """Run the monitor with auto-refresh and user interaction"""
        print("🚀 Starting Enhanced Agent Monitor v2...")
        print("Loading configuration and initializing...")
        time.sleep(1)
        
        try:
            while True:
                # Record historical data
                self.record_historical_data()
                
                # Check for task completions
                self.check_for_completions()
                
                # Display current status
                self.display_status()
                
                # Handle user input if interactive
                if interactive:
                    for _ in range(self.config["refresh_interval"]):
                        if not self.handle_user_input():
                            raise KeyboardInterrupt
                        time.sleep(1)
                else:
                    time.sleep(self.config["refresh_interval"])
                
                # Auto-export if enabled
                if self.config["auto_export"]:
                    timestamp = datetime.now().strftime("%H%M")
                    if timestamp.endswith("00"):  # Every hour
                        self.export_metrics_to_csv()
                        
        except KeyboardInterrupt:
            print("\n👋 Monitor stopped")
            
            # Final export option
            print("\nWould you like to export final metrics? [y/N]")
            try:
                response = input().lower()
                if response == 'y':
                    export_path = self.export_metrics_to_csv()
                    print(f"📊 Final metrics exported to: {export_path}")
            except:
                pass

def main():
    """Main entry point with command line arguments"""
    parser = argparse.ArgumentParser(description='Enhanced Agent Status Monitor v2')
    parser.add_argument('--view', choices=['normal', 'compact', 'historical'], 
                       default='normal', help='Initial view mode')
    parser.add_argument('--config', default='tools/monitor_config.json',
                       help='Configuration file path')
    parser.add_argument('--export-only', action='store_true',
                       help='Export metrics and exit')
    parser.add_argument('--no-notifications', action='store_true',
                       help='Disable desktop notifications')
    parser.add_argument('--refresh', type=int, default=5,
                       help='Refresh interval in seconds')
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = EnhancedAgentMonitor(args.config)
    
    # Override config with command line args
    monitor.config["view_mode"] = args.view
    monitor.config["refresh_interval"] = args.refresh
    if args.no_notifications:
        monitor.config["notifications_enabled"] = False
    
    monitor.save_config()
    
    # Handle export-only mode
    if args.export_only:
        export_path = monitor.export_metrics_to_csv()
        print(f"📊 Metrics exported to: {export_path}")
        return
    
    # Run monitor
    monitor.run()

if __name__ == "__main__":
    main()