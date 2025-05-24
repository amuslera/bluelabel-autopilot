#!/usr/bin/env python3
"""
Email Workflow Runner CLI
Command-line interface for monitoring Gmail and triggering workflows.

Usage:
    python runner/email_workflow_runner.py --config config/email_workflow_config.yaml
    python runner/email_workflow_runner.py --one-shot  # Process one email and exit
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
import argparse
import yaml
from typing import Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.email.email_workflow_orchestrator import EmailWorkflowOrchestrator


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger('email_workflow_runner')


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load configuration from YAML file"""
    with open(config_path) as f:
        return yaml.safe_load(f)


def create_default_config() -> Dict[str, Any]:
    """Create default configuration"""
    return {
        "gmail": {
            "credentials_path": "credentials.json",
            "token_path": "token.json"
        },
        "routing": {
            "rules": [
                {
                    "name": "pdf_processor",
                    "workflow_path": "email/pdf_attachment_processor.yaml",
                    "has_attachment": True,
                    "attachment_type": "application/pdf",
                    "priority": 20
                },
                {
                    "name": "newsletter_digest",
                    "workflow_path": "email/newsletter_digest.yaml",
                    "from_domain": ["newsletter", "digest", "weekly", "daily"],
                    "priority": 15
                },
                {
                    "name": "url_extractor",
                    "workflow_path": "email/url_content_processor.yaml",
                    "subject_contains": ["link:", "url:", "check out", "interesting"],
                    "priority": 10
                }
            ],
            "default_workflow": "email/generic_email_handler.yaml",
            "workflows_dir": "./workflows"
        },
        "engine": {
            "storage_path": "./data/knowledge",
            "temp_path": "./data/temp"
        },
        "processing": {
            "mark_as_read": True,
            "add_label": "Processed",
            "error_label": "ProcessingError",
            "save_attachments": True
        }
    }


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Email Workflow Runner - Monitor Gmail and trigger workflows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run continuously with default config
  python runner/email_workflow_runner.py
  
  # Run with custom config
  python runner/email_workflow_runner.py --config config/email_workflows.yaml
  
  # Process one email and exit
  python runner/email_workflow_runner.py --one-shot
  
  # Save default config
  python runner/email_workflow_runner.py --save-config config/email_workflows.yaml
"""
    )
    
    parser.add_argument('--config', type=Path,
                       help='Path to configuration YAML file')
    parser.add_argument('--one-shot', action='store_true',
                       help='Process one email and exit')
    parser.add_argument('--save-config', type=Path,
                       help='Save default configuration to file and exit')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show configuration and exit without running')
    
    args = parser.parse_args()
    
    # Setup logging
    logger = setup_logging(args.verbose)
    
    # Handle save config
    if args.save_config:
        config = create_default_config()
        args.save_config.parent.mkdir(parents=True, exist_ok=True)
        with open(args.save_config, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        logger.info(f"Saved default configuration to {args.save_config}")
        return
    
    # Load configuration
    if args.config and args.config.exists():
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)
    else:
        logger.info("Using default configuration")
        config = create_default_config()
    
    # Show config in dry run mode
    if args.dry_run:
        print("\nConfiguration:")
        print("-" * 50)
        print(yaml.dump(config, default_flow_style=False, sort_keys=False))
        print("-" * 50)
        print("\nRouting Rules:")
        for rule in config['routing']['rules']:
            print(f"  Priority {rule['priority']}: {rule['name']} -> {rule['workflow_path']}")
        return
    
    # Create and run orchestrator
    try:
        logger.info("Starting Email Workflow Orchestrator")
        orchestrator = EmailWorkflowOrchestrator(config)
        
        # Run orchestrator
        await orchestrator.start(one_shot=args.one_shot)
        
        # Show final stats
        stats = orchestrator.get_stats()
        logger.info(f"\nFinal Statistics:")
        logger.info(f"  Total processed: {stats['total_processed']}")
        logger.info(f"  Successful: {stats['successful']}")
        logger.info(f"  Failed: {stats['failed']}")
        
        if stats['total_processed'] > 0:
            logger.info(f"  Average processing time: {stats['average_processing_time_ms']:.0f}ms")
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())