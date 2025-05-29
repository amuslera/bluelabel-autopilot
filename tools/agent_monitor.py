#!/usr/bin/env python3
"""
Simple Agent Status Monitor
Shows real-time status of all agents and sprint progress
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path

class AgentMonitor:
    def __init__(self):
        self.base_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-autopilot")
        self.postbox_path = self.base_path / "postbox"
        self.sprint_file = self.base_path / ".sprint" / "progress.json"
        
    def get_agent_status(self, agent_id):
        """Check agent's current task from outbox"""
        outbox_file = self.postbox_path / agent_id / "outbox.json"
        
        if not outbox_file.exists():
            return {"status": "no_outbox", "current_task": None, "pending_tasks": []}
            
        try:
            with open(outbox_file) as f:
                outbox = json.load(f)
                
            # Check if agent is decommissioned
            if outbox.get("status") == "DECOMMISSIONED - No longer active":
                return {"status": "inactive", "current_task": None, "pending_tasks": []}
                
            tasks = outbox.get("tasks", [])
            
            # Find active and pending tasks
            active_task = None
            pending_tasks = []
            
            for task in tasks:
                if task.get("status") == "in_progress":
                    active_task = task
                elif task.get("status") == "pending":
                    pending_tasks.append(task)
                    
            if active_task:
                return {
                    "status": "working",
                    "current_task": active_task,
                    "pending_tasks": pending_tasks
                }
            elif pending_tasks:
                return {
                    "status": "ready",
                    "current_task": None,
                    "pending_tasks": pending_tasks
                }
                
            return {"status": "idle", "current_task": None, "pending_tasks": []}
            
        except Exception as e:
            return {"status": "error", "current_task": None, "pending_tasks": [], "error": str(e)}
    
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
        # These would typically come from a backlog file
        # For now, returning placeholder tasks
        return [
            "TASK-165H: API documentation generator",
            "TASK-165I: Agent communication protocol",
            "TASK-165J: Error recovery system",
            "TASK-165K: Performance optimization",
            "TASK-165L: Security audit tools"
        ]
    
    def display_status(self):
        """Display current status"""
        os.system('clear')
        
        print("=" * 80)
        print(f"🚀 AGENT STATUS MONITOR - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Agent statuses (excluding WA)
        agents = ["CA", "CB", "CC", "ARCH"]
        
        print("AGENT STATUS:")
        print("-" * 80)
        
        for agent in agents:
            status = self.get_agent_status(agent)
            
            if status["status"] == "working":
                task = status["current_task"]
                print(f"{agent} [Working]: {task['task_id']} - {task['title']} ⚡")
            elif status["status"] == "ready":
                pending = status["pending_tasks"]
                print(f"{agent} [Ready]: {len(pending)} task(s) pending ✓")
                if pending:
                    print(f"      Next: {pending[0]['task_id']} - {pending[0]['title']}")
            elif status["status"] == "idle":
                print(f"{agent} [Idle]: No tasks assigned 💤")
            elif status["status"] == "inactive":
                print(f"{agent} [Inactive]: Decommissioned ❌")
            else:
                print(f"{agent} [Error]: {status.get('error', 'Unknown error')} ⚠️")
        
        # WA status (always show as inactive)
        print("WA [Inactive]: Decommissioned ❌")
        
        print()
        
        # Current task assignments
        print("CURRENT TASK ASSIGNMENTS:")
        print("-" * 80)
        
        progress = self.get_sprint_progress()
        tasks = progress.get("tasks", {})
        
        # Group by agent
        agent_tasks = {}
        for task_id, task_info in tasks.items():
            agent = task_info.get("agent", "Unknown")
            if agent not in agent_tasks:
                agent_tasks[agent] = []
            agent_tasks[agent].append({
                "id": task_id,
                "title": task_info.get("title", "Unknown"),
                "status": task_info.get("status", "unknown")
            })
        
        for agent in ["CA", "CB", "CC", "ARCH"]:
            if agent in agent_tasks:
                print(f"{agent}:")
                for task in agent_tasks[agent]:
                    status_icon = "✓" if task["status"] == "completed" else "○"
                    print(f"  {status_icon} {task['id']}: {task['title']} ({task['status']})")
            else:
                print(f"{agent}: No tasks assigned")
        print()
        
        # Sprint progress
        print("SPRINT PROGRESS:")
        print("-" * 80)
        
        total = progress.get("total_tasks", 0)
        completed = progress.get("completed", 0)
        in_progress = progress.get("in_progress", 0)
        
        if total > 0:
            percent = int((completed / total) * 100)
            bar_length = 40
            filled = int(bar_length * completed / total)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(f"Progress: [{bar}] {percent}%")
            print(f"Tasks: {completed}/{total} complete, {in_progress} in progress")
        else:
            print("No sprint tasks defined")
        
        print()
        
        # Next planned tasks
        print("NEXT 5 PLANNED TASKS:")
        print("-" * 80)
        next_tasks = self.get_next_planned_tasks()
        for i, task in enumerate(next_tasks, 1):
            print(f"{i}. {task}")
        
        print()
        print("Press Ctrl+C to exit | Auto-refresh every 5 seconds")
    
    def run(self):
        """Run the monitor with auto-refresh"""
        try:
            while True:
                self.display_status()
                time.sleep(5)  # Refresh every 5 seconds
        except KeyboardInterrupt:
            print("\nMonitor stopped")

if __name__ == "__main__":
    monitor = AgentMonitor()
    monitor.run()