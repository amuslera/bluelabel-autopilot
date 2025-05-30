#!/usr/bin/env python3
"""
AIOS v2 Dependency Resolver and API Startup Helper
Identifies and resolves missing dependencies for AIOS v2
"""

import subprocess
import sys
import os
import time
from pathlib import Path

class DependencyResolver:
    def __init__(self, project_path: str = "/Users/arielmuslera/Development/Projects/bluelabel-AIOS-V2"):
        self.project_path = Path(project_path)
        self.requirements_file = self.project_path / "requirements.txt"
        
    def check_project_exists(self) -> bool:
        """Check if AIOS v2 project exists"""
        exists = self.project_path.exists()
        print(f"📁 Project path: {self.project_path}")
        print(f"✅ Project exists: {exists}")
        return exists
        
    def read_requirements(self) -> list:
        """Read requirements.txt file"""
        if not self.requirements_file.exists():
            print(f"❌ Requirements file not found: {self.requirements_file}")
            return []
            
        with open(self.requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
        print(f"📦 Found {len(requirements)} requirements")
        return requirements
        
    def check_installed_packages(self, requirements: list) -> dict:
        """Check which packages are already installed"""
        result = {"installed": [], "missing": []}
        
        for req in requirements:
            # Extract package name (handle version specifiers)
            package_name = req.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('~=')[0]
            
            try:
                subprocess.run([sys.executable, "-c", f"import {package_name}"], 
                             check=True, capture_output=True)
                result["installed"].append(req)
            except (subprocess.CalledProcessError, ImportError):
                result["missing"].append(req)
                
        print(f"✅ Installed: {len(result['installed'])} packages")
        print(f"❌ Missing: {len(result['missing'])} packages")
        
        if result["missing"]:
            print("\nMissing packages:")
            for pkg in result["missing"]:
                print(f"  - {pkg}")
                
        return result
        
    def install_missing_packages(self, missing_packages: list) -> bool:
        """Install missing packages"""
        if not missing_packages:
            print("✅ All packages already installed")
            return True
            
        print(f"\n🔧 Installing {len(missing_packages)} missing packages...")
        
        # Install packages one by one to handle individual failures
        failed_packages = []
        
        for package in missing_packages:
            print(f"Installing {package}...")
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", package
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"✅ {package} installed successfully")
                else:
                    print(f"❌ Failed to install {package}: {result.stderr}")
                    failed_packages.append(package)
                    
            except subprocess.TimeoutExpired:
                print(f"❌ Timeout installing {package}")
                failed_packages.append(package)
            except Exception as e:
                print(f"❌ Error installing {package}: {e}")
                failed_packages.append(package)
                
        if failed_packages:
            print(f"\n❌ Failed to install {len(failed_packages)} packages:")
            for pkg in failed_packages:
                print(f"  - {pkg}")
            return False
        else:
            print("\n✅ All packages installed successfully")
            return True
            
    def verify_critical_imports(self) -> dict:
        """Verify critical imports for AIOS v2"""
        critical_packages = [
            "fastapi",
            "uvicorn", 
            "pydantic",
            "sqlalchemy",
            "psycopg2",
            "redis",
            "chromadb",
            "pdfplumber",
            "requests",
            "anthropic",
            "openai"
        ]
        
        result = {"success": [], "failed": []}
        
        print("\n🔍 Verifying critical imports...")
        
        for package in critical_packages:
            try:
                subprocess.run([sys.executable, "-c", f"import {package}"], 
                             check=True, capture_output=True)
                result["success"].append(package)
                print(f"✅ {package}")
            except subprocess.CalledProcessError:
                result["failed"].append(package)
                print(f"❌ {package}")
                
        return result
        
    def test_api_startup(self) -> bool:
        """Test if API can start successfully"""
        print("\n🚀 Testing API startup...")
        
        # Set environment variables
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_path)
        
        try:
            # Start API in background and test
            api_script = self.project_path / "apps" / "api" / "main.py"
            
            if not api_script.exists():
                print(f"❌ API script not found: {api_script}")
                return False
                
            print(f"Starting API from: {api_script}")
            
            # Test import without running
            test_cmd = [
                sys.executable, "-c", 
                f"import sys; sys.path.insert(0, '{self.project_path}'); "
                "from apps.api.main import app; print('✅ API imports successfully')"
            ]
            
            result = subprocess.run(test_cmd, capture_output=True, text=True, env=env, timeout=30)
            
            if result.returncode == 0:
                print("✅ API startup test passed")
                return True
            else:
                print(f"❌ API startup test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ API startup test error: {e}")
            return False
            
    def generate_startup_script(self) -> str:
        """Generate a startup script for AIOS v2"""
        script_content = f"""#!/bin/bash
# AIOS v2 Startup Script
# Generated by dependency resolver

echo "🚀 Starting AIOS v2..."

# Check if Docker services are running
echo "📋 Checking Docker services..."
docker ps | grep -E "(postgres|redis|chromadb)" || {{
    echo "❌ Docker services not running. Starting..."
    docker-compose -f {self.project_path}/docker-compose.yml up -d
    sleep 30
}}

# Set Python path
export PYTHONPATH={self.project_path}

# Start API server
echo "🔧 Starting API server..."
cd {self.project_path}
python3 apps/api/main.py

echo "✅ AIOS v2 startup complete"
"""
        
        script_path = Path("/tmp/start_aios_v2.sh")
        with open(script_path, 'w') as f:
            f.write(script_content)
            
        os.chmod(script_path, 0o755)
        print(f"\n📝 Startup script created: {script_path}")
        return str(script_path)

def main():
    print("🔧 AIOS v2 Dependency Resolver & API Startup Helper")
    print("=" * 50)
    
    resolver = DependencyResolver()
    
    # Step 1: Check project exists
    if not resolver.check_project_exists():
        print("❌ AIOS v2 project not found. Exiting.")
        return 1
        
    # Step 2: Read requirements
    requirements = resolver.read_requirements()
    if not requirements:
        print("❌ No requirements found. Exiting.")
        return 1
        
    # Step 3: Check installed packages
    package_status = resolver.check_installed_packages(requirements)
    
    # Step 4: Install missing packages
    if package_status["missing"]:
        install_success = resolver.install_missing_packages(package_status["missing"])
        if not install_success:
            print("❌ Failed to install some packages. Manual intervention may be required.")
            
    # Step 5: Verify critical imports
    import_status = resolver.verify_critical_imports()
    
    if import_status["failed"]:
        print(f"\n❌ {len(import_status['failed'])} critical imports failed")
        print("Manual installation may be required for:")
        for pkg in import_status["failed"]:
            print(f"  pip install {pkg}")
    else:
        print("\n✅ All critical imports successful")
        
    # Step 6: Test API startup
    api_test = resolver.test_api_startup()
    
    # Step 7: Generate startup script
    startup_script = resolver.generate_startup_script()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPENDENCY RESOLUTION SUMMARY")
    print("=" * 50)
    print(f"✅ Installed packages: {len(package_status['installed'])}")
    print(f"❌ Missing packages: {len(package_status['missing'])}")
    print(f"✅ Working imports: {len(import_status['success'])}")
    print(f"❌ Failed imports: {len(import_status['failed'])}")
    print(f"🚀 API startup test: {'✅ PASS' if api_test else '❌ FAIL'}")
    
    if api_test and not import_status["failed"]:
        print("\n🎉 AIOS v2 is ready to run!")
        print(f"Use: {startup_script}")
    else:
        print("\n⚠️  AIOS v2 needs manual fixes before running")
        
    return 0 if api_test and not import_status["failed"] else 1

if __name__ == "__main__":
    sys.exit(main())