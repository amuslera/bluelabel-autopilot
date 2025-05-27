#!/usr/bin/env python3
"""
Auto-Summary Generator for Agent Activity Logs
Generates weekly-style reports from task logs and outbox entries.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class SummaryGenerator:
    def __init__(self, task_cards_path: str, outbox_path: str, output_path: str):
        self.task_cards_path = task_cards_path
        self.outbox_path = outbox_path
        self.output_path = output_path
        self.tasks: List[Dict] = []
        self.milestones: List[str] = []

    def read_task_cards(self) -> None:
        """Read and parse TASK_CARDS.md for recent tasks."""
        with open(self.task_cards_path, 'r') as f:
            content = f.read()
            
        # Extract task blocks
        task_blocks = content.split('### TASK-')[1:]
        for block in task_blocks:
            task_id = f"TASK-{block.split('\n')[0]}"
            lines = block.split('\n')
            
            task = {
                'id': task_id,
                'agent': '',
                'status': '',
                'date': '',
                'branch': '',
                'objective': '',
                'actions': [],
                'outcome': ''
            }
            
            for line in lines:
                if line.startswith('**Agent**:'):
                    task['agent'] = line.split('**Agent**:')[1].strip()
                elif line.startswith('**Status**:'):
                    task['status'] = line.split('**Status**:')[1].strip()
                elif line.startswith('**Date**:'):
                    task['date'] = line.split('**Date**:')[1].strip()
                elif line.startswith('**Branch**:'):
                    task['branch'] = line.split('**Branch**:')[1].strip()
                elif line.startswith('**Objective**'):
                    task['objective'] = lines[lines.index(line) + 1].strip()
                elif line.startswith('**Actions Taken**'):
                    action_lines = []
                    idx = lines.index(line) + 1
                    while idx < len(lines) and not lines[idx].startswith('**'):
                        if lines[idx].strip().startswith('- '):
                            action_lines.append(lines[idx].strip()[2:])
                        idx += 1
                    task['actions'] = action_lines
                elif line.startswith('**Outcome**'):
                    task['outcome'] = lines[lines.index(line) + 1].strip()
            
            self.tasks.append(task)

    def read_outbox(self) -> None:
        """Read and parse outbox.json for additional task details."""
        with open(self.outbox_path, 'r') as f:
            content = f.read()
            # Handle multiple JSON objects
            reports = []
            for obj in content.split('}\n{'):
                if obj.startswith('{'):
                    reports.append(json.loads(obj))
                else:
                    reports.append(json.loads('{' + obj))
            
            # Update tasks with outbox details
            for report in reports:
                task_id = report.get('task_id')
                if task_id:
                    for task in self.tasks:
                        if task['id'] == task_id:
                            task['summary'] = report.get('summary', '')
                            task['files_modified'] = report.get('files_modified', [])
                            task['files_created'] = report.get('files_created', [])
                            break

    def identify_milestones(self) -> None:
        """Identify system-level milestones from tasks."""
        milestone_keywords = ['reboot', 'merge', 'release', 'phase', 'sprint']
        for task in self.tasks:
            if any(keyword in task['objective'].lower() for keyword in milestone_keywords):
                self.milestones.append(f"{task['id']}: {task['objective']}")

    def generate_summary(self) -> str:
        """Generate the weekly summary report."""
        # Group tasks by agent
        agent_tasks: Dict[str, List[Dict]] = {
            'CA': [],
            'CC': [],
            'ARCH': []
        }
        
        for task in self.tasks:
            if task['agent'] in agent_tasks:
                agent_tasks[task['agent']].append(task)

        # Generate markdown
        now = datetime.now()
        summary = f"""# Weekly Agent Activity Summary
Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}

## System Milestones
{chr(10).join(f"- {milestone}" for milestone in self.milestones)}

"""

        # Add agent sections
        for agent, tasks in agent_tasks.items():
            summary += f"\n## {agent} Activity\n"
            for task in tasks:
                summary += f"\n### {task['id']}: {task['objective']}\n"
                summary += f"- Status: {task['status']}\n"
                summary += f"- Date: {task['date']}\n"
                if 'summary' in task:
                    summary += f"- Summary: {task['summary']}\n"
                if task['actions']:
                    summary += "- Actions:\n"
                    for action in task['actions']:
                        summary += f"  - {action}\n"
                if task['outcome']:
                    summary += f"- Outcome: {task['outcome']}\n"

        return summary

    def write_summary(self) -> None:
        """Write the summary to the output file."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w') as f:
            f.write(self.generate_summary())

def main():
    # Initialize paths
    base_dir = Path(__file__).parent.parent
    task_cards_path = base_dir / 'TASK_CARDS.md'
    outbox_path = base_dir / 'postbox' / 'CA' / 'outbox.json'
    output_path = base_dir / 'reports' / 'weekly_summary.md'

    # Generate summary
    generator = SummaryGenerator(
        str(task_cards_path),
        str(outbox_path),
        str(output_path)
    )
    
    generator.read_task_cards()
    generator.read_outbox()
    generator.identify_milestones()
    generator.write_summary()

if __name__ == '__main__':
    main() 