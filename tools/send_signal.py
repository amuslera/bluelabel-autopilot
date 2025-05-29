#!/usr/bin/env python3
"""
Send Signal Tool - Inter-agent communication signal creator
Part of TASK-165I: Agent Communication Protocol
"""

import json
import os
import sys
import argparse
import random
import string
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

class SignalSender:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.signals_dir = self.project_root / ".signals"
        self.active_dir = self.signals_dir / "active"
        self.archive_dir = self.signals_dir / "archive"
        self.signal_log = self.signals_dir / "signal_log.json"
        
        # Valid signal types
        self.valid_signal_types = [
            "READY", "BLOCKED", "COMPLETED", "NEEDS_HELP", 
            "RESOURCE_CLAIM", "RESOURCE_RELEASE", 
            "HANDOFF_REQUEST", "HANDOFF_ACCEPT"
        ]
        
        # Agent IDs
        self.valid_agents = ["CA", "CB", "CC", "WA", "ARCH", "BLUE"]
        
        # Ensure directories exist
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create signal directories if they don't exist"""
        self.signals_dir.mkdir(exist_ok=True)
        self.active_dir.mkdir(exist_ok=True)
        self.archive_dir.mkdir(exist_ok=True)
        
        # Create today's signal directory
        today = datetime.now().strftime("%Y%m%d")
        today_dir = self.signals_dir / today
        today_dir.mkdir(exist_ok=True)
        
        # Initialize signal log if it doesn't exist
        if not self.signal_log.exists():
            self.initialize_signal_log()
    
    def initialize_signal_log(self):
        """Initialize the master signal log"""
        initial_log = {
            "version": "1.0",
            "created": datetime.utcnow().isoformat() + "Z",
            "total_signals": 0,
            "last_signal_id": None,
            "agents": {agent: {"signals_sent": 0, "last_activity": None} for agent in self.valid_agents}
        }
        
        with open(self.signal_log, 'w') as f:
            json.dump(initial_log, f, indent=2)
    
    def generate_signal_id(self) -> str:
        """Generate unique signal ID"""
        now = datetime.now()
        date_part = now.strftime("%Y%m%d")
        time_part = now.strftime("%H%M%S")
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        
        return f"SIG-{date_part}-{time_part}-{random_part}"
    
    def validate_agent(self, agent_id: str) -> bool:
        """Validate agent ID"""
        return agent_id in self.valid_agents
    
    def validate_signal_type(self, signal_type: str) -> bool:
        """Validate signal type"""
        return signal_type in self.valid_signal_types
    
    def parse_context(self, context_str: Optional[str]) -> Dict[str, Any]:
        """Parse context string to JSON"""
        if not context_str:
            return {}
        
        try:
            return json.loads(context_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in context: {e}")
    
    def get_current_agent(self) -> str:
        """Get current agent ID from environment or config"""
        # Try environment variable first
        agent_id = os.getenv('AGENT_ID')
        
        if agent_id and self.validate_agent(agent_id):
            return agent_id
        
        # Try to infer from hostname or other context
        # For now, default to CA - this should be configurable
        return "CA"
    
    def create_signal(self, signal_type: str, message: str, to_agent: Optional[str] = None,
                     context: Optional[Dict[str, Any]] = None, priority: str = "MEDIUM",
                     response_required: bool = False, expires_in_hours: Optional[int] = None) -> Dict[str, Any]:
        """Create a signal object"""
        
        # Validate inputs
        if not self.validate_signal_type(signal_type):
            raise ValueError(f"Invalid signal type: {signal_type}")
        
        from_agent = self.get_current_agent()
        
        if to_agent and not self.validate_agent(to_agent):
            raise ValueError(f"Invalid target agent: {to_agent}")
        
        if priority not in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]:
            raise ValueError(f"Invalid priority: {priority}")
        
        # Generate signal
        signal_id = self.generate_signal_id()
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        signal = {
            "signal_id": signal_id,
            "signal_type": signal_type,
            "timestamp": timestamp,
            "from_agent": from_agent,
            "message": message,
            "priority": priority,
            "response_required": response_required
        }
        
        # Add optional fields
        if to_agent:
            signal["to_agent"] = to_agent
        
        if context:
            signal["context"] = context
        
        if expires_in_hours:
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            signal["expires_at"] = expires_at.isoformat() + "Z"
        
        # Set response_required based on signal type
        if signal_type in ["NEEDS_HELP", "HANDOFF_REQUEST"]:
            signal["response_required"] = True
        
        return signal
    
    def save_signal(self, signal: Dict[str, Any]) -> Path:
        """Save signal to appropriate locations"""
        signal_id = signal["signal_id"]
        signal_type = signal["signal_type"]
        from_agent = signal["from_agent"]
        to_agent = signal.get("to_agent", "ALL")
        
        # Save to daily directory
        today = datetime.now().strftime("%Y%m%d")
        today_dir = self.signals_dir / today
        
        # Create filename: timestamp_from_to_type.json
        timestamp = datetime.now().strftime("%H%M%S")
        filename = f"{timestamp}_{from_agent}_{to_agent}_{signal_type}.json"
        daily_file = today_dir / filename
        
        with open(daily_file, 'w') as f:
            json.dump(signal, f, indent=2)
        
        # Save to active directory if response required
        if signal.get("response_required", False):
            active_file = self.active_dir / f"{signal_id}.json"
            with open(active_file, 'w') as f:
                json.dump(signal, f, indent=2)
        
        # Update signal log
        self.update_signal_log(signal)
        
        # Update daily index
        self.update_daily_index(today_dir, signal)
        
        return daily_file
    
    def update_signal_log(self, signal: Dict[str, Any]):
        """Update the master signal log"""
        try:
            with open(self.signal_log, 'r') as f:
                log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            log = {
                "version": "1.0",
                "created": datetime.utcnow().isoformat() + "Z",
                "total_signals": 0,
                "agents": {agent: {"signals_sent": 0, "last_activity": None} for agent in self.valid_agents}
            }
        
        # Update log
        log["total_signals"] += 1
        log["last_signal_id"] = signal["signal_id"]
        log["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        from_agent = signal["from_agent"]
        if from_agent in log["agents"]:
            log["agents"][from_agent]["signals_sent"] += 1
            log["agents"][from_agent]["last_activity"] = signal["timestamp"]
        
        # Add signal summary to log
        if "recent_signals" not in log:
            log["recent_signals"] = []
        
        signal_summary = {
            "signal_id": signal["signal_id"],
            "type": signal["signal_type"],
            "from": signal["from_agent"],
            "to": signal.get("to_agent"),
            "timestamp": signal["timestamp"],
            "priority": signal["priority"]
        }
        
        log["recent_signals"].append(signal_summary)
        
        # Keep only last 100 recent signals
        log["recent_signals"] = log["recent_signals"][-100:]
        
        with open(self.signal_log, 'w') as f:
            json.dump(log, f, indent=2)
    
    def update_daily_index(self, daily_dir: Path, signal: Dict[str, Any]):
        """Update daily signal index"""
        index_file = daily_dir / "signal_index.json"
        
        try:
            with open(index_file, 'r') as f:
                index = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            index = {
                "date": daily_dir.name,
                "total_signals": 0,
                "signals_by_type": {},
                "signals_by_agent": {},
                "signals": []
            }
        
        # Update index
        index["total_signals"] += 1
        
        signal_type = signal["signal_type"]
        index["signals_by_type"][signal_type] = index["signals_by_type"].get(signal_type, 0) + 1
        
        from_agent = signal["from_agent"]
        index["signals_by_agent"][from_agent] = index["signals_by_agent"].get(from_agent, 0) + 1
        
        # Add signal reference
        signal_ref = {
            "signal_id": signal["signal_id"],
            "type": signal_type,
            "from": from_agent,
            "to": signal.get("to_agent"),
            "timestamp": signal["timestamp"],
            "priority": signal["priority"],
            "response_required": signal.get("response_required", False)
        }
        
        index["signals"].append(signal_ref)
        index["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def send_signal(self, signal_type: str, message: str, to_agent: Optional[str] = None,
                   context: Optional[str] = None, priority: str = "MEDIUM",
                   response_required: bool = False, expires_in_hours: Optional[int] = None,
                   verbose: bool = False) -> str:
        """Send a signal and return the signal ID"""
        
        # Parse context
        context_obj = self.parse_context(context) if context else {}
        
        # Create signal
        signal = self.create_signal(
            signal_type=signal_type,
            message=message,
            to_agent=to_agent,
            context=context_obj,
            priority=priority,
            response_required=response_required,
            expires_in_hours=expires_in_hours
        )
        
        # Save signal
        signal_file = self.save_signal(signal)
        
        if verbose:
            print(f"✓ Signal created: {signal['signal_id']}")
            print(f"  Type: {signal_type}")
            print(f"  From: {signal['from_agent']}")
            if to_agent:
                print(f"  To: {to_agent}")
            print(f"  Priority: {priority}")
            print(f"  File: {signal_file}")
            if signal.get("response_required"):
                print(f"  Response required: Yes")
            print(f"  Message: {message}")
        
        return signal["signal_id"]
    
    def list_signal_types(self):
        """List available signal types with descriptions"""
        descriptions = {
            "READY": "Agent is ready for new tasks or dependencies resolved",
            "BLOCKED": "Agent is blocked waiting for dependencies or resources",
            "COMPLETED": "Task completion announcement with deliverables",
            "NEEDS_HELP": "Request assistance from other agents",
            "RESOURCE_CLAIM": "Claim exclusive access to shared resources",
            "RESOURCE_RELEASE": "Release claimed resources for other agents",
            "HANDOFF_REQUEST": "Request task handoff to another agent",
            "HANDOFF_ACCEPT": "Confirm acceptance of task handoff"
        }
        
        print("Available Signal Types:")
        print("=" * 50)
        for signal_type in self.valid_signal_types:
            print(f"{signal_type:18} - {descriptions[signal_type]}")
    
    def send_completion_signal(self, task_id: str, deliverables: list = None, 
                              follow_up: bool = False):
        """Send a task completion signal with standard format"""
        context = {
            "completed_task": task_id,
            "deliverables": deliverables or [],
            "follow_up_available": follow_up
        }
        
        message = f"Task {task_id} completed successfully"
        if deliverables:
            message += f" with {len(deliverables)} deliverables"
        
        return self.send_signal(
            signal_type="COMPLETED",
            message=message,
            context=json.dumps(context),
            priority="LOW"
        )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Send inter-agent communication signals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Send ready signal
  python3 tools/send_signal.py --type READY --message "Available for new tasks"
  
  # Send blocked signal to specific agent
  python3 tools/send_signal.py --type BLOCKED --to CB --message "Waiting for API" \\
    --context '{"blocked_task": "TASK-165F", "waiting_for": "TASK-165E"}'
  
  # Send completion signal
  python3 tools/send_signal.py --type COMPLETED --message "Dashboard complete" \\
    --context '{"task_id": "TASK-165G", "deliverables": ["UI", "API", "docs"]}'
  
  # Send help request with high priority
  python3 tools/send_signal.py --type NEEDS_HELP --message "Database issue" \\
    --priority HIGH --response-required
        """
    )
    
    # Main arguments
    parser.add_argument('--type', required=True, help='Signal type')
    parser.add_argument('--message', required=True, help='Signal message')
    parser.add_argument('--to', help='Target agent ID')
    parser.add_argument('--context', help='JSON context object')
    parser.add_argument('--priority', default='MEDIUM', 
                       choices=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
                       help='Signal priority')
    parser.add_argument('--response-required', action='store_true',
                       help='Signal requires response')
    parser.add_argument('--expires-in', type=int,
                       help='Signal expires in N hours')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    # Utility commands
    parser.add_argument('--list-types', action='store_true',
                       help='List available signal types')
    
    # Task completion helper
    parser.add_argument('--complete-task', help='Send completion signal for task ID')
    parser.add_argument('--deliverables', nargs='*', help='Task deliverables')
    parser.add_argument('--follow-up', action='store_true',
                       help='Follow-up work available')
    
    args = parser.parse_args()
    
    sender = SignalSender()
    
    try:
        if args.list_types:
            sender.list_signal_types()
            return
        
        if args.complete_task:
            signal_id = sender.send_completion_signal(
                task_id=args.complete_task,
                deliverables=args.deliverables,
                follow_up=args.follow_up
            )
            print(f"✓ Completion signal sent: {signal_id}")
            return
        
        # Send signal
        signal_id = sender.send_signal(
            signal_type=args.type,
            message=args.message,
            to_agent=args.to,
            context=args.context,
            priority=args.priority,
            response_required=args.response_required,
            expires_in_hours=args.expires_in,
            verbose=args.verbose
        )
        
        if not args.verbose:
            print(f"✓ Signal sent: {signal_id}")
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 