#!/usr/bin/env python3
"""
Migration script to transition from WorkflowEngine to UnifiedWorkflowEngine.

This script:
1. Validates existing workflows work with both engines
2. Compares performance between engines
3. Updates configuration to use the unified engine
4. Provides rollback instructions
"""

import asyncio
import sys
import os
from pathlib import Path
import time
import json
import yaml
from typing import Dict, List, Tuple
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflow_engine import WorkflowEngine, run_workflow
from core.unified_workflow_engine import UnifiedWorkflowEngine, EngineType, create_unified_engine
from core.workflow_engine_v2 import WorkflowEngineV2, run_workflow_v2
from core.agent_registry import registry, register_agent
from agents.ingestion_agent import IngestionAgent
from agents.digest_agent import DigestAgent
from interfaces.run_models import WorkflowStatus


class WorkflowMigrator:
    """Handles migration from legacy to unified workflow engine."""
    
    def __init__(self, dry_run: bool = True):
        """Initialize the migrator.
        
        Args:
            dry_run: If True, only test without making changes
        """
        self.dry_run = dry_run
        self.results = {
            'tested': 0,
            'passed': 0,
            'failed': 0,
            'performance': {},
            'errors': []
        }
        
        # Register agents for V2 engine
        register_agent('ingestion_agent', IngestionAgent, version="1.0.0")
        register_agent('digest_agent', DigestAgent, version="1.0.0")
        
    def find_workflow_files(self, directory: Path) -> List[Path]:
        """Find all workflow YAML files in a directory.
        
        Args:
            directory: Directory to search
            
        Returns:
            List of workflow file paths
        """
        workflows = []
        for yaml_file in directory.rglob("*.yaml"):
            # Skip non-workflow files
            if yaml_file.name in ['docker-compose.yaml', 'openapi.yaml']:
                continue
                
            # Check if it's a workflow file
            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)
                    if 'workflow' in data and 'steps' in data:
                        workflows.append(yaml_file)
            except:
                pass
                
        return workflows
    
    async def test_workflow_compatibility(self, workflow_path: Path) -> Tuple[bool, Dict[str, any]]:
        """Test if a workflow works with both engines.
        
        Args:
            workflow_path: Path to workflow file
            
        Returns:
            Tuple of (success, performance_data)
        """
        print(f"\nTesting: {workflow_path}")
        performance = {}
        
        try:
            # Test with legacy engine
            print("  - Testing with legacy WorkflowEngine...")
            start_time = time.time()
            
            legacy_result = await run_workflow(
                str(workflow_path),
                persist=False
            )
            
            legacy_time = (time.time() - start_time) * 1000
            performance['legacy_ms'] = legacy_time
            
            if legacy_result.status != WorkflowStatus.SUCCESS:
                raise Exception(f"Legacy engine failed: {legacy_result.errors}")
            
            print(f"    ✓ Legacy engine: {legacy_time:.2f}ms")
            
            # Test with unified engine (sequential mode)
            print("  - Testing with UnifiedEngine (sequential)...")
            start_time = time.time()
            
            unified_seq = UnifiedWorkflowEngine(engine_type=EngineType.SEQUENTIAL)
            unified_result = await unified_seq.execute_workflow(
                workflow_path,
                persist=False
            )
            
            unified_time = (time.time() - start_time) * 1000
            performance['unified_sequential_ms'] = unified_time
            
            if unified_result.status != WorkflowStatus.SUCCESS:
                raise Exception(f"Unified engine failed: {unified_result.errors}")
            
            print(f"    ✓ Unified engine: {unified_time:.2f}ms")
            
            # Test with V2 engine (with DI)
            print("  - Testing with WorkflowEngineV2 (DI)...")
            start_time = time.time()
            
            v2_result = await run_workflow_v2(
                str(workflow_path),
                persist=False
            )
            
            v2_time = (time.time() - start_time) * 1000
            performance['v2_di_ms'] = v2_time
            
            if v2_result.status != WorkflowStatus.SUCCESS:
                raise Exception(f"V2 engine failed: {v2_result.errors}")
            
            print(f"    ✓ V2 engine: {v2_time:.2f}ms")
            
            # Calculate overhead
            overhead = unified_time - legacy_time
            performance['overhead_ms'] = overhead
            performance['overhead_percent'] = (overhead / legacy_time) * 100
            
            print(f"  ✓ All engines successful! Overhead: {overhead:.2f}ms ({performance['overhead_percent']:.1f}%)")
            
            return True, performance
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            self.results['errors'].append({
                'workflow': str(workflow_path),
                'error': str(e)
            })
            return False, performance
    
    async def migrate_workflows(self, workflow_dir: Path):
        """Migrate all workflows in a directory.
        
        Args:
            workflow_dir: Directory containing workflows
        """
        print(f"Migrating workflows in: {workflow_dir}")
        print(f"Dry run: {self.dry_run}")
        print("-" * 60)
        
        # Find all workflows
        workflows = self.find_workflow_files(workflow_dir)
        print(f"Found {len(workflows)} workflow files")
        
        if not workflows:
            print("No workflows found!")
            return
        
        # Test each workflow
        for workflow in workflows:
            self.results['tested'] += 1
            success, performance = await self.test_workflow_compatibility(workflow)
            
            if success:
                self.results['passed'] += 1
                self.results['performance'][str(workflow)] = performance
            else:
                self.results['failed'] += 1
        
        # Generate report
        self.generate_report()
        
        # Update configuration if not dry run
        if not self.dry_run and self.results['failed'] == 0:
            self.update_configuration()
    
    def generate_report(self):
        """Generate migration report."""
        print("\n" + "=" * 60)
        print("MIGRATION REPORT")
        print("=" * 60)
        
        print(f"\nSummary:")
        print(f"  - Workflows tested: {self.results['tested']}")
        print(f"  - Passed: {self.results['passed']}")
        print(f"  - Failed: {self.results['failed']}")
        
        if self.results['performance']:
            print(f"\nPerformance Analysis:")
            
            total_overhead = 0
            max_overhead = 0
            min_overhead = float('inf')
            
            for workflow, perf in self.results['performance'].items():
                overhead = perf.get('overhead_ms', 0)
                total_overhead += overhead
                max_overhead = max(max_overhead, overhead)
                min_overhead = min(min_overhead, overhead)
                
                print(f"  {Path(workflow).name}:")
                print(f"    - Legacy: {perf.get('legacy_ms', 0):.2f}ms")
                print(f"    - Unified: {perf.get('unified_sequential_ms', 0):.2f}ms")
                print(f"    - V2 (DI): {perf.get('v2_di_ms', 0):.2f}ms")
                print(f"    - Overhead: {overhead:.2f}ms ({perf.get('overhead_percent', 0):.1f}%)")
            
            avg_overhead = total_overhead / len(self.results['performance'])
            print(f"\nOverhead Statistics:")
            print(f"  - Average: {avg_overhead:.2f}ms")
            print(f"  - Max: {max_overhead:.2f}ms")
            print(f"  - Min: {min_overhead:.2f}ms")
            
            if max_overhead < 100:
                print(f"  ✓ All overheads under 100ms requirement!")
            else:
                print(f"  ⚠ Warning: Some overheads exceed 100ms")
        
        if self.results['errors']:
            print(f"\nErrors:")
            for error in self.results['errors']:
                print(f"  - {error['workflow']}: {error['error']}")
        
        # Save detailed report
        report_path = Path('migration_report.json')
        with open(report_path, 'w') as f:
            json.dump({
                'timestamp': datetime.utcnow().isoformat(),
                'results': self.results
            }, f, indent=2)
        print(f"\nDetailed report saved to: {report_path}")
    
    def update_configuration(self):
        """Update configuration to use unified engine."""
        print("\nUpdating configuration...")
        
        # Create .env file with engine configuration
        env_content = """# Bluelabel Autopilot Configuration
# Generated by migration script

# Use unified workflow engine
WORKFLOW_ENGINE_TYPE=sequential

# To use stateful DAG engine (when ready):
# WORKFLOW_ENGINE_TYPE=stateful_dag
"""
        
        env_path = Path('.env')
        if env_path.exists():
            print(f"  ⚠ .env file already exists, creating .env.unified")
            env_path = Path('.env.unified')
        
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"  ✓ Created {env_path}")
        
        # Create rollback instructions
        rollback_content = """# Rollback Instructions

If you need to rollback to the legacy engine:

1. Remove or rename the .env file:
   ```bash
   mv .env .env.backup
   ```

2. Or explicitly set the engine type:
   ```bash
   export WORKFLOW_ENGINE_TYPE=sequential
   ```

3. The legacy WorkflowEngine is still available at:
   ```python
   from core.workflow_engine import WorkflowEngine
   ```

4. All existing code remains compatible.

## Verification

To verify which engine is being used:
```python
from core.unified_workflow_engine import UnifiedWorkflowEngine
engine = UnifiedWorkflowEngine()
print(engine.engine_type)
```
"""
        
        with open('ROLLBACK_INSTRUCTIONS.md', 'w') as f:
            f.write(rollback_content)
        
        print("  ✓ Created ROLLBACK_INSTRUCTIONS.md")
        print("\nMigration complete! 🎉")


async def main():
    """Main migration entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate workflows to UnifiedWorkflowEngine"
    )
    parser.add_argument(
        "workflow_dir",
        type=Path,
        help="Directory containing workflow files"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute migration (default is dry run)"
    )
    
    args = parser.parse_args()
    
    if not args.workflow_dir.exists():
        print(f"Error: Directory not found: {args.workflow_dir}")
        sys.exit(1)
    
    # Create migrator
    migrator = WorkflowMigrator(dry_run=not args.execute)
    
    # Run migration
    await migrator.migrate_workflows(args.workflow_dir)
    
    # Exit with error if any workflows failed
    if migrator.results['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())