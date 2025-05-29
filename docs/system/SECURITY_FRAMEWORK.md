# Security Framework Documentation

## Overview

This document outlines the security framework for the orchestration system, including best practices, security controls, and guidelines for maintaining a secure environment. The framework follows OWASP best practices and addresses common security vulnerabilities.

## Security Audit Tool

The system includes a comprehensive security audit tool (`tools/security_audit.py`) that automatically scans for vulnerabilities:

### Running Security Audits

```bash
# Audit entire project
python3 tools/security_audit.py

# Audit specific directory
python3 tools/security_audit.py /path/to/directory

# Generate JSON report
python3 tools/security_audit.py --output security_report.json

# Non-recursive scan
python3 tools/security_audit.py --no-recursive
```

### Vulnerability Detection

The security audit tool detects:

1. **Hardcoded Credentials** (CWE-798)
   - API keys, passwords, tokens
   - High-entropy strings that may be secrets
   - Private keys and certificates

2. **Command Injection** (CWE-78)
   - Unsafe use of os.system, subprocess
   - Eval and exec usage
   - Unquoted variables in shell scripts

3. **Path Traversal** (CWE-22)
   - Directory traversal attempts
   - Unsafe file path handling

4. **Weak File Permissions** (CWE-732)
   - World-writable files
   - World-readable sensitive files
   - Incorrect execute permissions

5. **Input Validation Issues** (CWE-20)
   - Missing input sanitization
   - Unsafe JSON parsing
   - Command argument validation

## Security Best Practices

### 1. Input Validation and Sanitization

Always validate and sanitize user input before processing:

```python
from tools.security_audit import InputValidator

validator = InputValidator()

# Sanitize filenames
safe_filename = validator.sanitize_filename(user_input)

# Validate paths
safe_path = validator.sanitize_path(user_path, base_directory)
if not safe_path:
    raise ValueError("Invalid path")

# Sanitize command arguments
safe_arg = validator.sanitize_command_arg(user_arg)

# Validate JSON input
is_valid, data, error = validator.validate_json_input(json_string)
if not is_valid:
    raise ValueError(f"Invalid JSON: {error}")

# Validate IDs
if not validator.validate_agent_id(agent_id):
    raise ValueError("Invalid agent ID")
```

### 2. Credential Management

**Never hardcode credentials in source code!**

#### ❌ Bad Practice:
```python
API_KEY = "sk-1234567890abcdef"
password = "admin123"
```

#### ✅ Good Practice:
```python
import os
from services.security.credential_manager import CredentialManager

# Use environment variables
API_KEY = os.environ.get('API_KEY')

# Use credential manager
cred_manager = CredentialManager()
password = cred_manager.get_credential('db_password')
```

#### Credential Storage Guidelines:
1. Use environment variables for configuration
2. Store secrets in secure vaults (e.g., HashiCorp Vault)
3. Use the credential manager service
4. Rotate credentials regularly
5. Never commit `.env` files to version control

### 3. Command Execution Security

#### ❌ Dangerous Command Execution:
```python
# Never use shell=True with user input
os.system(f"process {user_input}")
subprocess.call(user_input, shell=True)

# Never use eval/exec with user input
eval(user_code)
exec(user_script)
```

#### ✅ Safe Command Execution:
```python
# Use subprocess with shell=False and argument list
subprocess.run(['process', safe_filename], shell=False, check=True)

# If you must evaluate code, use ast.literal_eval for literals only
import ast
data = ast.literal_eval(user_data_string)  # Only for literals

# For complex operations, use whitelisting
ALLOWED_OPERATIONS = {'add', 'subtract', 'multiply'}
if operation in ALLOWED_OPERATIONS:
    result = perform_operation(operation, args)
```

### 4. File Operations Security

#### Path Traversal Prevention:
```python
from tools.security_audit import InputValidator

validator = InputValidator()

# Always validate paths
def safe_file_read(filename, base_dir):
    # Sanitize filename
    safe_name = validator.sanitize_filename(filename)
    
    # Validate full path
    full_path = validator.sanitize_path(
        os.path.join(base_dir, safe_name), 
        base_dir
    )
    
    if not full_path:
        raise ValueError("Invalid file path")
    
    with open(full_path, 'r') as f:
        return f.read()
```

#### File Permission Security:
```python
import stat

# Set secure permissions for sensitive files
def set_secure_permissions(file_path):
    # Remove world read/write permissions
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR)  # 600
    
# Check permissions before processing
def check_file_security(file_path):
    stats = os.stat(file_path)
    
    # Ensure not world-writable
    if stats.st_mode & stat.S_IWOTH:
        raise PermissionError("File is world-writable")
```

### 5. Secure Coding Patterns

#### Use Context Managers:
```python
# Good: Automatic resource cleanup
with file_transaction('/path/to/file') as f:
    process_file(f)

# Good: Automatic lock release
with get_task_lock(task_id) as lock:
    perform_task()
```

#### Validate Early, Fail Fast:
```python
def process_task(agent_id, task_id, data):
    # Validate all inputs first
    if not validator.validate_agent_id(agent_id):
        raise ValueError("Invalid agent ID")
    
    if not validator.validate_task_id(task_id):
        raise ValueError("Invalid task ID")
    
    is_valid, parsed_data, error = validator.validate_json_input(data)
    if not is_valid:
        raise ValueError(f"Invalid data: {error}")
    
    # Now safe to process
    return execute_task(agent_id, task_id, parsed_data)
```

### 6. Security Headers and Configuration

For web-based components:

```python
# Add security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    return response

# Disable debug in production
app.config['DEBUG'] = False

# Use secure session cookies
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
```

## Security Checklist

Before deploying or committing code, verify:

### Code Review Checklist:
- [ ] No hardcoded credentials or secrets
- [ ] All user inputs are validated and sanitized
- [ ] File operations validate paths and permissions
- [ ] Command execution uses safe patterns (no shell=True with user input)
- [ ] No use of eval/exec with user input
- [ ] Proper error handling (no stack traces to users)
- [ ] Logging doesn't expose sensitive data

### Deployment Checklist:
- [ ] Run security audit: `python3 tools/security_audit.py`
- [ ] All critical/high findings addressed
- [ ] File permissions are restrictive (no world-writable)
- [ ] Environment variables used for configuration
- [ ] Debug mode disabled
- [ ] Logs don't contain secrets

### Regular Maintenance:
- [ ] Weekly security audits
- [ ] Monthly credential rotation
- [ ] Quarterly dependency updates
- [ ] Annual penetration testing

## Incident Response

If a security issue is discovered:

1. **Immediate Actions:**
   - Isolate affected systems
   - Rotate compromised credentials
   - Review logs for exploitation

2. **Investigation:**
   - Run security audit on affected components
   - Check git history for introduction of vulnerability
   - Identify scope of potential impact

3. **Remediation:**
   - Fix vulnerability following secure coding practices
   - Test fix thoroughly
   - Deploy patch

4. **Post-Incident:**
   - Document incident and response
   - Update security practices if needed
   - Share learnings with team

## Security Tools Integration

### Pre-commit Hooks

Add security checks to your git workflow:

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run security audit
python3 tools/security_audit.py --output /tmp/security_report.json

# Check for critical issues
if grep -q '"severity": "critical"' /tmp/security_report.json; then
    echo "CRITICAL security issues found! Commit blocked."
    echo "Run: python3 tools/security_audit.py"
    exit 1
fi
```

### CI/CD Integration

```yaml
# .github/workflows/security.yml
security-check:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v2
    - name: Run Security Audit
      run: |
        python3 tools/security_audit.py --output security_report.json
        if grep -q '"severity": "critical"' security_report.json; then
          echo "Critical security issues found!"
          exit 1
        fi
    - name: Upload Security Report
      uses: actions/upload-artifact@v2
      with:
        name: security-report
        path: security_report.json
```

## Compliance and Standards

This security framework aligns with:

1. **OWASP Top 10 (2021)**
   - A01: Broken Access Control
   - A02: Cryptographic Failures
   - A03: Injection
   - A04: Insecure Design
   - A05: Security Misconfiguration

2. **CWE/SANS Top 25**
   - CWE-78: OS Command Injection
   - CWE-798: Use of Hard-coded Credentials
   - CWE-22: Path Traversal
   - CWE-732: Incorrect Permission Assignment

3. **Security Standards**
   - ISO 27001/27002
   - NIST Cybersecurity Framework
   - SOC 2 Type II requirements

## Resources

### Internal Documentation:
- [Error Recovery System](./ERROR_RECOVERY.md) - Secure error handling
- [Agent Autonomy Guidelines](./AGENT_AUTONOMY_GUIDELINES.md) - Secure agent operations

### External Resources:
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [CWE - Common Weakness Enumeration](https://cwe.mitre.org/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Summary

Security is everyone's responsibility. By following these practices and using the provided tools, we can maintain a secure orchestration system. Regular audits, proper input validation, secure credential management, and safe coding practices are essential for preventing vulnerabilities.

Remember: **When in doubt, choose the more secure option.**