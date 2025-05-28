#!/usr/bin/env python3
"""
Quick script to build and test autonomous orchestration
Run this to set up overnight development!
"""

import os
import subprocess

def setup_autonomy():
    print("🚀 Building Autonomous Orchestrator for Overnight Development")
    
    # 1. Create requirements
    requirements = """anthropic>=0.28.0
openai>=1.35.0
watchdog>=4.0.0
schedule>=1.2.0
python-dotenv>=1.0.0
rich>=13.7.0"""
    
    with open("orchestrator/requirements.txt", "w") as f:
        f.write(requirements)
    
    # 2. Create .env template
    env_template = """# API Keys for Autonomous Orchestration
ANTHROPIC_API_KEY=your-claude-api-key
OPENAI_API_KEY=your-openai-api-key

# Optional: Notifications
SLACK_WEBHOOK=your-slack-webhook  # Get progress updates!
"""
    
    with open("orchestrator/.env.template", "w") as f:
        f.write(env_template)
    
    # 3. Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run(["pip", "install", "-r", "orchestrator/requirements.txt"])
    
    print("""
✅ Autonomy Setup Complete!

Next Steps:
1. Copy orchestrator/.env.template to orchestrator/.env
2. Add your API keys
3. Run: python orchestrator/autonomous_orchestrator.py

Expected Results (Overnight):
- 50-100 completed tasks
- Full test coverage
- Working demo
- Performance optimizations
- Complete documentation

Investment: 2 hours setup
Return: 8-10 hours of development EVERY NIGHT!

Ready to let the agents work while you sleep? 🌙
""")

if __name__ == "__main__":
    setup_autonomy()