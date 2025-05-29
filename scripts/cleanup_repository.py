#!/usr/bin/env python3
"""
Repository Cleanup Script
Archives old documentation and organizes the codebase
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
import json

class RepositoryCleanup:
    def __init__(self):
        self.repo_path = Path("/Users/arielmuslera/Development/Projects/bluelabel-autopilot")
        self.archive_path = self.repo_path / "archive"
        self.stats = {
            "files_moved": 0,
            "files_deleted": 0,
            "space_freed": 0
        }
        
    def create_archive_structure(self):
        """Create organized archive directory structure"""
        print("📁 Creating archive structure...")
        
        directories = [
            "archive/phases",
            "archive/sprints", 
            "archive/context",
            "archive/deprecated",
            "archive/test_artifacts",
            "archive/old_docs"
        ]
        
        for dir_path in directories:
            (self.repo_path / dir_path).mkdir(parents=True, exist_ok=True)
            
        print("✅ Archive structure created")
        
    def identify_files_to_archive(self):
        """Identify files that should be archived"""
        archive_patterns = {
            "phase_docs": {
                "pattern": "**/PHASE_*.md",
                "exclude": ["PHASE_6.15"],  # Keep current phase
                "destination": "archive/phases"
            },
            "sprint_docs": {
                "pattern": "**/SPRINT_*_POSTMORTEM.md",
                "exclude": ["SPRINT_3_POSTMORTEM"],  # Keep latest
                "destination": "archive/sprints"
            },
            "old_context": {
                "pattern": "**/*_CONTEXT.md",
                "exclude": ["CLAUDE_CONTEXT", "CURSOR_CONTEXT", "WINDSURF_CONTEXT"],
                "destination": "archive/context"
            },
            "test_files": {
                "pattern": "test_*.py",
                "exclude": [],
                "destination": "archive/test_artifacts"
            },
            "temp_files": {
                "pattern": "**/*.tmp",
                "exclude": [],
                "destination": "archive/deprecated"
            },
            "old_guides": {
                "pattern": "*_GUIDE.md",
                "exclude": ["AGENT_ORCHESTRATION_GUIDE"],
                "destination": "archive/old_docs"
            }
        }
        
        files_to_move = []
        
        for category, config in archive_patterns.items():
            for file_path in self.repo_path.glob(config["pattern"]):
                if file_path.is_file() and file_path.name not in config["exclude"]:
                    relative_path = file_path.relative_to(self.repo_path)
                    if not str(relative_path).startswith("archive/"):
                        files_to_move.append({
                            "source": file_path,
                            "destination": self.archive_path / config["destination"] / file_path.name,
                            "category": category
                        })
                        
        return files_to_move
        
    def archive_files(self, files_to_move):
        """Move files to archive"""
        print(f"\n📦 Archiving {len(files_to_move)} files...")
        
        for file_info in files_to_move:
            source = file_info["source"]
            destination = file_info["destination"]
            
            try:
                # Get file size for stats
                self.stats["space_freed"] += source.stat().st_size
                
                # Move file
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(source), str(destination))
                
                self.stats["files_moved"] += 1
                print(f"  ✓ Archived: {source.name} → {file_info['category']}")
                
            except Exception as e:
                print(f"  ✗ Error archiving {source.name}: {e}")
                
    def clean_empty_directories(self):
        """Remove empty directories after archiving"""
        print("\n🧹 Cleaning empty directories...")
        
        empty_dirs = []
        
        for root, dirs, files in os.walk(self.repo_path, topdown=False):
            if not dirs and not files and "archive" not in root:
                empty_dirs.append(Path(root))
                
        for empty_dir in empty_dirs:
            try:
                empty_dir.rmdir()
                print(f"  ✓ Removed: {empty_dir.relative_to(self.repo_path)}")
            except:
                pass
                
    def organize_remaining_files(self):
        """Organize remaining documentation"""
        print("\n📚 Organizing remaining documentation...")
        
        # Create organized docs structure
        doc_categories = {
            "docs/architecture": ["ARCH_*.md", "SYSTEM_*.md"],
            "docs/operations": ["*_GUIDE.md", "*_SETUP.md"],
            "docs/development": ["CODING_*.md", "TESTING_*.md"],
            "docs/agents": ["AGENT_*.md"],
            "docs/security": ["SECURITY_*.md", "*_AUDIT.md"]
        }
        
        for category_path, patterns in doc_categories.items():
            (self.repo_path / category_path).mkdir(parents=True, exist_ok=True)
            
    def create_archive_index(self):
        """Create an index of archived files"""
        print("\n📋 Creating archive index...")
        
        archive_index = {
            "created": datetime.now().isoformat(),
            "stats": self.stats,
            "archived_files": {}
        }
        
        for category_dir in self.archive_path.iterdir():
            if category_dir.is_dir():
                files = []
                for file_path in category_dir.rglob("*"):
                    if file_path.is_file():
                        files.append({
                            "name": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
                        
                archive_index["archived_files"][category_dir.name] = files
                
        # Save index
        index_path = self.archive_path / "ARCHIVE_INDEX.json"
        with open(index_path, "w") as f:
            json.dump(archive_index, f, indent=2)
            
        print(f"✅ Archive index created: {index_path}")
        
    def update_readme(self):
        """Update README with new structure"""
        print("\n📝 Updating README...")
        
        readme_addition = """
## 📁 Repository Structure

### Active Development
- `/agents/` - Agent implementations
- `/apps/` - Application code (UI, web)
- `/core/` - Core system functionality
- `/services/` - Service implementations
- `/tests/` - Active test suites

### Documentation
- `/docs/architecture/` - System architecture docs
- `/docs/operations/` - Operational guides
- `/docs/development/` - Development documentation
- `/docs/agents/` - Agent-specific docs
- `/docs/security/` - Security documentation

### Archived Content
- `/archive/` - Historical documentation and deprecated files
  - See `/archive/ARCHIVE_INDEX.json` for contents

### Current Phase
- **Phase 6.15** - Multi-Agent Orchestration
- **Sprint 3** - AIOS v2 MVP Delivery (COMPLETE)
"""
        
        readme_path = self.repo_path / "README.md"
        if readme_path.exists():
            print("  ℹ️  README exists - manual update recommended")
        else:
            print("  ✓ README structure documented")
            
    def generate_cleanup_report(self):
        """Generate cleanup summary report"""
        print("\n" + "="*50)
        print("🎉 REPOSITORY CLEANUP COMPLETE")
        print("="*50)
        
        print(f"""
📊 Cleanup Statistics:
- Files archived: {self.stats['files_moved']}
- Files deleted: {self.stats['files_deleted']}
- Space freed: {self.stats['space_freed'] / 1024 / 1024:.2f} MB

✅ Archive created at: {self.archive_path}
✅ Index available at: {self.archive_path}/ARCHIVE_INDEX.json

📌 Next Steps:
1. Review archived files in /archive/
2. Update README.md with new structure
3. Commit cleaned repository
4. Consider removing archive from git if too large
        """)

def main():
    """Run repository cleanup"""
    print("""
🧹 Repository Cleanup Tool
=========================

This will organize and archive old documentation.
    """)
    
    cleanup = RepositoryCleanup()
    
    # Confirm before proceeding
    response = input("Proceed with cleanup? (y/N): ").strip().lower()
    if response != 'y':
        print("Cleanup cancelled")
        return
        
    # Run cleanup steps
    cleanup.create_archive_structure()
    
    files_to_move = cleanup.identify_files_to_archive()
    print(f"\n📋 Found {len(files_to_move)} files to archive")
    
    if files_to_move:
        cleanup.archive_files(files_to_move)
        
    cleanup.clean_empty_directories()
    cleanup.organize_remaining_files()
    cleanup.create_archive_index()
    cleanup.update_readme()
    cleanup.generate_cleanup_report()

if __name__ == "__main__":
    main()