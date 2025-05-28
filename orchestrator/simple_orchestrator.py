#!/usr/bin/env python3
"""
Simplest Possible Autonomous Orchestrator
Just 50 lines to enable overnight development!
"""

import time
import subprocess
import json
from datetime import datetime
from pathlib import Path

class SimpleOrchestrator:
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.last_cc_activity = time.time()
        self.last_ca_activity = time.time()
        
    def check_activity(self):
        """Check if agents have been active recently"""
        # Check CC status file
        cc_status = self.root / "CC_LIVE_STATUS.md"
        if cc_status.exists():
            cc_modified = cc_status.stat().st_mtime
            if cc_modified > self.last_cc_activity:
                self.last_cc_activity = cc_modified
                print(f"✅ CC active at {datetime.fromtimestamp(cc_modified)}")
        
        # Check CA status file  
        ca_status = self.root / "CA_LIVE_STATUS.md"
        if ca_status.exists():
            ca_modified = ca_status.stat().st_mtime
            if ca_modified > self.last_ca_activity:
                self.last_ca_activity = ca_modified
                print(f"✅ CA active at {datetime.fromtimestamp(ca_modified)}")
        
        # Check if either agent is stalled (>15 mins)
        current_time = time.time()
        cc_stalled = (current_time - self.last_cc_activity) > 900
        ca_stalled = (current_time - self.last_ca_activity) > 900
        
        return cc_stalled, ca_stalled
    
    def prompt_agent_via_cli(self, agent, message):
        """Prompt agent using your existing CLI interface"""
        # This assumes you have a way to send prompts via CLI
        # Adjust based on your actual setup
        print(f"📨 Prompting {agent}: {message}")
        
        # Example: Use applescript to focus window and type
        # Or: Use API calls if you have them set up
        # Or: Create a prompt file they check
        
        prompt_file = self.root / f"postbox/{agent}/WAKE_UP.md"
        prompt_file.write_text(f"""
# Wake Up {agent}!

Time: {datetime.now()}

{message}

Delete this file after reading and continue with your tasks.
""")
    
    def run(self):
        """Main loop - run this and go to sleep!"""
        print("🌙 Starting Overnight Orchestrator")
        print("💤 You can go to sleep - I'll keep the agents working!")
        
        while True:
            try:
                cc_stalled, ca_stalled = self.check_activity()
                
                if cc_stalled:
                    print("⚠️  CC appears stalled - waking up...")
                    self.prompt_agent_via_cli("CC", 
                        "Check your inbox at /postbox/CC/inbox/ for tasks. Continue autonomous execution.")
                
                if ca_stalled:
                    print("⚠️  CA appears stalled - waking up...")
                    self.prompt_agent_via_cli("CA",
                        "Check your inbox at /postbox/CA/inbox/ for tasks. Continue autonomous execution.")
                
                # Check every 5 minutes
                print(f"😴 Sleeping until {datetime.now().strftime('%H:%M:%S')}...")
                time.sleep(300)
                
            except KeyboardInterrupt:
                print("\n☀️  Good morning! Stopping orchestrator.")
                break

if __name__ == "__main__":
    orchestrator = SimpleOrchestrator()
    orchestrator.run()