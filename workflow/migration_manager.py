#!/usr/bin/env python3
"""
Workflow Versioning and Migration Manager

Handles workflow version management, schema migrations, and backward compatibility
for the orchestration engine.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import re


@dataclass
class MigrationScript:
    """Migration script definition"""
    from_version: str
    to_version: str
    description: str
    migration_function: str
    rollback_function: Optional[str] = None


class WorkflowMigrationManager:
    """Manages workflow versioning and migrations"""
    
    def __init__(self, base_path: str = "/Users/arielmuslera/Development/Projects/bluelabel-autopilot"):
        self.base_path = Path(base_path)
        self.workflows_dir = self.base_path / "workflow" / "instances"
        self.templates_dir = self.base_path / "workflow" / "templates"
        self.migrations_dir = self.base_path / "workflow" / "migrations"
        self.backups_dir = self.base_path / "workflow" / "backups"
        
        # Create directories
        for dir_path in [self.migrations_dir, self.backups_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            
        # Current schema version
        self.current_version = "2.0.0"
        
        # Migration registry
        self.migrations = self._register_migrations()
        
    def _register_migrations(self) -> List[MigrationScript]:
        """Register all available migrations"""
        return [
            MigrationScript(
                from_version="1.0.0",
                to_version="1.1.0",
                description="Add execution_mode field to tasks",
                migration_function="migrate_1_0_to_1_1"
            ),
            MigrationScript(
                from_version="1.1.0",
                to_version="1.2.0",
                description="Add conditions array to tasks",
                migration_function="migrate_1_1_to_1_2"
            ),
            MigrationScript(
                from_version="1.2.0",
                to_version="2.0.0",
                description="Add checkpoints and execution history",
                migration_function="migrate_1_2_to_2_0"
            )
        ]
        
    def detect_workflow_version(self, workflow_data: Dict[str, Any]) -> str:
        """Detect workflow schema version"""
        # Check for version field
        if 'version' in workflow_data:
            return workflow_data['version']
            
        # Heuristic detection based on schema features
        tasks = workflow_data.get('tasks', {})
        
        if not tasks:
            return "1.0.0"
            
        # Check for v2.0.0 features
        if 'checkpoints' in workflow_data or 'execution_history' in workflow_data:
            return "2.0.0"
            
        # Check for v1.2.0 features
        first_task = next(iter(tasks.values()), {})
        if 'conditions' in first_task:
            return "1.2.0"
            
        # Check for v1.1.0 features
        if 'execution_mode' in first_task:
            return "1.1.0"
            
        return "1.0.0"
        
    def needs_migration(self, workflow_data: Dict[str, Any]) -> bool:
        """Check if workflow needs migration"""
        current_version = self.detect_workflow_version(workflow_data)
        return self._compare_versions(current_version, self.current_version) < 0
        
    def _compare_versions(self, v1: str, v2: str) -> int:
        """Compare two version strings (-1: v1 < v2, 0: equal, 1: v1 > v2)"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        
        # Pad with zeros
        max_len = max(len(v1_parts), len(v2_parts))
        v1_parts += [0] * (max_len - len(v1_parts))
        v2_parts += [0] * (max_len - len(v2_parts))
        
        for i in range(max_len):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
                
        return 0
        
    def migrate_workflow(self, workflow_data: Dict[str, Any], target_version: Optional[str] = None) -> Dict[str, Any]:
        """Migrate workflow to target version"""
        if target_version is None:
            target_version = self.current_version
            
        current_version = self.detect_workflow_version(workflow_data)
        
        if self._compare_versions(current_version, target_version) >= 0:
            return workflow_data  # Already at target version or newer
            
        # Find migration path
        migration_path = self._find_migration_path(current_version, target_version)
        
        if not migration_path:
            raise ValueError(f"No migration path found from {current_version} to {target_version}")
            
        # Apply migrations in sequence
        migrated_data = workflow_data.copy()
        
        for migration in migration_path:
            migrated_data = self._apply_migration(migrated_data, migration)
            
        return migrated_data
        
    def _find_migration_path(self, from_version: str, to_version: str) -> List[MigrationScript]:
        """Find migration path between versions"""
        # Simple linear path for now - could be enhanced for complex dependency graphs
        path = []
        current = from_version
        
        while self._compare_versions(current, to_version) < 0:
            # Find migration from current version
            migration = None
            for m in self.migrations:
                if m.from_version == current:
                    migration = m
                    break
                    
            if not migration:
                return []  # No path found
                
            path.append(migration)
            current = migration.to_version
            
        return path
        
    def _apply_migration(self, workflow_data: Dict[str, Any], migration: MigrationScript) -> Dict[str, Any]:
        """Apply specific migration"""
        migration_func = getattr(self, migration.migration_function)
        return migration_func(workflow_data)
        
    def migrate_1_0_to_1_1(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1.0.0 to 1.1.0"""
        migrated = workflow_data.copy()
        migrated['version'] = "1.1.0"
        
        # Add execution_mode to all tasks
        tasks = migrated.get('tasks', {})
        for task_id, task_data in tasks.items():
            if 'execution_mode' not in task_data:
                task_data['execution_mode'] = 'sequential'
                
        return migrated
        
    def migrate_1_1_to_1_2(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1.1.0 to 1.2.0"""
        migrated = workflow_data.copy()
        migrated['version'] = "1.2.0"
        
        # Add conditions array to all tasks
        tasks = migrated.get('tasks', {})
        for task_id, task_data in tasks.items():
            if 'conditions' not in task_data:
                task_data['conditions'] = []
                
        return migrated
        
    def migrate_1_2_to_2_0(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate from version 1.2.0 to 2.0.0"""
        migrated = workflow_data.copy()
        migrated['version'] = "2.0.0"
        
        # Add checkpoints and execution_history
        if 'checkpoints' not in migrated:
            migrated['checkpoints'] = []
            
        if 'execution_history' not in migrated:
            migrated['execution_history'] = []
            
        # Add retry settings to tasks
        tasks = migrated.get('tasks', {})
        for task_id, task_data in tasks.items():
            if 'retry_count' not in task_data:
                task_data['retry_count'] = 3
            if 'retry_delay' not in task_data:
                task_data['retry_delay'] = 5
                
        return migrated
        
    def backup_workflow(self, workflow_id: str) -> str:
        """Create backup of workflow before migration"""
        workflow_file = self.workflows_dir / f"{workflow_id}.json"
        
        if not workflow_file.exists():
            raise FileNotFoundError(f"Workflow file not found: {workflow_file}")
            
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{workflow_id}_backup_{timestamp}.json"
        backup_file = self.backups_dir / backup_filename
        
        # Copy file
        shutil.copy2(workflow_file, backup_file)
        
        return str(backup_file)
        
    def restore_workflow(self, workflow_id: str, backup_file: str) -> bool:
        """Restore workflow from backup"""
        backup_path = Path(backup_file)
        workflow_file = self.workflows_dir / f"{workflow_id}.json"
        
        if not backup_path.exists():
            return False
            
        try:
            shutil.copy2(backup_path, workflow_file)
            return True
        except Exception:
            return False
            
    def migrate_workflow_file(self, workflow_id: str, target_version: Optional[str] = None) -> Tuple[bool, str]:
        """Migrate workflow file in place"""
        workflow_file = self.workflows_dir / f"{workflow_id}.json"
        
        if not workflow_file.exists():
            return False, f"Workflow file not found: {workflow_file}"
            
        try:
            # Load current workflow
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
                
            # Check if migration is needed
            if not self.needs_migration(workflow_data):
                return True, "Workflow is already at target version"
                
            # Create backup
            backup_file = self.backup_workflow(workflow_id)
            
            # Migrate
            migrated_data = self.migrate_workflow(workflow_data, target_version)
            
            # Save migrated workflow
            with open(workflow_file, 'w') as f:
                json.dump(migrated_data, f, indent=2)
                
            return True, f"Migration successful. Backup created: {backup_file}"
            
        except Exception as e:
            return False, f"Migration failed: {str(e)}"
            
    def migrate_all_workflows(self, target_version: Optional[str] = None) -> Dict[str, Tuple[bool, str]]:
        """Migrate all workflows in the system"""
        results = {}
        
        for workflow_file in self.workflows_dir.glob("*.json"):
            workflow_id = workflow_file.stem
            success, message = self.migrate_workflow_file(workflow_id, target_version)
            results[workflow_id] = (success, message)
            
        return results
        
    def validate_migrated_workflow(self, workflow_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate migrated workflow data"""
        errors = []
        
        # Check required fields
        required_fields = ['id', 'name', 'version', 'tasks']
        for field in required_fields:
            if field not in workflow_data:
                errors.append(f"Missing required field: {field}")
                
        # Validate version format
        version = workflow_data.get('version', '')
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            errors.append(f"Invalid version format: {version}")
            
        # Validate tasks
        tasks = workflow_data.get('tasks', {})
        for task_id, task_data in tasks.items():
            task_required = ['id', 'name', 'agent_id', 'action']
            for field in task_required:
                if field not in task_data:
                    errors.append(f"Task {task_id}: Missing required field: {field}")
                    
            # Check v2.0.0 specific fields
            if self._compare_versions(version, "2.0.0") >= 0:
                if 'retry_count' not in task_data:
                    errors.append(f"Task {task_id}: Missing retry_count (required in v2.0.0)")
                if 'retry_delay' not in task_data:
                    errors.append(f"Task {task_id}: Missing retry_delay (required in v2.0.0)")
                    
        return len(errors) == 0, errors
        
    def get_migration_status(self) -> Dict[str, Any]:
        """Get migration status for all workflows"""
        status = {
            "current_schema_version": self.current_version,
            "workflows": {},
            "summary": {
                "total": 0,
                "up_to_date": 0,
                "needs_migration": 0,
                "versions": {}
            }
        }
        
        for workflow_file in self.workflows_dir.glob("*.json"):
            try:
                with open(workflow_file, 'r') as f:
                    workflow_data = json.load(f)
                    
                workflow_id = workflow_file.stem
                version = self.detect_workflow_version(workflow_data)
                needs_migration = self.needs_migration(workflow_data)
                
                status["workflows"][workflow_id] = {
                    "current_version": version,
                    "needs_migration": needs_migration,
                    "target_version": self.current_version
                }
                
                # Update summary
                status["summary"]["total"] += 1
                if needs_migration:
                    status["summary"]["needs_migration"] += 1
                else:
                    status["summary"]["up_to_date"] += 1
                    
                # Version distribution
                if version not in status["summary"]["versions"]:
                    status["summary"]["versions"][version] = 0
                status["summary"]["versions"][version] += 1
                
            except Exception as e:
                status["workflows"][workflow_file.stem] = {
                    "error": str(e)
                }
                
        return status
        
    def cleanup_backups(self, days_to_keep: int = 30):
        """Clean up old backup files"""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 3600)
        
        for backup_file in self.backups_dir.glob("*_backup_*.json"):
            try:
                if backup_file.stat().st_mtime < cutoff_date:
                    backup_file.unlink()
            except Exception:
                continue


def main():
    """CLI interface for migration manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Workflow Migration Manager")
    parser.add_argument("command", choices=["status", "migrate", "migrate-all", "backup", "restore", "validate", "cleanup"],
                       help="Command to execute")
    parser.add_argument("--workflow-id", help="Specific workflow ID")
    parser.add_argument("--target-version", help="Target version for migration")
    parser.add_argument("--backup-file", help="Backup file for restore")
    parser.add_argument("--days", type=int, default=30, help="Days to keep backups")
    
    args = parser.parse_args()
    
    manager = WorkflowMigrationManager()
    
    if args.command == "status":
        status = manager.get_migration_status()
        
        print("\nMigration Status Report")
        print("=" * 50)
        print(f"Current Schema Version: {status['current_schema_version']}")
        print(f"Total Workflows: {status['summary']['total']}")
        print(f"Up to Date: {status['summary']['up_to_date']}")
        print(f"Need Migration: {status['summary']['needs_migration']}")
        
        print("\nVersion Distribution:")
        for version, count in status['summary']['versions'].items():
            print(f"  {version}: {count} workflows")
            
        if status['summary']['needs_migration'] > 0:
            print("\nWorkflows Needing Migration:")
            for wf_id, wf_status in status['workflows'].items():
                if wf_status.get('needs_migration', False):
                    print(f"  {wf_id}: {wf_status['current_version']} -> {wf_status['target_version']}")
                    
    elif args.command == "migrate":
        if not args.workflow_id:
            print("--workflow-id required for migrate command")
            return
            
        success, message = manager.migrate_workflow_file(args.workflow_id, args.target_version)
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            
    elif args.command == "migrate-all":
        print("Migrating all workflows...")
        results = manager.migrate_all_workflows(args.target_version)
        
        success_count = sum(1 for success, _ in results.values() if success)
        total_count = len(results)
        
        print(f"\nMigration Results: {success_count}/{total_count} successful")
        
        for workflow_id, (success, message) in results.items():
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {workflow_id}: {message}")
            
    elif args.command == "backup":
        if not args.workflow_id:
            print("--workflow-id required for backup command")
            return
            
        try:
            backup_file = manager.backup_workflow(args.workflow_id)
            print(f"✅ Backup created: {backup_file}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            
    elif args.command == "restore":
        if not args.workflow_id or not args.backup_file:
            print("--workflow-id and --backup-file required for restore command")
            return
            
        success = manager.restore_workflow(args.workflow_id, args.backup_file)
        if success:
            print(f"✅ Workflow {args.workflow_id} restored from {args.backup_file}")
        else:
            print(f"❌ Restore failed")
            
    elif args.command == "validate":
        if not args.workflow_id:
            print("--workflow-id required for validate command")
            return
            
        workflow_file = manager.workflows_dir / f"{args.workflow_id}.json"
        if not workflow_file.exists():
            print(f"❌ Workflow file not found: {workflow_file}")
            return
            
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
            
        valid, errors = manager.validate_migrated_workflow(workflow_data)
        
        if valid:
            print(f"✅ Workflow {args.workflow_id} is valid")
        else:
            print(f"❌ Workflow {args.workflow_id} has validation errors:")
            for error in errors:
                print(f"  - {error}")
                
    elif args.command == "cleanup":
        manager.cleanup_backups(args.days)
        print(f"✅ Cleaned up backup files older than {args.days} days")


if __name__ == "__main__":
    main()