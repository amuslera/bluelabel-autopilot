#!/usr/bin/env python3
"""
Dynamic Agent Status Monitor v3
Automatically reads tasks from .md files and JSON files
No more manual updates needed!
"""

import json
import os
import re
import time
import csv
import threading
import subprocess
import pyperclip
from datetime import datetime, timedelta, timezone
from pathlib import Path
import shutil
import argparse
import glob

class DynamicAgentMonitor:
    def __init__(self, config_file="tools/monitor_config.json"):
        self.base_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-autopilot")
        self.postbox_path = self.base_path / "postbox"
        self.sprint_file = self.base_path / ".sprint" / "progress.json"
        self.metrics_path = self.base_path / ".metrics"
        self.config_file = self.base_path / config_file
        self.start_times = {}
        self.historical_data = []
        self.last_notification_time = {}
        
        # Load user preferences
        self.config = self.load_config()
        
        # Initialize metrics directory
        self.metrics_path.mkdir(exist_ok=True)
        (self.metrics_path / "agents").mkdir(exist_ok=True)
        (self.metrics_path / "exports").mkdir(exist_ok=True)

    def load_config(self):
        """Load user configuration preferences"""
        default_config = {
            "view_mode": "normal",
            "auto_export": False,
            "notifications_enabled": True,
            "refresh_interval": 10,
            "max_history_hours": 24,
            "export_format": "csv"
        }
        
        if not self.config_file.exists():
            with open(self.config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
        
        try:
            with open(self.config_file) as f:
                config = json.load(f)
            return {**default_config, **config}
        except:
            return default_config

    def parse_task_from_md(self, md_file_path):
        """Parse task information from .md file"""
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract task info using regex
            task_info = {}
            
            # Task ID and title from first line
            title_match = re.search(r'# (TASK-[\w\d-]+): (.+)', content)
            if title_match:
                task_info['task_id'] = title_match.group(1)
                task_info['title'] = title_match.group(2)
            
            # Priority
            priority_match = re.search(r'\*\*Priority:\*\* (\w+)', content)
            if priority_match:
                task_info['priority'] = priority_match.group(1)
            
            # Agent
            agent_match = re.search(r'\*\*Agent:\*\* (\w+)', content)
            if agent_match:
                task_info['agent'] = agent_match.group(1)
            
            # Estimated hours
            hours_match = re.search(r'\*\*Estimated Hours:\*\* ([\d-]+)', content)
            if hours_match:
                task_info['estimated_hours'] = hours_match.group(1)
            
            # Context/description
            context_match = re.search(r'## Context\s*(.*?)(?=##|$)', content, re.DOTALL)
            if context_match:
                task_info['context'] = context_match.group(1).strip()[:200] + "..."
            
            # Deliverables count
            deliverables = re.findall(r'- \[ \]', content)
            task_info['deliverables_count'] = len(deliverables)
            
            return task_info
        except Exception as e:
            return {"error": str(e)}

    def get_agent_inbox_tasks(self, agent_id):
        """Get all tasks from agent's inbox directory"""
        inbox_path = self.postbox_path / agent_id / "inbox"
        if not inbox_path.exists():
            return []
        
        tasks = []
        for md_file in inbox_path.glob("*.md"):
            task_info = self.parse_task_from_md(md_file)
            if 'task_id' in task_info:
                task_info['file'] = md_file.name
                task_info['status'] = 'pending'
                tasks.append(task_info)
        
        return tasks

    def get_dynamic_agent_status(self, agent_id):
        """Get agent status by reading both inbox and outbox"""
        outbox_file = self.postbox_path / agent_id / "outbox.json"
        
        # Get inbox tasks
        inbox_tasks = self.get_agent_inbox_tasks(agent_id)
        
        # Get outbox info
        outbox_data = {"tasks": [], "history": []}
        if outbox_file.exists():
            try:
                with open(outbox_file) as f:
                    outbox_data = json.load(f)
            except:
                pass
        
        # Find active task
        active_task = None
        for task in outbox_data.get("tasks", []):
            if task.get("status") == "in_progress":
                active_task = task
                break
        
        # Determine status
        if active_task:
            return {
                "status": "working",
                "current_task": active_task,
                "pending_tasks": inbox_tasks,
                "history": outbox_data.get("history", [])[-3:],
                "total_completed": outbox_data.get("metadata", {}).get("total_tasks_completed", 0)
            }
        elif inbox_tasks:
            return {
                "status": "ready",
                "current_task": None,
                "pending_tasks": inbox_tasks,
                "history": outbox_data.get("history", [])[-3:],
                "total_completed": outbox_data.get("metadata", {}).get("total_tasks_completed", 0)
            }
        else:
            return {
                "status": "idle",
                "current_task": None,
                "pending_tasks": [],
                "history": outbox_data.get("history", [])[-3:],
                "total_completed": outbox_data.get("metadata", {}).get("total_tasks_completed", 0)
            }

    def get_dynamic_sprint_info(self):
        """Dynamically determine sprint info from files"""
        progress = self.get_sprint_progress()
        sprint_id = progress.get("sprint_id", "Unknown")
        phase = progress.get("phase", "Unknown Phase")
        
        # Count total tasks across all agents
        total_pending = 0
        total_in_progress = 0
        total_completed = progress.get("completed", 0)
        
        for agent in ["CA", "CB", "CC"]:
            status = self.get_dynamic_agent_status(agent)
            total_pending += len(status["pending_tasks"])
            if status["status"] == "working":
                total_in_progress += 1
        
        # Determine goals based on current tasks
        current_tasks = []
        for agent in ["CA", "CB", "CC"]:
            status = self.get_dynamic_agent_status(agent)
            if status["current_task"]:
                current_tasks.append(status["current_task"]["title"])
            for task in status["pending_tasks"]:
                current_tasks.append(task["title"])
        
        # Create dynamic theme
        if any("ROI" in task for task in current_tasks):
            theme = "Voice-to-Table Automation"
            goals = "Implement ROI Report Automation workflow end-to-end"
        elif any("Deploy" in task for task in current_tasks):
            theme = "Launch Ready"
            goals = "Production deployment & user experience polish"
        elif any("Integration" in task for task in current_tasks):
            theme = "Full Stack Integration"
            goals = "Connect frontend, backend, and AI services"
        else:
            theme = "Production MVP"
            goals = "Building production-ready AI Operating System"
        
        return {
            "sprint_id": sprint_id,
            "phase": phase,
            "theme": theme,
            "goals": goals,
            "key_metrics": f"{total_completed} completed, {total_in_progress} active, {total_pending} pending"
        }

    def get_sprint_progress(self):
        """Load sprint progress from file"""
        if not self.sprint_file.exists():
            return {"total_tasks": 0, "completed": 0, "in_progress": 0, "tasks": {}}
            
        try:
            with open(self.sprint_file) as f:
                return json.load(f)
        except:
            return {"total_tasks": 0, "completed": 0, "in_progress": 0, "tasks": {}}

    def get_terminal_width(self):
        """Get terminal width for responsive display"""
        return shutil.get_terminal_size().columns

    def format_duration(self, start_time):
        """Format duration since start time"""
        if not start_time:
            return "unknown"
        
        try:
            if isinstance(start_time, str):
                start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            else:
                start_dt = start_time
            
            duration = datetime.now(timezone.utc) - start_dt.replace(tzinfo=timezone.utc)
            
            if duration.total_seconds() < 3600:
                return f"{int(duration.total_seconds() / 60)}m"
            else:
                return f"{int(duration.total_seconds() / 3600)}h{int((duration.total_seconds() % 3600) / 60)}m"
        except:
            return "unknown"

    def get_priority_icon(self, priority):
        """Get icon for priority level"""
        priority_str = str(priority).upper()
        return {
            "HIGH": "🔴",
            "CRITICAL": "🚨",
            "MEDIUM": "🟡", 
            "LOW": "🟢"
        }.get(priority_str, "⚪")

    def show_progress_bar(self, percentage, width=50):
        """Display a colored progress bar"""
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        
        # Color based on progress
        if percentage >= 80:
            color = "\033[32m"  # Green
        elif percentage >= 60:
            color = "\033[33m"  # Yellow
        else:
            color = "\033[31m"  # Red
        
        print(f"{color}[{bar}] {percentage:.0f}%\033[0m")

    def display_normal_view(self):
        """Display enhanced normal view with dynamic data"""
        width = self.get_terminal_width()
        
        # Clear screen
        print("\033[2J\033[H", end='')
        
        # Header with sprint information
        sprint_info = self.get_dynamic_sprint_info()
        
        print("=" * width)
        print(f"🚀 DYNAMIC AGENT MONITOR v3 - {datetime.now().strftime('%H:%M:%S')} | {sprint_info['sprint_id']}")
        print("=" * width)
        print(f"📋 PHASE: {sprint_info['phase']}")
        print(f"🎯 THEME: {sprint_info['theme']}")
        print(f"📊 GOALS: {sprint_info['goals']}")
        print(f"📈 METRICS: {sprint_info['key_metrics']}")
        print("=" * width)
        print()
        
        # Agent status - dynamically generated
        agents = ["CA", "CB", "CC"]
        
        print("🤖 AGENT STATUS:")
        print("-" * width)
        
        for agent in agents:
            status = self.get_dynamic_agent_status(agent)
            agent_names = {
                "CA": "Frontend (Cursor)",
                "CB": "Backend (Claude)",  
                "CC": "Testing (Claude)"
            }
            
            agent_name = agent_names.get(agent, agent)
            
            if status["status"] == "working":
                task = status["current_task"]
                duration = self.format_duration(task.get("started_at") or task.get("created_at"))
                priority_icon = self.get_priority_icon(task.get("priority", "MEDIUM"))
                print(f"🔄 {agent} ({agent_name}) - Total completed: {status['total_completed']}")
                print(f"   ├─ WORKING: {task['task_id']} - {task['title']} {priority_icon}")
                print(f"   └─ Duration: {duration}")
                
            elif status["status"] == "ready":
                pending = status["pending_tasks"]
                print(f"✅ {agent} ({agent_name}) - Total completed: {status['total_completed']}")
                print(f"   ├─ READY: {len(pending)} task(s) pending")
                if pending:
                    priority_icon = self.get_priority_icon(pending[0].get("priority", "MEDIUM"))
                    print(f"   └─ Next: {pending[0]['task_id']} - {pending[0]['title']} {priority_icon}")
                else:
                    print(f"   └─ Awaiting task assignment")
                    
            else:
                print(f"💤 {agent} ({agent_name}) - Total completed: {status['total_completed']}")
                print(f"   └─ IDLE: No active or pending tasks")
            
            print()
        
        # Sprint progress
        progress = self.get_sprint_progress()
        if progress.get("total_tasks", 0) > 0:
            completed = progress.get("completed", 0)
            total = progress.get("total_tasks", 0)
            in_progress = progress.get("in_progress", 0)
            percentage = (completed / total * 100) if total > 0 else 0
            
            print("📊 SPRINT PROGRESS:")
            print("-" * width)
            print(f"Tasks: {completed} completed | {in_progress} in progress | {total - completed - in_progress} pending")
            self.show_progress_bar(percentage, width - 10)
            print()
        
        # Recent activity from outbox history
        print("📝 RECENT ACTIVITY:")
        print("-" * width)
        
        all_recent = []
        for agent in agents:
            status = self.get_dynamic_agent_status(agent)
            for item in status["history"]:
                if "timestamp" in item:
                    all_recent.append({
                        "agent": agent,
                        "task": item.get("task_id", "Unknown"),
                        "summary": item.get("summary", "No summary"),
                        "timestamp": item["timestamp"]
                    })
        
        # Sort by timestamp and show recent 5
        all_recent.sort(key=lambda x: x["timestamp"], reverse=True)
        for item in all_recent[:5]:
            timestamp = datetime.fromisoformat(item["timestamp"].replace('Z', '+00:00'))
            time_str = timestamp.strftime("%H:%M")
            print(f"[{time_str}] {item['agent']}: {item['task']} - {item['summary'][:60]}...")
        
        if not all_recent:
            print("No recent activity found")
        
        print(f"\n[c]opy [e]xport [r]efresh [q]uit | Auto-refresh: {self.config['refresh_interval']}s")

    def run_monitor(self):
        """Run the dynamic monitor"""
        try:
            while True:
                if self.config['view_mode'] == 'normal':
                    self.display_normal_view()
                
                # Wait for refresh interval
                time.sleep(self.config['refresh_interval'])
                
        except KeyboardInterrupt:
            print("\n\nMonitor stopped.")

def main():
    parser = argparse.ArgumentParser(description='Dynamic Agent Monitor v3')
    parser.add_argument('--refresh', '-r', type=int, default=10, help='Refresh interval in seconds')
    parser.add_argument('--view', '-v', choices=['normal', 'compact'], default='normal', help='View mode')
    
    args = parser.parse_args()
    
    monitor = DynamicAgentMonitor()
    monitor.config['refresh_interval'] = args.refresh
    monitor.config['view_mode'] = args.view
    
    print("🚀 Starting Dynamic Agent Monitor v3...")
    print("📊 Auto-detecting tasks from .md files and JSON...")
    print("⚡ No manual updates needed!")
    print()
    
    monitor.run_monitor()

if __name__ == "__main__":
    main()