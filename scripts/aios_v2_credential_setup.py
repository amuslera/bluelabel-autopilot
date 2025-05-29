#!/usr/bin/env python3
"""
AIOS v2 Credential Setup Helper
Helps create new credentials and validate configuration
"""

import os
import sys
import json
import getpass
from pathlib import Path
from typing import Dict, List, Optional

class CredentialSetup:
    def __init__(self):
        self.aios_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2")
        self.env_path = self.aios_path / ".env"
        self.env_example_path = self.aios_path / ".env.example"
        self.credentials_needed = []
        
    def check_current_setup(self):
        """Check current credential setup status"""
        print("🔍 Checking AIOS v2 credential setup...\n")
        
        # Check if .env exists
        if self.env_path.exists():
            print("⚠️  WARNING: .env file exists - checking for exposed credentials...")
            self.scan_for_exposed_credentials()
        else:
            print("✅ No .env file found (good - start fresh)")
            
        # Check .env.example
        if self.env_example_path.exists():
            print("✅ .env.example template exists")
        else:
            print("❌ .env.example missing - security setup may be incomplete")
            
        # Check .gitignore
        gitignore_path = self.aios_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path) as f:
                content = f.read()
                if ".env" in content:
                    print("✅ .env is in .gitignore")
                else:
                    print("❌ .env is NOT in .gitignore - CRITICAL!")
        
    def scan_for_exposed_credentials(self):
        """Scan for known exposed credentials"""
        exposed_patterns = [
            "sk-proj-DLZUH9x31",
            "sk-ant-api03-odcklFFz",
            "AIzaSyAw6wWezz1TDJGG9xCUKZgmvPdWXF0KJlw",
            "1094552487600-r4r8i8kmbl2hbh57q4pdjpdqt01sm5pr",
            "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"
        ]
        
        if self.env_path.exists():
            with open(self.env_path) as f:
                content = f.read()
                for pattern in exposed_patterns:
                    if pattern in content:
                        print(f"🚨 EXPOSED CREDENTIAL FOUND: {pattern[:20]}...")
                        
    def create_new_env(self):
        """Create new .env file with secure credentials"""
        print("\n📝 Creating new .env file...\n")
        
        if not self.env_example_path.exists():
            print("❌ Error: .env.example not found")
            return
            
        # Read template
        with open(self.env_example_path) as f:
            template = f.read()
            
        # Parse required credentials
        env_vars = {}
        for line in template.split('\n'):
            if '=' in line and not line.strip().startswith('#'):
                key = line.split('=')[0].strip()
                env_vars[key] = ""
                
        print("Please provide new credentials (or press Enter to skip):\n")
        
        # Collect credentials
        new_env_content = []
        
        # Core settings
        env_vars['ENVIRONMENT'] = 'development'
        env_vars['DEBUG'] = 'true'
        env_vars['API_DEBUG'] = 'true'
        env_vars['SECRET_KEY'] = self.generate_secret_key()
        env_vars['JWT_SECRET_KEY'] = self.generate_secret_key()
        
        # Collect API keys
        critical_keys = {
            'ANTHROPIC_API_KEY': 'Anthropic API key (sk-ant-...)',
            'OPENAI_API_KEY': 'OpenAI API key (sk-...)',
            'GOOGLE_CLIENT_ID': 'Google OAuth Client ID',
            'GOOGLE_CLIENT_SECRET': 'Google OAuth Client Secret'
        }
        
        for key, description in critical_keys.items():
            value = getpass.getpass(f"{description}: ").strip()
            if value:
                env_vars[key] = value
                
        # Write new .env
        print("\n✍️  Writing new .env file...")
        
        with open(self.env_path, 'w') as f:
            f.write("# AIOS v2 Environment Configuration\n")
            f.write("# Generated securely - DO NOT COMMIT\n\n")
            
            for key, value in env_vars.items():
                if value:
                    f.write(f"{key}={value}\n")
                    
        # Set permissions
        os.chmod(self.env_path, 0o600)
        print("✅ .env file created with secure permissions (600)")
        
    def generate_secret_key(self, length=32):
        """Generate secure secret key"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
        
    def validate_services(self):
        """Validate external service connections"""
        print("\n🧪 Validating service connections...\n")
        
        # This would run actual connection tests
        services = [
            "Database (PostgreSQL)",
            "LLM APIs (OpenAI/Anthropic)",
            "Gmail OAuth",
            "Redis Cache"
        ]
        
        for service in services:
            print(f"Testing {service}... [Would test in real implementation]")
            
    def setup_production_secrets(self):
        """Guide for production secrets management"""
        print("\n🔐 Production Secrets Management Setup\n")
        
        print("""
For production, use one of these approaches:

1. **AWS Secrets Manager**
   ```bash
   aws secretsmanager create-secret --name aios-v2/production
   aws secretsmanager put-secret-value --secret-id aios-v2/production --secret-string file://.env
   ```

2. **HashiCorp Vault**
   ```bash
   vault kv put secret/aios-v2 @.env
   ```

3. **Kubernetes Secrets**
   ```bash
   kubectl create secret generic aios-v2-secrets --from-env-file=.env
   ```

4. **Docker Secrets** (for Swarm)
   ```bash
   docker secret create aios_v2_env .env
   ```

Never store production credentials in:
- Git repositories
- Docker images
- Plain text files
- Environment variables in CI/CD logs
        """)

def main():
    print("""
🔐 AIOS v2 Credential Setup Helper
==================================

This tool helps you:
1. Check current credential setup
2. Create new secure credentials
3. Validate service connections
4. Set up production secrets
    """)
    
    setup = CredentialSetup()
    
    while True:
        print("\nOptions:")
        print("1. Check current setup")
        print("2. Create new .env file")
        print("3. Validate services")
        print("4. Production setup guide")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            setup.check_current_setup()
        elif choice == '2':
            setup.create_new_env()
        elif choice == '3':
            setup.validate_services()
        elif choice == '4':
            setup.setup_production_secrets()
        elif choice == '5':
            print("\n✅ Remember to:")
            print("- Rotate all exposed credentials")
            print("- Never commit .env files")
            print("- Use secrets management in production")
            break
        else:
            print("Invalid option")

if __name__ == "__main__":
    main()