#!/usr/bin/env python3
"""
Workflow Executor with Email Delivery
Extension of the workflow executor that sends results via email on completion.
"""

import asyncio
import argparse
import sys
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from runner.workflow_executor import setup_logging, run_workflow_cli
from services.email.email_output_adapter import EmailOutAdapter
from services.email.email_output_formatter import format_digest_markdown
from core.workflow_engine import run_workflow
from interfaces.run_models import WorkflowRunResult


async def create_email_callback(config: dict):
    """
    Create email delivery callback from configuration.
    
    Args:
        config: Email configuration dict
        
    Returns:
        Async callback function
    """
    if not config.get('enabled', False):
        return None
    
    adapter = EmailOutAdapter(config.get('smtp', {}))
    recipient = config.get('recipient')
    subject_template = config.get('subject', 'Workflow Complete: {workflow_name}')
    
    async def send_email(result: WorkflowRunResult):
        """Send workflow results via email"""
        try:
            # Extract output from last step
            output_data = None
            for step_id in reversed(result.execution_order or []):
                step_result = result.step_outputs.get(step_id)
                if step_result and step_result.status == "success" and step_result.result:
                    output_data = step_result.result
                    break
            
            if not output_data:
                return
            
            # Format output
            digest_data = {
                'title': result.workflow_name,
                'content': output_data.get('digest', output_data.get('summary', str(output_data))),
                'timestamp': result.completed_at.isoformat() if result.completed_at else None
            }
            
            content = format_digest_markdown(digest_data)
            subject = subject_template.format(workflow_name=result.workflow_name)
            
            # Send email
            await adapter.send_output(
                content=content,
                subject=subject,
                recipient=recipient,
                content_type='html'
            )
            
        except Exception as e:
            # Log but don't fail workflow
            print(f"Email delivery error: {e}")
    
    return send_email


async def run_workflow_with_email(workflow_file: Path, email_config: dict = None, **kwargs):
    """
    Run workflow with optional email delivery.
    
    Args:
        workflow_file: Path to workflow YAML
        email_config: Email configuration dict
        **kwargs: Additional arguments for workflow execution
    """
    # Create email callback if configured
    on_complete = None
    if email_config:
        on_complete = await create_email_callback(email_config)
    
    # Run workflow
    result = await run_workflow(
        path=str(workflow_file),
        on_complete=on_complete,
        **kwargs
    )
    
    return result


def main():
    """Main entry point with email support"""
    parser = argparse.ArgumentParser(
        description='Workflow Executor with Email Delivery',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('workflow_file', type=Path,
                       help='Path to workflow YAML file')
    parser.add_argument('--email-config', type=Path,
                       help='Path to email configuration YAML file')
    parser.add_argument('--email-recipient', 
                       help='Email recipient (overrides config file)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--log-file', type=Path,
                       help='Path to log file')
    parser.add_argument('--storage-path', type=Path, default='./data/knowledge',
                       help='Path to content storage directory')
    parser.add_argument('--temp-path', type=Path, default='./data/temp',
                       help='Path to temporary files directory')
    
    args = parser.parse_args()
    
    # Validate workflow file
    if not args.workflow_file.exists():
        print(f"Error: Workflow file not found: {args.workflow_file}")
        sys.exit(1)
    
    # Load email config if provided
    email_config = None
    if args.email_config and args.email_config.exists():
        with open(args.email_config) as f:
            email_config = yaml.safe_load(f)
        
        # Override recipient if provided
        if args.email_recipient:
            email_config['recipient'] = args.email_recipient
    
    # Setup logging
    logger = setup_logging(
        log_file=args.log_file,
        verbose=args.verbose
    )
    
    # Run workflow
    try:
        asyncio.run(run_workflow_with_email(
            workflow_file=args.workflow_file,
            email_config=email_config,
            storage_path=str(args.storage_path),
            temp_path=str(args.temp_path),
            persist=True
        ))
    except KeyboardInterrupt:
        print("\nWorkflow execution interrupted")
        sys.exit(1)


# Example email configuration file (email_config.yaml):
"""
enabled: true
smtp:
  smtp_server: smtp.gmail.com
  smtp_port: 587
  smtp_username: your-email@gmail.com
  smtp_password: your-app-password
  from_email: your-email@gmail.com
  use_tls: true
recipient: recipient@example.com
subject: "Workflow Complete: {workflow_name}"
"""


if __name__ == '__main__':
    main()