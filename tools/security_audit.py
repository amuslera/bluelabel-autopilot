#!/usr/bin/env python3
"""
Security Audit Framework for the Orchestration System.

Provides comprehensive security scanning, vulnerability detection, and 
compliance checking following OWASP best practices.
"""

import os
import re
import ast
import json
import stat
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import hashlib


class SecurityLevel(Enum):
    """Security risk levels for findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(Enum):
    """Types of security vulnerabilities."""
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    HARDCODED_SECRET = "hardcoded_secret"
    WEAK_PERMISSIONS = "weak_permissions"
    UNSAFE_DESERIALIZATION = "unsafe_deserialization"
    SQL_INJECTION = "sql_injection"
    XSS = "cross_site_scripting"
    INSECURE_RANDOM = "insecure_random"
    MISSING_INPUT_VALIDATION = "missing_input_validation"
    EXPOSED_DEBUG_INFO = "exposed_debug_info"


@dataclass
class SecurityFinding:
    """Represents a security finding."""
    vulnerability_type: VulnerabilityType
    severity: SecurityLevel
    file_path: str
    line_number: Optional[int]
    description: str
    recommendation: str
    code_snippet: Optional[str] = None
    cwe_id: Optional[str] = None
    owasp_category: Optional[str] = None


class InputValidator:
    """Validates and sanitizes various types of input."""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal attacks.
        
        Args:
            filename: Raw filename input
            
        Returns:
            Sanitized filename safe for use
        """
        # Remove any path separators
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Prevent directory traversal
        filename = filename.replace('..', '')
        
        # Limit length
        max_length = 255
        if len(filename) > max_length:
            name, ext = os.path.splitext(filename)
            filename = name[:max_length-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def sanitize_path(path: str, base_path: str) -> Optional[str]:
        """
        Sanitize and validate file path.
        
        Args:
            path: Path to validate
            base_path: Base directory that path must be within
            
        Returns:
            Sanitized absolute path or None if invalid
        """
        try:
            # Resolve to absolute path
            abs_path = os.path.abspath(path)
            abs_base = os.path.abspath(base_path)
            
            # Ensure path is within base directory
            if not abs_path.startswith(abs_base):
                return None
            
            return abs_path
        except Exception:
            return None
    
    @staticmethod
    def sanitize_command_arg(arg: str) -> str:
        """
        Sanitize command line argument to prevent injection.
        
        Args:
            arg: Command argument to sanitize
            
        Returns:
            Sanitized argument
        """
        # Remove shell metacharacters
        dangerous_chars = ';&|`$(){}[]<>*?!~'
        for char in dangerous_chars:
            arg = arg.replace(char, '')
        
        # Escape quotes
        arg = arg.replace('"', '\\"').replace("'", "\\'")
        
        return arg
    
    @staticmethod
    def validate_json_input(json_str: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Validate JSON input safely.
        
        Args:
            json_str: JSON string to validate
            
        Returns:
            Tuple of (is_valid, parsed_data, error_message)
        """
        try:
            # Limit input size to prevent DoS
            max_size = 10 * 1024 * 1024  # 10MB
            if len(json_str) > max_size:
                return False, None, "JSON input too large"
            
            # Parse JSON
            data = json.loads(json_str)
            
            # Basic structure validation
            if not isinstance(data, (dict, list)):
                return False, None, "JSON must be object or array"
            
            return True, data, None
            
        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON: {e}"
        except Exception as e:
            return False, None, f"JSON validation error: {e}"
    
    @staticmethod
    def validate_agent_id(agent_id: str) -> bool:
        """Validate agent ID format."""
        return bool(re.match(r'^[A-Z]{2,4}$', agent_id))
    
    @staticmethod
    def validate_task_id(task_id: str) -> bool:
        """Validate task ID format."""
        return bool(re.match(r'^TASK-[A-Z0-9\-]+$', task_id))


class CredentialScanner:
    """Scans for hardcoded credentials and secrets."""
    
    # Common patterns for secrets
    SECRET_PATTERNS = [
        # API Keys
        (r'(?i)(api[_\s\-]?key|apikey)\s*[:=]\s*["\']([^"\']+)["\']', "API Key"),
        (r'(?i)(api[_\s\-]?secret|apisecret)\s*[:=]\s*["\']([^"\']+)["\']', "API Secret"),
        
        # Passwords
        (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']+)["\']', "Password"),
        (r'(?i)(pass)\s*[:=]\s*["\']([^"\']+)["\']', "Password"),
        
        # Tokens
        (r'(?i)(auth[_\s\-]?token|token)\s*[:=]\s*["\']([^"\']+)["\']', "Auth Token"),
        (r'(?i)(access[_\s\-]?token)\s*[:=]\s*["\']([^"\']+)["\']', "Access Token"),
        
        # AWS
        (r'AKIA[0-9A-Z]{16}', "AWS Access Key"),
        (r'(?i)(aws[_\s\-]?secret[_\s\-]?access[_\s\-]?key)\s*[:=]\s*["\']([^"\']+)["\']', "AWS Secret Key"),
        
        # Database
        (r'(?i)(db[_\s\-]?password|database[_\s\-]?password)\s*[:=]\s*["\']([^"\']+)["\']', "Database Password"),
        (r'(?i)(connection[_\s\-]?string)\s*[:=]\s*["\']([^"\']+)["\']', "Connection String"),
        
        # Private Keys
        (r'-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----', "Private Key"),
        (r'-----BEGIN OPENSSH PRIVATE KEY-----', "SSH Private Key"),
        
        # Generic secrets
        (r'(?i)(secret)\s*[:=]\s*["\']([^"\']{8,})["\']', "Secret"),
    ]
    
    # Entropy threshold for detecting high-entropy strings (potential secrets)
    ENTROPY_THRESHOLD = 4.5
    
    @staticmethod
    def calculate_entropy(s: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not s:
            return 0
        
        prob = [float(s.count(c)) / len(s) for c in dict.fromkeys(list(s))]
        entropy = -sum([p * __import__('math').log(p) / __import__('math').log(2.0) for p in prob if p > 0])
        
        return entropy
    
    def scan_file(self, file_path: Path) -> List[SecurityFinding]:
        """Scan a file for hardcoded credentials."""
        findings = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
            
            # Check against known patterns
            for pattern, secret_type in self.SECRET_PATTERNS:
                for match in re.finditer(pattern, content):
                    line_no = content[:match.start()].count('\n') + 1
                    
                    # Get the actual secret value
                    if match.groups():
                        secret_value = match.group(1) if len(match.groups()) == 1 else match.group(2)
                    else:
                        secret_value = match.group(0)
                    
                    # Skip if it's a placeholder or example
                    if self._is_placeholder(secret_value):
                        continue
                    
                    findings.append(SecurityFinding(
                        vulnerability_type=VulnerabilityType.HARDCODED_SECRET,
                        severity=SecurityLevel.HIGH,
                        file_path=str(file_path),
                        line_number=line_no,
                        description=f"Potential {secret_type} found in source code",
                        recommendation="Store secrets in environment variables or secure vaults",
                        code_snippet=lines[line_no-1].strip() if line_no <= len(lines) else None,
                        cwe_id="CWE-798",
                        owasp_category="A02:2021 - Cryptographic Failures"
                    ))
            
            # Check for high-entropy strings
            for i, line in enumerate(lines):
                for word in re.findall(r'["\']([^"\']{16,})["\']', line):
                    if self.calculate_entropy(word) > self.ENTROPY_THRESHOLD:
                        if not self._is_placeholder(word):
                            findings.append(SecurityFinding(
                                vulnerability_type=VulnerabilityType.HARDCODED_SECRET,
                                severity=SecurityLevel.MEDIUM,
                                file_path=str(file_path),
                                line_number=i + 1,
                                description="High entropy string detected (possible secret)",
                                recommendation="Review if this is a secret and move to secure storage",
                                code_snippet=line.strip(),
                                cwe_id="CWE-798"
                            ))
        
        except Exception:
            pass  # Skip files that can't be read
        
        return findings
    
    def _is_placeholder(self, value: str) -> bool:
        """Check if a value is likely a placeholder."""
        placeholders = [
            'your-', 'example', 'test', 'demo', 'sample', 'dummy',
            'xxx', 'placeholder', 'changeme', 'default', '<', '>'
        ]
        
        value_lower = value.lower()
        return any(p in value_lower for p in placeholders)


class CommandInjectionScanner:
    """Scans for command injection vulnerabilities."""
    
    DANGEROUS_FUNCTIONS = {
        'python': [
            'os.system', 'subprocess.call', 'subprocess.run', 'subprocess.Popen',
            'eval', 'exec', 'compile', '__import__'
        ],
        'bash': [
            'eval', 'source', '`.+`', r'\$\(.+\)'
        ]
    }
    
    def scan_python_file(self, file_path: Path) -> List[SecurityFinding]:
        """Scan Python file for command injection vulnerabilities."""
        findings = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
                lines = content.splitlines()
            
            for node in ast.walk(tree):
                # Check for dangerous function calls
                if isinstance(node, ast.Call):
                    func_name = self._get_function_name(node)
                    
                    if func_name in ['os.system', 'subprocess.call', 'subprocess.run']:
                        if self._has_dynamic_input(node):
                            findings.append(SecurityFinding(
                                vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                                severity=SecurityLevel.CRITICAL,
                                file_path=str(file_path),
                                line_number=node.lineno,
                                description=f"Potential command injection via {func_name}",
                                recommendation="Use subprocess with shell=False and pass arguments as list",
                                code_snippet=lines[node.lineno-1].strip() if node.lineno <= len(lines) else None,
                                cwe_id="CWE-78",
                                owasp_category="A03:2021 - Injection"
                            ))
                    
                    elif func_name in ['eval', 'exec']:
                        findings.append(SecurityFinding(
                            vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                            severity=SecurityLevel.HIGH,
                            file_path=str(file_path),
                            line_number=node.lineno,
                            description=f"Use of dangerous function {func_name}",
                            recommendation="Avoid eval/exec or use ast.literal_eval for safe evaluation",
                            code_snippet=lines[node.lineno-1].strip() if node.lineno <= len(lines) else None,
                            cwe_id="CWE-95",
                            owasp_category="A03:2021 - Injection"
                        ))
        
        except Exception:
            pass
        
        return findings
    
    def scan_bash_file(self, file_path: Path) -> List[SecurityFinding]:
        """Scan bash script for command injection vulnerabilities."""
        findings = []
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            for i, line in enumerate(lines):
                # Check for eval usage
                if re.search(r'\beval\b', line):
                    findings.append(SecurityFinding(
                        vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                        severity=SecurityLevel.HIGH,
                        file_path=str(file_path),
                        line_number=i + 1,
                        description="Use of eval command in shell script",
                        recommendation="Avoid eval or carefully validate all input",
                        code_snippet=line.strip(),
                        cwe_id="CWE-78"
                    ))
                
                # Check for unquoted variables in commands
                if re.search(r'\$[A-Za-z_][A-Za-z0-9_]*(?!["\'])', line):
                    if any(cmd in line for cmd in ['rm', 'mv', 'cp', 'chmod']):
                        findings.append(SecurityFinding(
                            vulnerability_type=VulnerabilityType.COMMAND_INJECTION,
                            severity=SecurityLevel.MEDIUM,
                            file_path=str(file_path),
                            line_number=i + 1,
                            description="Unquoted variable in command",
                            recommendation="Always quote variables: \"$VAR\"",
                            code_snippet=line.strip(),
                            cwe_id="CWE-78"
                        ))
        
        except Exception:
            pass
        
        return findings
    
    def _get_function_name(self, node: ast.Call) -> Optional[str]:
        """Extract function name from AST node."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            current = node.func
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return None
    
    def _has_dynamic_input(self, node: ast.Call) -> bool:
        """Check if function call has dynamic input."""
        for arg in node.args:
            if not isinstance(arg, ast.Constant):
                return True
        return False


class FilePermissionChecker:
    """Checks file permissions for security issues."""
    
    def check_file_permissions(self, file_path: Path) -> List[SecurityFinding]:
        """Check if file has secure permissions."""
        findings = []
        
        try:
            stats = os.stat(file_path)
            mode = stats.st_mode
            
            # Check for world-writable files
            if mode & stat.S_IWOTH:
                findings.append(SecurityFinding(
                    vulnerability_type=VulnerabilityType.WEAK_PERMISSIONS,
                    severity=SecurityLevel.HIGH,
                    file_path=str(file_path),
                    line_number=None,
                    description="File is world-writable",
                    recommendation="Remove world write permission: chmod o-w",
                    cwe_id="CWE-732",
                    owasp_category="A01:2021 - Broken Access Control"
                ))
            
            # Check for world-readable sensitive files
            if self._is_sensitive_file(file_path) and mode & stat.S_IROTH:
                findings.append(SecurityFinding(
                    vulnerability_type=VulnerabilityType.WEAK_PERMISSIONS,
                    severity=SecurityLevel.MEDIUM,
                    file_path=str(file_path),
                    line_number=None,
                    description="Sensitive file is world-readable",
                    recommendation="Remove world read permission: chmod o-r",
                    cwe_id="CWE-732"
                ))
            
            # Check for executable files
            if mode & stat.S_IXUSR and file_path.suffix not in ['.sh', '.py']:
                findings.append(SecurityFinding(
                    vulnerability_type=VulnerabilityType.WEAK_PERMISSIONS,
                    severity=SecurityLevel.LOW,
                    file_path=str(file_path),
                    line_number=None,
                    description="Non-script file has execute permission",
                    recommendation="Remove execute permission if not needed",
                    cwe_id="CWE-732"
                ))
        
        except Exception:
            pass
        
        return findings
    
    def _is_sensitive_file(self, file_path: Path) -> bool:
        """Check if file might contain sensitive data."""
        sensitive_patterns = [
            'config', 'credential', 'secret', 'key', 'token',
            'password', 'private', '.env'
        ]
        
        file_str = str(file_path).lower()
        return any(pattern in file_str for pattern in sensitive_patterns)


class SecurityAuditor:
    """Main security auditor that orchestrates all scanners."""
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize security auditor."""
        self.base_path = base_path or Path.cwd()
        self.credential_scanner = CredentialScanner()
        self.injection_scanner = CommandInjectionScanner()
        self.permission_checker = FilePermissionChecker()
        self.input_validator = InputValidator()
        
        # Files to skip
        self.skip_patterns = [
            '*.pyc', '__pycache__', '.git', 'node_modules',
            '*.log', '*.tmp', '.pytest_cache'
        ]
    
    def audit_directory(self, 
                       directory: Optional[Path] = None,
                       recursive: bool = True) -> Dict[str, Any]:
        """
        Perform security audit on directory.
        
        Args:
            directory: Directory to audit (defaults to base_path)
            recursive: Whether to scan subdirectories
            
        Returns:
            Audit report with findings
        """
        directory = directory or self.base_path
        findings = []
        files_scanned = 0
        
        # Collect files to scan
        if recursive:
            files = list(directory.rglob('*'))
        else:
            files = list(directory.glob('*'))
        
        # Filter files
        files = [f for f in files if f.is_file() and not self._should_skip(f)]
        
        # Scan each file
        for file_path in files:
            files_scanned += 1
            
            # Scan based on file type
            if file_path.suffix == '.py':
                findings.extend(self.credential_scanner.scan_file(file_path))
                findings.extend(self.injection_scanner.scan_python_file(file_path))
            elif file_path.suffix == '.sh':
                findings.extend(self.credential_scanner.scan_file(file_path))
                findings.extend(self.injection_scanner.scan_bash_file(file_path))
            else:
                findings.extend(self.credential_scanner.scan_file(file_path))
            
            # Check permissions
            findings.extend(self.permission_checker.check_file_permissions(file_path))
        
        # Generate report
        report = self._generate_report(findings, files_scanned)
        
        return report
    
    def audit_file(self, file_path: Path) -> List[SecurityFinding]:
        """Audit a single file."""
        findings = []
        
        if file_path.exists() and file_path.is_file():
            if file_path.suffix == '.py':
                findings.extend(self.credential_scanner.scan_file(file_path))
                findings.extend(self.injection_scanner.scan_python_file(file_path))
            elif file_path.suffix == '.sh':
                findings.extend(self.credential_scanner.scan_file(file_path))
                findings.extend(self.injection_scanner.scan_bash_file(file_path))
            else:
                findings.extend(self.credential_scanner.scan_file(file_path))
            
            findings.extend(self.permission_checker.check_file_permissions(file_path))
        
        return findings
    
    def validate_input(self, input_type: str, value: str) -> Tuple[bool, Optional[str]]:
        """
        Validate and sanitize input.
        
        Args:
            input_type: Type of input (filename, path, json, agent_id, task_id)
            value: Input value to validate
            
        Returns:
            Tuple of (is_valid, sanitized_value)
        """
        if input_type == "filename":
            sanitized = self.input_validator.sanitize_filename(value)
            return True, sanitized
        
        elif input_type == "path":
            sanitized = self.input_validator.sanitize_path(value, str(self.base_path))
            return sanitized is not None, sanitized
        
        elif input_type == "json":
            is_valid, data, error = self.input_validator.validate_json_input(value)
            return is_valid, json.dumps(data) if is_valid else None
        
        elif input_type == "agent_id":
            is_valid = self.input_validator.validate_agent_id(value)
            return is_valid, value if is_valid else None
        
        elif input_type == "task_id":
            is_valid = self.input_validator.validate_task_id(value)
            return is_valid, value if is_valid else None
        
        elif input_type == "command_arg":
            sanitized = self.input_validator.sanitize_command_arg(value)
            return True, sanitized
        
        return False, None
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        for pattern in self.skip_patterns:
            if file_path.match(pattern):
                return True
        return False
    
    def _generate_report(self, findings: List[SecurityFinding], files_scanned: int) -> Dict[str, Any]:
        """Generate security audit report."""
        # Group findings by severity
        by_severity = {level: [] for level in SecurityLevel}
        for finding in findings:
            by_severity[finding.severity].append(finding)
        
        # Count by type
        by_type = {}
        for finding in findings:
            vuln_type = finding.vulnerability_type.value
            by_type[vuln_type] = by_type.get(vuln_type, 0) + 1
        
        # Calculate risk score (simple scoring)
        risk_score = (
            len(by_severity[SecurityLevel.CRITICAL]) * 10 +
            len(by_severity[SecurityLevel.HIGH]) * 5 +
            len(by_severity[SecurityLevel.MEDIUM]) * 3 +
            len(by_severity[SecurityLevel.LOW]) * 1
        )
        
        # Convert findings to dict with enum values as strings
        findings_list = []
        for f in findings:
            finding_dict = asdict(f)
            finding_dict['vulnerability_type'] = f.vulnerability_type.value
            finding_dict['severity'] = f.severity.value
            findings_list.append(finding_dict)
        
        report = {
            "scan_date": datetime.now().isoformat(),
            "files_scanned": files_scanned,
            "total_findings": len(findings),
            "risk_score": risk_score,
            "findings_by_severity": {
                level.value: len(items) for level, items in by_severity.items()
            },
            "findings_by_type": by_type,
            "findings": findings_list,
            "summary": self._generate_summary(findings, risk_score)
        }
        
        return report
    
    def _generate_summary(self, findings: List[SecurityFinding], risk_score: int) -> str:
        """Generate human-readable summary."""
        if not findings:
            return "No security issues found. System appears secure."
        
        critical_count = sum(1 for f in findings if f.severity == SecurityLevel.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == SecurityLevel.HIGH)
        
        if risk_score > 50:
            status = "CRITICAL - Immediate action required"
        elif risk_score > 20:
            status = "HIGH - Security improvements needed"
        elif risk_score > 10:
            status = "MEDIUM - Some security concerns"
        else:
            status = "LOW - Minor security improvements suggested"
        
        summary = f"Security Status: {status}\n"
        summary += f"Risk Score: {risk_score}\n"
        
        if critical_count > 0:
            summary += f"\n⚠️  {critical_count} CRITICAL issues require immediate attention!"
        if high_count > 0:
            summary += f"\n⚠️  {high_count} HIGH severity issues should be addressed soon."
        
        return summary


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security audit for orchestration system")
    parser.add_argument("path", nargs="?", default=".", help="Path to audit")
    parser.add_argument("--output", "-o", help="Output file for report (JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--no-recursive", action="store_true", help="Don't scan subdirectories")
    
    args = parser.parse_args()
    
    # Run audit
    auditor = SecurityAuditor()
    report = auditor.audit_directory(
        Path(args.path),
        recursive=not args.no_recursive
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to: {args.output}")
    
    # Print summary
    print("\n" + "="*60)
    print("SECURITY AUDIT REPORT")
    print("="*60)
    print(f"Files scanned: {report['files_scanned']}")
    print(f"Total findings: {report['total_findings']}")
    print(f"Risk score: {report['risk_score']}")
    print("\nFindings by severity:")
    for severity, count in report['findings_by_severity'].items():
        if count > 0:
            print(f"  {severity.upper()}: {count}")
    print("\n" + report['summary'])
    
    # Exit with error code if critical issues found
    if report['findings_by_severity'].get('critical', 0) > 0:
        exit(1)


if __name__ == "__main__":
    main()