#!/usr/bin/env python3
"""
Quick agent status checker
Shows current status of all agents and their tasks
"""

import json
from pathlib import Path
from datetime import datetime

def check_agent_status(agent_id):
    """Check an agent's current task status"""
    outbox_file = Path(f"postbox/{agent_id}/outbox.json")
    
    if not outbox_file.exists():
        return {"status": "no_outbox", "task": None}
    
    try:
        with open(outbox_file) as f:
            data = json.load(f)
            
        # Handle both list and dict formats
        if isinstance(data, list):
            # Old format - likely completed tasks
            return {"status": "legacy_format", "task": None}
            
        tasks = data.get("tasks", [])
        
        # Find active task
        for task in tasks:
            if task.get("status") == "in_progress":
                return {
                    "status": "working",
                    "task": task["task_id"],
                    "title": task.get("title", "Unknown")
                }
        
        # Find pending tasks
        pending = [t for t in tasks if t.get("status") == "pending"]
        if pending:
            return {
                "status": "ready",
                "task": pending[0]["task_id"],
                "title": pending[0].get("title", "Unknown"),
                "pending_count": len(pending)
            }
            
        return {"status": "idle", "task": None}
        
    except Exception as e:
        return {"status": "error", "task": None, "error": str(e)}

def main():
    """Display agent status summary"""
    print(f"\n🚀 AGENT STATUS - {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 50)
    
    agents = ["CA", "CB", "CC", "ARCH"]
    
    for agent in agents:
        status = check_agent_status(agent)
        
        if status["status"] == "working":
            print(f"{agent}: 🔄 Working on {status['task']} - {status['title']}")
        elif status["status"] == "ready":
            print(f"{agent}: ✅ Ready - {status['pending_count']} task(s) pending")
            print(f"      Next: {status['task']} - {status['title']}")
        elif status["status"] == "idle":
            print(f"{agent}: 💤 Idle - No tasks")
        elif status["status"] == "no_outbox":
            print(f"{agent}: ❓ No outbox file")
        else:
            print(f"{agent}: ❌ Error - {status.get('error', 'Unknown')}")
    
    print("\n📝 Sprint Progress")
    print("-" * 20)
    
    # Load sprint progress
    progress_file = Path(".sprint/progress.json")
    if progress_file.exists():
        with open(progress_file) as f:
            progress = json.load(f)
            
        total = progress.get("total_tasks", 0)
        completed = progress.get("completed", 0)
        in_progress = progress.get("in_progress", 0)
        
        if total > 0:
            percent = int((completed / total) * 100)
            print(f"Tasks: {completed}/{total} complete ({percent}%)")
            print(f"In Progress: {in_progress}")
        else:
            print("No sprint tasks defined")
    else:
        print("No sprint progress file")
    
    print()

if __name__ == "__main__":
    main()