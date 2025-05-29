#!/usr/bin/env python3
"""
Check Signals Tool - Inter-agent communication signal monitor
Part of TASK-165I: Agent Communication Protocol
"""

import json
import os
import sys
import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

class SignalChecker:
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.signals_dir = self.project_root / ".signals"
        self.active_dir = self.signals_dir / "active"
        self.archive_dir = self.signals_dir / "archive"
        self.signal_log = self.signals_dir / "signal_log.json"
        
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
    
    def get_current_agent(self) -> str:
        """Get current agent ID from environment or config"""
        # Try environment variable first
        agent_id = os.getenv('AGENT_ID')
        
        if agent_id and agent_id in self.valid_agents:
            return agent_id
        
        # Default to CA - this should be configurable
        return "CA"
    
    def load_signal_log(self) -> Dict[str, Any]:
        """Load the master signal log"""
        try:
            with open(self.signal_log, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "version": "1.0",
                "total_signals": 0,
                "agents": {},
                "recent_signals": []
            }
    
    def load_signal(self, signal_file: Path) -> Optional[Dict[str, Any]]:
        """Load a signal from file"""
        try:
            with open(signal_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading signal {signal_file}: {e}", file=sys.stderr)
            return None
    
    def get_signals_for_date(self, date: str) -> List[Dict[str, Any]]:
        """Get all signals for a specific date"""
        date_dir = self.signals_dir / date
        signals = []
        
        if not date_dir.exists():
            return signals
        
        for signal_file in date_dir.glob("*.json"):
            if signal_file.name == "signal_index.json":
                continue
            
            signal = self.load_signal(signal_file)
            if signal:
                signals.append(signal)
        
        return sorted(signals, key=lambda x: x.get("timestamp", ""))
    
    def get_signals_for_agent(self, agent_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get signals for specific agent over last N days"""
        signals = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            date_signals = self.get_signals_for_date(date)
            
            # Filter signals for this agent
            agent_signals = [s for s in date_signals 
                           if s.get("to_agent") == agent_id or 
                              (s.get("to_agent") is None and s.get("from_agent") != agent_id)]
            
            signals.extend(agent_signals)
        
        return sorted(signals, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def get_signals_from_agent(self, agent_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get signals sent by specific agent over last N days"""
        signals = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            date_signals = self.get_signals_for_date(date)
            
            # Filter signals from this agent
            agent_signals = [s for s in date_signals if s.get("from_agent") == agent_id]
            signals.extend(agent_signals)
        
        return sorted(signals, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def get_active_signals(self) -> List[Dict[str, Any]]:
        """Get signals that require responses"""
        signals = []
        
        for signal_file in self.active_dir.glob("*.json"):
            signal = self.load_signal(signal_file)
            if signal:
                # Check if signal has expired
                if self.is_signal_expired(signal):
                    self.archive_expired_signal(signal_file, signal)
                else:
                    signals.append(signal)
        
        return sorted(signals, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def is_signal_expired(self, signal: Dict[str, Any]) -> bool:
        """Check if signal has expired"""
        expires_at = signal.get("expires_at")
        if not expires_at:
            return False
        
        try:
            expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            return datetime.now(expiry_time.tzinfo) > expiry_time
        except:
            return False
    
    def archive_expired_signal(self, signal_file: Path, signal: Dict[str, Any]):
        """Move expired signal to archive"""
        try:
            # Create archive directory for this month
            timestamp = signal.get("timestamp", "")
            if timestamp:
                month = timestamp[:7].replace("-", "")  # YYYYMM
                month_dir = self.archive_dir / month
                month_dir.mkdir(exist_ok=True)
                
                # Move signal to archive
                archive_file = month_dir / signal_file.name
                signal_file.rename(archive_file)
        except Exception as e:
            print(f"Error archiving signal: {e}", file=sys.stderr)
    
    def filter_signals(self, signals: List[Dict[str, Any]], 
                      signal_type: Optional[str] = None,
                      priority: Optional[str] = None,
                      response_required: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Filter signals by criteria"""
        filtered = signals
        
        if signal_type:
            filtered = [s for s in filtered if s.get("signal_type") == signal_type]
        
        if priority:
            filtered = [s for s in filtered if s.get("priority") == priority]
        
        if response_required is not None:
            filtered = [s for s in filtered if s.get("response_required") == response_required]
        
        return filtered
    
    def format_signal(self, signal: Dict[str, Any], verbose: bool = False) -> str:
        """Format signal for display"""
        signal_id = signal.get("signal_id", "UNKNOWN")
        signal_type = signal.get("signal_type", "UNKNOWN")
        from_agent = signal.get("from_agent", "UNKNOWN")
        to_agent = signal.get("to_agent", "ALL")
        priority = signal.get("priority", "MEDIUM")
        message = signal.get("message", "")
        timestamp = signal.get("timestamp", "")
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            time_str = timestamp
        
        # Priority indicator
        priority_icon = {
            "LOW": "🟢",
            "MEDIUM": "🟡", 
            "HIGH": "🟠",
            "CRITICAL": "🔴"
        }.get(priority, "⚪")
        
        # Signal type icon
        type_icon = {
            "READY": "✅",
            "BLOCKED": "🚫",
            "COMPLETED": "🎉",
            "NEEDS_HELP": "🆘",
            "RESOURCE_CLAIM": "🔒",
            "RESOURCE_RELEASE": "🔓",
            "HANDOFF_REQUEST": "🤝",
            "HANDOFF_ACCEPT": "👍"
        }.get(signal_type, "📡")
        
        output = f"{type_icon} {signal_id} [{time_str}]"
        output += f"\n  {signal_type} from {from_agent}"
        if to_agent != "ALL":
            output += f" to {to_agent}"
        output += f" {priority_icon} {priority}"
        
        if signal.get("response_required"):
            output += " ⏰ Response Required"
        
        if signal.get("expires_at"):
            output += " ⏳ Expires"
        
        output += f"\n  💬 {message}"
        
        if verbose and signal.get("context"):
            output += f"\n  📄 Context: {json.dumps(signal['context'], indent=2)}"
        
        return output
    
    def print_signals(self, signals: List[Dict[str, Any]], title: str, verbose: bool = False):
        """Print formatted signals"""
        if not signals:
            print(f"\n{title}: No signals found")
            return
        
        print(f"\n{title} ({len(signals)} signals):")
        print("=" * (len(title) + 20))
        
        for signal in signals:
            print(self.format_signal(signal, verbose))
            print()
    
    def get_signal_stats(self) -> Dict[str, Any]:
        """Get signal statistics"""
        log = self.load_signal_log()
        
        # Count active signals
        active_signals = self.get_active_signals()
        
        # Count signals by type for last 7 days
        signals_7d = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            signals_7d.extend(self.get_signals_for_date(date))
        
        type_counts = {}
        priority_counts = {}
        agent_counts = {}
        
        for signal in signals_7d:
            signal_type = signal.get("signal_type", "UNKNOWN")
            priority = signal.get("priority", "MEDIUM")
            from_agent = signal.get("from_agent", "UNKNOWN")
            
            type_counts[signal_type] = type_counts.get(signal_type, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
            agent_counts[from_agent] = agent_counts.get(from_agent, 0) + 1
        
        return {
            "total_signals": log.get("total_signals", 0),
            "active_signals": len(active_signals),
            "signals_last_7_days": len(signals_7d),
            "signals_by_type": type_counts,
            "signals_by_priority": priority_counts,
            "signals_by_agent": agent_counts,
            "last_signal_time": log.get("last_updated")
        }
    
    def print_stats(self):
        """Print signal statistics"""
        stats = self.get_signal_stats()
        
        print("📊 Signal Statistics")
        print("=" * 40)
        print(f"Total signals sent: {stats['total_signals']}")
        print(f"Active signals: {stats['active_signals']}")
        print(f"Signals last 7 days: {stats['signals_last_7_days']}")
        
        if stats.get("last_signal_time"):
            print(f"Last signal: {stats['last_signal_time']}")
        
        print("\n📈 Signals by Type (7 days):")
        for signal_type, count in sorted(stats['signals_by_type'].items()):
            print(f"  {signal_type}: {count}")
        
        print("\n🎯 Signals by Priority (7 days):")
        for priority, count in sorted(stats['signals_by_priority'].items()):
            print(f"  {priority}: {count}")
        
        print("\n👥 Signals by Agent (7 days):")
        for agent, count in sorted(stats['signals_by_agent'].items()):
            print(f"  {agent}: {count}")
    
    def monitor_signals(self, agent_id: Optional[str] = None, interval: int = 5):
        """Monitor signals in real-time"""
        if not agent_id:
            agent_id = self.get_current_agent()
        
        print(f"🔍 Monitoring signals for {agent_id} (refresh every {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        last_check = datetime.now()
        
        try:
            while True:
                # Check for new signals since last check
                signals = self.get_signals_for_agent(agent_id, days=1)
                new_signals = [s for s in signals 
                             if datetime.fromisoformat(s.get("timestamp", "").replace('Z', '+00:00')) > last_check]
                
                if new_signals:
                    print(f"\n🔔 New signals ({datetime.now().strftime('%H:%M:%S')}):")
                    for signal in new_signals:
                        print(self.format_signal(signal))
                        print()
                
                last_check = datetime.now()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n📡 Signal monitoring stopped")
    
    def check_signals(self, agent_id: Optional[str] = None, from_agent: Optional[str] = None,
                     signal_type: Optional[str] = None, priority: Optional[str] = None,
                     active_only: bool = False, stats_only: bool = False,
                     days: int = 7, verbose: bool = False):
        """Check signals with filtering options"""
        
        if stats_only:
            self.print_stats()
            return
        
        if not agent_id:
            agent_id = self.get_current_agent()
        
        if active_only:
            signals = self.get_active_signals()
            # Filter for current agent
            signals = [s for s in signals 
                      if s.get("to_agent") == agent_id or 
                         (s.get("to_agent") is None and s.get("from_agent") != agent_id)]
            title = f"Active Signals for {agent_id}"
        elif from_agent:
            signals = self.get_signals_from_agent(from_agent, days)
            title = f"Signals from {from_agent} (last {days} days)"
        else:
            signals = self.get_signals_for_agent(agent_id, days)
            title = f"Signals for {agent_id} (last {days} days)"
        
        # Apply filters
        signals = self.filter_signals(signals, signal_type, priority)
        
        self.print_signals(signals, title, verbose)
        
        # Show summary
        if signals and not verbose:
            print(f"\n💡 Use --verbose for detailed context information")
        
        # Show active signals reminder
        if not active_only:
            active_count = len(self.get_active_signals())
            if active_count > 0:
                print(f"\n⚠️  {active_count} active signals require responses (use --active to view)")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Check and monitor inter-agent communication signals",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all signals for current agent
  python3 tools/check_signals.py
  
  # Check signals from specific agent
  python3 tools/check_signals.py --from CA
  
  # Check active signals requiring response
  python3 tools/check_signals.py --active
  
  # Monitor signals in real-time
  python3 tools/check_signals.py --monitor
  
  # Filter by signal type and priority
  python3 tools/check_signals.py --type BLOCKED --priority HIGH
  
  # View statistics
  python3 tools/check_signals.py --stats
        """
    )
    
    # Main options
    parser.add_argument('--agent', help='Agent ID to check signals for')
    parser.add_argument('--from', dest='from_agent', help='Show signals from specific agent')
    parser.add_argument('--type', help='Filter by signal type')
    parser.add_argument('--priority', choices=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
                       help='Filter by priority')
    parser.add_argument('--active', action='store_true',
                       help='Show only active signals requiring response')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days to look back (default: 7)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Show detailed signal information')
    
    # Special modes
    parser.add_argument('--monitor', action='store_true',
                       help='Monitor signals in real-time')
    parser.add_argument('--interval', type=int, default=5,
                       help='Monitoring refresh interval in seconds')
    parser.add_argument('--stats', action='store_true',
                       help='Show signal statistics')
    
    args = parser.parse_args()
    
    checker = SignalChecker()
    
    try:
        if args.monitor:
            checker.monitor_signals(args.agent, args.interval)
        else:
            checker.check_signals(
                agent_id=args.agent,
                from_agent=args.from_agent,
                signal_type=args.type,
                priority=args.priority,
                active_only=args.active,
                stats_only=args.stats,
                days=args.days,
                verbose=args.verbose
            )
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main() 