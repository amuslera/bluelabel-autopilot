#!/usr/bin/env python3
"""
Dashboard Server - Backend API for Agent Status Dashboard
Provides real-time data endpoints for agent monitoring and task tracking
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import threading
import time

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

try:
    from flask import Flask, jsonify, render_template, send_from_directory, request
    from flask_cors import CORS
except ImportError:
    print("Flask and flask-cors required. Install with: pip install flask flask-cors")
    sys.exit(1)

class DashboardServer:
    def __init__(self, port=3000, debug=False):
        self.port = port
        self.debug = debug
        self.project_root = PROJECT_ROOT
        self.postbox_path = self.project_root / "postbox"
        self.sprint_path = self.project_root / ".sprint"
        self.dashboard_path = self.project_root / "apps" / "dashboard"
        
        # Agent configuration
        self.agents = {
            'CA': {'name': 'Cursor AI Frontend', 'role': 'Frontend Development', 'expertise': ['frontend', 'ui', 'react']},
            'CB': {'name': 'Claude Code Backend', 'role': 'Backend Development', 'expertise': ['python', 'backend', 'api']},
            'CC': {'name': 'Claude Code Testing', 'role': 'Quality Assurance', 'expertise': ['testing', 'qa', 'integration']},
            'WA': {'name': 'Windsurf Infrastructure', 'role': 'Infrastructure', 'expertise': ['devops', 'infrastructure', 'automation']},
            'ARCH': {'name': 'Architecture Agent', 'role': 'System Architecture', 'expertise': ['architecture', 'design', 'planning']},
            'BLUE': {'name': 'Blue Analysis', 'role': 'Data Analysis', 'expertise': ['analysis', 'monitoring', 'reporting']}
        }
        
        self.app = self.create_app()
        
    def create_app(self):
        """Create and configure Flask application"""
        app = Flask(__name__, 
                   static_folder=str(self.dashboard_path / "static"),
                   template_folder=str(self.dashboard_path))
        
        # Enable CORS for all routes
        CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
        
        # Register routes
        self.register_routes(app)
        
        return app
    
    def register_routes(self, app):
        """Register all application routes"""
        
        @app.route('/')
        def index():
            """Serve the main dashboard"""
            return send_from_directory(str(self.dashboard_path), 'index.html')
        
        @app.route('/static/<path:filename>')
        def static_files(filename):
            """Serve static files"""
            return send_from_directory(str(self.dashboard_path / "static"), filename)
        
        @app.route('/api/system/overview')
        def system_overview():
            """Get system overview statistics"""
            try:
                data = self.get_system_overview()
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/agents/<agent_id>/status')
        def agent_status(agent_id):
            """Get specific agent status"""
            try:
                if agent_id not in self.agents:
                    return jsonify({'error': 'Agent not found'}), 404
                
                data = self.get_agent_status(agent_id)
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/agents/status')
        def all_agents_status():
            """Get status for all agents"""
            try:
                data = {}
                for agent_id in self.agents:
                    data[agent_id] = self.get_agent_status(agent_id)
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/tasks/history')
        def task_history():
            """Get recent task history"""
            try:
                limit = request.args.get('limit', 50, type=int)
                agent_filter = request.args.get('agent', None)
                
                data = self.get_task_history(limit=limit, agent_filter=agent_filter)
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/metrics/performance')
        def performance_metrics():
            """Get performance metrics"""
            try:
                data = self.get_performance_metrics()
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/sprint/progress')
        def sprint_progress():
            """Get current sprint progress"""
            try:
                data = self.get_sprint_progress()
                return jsonify(data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/health')
        def health_check():
            """Health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'version': '1.0.0'
            })
    
    def get_system_overview(self) -> Dict[str, Any]:
        """Get system overview statistics"""
        total_tasks = 0
        completed_tasks = 0
        in_progress_tasks = 0
        pending_tasks = 0
        
        # Aggregate data from all agents
        for agent_id in self.agents:
            agent_data = self.load_agent_outbox(agent_id)
            if agent_data and 'tasks' in agent_data:
                for task in agent_data['tasks']:
                    total_tasks += 1
                    status = task.get('status', 'unknown')
                    if status == 'completed':
                        completed_tasks += 1
                    elif status == 'in_progress':
                        in_progress_tasks += 1
                    elif status == 'pending':
                        pending_tasks += 1
        
        # Calculate completion rate
        completion_rate = 0
        if total_tasks > 0:
            completion_rate = round((completed_tasks / total_tasks) * 100, 1)
        
        return {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'in_progress_tasks': in_progress_tasks,
            'pending_tasks': pending_tasks,
            'completion_rate': completion_rate,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """Get status for a specific agent"""
        agent_data = self.load_agent_outbox(agent_id)
        
        if not agent_data:
            return {
                'agent_id': agent_id,
                'status': 'offline',
                'error': 'No data available'
            }
        
        # Analyze tasks to determine status
        tasks = agent_data.get('tasks', [])
        
        # Count tasks by status
        pending_tasks = [t for t in tasks if t.get('status') == 'pending']
        in_progress_tasks = [t for t in tasks if t.get('status') == 'in_progress']
        completed_tasks = [t for t in tasks if t.get('status') == 'completed']
        
        # Determine agent status
        if in_progress_tasks:
            status = 'working'
            current_task = in_progress_tasks[0].get('task_id')
        elif pending_tasks:
            status = 'ready'
            current_task = None
        else:
            status = 'idle'
            current_task = None
        
        # Calculate metrics
        total_tasks = len(tasks)
        success_rate = 0
        if total_tasks > 0:
            success_rate = round((len(completed_tasks) / total_tasks) * 100, 1)
        
        # Calculate average duration
        avg_duration = self.calculate_average_duration(completed_tasks)
        
        return {
            'agent_id': agent_id,
            'agent_name': self.agents[agent_id]['name'],
            'status': status,
            'current_task': current_task,
            'pending_tasks': len(pending_tasks),
            'in_progress_tasks': len(in_progress_tasks),
            'completed_tasks': len(completed_tasks),
            'total_tasks': total_tasks,
            'success_rate': success_rate,
            'avg_duration': avg_duration,
            'last_updated': datetime.utcnow().isoformat()
        }
    
    def get_task_history(self, limit: int = 50, agent_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get recent task history across all agents"""
        all_tasks = []
        
        # Collect tasks from all agents
        for agent_id in self.agents:
            if agent_filter and agent_id != agent_filter:
                continue
                
            agent_data = self.load_agent_outbox(agent_id)
            if not agent_data or 'tasks' not in agent_data:
                continue
            
            for task in agent_data['tasks']:
                task_entry = {
                    'id': task.get('task_id', 'Unknown'),
                    'title': task.get('title', 'Unknown Task'),
                    'description': task.get('description', ''),
                    'agent': agent_id,
                    'agent_name': self.agents[agent_id]['name'],
                    'status': task.get('status', 'unknown'),
                    'priority': task.get('priority', 'MEDIUM'),
                    'estimated_hours': task.get('estimated_hours', 0),
                    'created_at': task.get('created_at'),
                    'started_at': task.get('started_at'),
                    'completed_at': task.get('completed_at'),
                }
                
                # Calculate duration if completed
                if task_entry['completed_at'] and task_entry['created_at']:
                    duration = self.calculate_task_duration(
                        task_entry['created_at'], 
                        task_entry['completed_at']
                    )
                    task_entry['duration'] = duration
                
                all_tasks.append(task_entry)
        
        # Sort by most recent first (use completed_at if available, otherwise created_at)
        def sort_key(task):
            timestamp = task.get('completed_at') or task.get('started_at') or task.get('created_at')
            if timestamp:
                try:
                    return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    return datetime.min
            return datetime.min
        
        all_tasks.sort(key=sort_key, reverse=True)
        
        # Apply limit
        limited_tasks = all_tasks[:limit]
        
        return {
            'tasks': limited_tasks,
            'total_count': len(all_tasks),
            'filtered_count': len(limited_tasks),
            'agent_filter': agent_filter
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        all_tasks = []
        
        # Collect all completed tasks
        for agent_id in self.agents:
            agent_data = self.load_agent_outbox(agent_id)
            if not agent_data or 'tasks' not in agent_data:
                continue
            
            completed_tasks = [t for t in agent_data['tasks'] if t.get('status') == 'completed']
            all_tasks.extend(completed_tasks)
        
        # Calculate metrics
        total_completed = len(all_tasks)
        avg_duration = self.calculate_average_duration(all_tasks)
        
        # Calculate success rate (assuming completed tasks are successful)
        total_tasks = 0
        for agent_id in self.agents:
            agent_data = self.load_agent_outbox(agent_id)
            if agent_data and 'tasks' in agent_data:
                total_tasks += len(agent_data['tasks'])
        
        success_rate = 0
        if total_tasks > 0:
            success_rate = round((total_completed / total_tasks) * 100, 1)
        
        # Count tasks this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        tasks_this_week = 0
        
        for task in all_tasks:
            completed_at = task.get('completed_at')
            if completed_at:
                try:
                    completed_date = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                    if completed_date >= week_ago:
                        tasks_this_week += 1
                except:
                    pass
        
        # Count active agents (agents with pending or in-progress tasks)
        active_agents = 0
        for agent_id in self.agents:
            agent_data = self.load_agent_outbox(agent_id)
            if agent_data and 'tasks' in agent_data:
                has_active_tasks = any(
                    t.get('status') in ['pending', 'in_progress'] 
                    for t in agent_data['tasks']
                )
                if has_active_tasks:
                    active_agents += 1
        
        return {
            'avg_duration': avg_duration,
            'success_rate': success_rate,
            'tasks_week': tasks_this_week,
            'active_agents': active_agents,
            'total_completed': total_completed,
            'total_tasks': total_tasks
        }
    
    def get_sprint_progress(self) -> Dict[str, Any]:
        """Get current sprint progress"""
        progress_file = self.sprint_path / "progress.json"
        
        if not progress_file.exists():
            return {
                'sprint_id': 'No active sprint',
                'total_tasks': 0,
                'completed': 0,
                'in_progress': 0,
                'completion_rate': 0
            }
        
        try:
            with open(progress_file, 'r') as f:
                data = json.load(f)
            
            # Calculate completion rate
            total = data.get('total_tasks', 0)
            completed = data.get('completed', 0)
            completion_rate = 0
            if total > 0:
                completion_rate = round((completed / total) * 100, 1)
            
            data['completion_rate'] = completion_rate
            return data
            
        except Exception as e:
            print(f"Error reading sprint progress: {e}")
            return {
                'error': 'Failed to load sprint progress',
                'total_tasks': 0,
                'completed': 0,
                'in_progress': 0,
                'completion_rate': 0
            }
    
    def load_agent_outbox(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Load agent outbox data"""
        outbox_file = self.postbox_path / agent_id / "outbox.json"
        
        if not outbox_file.exists():
            return None
        
        try:
            with open(outbox_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading outbox for {agent_id}: {e}")
            return None
    
    def calculate_average_duration(self, tasks: List[Dict[str, Any]]) -> float:
        """Calculate average task duration in hours"""
        durations = []
        
        for task in tasks:
            created_at = task.get('created_at')
            completed_at = task.get('completed_at')
            
            if created_at and completed_at:
                duration = self.calculate_task_duration(created_at, completed_at)
                if duration:
                    durations.append(float(duration.rstrip('h')))
        
        if not durations:
            return 0.0
        
        return round(sum(durations) / len(durations), 1)
    
    def calculate_task_duration(self, created_at: str, completed_at: str) -> Optional[str]:
        """Calculate duration between two timestamps"""
        try:
            start = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            end = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
            
            duration = end - start
            hours = duration.total_seconds() / 3600
            return f"{hours:.1f}h"
            
        except Exception as e:
            print(f"Error calculating duration: {e}")
            return None
    
    def run(self, host='localhost'):
        """Run the dashboard server"""
        print(f"""
🌐 Agent Status Dashboard Server
================================
Server: http://{host}:{self.port}
Dashboard: http://{host}:{self.port}
API Base: http://{host}:{self.port}/api
Health Check: http://{host}:{self.port}/api/health

Press Ctrl+C to stop
        """)
        
        try:
            self.app.run(
                host=host,
                port=self.port,
                debug=self.debug,
                threaded=True
            )
        except KeyboardInterrupt:
            print("\n🛑 Server stopped by user")
        except Exception as e:
            print(f"❌ Server error: {e}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Agent Status Dashboard Server')
    parser.add_argument('--port', type=int, default=3000, help='Server port (default: 3000)')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Ensure required directories exist
    dashboard_path = PROJECT_ROOT / "apps" / "dashboard"
    if not dashboard_path.exists():
        print(f"❌ Dashboard files not found at {dashboard_path}")
        print("Please ensure the dashboard files are properly installed.")
        sys.exit(1)
    
    # Create and run server
    server = DashboardServer(port=args.port, debug=args.debug)
    server.run(host=args.host)

if __name__ == '__main__':
    main() 