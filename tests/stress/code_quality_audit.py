#!/usr/bin/env python3
"""
Code Quality Audit for Bluelabel Autopilot
Checks for memory leaks, TODOs, error handling, and security issues.
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any
from datetime import datetime
import subprocess


class CodeQualityAuditor:
    """Comprehensive code quality auditing tool."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.issues = {
            "todos": [],
            "memory_leaks": [],
            "error_handling": [],
            "security": [],
            "logging": [],
            "performance": []
        }
        
    def audit_todos(self):
        """Find all TODO comments in the codebase."""
        print("🔍 Checking for TODOs...")
        
        patterns = [
            r'#\s*TODO[:\s]*(.*)',
            r'#\s*FIXME[:\s]*(.*)',
            r'#\s*HACK[:\s]*(.*)',
            r'#\s*XXX[:\s]*(.*)'
        ]
        
        for pattern in patterns:
            try:
                result = subprocess.run(
                    ['grep', '-r', '-n', '-E', pattern, '--include=*.py', str(self.project_root)],
                    capture_output=True,
                    text=True
                )
                
                for line in result.stdout.splitlines():
                    if 'test' not in line and '.git' not in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            self.issues["todos"].append({
                                "file": parts[0],
                                "line": parts[1],
                                "text": parts[2].strip()
                            })
            except Exception as e:
                print(f"Error scanning for TODOs: {e}")
    
    def audit_memory_leaks(self):
        """Check for potential memory leaks."""
        print("🔍 Checking for memory leaks...")
        
        # Patterns that might indicate memory leaks
        leak_patterns = [
            (r'\.append\(', "Unbounded list growth"),
            (r'cache\[.*\]\s*=', "Unbounded cache growth"),
            (r'while\s+True:', "Infinite loops without breaks"),
            (r'global\s+\w+', "Global variable accumulation")
        ]
        
        py_files = list(self.project_root.rglob("*.py"))
        
        for file_path in py_files:
            if 'test' in str(file_path) or '.git' in str(file_path):
                continue
                
            try:
                content = file_path.read_text()
                lines = content.splitlines()
                
                for i, line in enumerate(lines, 1):
                    for pattern, issue_type in leak_patterns:
                        if re.search(pattern, line):
                            # Check context to reduce false positives
                            context = '\n'.join(lines[max(0, i-3):min(len(lines), i+2)])
                            
                            # Skip if there's proper cleanup nearby
                            if 'clear()' in context or 'pop' in context or 'maxlen' in context:
                                continue
                                
                            self.issues["memory_leaks"].append({
                                "file": str(file_path),
                                "line": i,
                                "type": issue_type,
                                "code": line.strip()
                            })
            except Exception as e:
                print(f"Error checking {file_path}: {e}")
    
    def audit_error_handling(self):
        """Check for proper error handling."""
        print("🔍 Checking error handling...")
        
        py_files = list(self.project_root.rglob("*.py"))
        
        for file_path in py_files:
            if 'test' in str(file_path) or '.git' in str(file_path):
                continue
                
            try:
                content = file_path.read_text()
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # Check for bare except clauses
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        self.issues["error_handling"].append({
                            "file": str(file_path),
                            "line": node.lineno,
                            "type": "bare_except",
                            "message": "Bare except clause - should specify exception type"
                        })
                    
                    # Check for except Exception without logging
                    elif isinstance(node, ast.ExceptHandler):
                        if node.type and hasattr(node.type, 'id') and node.type.id == 'Exception':
                            # Check if there's logging in the handler
                            has_logging = any(
                                isinstance(n, ast.Call) and 
                                hasattr(n.func, 'attr') and 
                                n.func.attr in ['error', 'exception', 'warning']
                                for n in ast.walk(node)
                            )
                            
                            if not has_logging:
                                self.issues["error_handling"].append({
                                    "file": str(file_path),
                                    "line": node.lineno,
                                    "type": "unlogged_exception",
                                    "message": "Exception caught but not logged"
                                })
                                
            except Exception as e:
                print(f"Error parsing {file_path}: {e}")
    
    def audit_security(self):
        """Check for security issues."""
        print("🔍 Checking security...")
        
        security_patterns = [
            (r'eval\(', "Use of eval() - security risk"),
            (r'exec\(', "Use of exec() - security risk"),
            (r'__import__\(', "Dynamic import - potential security risk"),
            (r'pickle\.load', "Pickle deserialization - security risk"),
            (r'os\.system\(', "Shell command execution - use subprocess instead"),
            (r'password.*=.*["\']', "Hardcoded password"),
            (r'api_key.*=.*["\']', "Hardcoded API key"),
            (r'secret.*=.*["\']', "Hardcoded secret")
        ]
        
        py_files = list(self.project_root.rglob("*.py"))
        
        for file_path in py_files:
            if 'test' in str(file_path) or '.git' in str(file_path):
                continue
                
            try:
                content = file_path.read_text()
                lines = content.splitlines()
                
                for i, line in enumerate(lines, 1):
                    for pattern, issue_type in security_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.issues["security"].append({
                                "file": str(file_path),
                                "line": i,
                                "type": issue_type,
                                "code": line.strip()
                            })
            except Exception as e:
                print(f"Error checking {file_path}: {e}")
    
    def audit_logging(self):
        """Check logging configuration."""
        print("🔍 Checking logging...")
        
        py_files = list(self.project_root.rglob("*.py"))
        
        for file_path in py_files:
            if 'test' in str(file_path) or '.git' in str(file_path):
                continue
                
            try:
                content = file_path.read_text()
                
                # Check if file uses print instead of logging
                if 'print(' in content and 'logger' not in content:
                    self.issues["logging"].append({
                        "file": str(file_path),
                        "type": "uses_print",
                        "message": "Uses print() instead of logging"
                    })
                
                # Check for logger but no configuration
                if 'logger = logging.getLogger' in content:
                    if 'logging.basicConfig' not in content and 'main.py' not in str(file_path):
                        self.issues["logging"].append({
                            "file": str(file_path),
                            "type": "no_config",
                            "message": "Logger created but no configuration"
                        })
                        
            except Exception as e:
                print(f"Error checking {file_path}: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_issues": total_issues,
                "todos": len(self.issues["todos"]),
                "memory_leaks": len(self.issues["memory_leaks"]),
                "error_handling": len(self.issues["error_handling"]),
                "security": len(self.issues["security"]),
                "logging": len(self.issues["logging"])
            },
            "issues": self.issues,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        if self.issues["todos"]:
            recommendations.append(f"Address {len(self.issues['todos'])} TODO items before production")
        
        if self.issues["memory_leaks"]:
            recommendations.append("Review and fix potential memory leaks, especially in long-running processes")
        
        if self.issues["error_handling"]:
            recommendations.append("Improve error handling with specific exception types and proper logging")
        
        if self.issues["security"]:
            recommendations.append("CRITICAL: Address security issues immediately")
        
        if self.issues["logging"]:
            recommendations.append("Standardize logging across the codebase")
        
        return recommendations


def run_code_quality_audit():
    """Run comprehensive code quality audit."""
    print("🔍 Starting Code Quality Audit...")
    
    project_root = Path("/Users/arielmuslera/Development/Projects/bluelabel-autopilot")
    auditor = CodeQualityAuditor(project_root)
    
    # Run all audits
    auditor.audit_todos()
    auditor.audit_memory_leaks()
    auditor.audit_error_handling()
    auditor.audit_security()
    auditor.audit_logging()
    
    # Generate report
    report = auditor.generate_report()
    
    # Print summary
    print("\n📊 Code Quality Audit Summary:")
    print(f"Total Issues Found: {report['summary']['total_issues']}")
    print(f"  - TODOs: {report['summary']['todos']}")
    print(f"  - Memory Leaks: {report['summary']['memory_leaks']}")
    print(f"  - Error Handling: {report['summary']['error_handling']}")
    print(f"  - Security: {report['summary']['security']}")
    print(f"  - Logging: {report['summary']['logging']}")
    
    print("\n🔧 Recommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    # Save detailed report
    report_path = project_root / "docs" / "CODE_QUALITY_AUDIT.json"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Detailed report saved to {report_path}")
    
    return report


if __name__ == "__main__":
    run_code_quality_audit()