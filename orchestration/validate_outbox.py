#!/usr/bin/env python3
"""
Outbox Format Validator

Validates outbox.json files against the standardized schema defined in
/docs/system/OUTBOX_SCHEMA.md

Usage:
    python validate_outbox.py <path_to_outbox.json>
    python validate_outbox.py --all  # Validate all outbox files
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import argparse


class OutboxValidator:
    """Validates outbox.json files against the standard schema"""
    
    REQUIRED_FIELDS = ["agent_id", "agent_name", "agent_type", "version", "tasks", "history"]
    AGENT_TYPES = ["ai", "human", "hybrid"]
    TASK_STATUSES = ["pending", "in_progress", "completed", "failed", "blocked"]
    PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a single outbox.json file"""
        self.errors = []
        self.warnings = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False, self.errors, self.warnings
        except FileNotFoundError:
            self.errors.append(f"File not found: {file_path}")
            return False, self.errors, self.warnings
            
        # Validate required fields
        for field in self.REQUIRED_FIELDS:
            if field not in data:
                self.errors.append(f"Missing required field: '{field}'")
                
        # Validate agent_type
        if "agent_type" in data and data["agent_type"] not in self.AGENT_TYPES:
            self.errors.append(f"Invalid agent_type: '{data['agent_type']}'. Must be one of {self.AGENT_TYPES}")
            
        # Validate version
        if "version" in data and data["version"] != "1.0.0":
            self.warnings.append(f"Outdated schema version: '{data['version']}'. Current version is '1.0.0'")
            
        # Validate tasks array
        if "tasks" in data:
            if not isinstance(data["tasks"], list):
                self.errors.append("'tasks' must be an array")
            else:
                for i, task in enumerate(data["tasks"]):
                    self._validate_task(task, f"tasks[{i}]")
                    
        # Validate history array
        if "history" in data:
            if not isinstance(data["history"], list):
                self.errors.append("'history' must be an array")
            else:
                for i, entry in enumerate(data["history"]):
                    self._validate_history_entry(entry, f"history[{i}]")
                    
        # Validate expertise array
        if "expertise" in data and not isinstance(data["expertise"], list):
            self.errors.append("'expertise' must be an array of strings")
            
        return len(self.errors) == 0, self.errors, self.warnings
        
    def _validate_task(self, task: Dict[str, Any], path: str):
        """Validate a task object"""
        required_task_fields = ["task_id", "title", "status", "priority", "created_at"]
        
        for field in required_task_fields:
            if field not in task:
                self.errors.append(f"{path}: Missing required field '{field}'")
                
        # Validate status
        if "status" in task and task["status"] not in self.TASK_STATUSES:
            self.errors.append(f"{path}: Invalid status '{task['status']}'. Must be one of {self.TASK_STATUSES}")
            
        # Validate priority
        if "priority" in task and task["priority"] not in self.PRIORITIES:
            self.errors.append(f"{path}: Invalid priority '{task['priority']}'. Must be one of {self.PRIORITIES}")
            
        # Validate timestamps
        for timestamp_field in ["created_at", "started_at", "completed_at"]:
            if timestamp_field in task:
                self._validate_timestamp(task[timestamp_field], f"{path}.{timestamp_field}")
                
        # Validate arrays
        for array_field in ["deliverables", "dependencies"]:
            if array_field in task and not isinstance(task[array_field], list):
                self.errors.append(f"{path}.{array_field}: Must be an array")
                
        # Validate numbers
        for number_field in ["estimated_hours", "actual_hours"]:
            if number_field in task and not isinstance(task[number_field], (int, float)):
                self.errors.append(f"{path}.{number_field}: Must be a number")
                
    def _validate_history_entry(self, entry: Dict[str, Any], path: str):
        """Validate a history entry"""
        required_fields = ["task_id", "timestamp", "status"]
        
        for field in required_fields:
            if field not in entry:
                self.errors.append(f"{path}: Missing required field '{field}'")
                
        if "timestamp" in entry:
            self._validate_timestamp(entry["timestamp"], f"{path}.timestamp")
            
        if "files" in entry:
            if not isinstance(entry["files"], dict):
                self.errors.append(f"{path}.files: Must be an object")
            else:
                for file_type in ["created", "modified"]:
                    if file_type in entry["files"] and not isinstance(entry["files"][file_type], list):
                        self.errors.append(f"{path}.files.{file_type}: Must be an array")
                        
    def _validate_timestamp(self, timestamp: str, path: str):
        """Validate ISO 8601 timestamp format"""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            self.errors.append(f"{path}: Invalid timestamp format. Must be ISO 8601 (e.g., 2025-05-29T10:00:00Z)")


def find_all_outbox_files(base_path: Path) -> List[Path]:
    """Find all outbox.json files in the postbox directory"""
    postbox_dir = base_path / "postbox"
    outbox_files = []
    
    if postbox_dir.exists():
        for agent_dir in postbox_dir.iterdir():
            if agent_dir.is_dir():
                outbox_file = agent_dir / "outbox.json"
                if outbox_file.exists():
                    outbox_files.append(outbox_file)
                    
    return outbox_files


def main():
    parser = argparse.ArgumentParser(description="Validate outbox.json files")
    parser.add_argument("file", nargs="?", help="Path to outbox.json file to validate")
    parser.add_argument("--all", action="store_true", help="Validate all outbox files")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix common issues (not implemented)")
    
    args = parser.parse_args()
    
    validator = OutboxValidator()
    base_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-autopilot")
    
    if args.all:
        # Validate all outbox files
        outbox_files = find_all_outbox_files(base_path)
        
        if not outbox_files:
            print("No outbox.json files found")
            sys.exit(1)
            
        all_valid = True
        for file_path in outbox_files:
            print(f"\nValidating {file_path.relative_to(base_path)}...")
            valid, errors, warnings = validator.validate_file(file_path)
            
            if valid and not warnings:
                print("✅ Valid")
            elif valid and warnings:
                print("⚠️  Valid with warnings:")
                for warning in warnings:
                    print(f"   - {warning}")
            else:
                print("❌ Invalid:")
                for error in errors:
                    print(f"   - {error}")
                all_valid = False
                
        sys.exit(0 if all_valid else 1)
        
    elif args.file:
        # Validate single file
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path
            
        print(f"Validating {file_path}...")
        valid, errors, warnings = validator.validate_file(file_path)
        
        if valid and not warnings:
            print("✅ Valid outbox.json file")
        elif valid and warnings:
            print("⚠️  Valid with warnings:")
            for warning in warnings:
                print(f"- {warning}")
        else:
            print("❌ Invalid outbox.json file:")
            for error in errors:
                print(f"- {error}")
                
        sys.exit(0 if valid else 1)
        
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()