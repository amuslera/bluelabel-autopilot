#!/usr/bin/env python3
"""
Workflow Management CLI Tool

Command-line interface for managing workflows: start, stop, inspect, debug,
and monitor workflow execution in the advanced orchestration system.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import textwrap

# Import workflow components
sys.path.append(str(Path(__file__).parent.parent))
from workflow.orchestration_engine import WorkflowOrchestrator, WorkflowStatus
from workflow.workflow_monitor import WorkflowMonitor
from workflow.migration_manager import WorkflowMigrationManager


class WorkflowCLI:
    """Command-line interface for workflow management"""
    
    def __init__(self):
        self.orchestrator = WorkflowOrchestrator()
        self.monitor = WorkflowMonitor()
        self.migration_manager = WorkflowMigrationManager()
        
    async def create_workflow(self, template_path: str, parameters: Dict[str, Any] = None) -> str:
        """Create workflow from template"""
        template_file = Path(template_path)
        
        if not template_file.exists():
            # Try in templates directory
            template_file = self.orchestrator.templates_dir / template_path
            if not template_file.exists():
                template_file = self.orchestrator.templates_dir / f"{template_path}.json"
                
        if not template_file.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        # Load template
        with open(template_file, 'r') as f:
            template_data = json.load(f)
            
        # Apply parameters if provided
        if parameters:
            template_data = self._apply_template_parameters(template_data, parameters)
            
        # Create workflow
        workflow_id = await self.orchestrator.create_workflow(template_data)
        return workflow_id
        
    def _apply_template_parameters(self, template_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Apply parameters to template"""
        # Simple string replacement for now - could be enhanced with proper templating
        template_str = json.dumps(template_data)
        
        for key, value in parameters.items():
            placeholder = f"{{{{{key}}}}}"
            template_str = template_str.replace(placeholder, str(value))
            
        return json.loads(template_str)
        
    async def start_workflow(self, workflow_id: str) -> bool:
        """Start workflow execution"""
        return await self.orchestrator.start_workflow(workflow_id)
        
    async def stop_workflow(self, workflow_id: str, force: bool = False) -> bool:
        """Stop workflow execution"""
        if force:
            return await self.orchestrator.cancel_workflow(workflow_id)
        else:
            return await self.orchestrator.pause_workflow(workflow_id)
            
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume paused workflow"""
        return await self.orchestrator.resume_workflow(workflow_id)
        
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        return self.orchestrator.get_workflow_status(workflow_id)
        
    def list_workflows(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """List workflows"""
        return self.orchestrator.list_workflows(status_filter)
        
    async def inspect_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Inspect workflow details"""
        workflow = await self.orchestrator._load_workflow(workflow_id)
        if workflow:
            # Convert to dict for display
            workflow_dict = {
                "id": workflow.id,
                "name": workflow.name,
                "version": workflow.version,
                "description": workflow.description,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "error": workflow.error,
                "task_count": len(workflow.tasks),
                "completed_tasks": sum(1 for t in workflow.tasks.values() if t.status.value == 'completed'),
                "failed_tasks": sum(1 for t in workflow.tasks.values() if t.status.value == 'failed'),
                "running_tasks": sum(1 for t in workflow.tasks.values() if t.status.value == 'running'),
                "metadata": workflow.metadata
            }
            return workflow_dict
        return None
        
    async def debug_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Debug workflow execution"""
        workflow = await self.orchestrator._load_workflow(workflow_id)
        if not workflow:
            return {"error": "Workflow not found"}
            
        debug_info = {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "execution_history": workflow.execution_history[-20:],  # Last 20 events
            "task_details": {},
            "health_check": None,
            "suggestions": []
        }
        
        # Analyze tasks
        for task_id, task in workflow.tasks.items():
            debug_info["task_details"][task_id] = {
                "status": task.status.value,
                "dependencies": task.dependencies,
                "error": task.error,
                "retry_count": len([h for h in workflow.execution_history if h.get('task_id') == task_id and h.get('action') == 'error']),
                "execution_time": None
            }
            
            # Calculate execution time
            if task.started_at and task.completed_at:
                execution_time = (task.completed_at - task.started_at).total_seconds()
                debug_info["task_details"][task_id]["execution_time"] = execution_time
                
        # Get health check
        health = self.monitor.get_workflow_health(workflow_id)
        if health:
            debug_info["health_check"] = {
                "health_score": health.health_score,
                "issues": health.issues,
                "metrics": health.metrics
            }
            
        # Generate suggestions
        if workflow.status == WorkflowStatus.FAILED:
            debug_info["suggestions"].append("Check task error messages and dependencies")
            
        if any(t.error for t in workflow.tasks.values()):
            debug_info["suggestions"].append("Review failed task logs and retry configuration")
            
        failed_tasks = [t for t in workflow.tasks.values() if t.status.value == 'failed']
        if failed_tasks:
            debug_info["suggestions"].append(f"Consider rollback to previous checkpoint for failed tasks: {[t.id for t in failed_tasks]}")
            
        return debug_info
        
    async def rollback_workflow(self, workflow_id: str, checkpoint_id: Optional[str] = None) -> bool:
        """Rollback workflow to checkpoint"""
        return await self.orchestrator.rollback_workflow(workflow_id, checkpoint_id)
        
    def list_templates(self) -> List[Dict[str, Any]]:
        """List available workflow templates"""
        templates = []
        
        for template_file in self.orchestrator.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template_data = json.load(f)
                    
                templates.append({
                    "filename": template_file.name,
                    "name": template_data.get('name', 'Unknown'),
                    "version": template_data.get('version', '1.0.0'),
                    "description": template_data.get('description', ''),
                    "template_type": template_data.get('metadata', {}).get('template_type', 'custom'),
                    "use_cases": template_data.get('metadata', {}).get('use_cases', [])
                })
                
            except Exception as e:
                templates.append({
                    "filename": template_file.name,
                    "error": str(e)
                })
                
        return templates
        
    async def monitor_workflow(self, workflow_id: str, interval: int = 5, duration: int = 300):
        """Monitor workflow execution in real-time"""
        start_time = datetime.now()
        end_time = start_time.timestamp() + duration
        
        print(f"Monitoring workflow {workflow_id} for {duration} seconds...")
        print("Press Ctrl+C to stop early\n")
        
        try:
            while datetime.now().timestamp() < end_time:
                status = self.get_workflow_status(workflow_id)
                if not status:
                    print("❌ Workflow not found")
                    break
                    
                # Clear screen and show status
                print(f"\r⏰ {datetime.now().strftime('%H:%M:%S')} | "
                      f"Status: {status['status']} | "
                      f"Progress: {status['progress']['percentage']:.1f}% "
                      f"({status['progress']['completed']}/{status['progress']['total']})", 
                      end='', flush=True)
                
                # Check if workflow completed
                if status['status'] in ['completed', 'failed', 'cancelled']:
                    print(f"\n\n🏁 Workflow {status['status']}")
                    break
                    
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped")
            
    def format_workflow_status(self, status: Dict[str, Any]) -> str:
        """Format workflow status for display"""
        lines = []
        lines.append(f"Workflow: {status['name']} ({status['workflow_id']})")
        lines.append(f"Status: {status['status']}")
        lines.append(f"Progress: {status['progress']['completed']}/{status['progress']['total']} tasks ({status['progress']['percentage']:.1f}%)")
        
        if status['started_at']:
            lines.append(f"Started: {status['started_at']}")
            
        if status['completed_at']:
            lines.append(f"Completed: {status['completed_at']}")
            
        if status['error']:
            lines.append(f"Error: {status['error']}")
            
        return '\n'.join(lines)


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Workflow Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          # List all workflows
          workflow_cli.py list
          
          # Create workflow from template
          workflow_cli.py create approval_chain --param level1_approver=alice --param level2_approver=bob
          
          # Start workflow
          workflow_cli.py start workflow-123
          
          # Monitor workflow execution
          workflow_cli.py monitor workflow-123 --duration 600
          
          # Debug failed workflow
          workflow_cli.py debug workflow-123
          
          # List available templates
          workflow_cli.py templates
        """)
    )
    
    parser.add_argument("command", choices=[
        "create", "start", "stop", "resume", "status", "list", "inspect", "debug", 
        "monitor", "rollback", "templates", "health", "migrate"
    ], help="Command to execute")
    
    parser.add_argument("workflow_id", nargs="?", help="Workflow ID")
    parser.add_argument("--template", help="Template name/path for create command")
    parser.add_argument("--param", action="append", help="Template parameters (key=value)")
    parser.add_argument("--status-filter", choices=["created", "running", "completed", "failed", "cancelled", "paused"], 
                       help="Filter workflows by status")
    parser.add_argument("--force", action="store_true", help="Force operation (e.g., cancel vs pause)")
    parser.add_argument("--checkpoint", help="Checkpoint ID for rollback")
    parser.add_argument("--interval", type=int, default=5, help="Monitoring interval in seconds")
    parser.add_argument("--duration", type=int, default=300, help="Monitoring duration in seconds")
    parser.add_argument("--output", choices=["table", "json"], default="table", help="Output format")
    
    args = parser.parse_args()
    
    cli = WorkflowCLI()
    
    try:
        if args.command == "create":
            if not args.template:
                print("❌ --template required for create command")
                return
                
            # Parse parameters
            parameters = {}
            if args.param:
                for param in args.param:
                    if '=' in param:
                        key, value = param.split('=', 1)
                        parameters[key] = value
                        
            workflow_id = await cli.create_workflow(args.template, parameters)
            print(f"✅ Workflow created: {workflow_id}")
            
        elif args.command == "start":
            if not args.workflow_id:
                print("❌ Workflow ID required")
                return
                
            success = await cli.start_workflow(args.workflow_id)
            if success:
                print(f"✅ Workflow {args.workflow_id} started")
            else:
                print(f"❌ Failed to start workflow {args.workflow_id}")
                
        elif args.command == "stop":
            if not args.workflow_id:
                print("❌ Workflow ID required")
                return
                
            success = await cli.stop_workflow(args.workflow_id, args.force)
            action = "cancelled" if args.force else "paused"
            if success:
                print(f"✅ Workflow {args.workflow_id} {action}")
            else:
                print(f"❌ Failed to {action.replace('ed', '')} workflow {args.workflow_id}")
                
        elif args.command == "resume":
            if not args.workflow_id:
                print("❌ Workflow ID required")
                return
                
            success = await cli.resume_workflow(args.workflow_id)
            if success:
                print(f"✅ Workflow {args.workflow_id} resumed")
            else:
                print(f"❌ Failed to resume workflow {args.workflow_id}")
                
        elif args.command == "status":
            if not args.workflow_id:
                print("❌ Workflow ID required")
                return
                
            status = cli.get_workflow_status(args.workflow_id)
            if status:
                if args.output == "json":
                    print(json.dumps(status, indent=2))
                else:
                    print(cli.format_workflow_status(status))
            else:
                print(f"❌ Workflow {args.workflow_id} not found")
                
        elif args.command == "list":
            workflows = cli.list_workflows(args.status_filter)
            
            if args.output == "json":
                print(json.dumps(workflows, indent=2))
            else:
                if not workflows:
                    print("No workflows found")
                else:
                    print(f"{'ID':<20} {'Name':<25} {'Status':<12} {'Progress':<10} {'Created':<20}")
                    print("-" * 87)
                    for wf in workflows:
                        created = wf['created_at'][:19] if wf.get('created_at') else 'Unknown'
                        progress = f"{wf['progress']['percentage']:.0f}%" if 'progress' in wf else 'N/A'
                        print(f"{wf['workflow_id']:<20} {wf['name'][:24]:<25} {wf['status']:<12} {progress:<10} {created:<20}")
                        
        elif args.command == "inspect":
            if not args.workflow_id:
                print("❌ Workflow ID required")
                return
                
            details = await cli.inspect_workflow(args.workflow_id)
            if details:
                if args.output == "json":
                    print(json.dumps(details, indent=2))
                else:
                    print(f"Workflow Details: {details['name']}")
                    print(f"ID: {details['id']}")
                    print(f"Version: {details['version']}")
                    print(f"Status: {details['status']}")
                    print(f"Description: {details['description']}")
                    print(f"Tasks: {details['completed_tasks']}/{details['task_count']} completed")
                    if details['error']:
                        print(f"Error: {details['error']}")
            else:
                print(f"❌ Workflow {args.workflow_id} not found")
                
        elif args.command == "debug":
            if not args.workflow_id:
                print("❌ Workflow ID required")
                return
                
            debug_info = await cli.debug_workflow(args.workflow_id)
            
            if args.output == "json":
                print(json.dumps(debug_info, indent=2))
            else:
                print(f"Debug Information for {debug_info['workflow_id']}")
                print(f"Status: {debug_info['status']}")
                
                if debug_info['health_check']:
                    health = debug_info['health_check']
                    print(f"Health Score: {health['health_score']:.1f}/100")
                    if health['issues']:
                        print("Issues:")
                        for issue in health['issues']:
                            print(f"  - {issue}")
                            
                if debug_info['suggestions']:
                    print("Suggestions:")
                    for suggestion in debug_info['suggestions']:
                        print(f"  💡 {suggestion}")
                        
        elif args.command == "monitor":
            if not args.workflow_id:
                print("❌ Workflow ID required")
                return
                
            await cli.monitor_workflow(args.workflow_id, args.interval, args.duration)
            
        elif args.command == "rollback":
            if not args.workflow_id:
                print("❌ Workflow ID required")
                return
                
            success = await cli.rollback_workflow(args.workflow_id, args.checkpoint)
            if success:
                print(f"✅ Workflow {args.workflow_id} rolled back")
            else:
                print(f"❌ Failed to rollback workflow {args.workflow_id}")
                
        elif args.command == "templates":
            templates = cli.list_templates()
            
            if args.output == "json":
                print(json.dumps(templates, indent=2))
            else:
                if not templates:
                    print("No templates found")
                else:
                    print(f"{'Filename':<25} {'Name':<30} {'Type':<20} {'Description':<40}")
                    print("-" * 115)
                    for template in templates:
                        if 'error' not in template:
                            desc = template['description'][:39] if template['description'] else 'No description'
                            print(f"{template['filename']:<25} {template['name'][:29]:<30} {template['template_type']:<20} {desc:<40}")
                            
        elif args.command == "health":
            health_summary = cli.monitor.get_system_health_summary()
            
            if args.output == "json":
                print(json.dumps(health_summary, indent=2))
            else:
                summary = health_summary['summary']
                print("System Health Summary")
                print(f"Total Workflows: {summary['total_workflows']}")
                print(f"Healthy: {summary['healthy_workflows']}")
                print(f"Warning: {summary['warning_workflows']}")
                print(f"Critical: {summary['critical_workflows']}")
                print(f"Average Health: {summary['average_health']:.1f}/100")
                
        elif args.command == "migrate":
            if args.workflow_id:
                # Migrate specific workflow
                success, message = cli.migration_manager.migrate_workflow_file(args.workflow_id)
                if success:
                    print(f"✅ {message}")
                else:
                    print(f"❌ {message}")
            else:
                # Show migration status
                status = cli.migration_manager.get_migration_status()
                print(f"Schema Version: {status['current_schema_version']}")
                print(f"Workflows: {status['summary']['up_to_date']} up-to-date, {status['summary']['needs_migration']} need migration")
                
    except KeyboardInterrupt:
        print("\n❌ Command interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())