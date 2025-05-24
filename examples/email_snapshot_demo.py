"""
Email Snapshot Demo

This script demonstrates how to use the EmailOutAdapter with the new snapshot functionality
that saves email output to disk for debugging and auditing purposes.
"""

import asyncio
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the email components
from services.email.email_output_adapter import EmailOutAdapter
from services.email.email_output_formatter import (
    format_digest_markdown,
    format_digest_plaintext,
    format_digest_html
)

# Sample configuration - replace with your actual SMTP settings
SMTP_CONFIG = {
    'smtp_server': 'smtp.example.com',
    'smtp_port': 587,
    'smtp_username': 'your-email@example.com',
    'smtp_password': 'your-password',
    'from_email': 'your-email@example.com',
    'use_tls': True
}

# Sample workflow result data
SAMPLE_WORKFLOW_RESULT = {
    'workflow_name': 'daily_digest',
    'title': 'Daily Digest - May 24, 2024',
    'content': (
        '## Project Updates\n\n'
        '- Completed email snapshot functionality\n'
        '- Fixed bug in workflow execution\n\n'
        '## Next Steps\n\n'
        '- Implement user notifications\n'
        '- Add more test coverage\n\n'
        '## Metrics\n\n'
        '- 42 tasks completed\n'
        '- 8 issues resolved\n'
        '- 3 new features added'
    ),
    'source': {
        'url': 'https://example.com/digests/2024-05-24',
        'tags': ['digest', 'daily', 'may-2024']
    },
    'timestamp': '2024-05-24T10:30:00-07:00'
}

async def main():
    """Run the email snapshot demo."""
    # Initialize the email adapter
    email_adapter = EmailOutAdapter(SMTP_CONFIG)
    
    # Test with markdown formatter
    logger.info("Sending email with markdown formatter...")
    success = await email_adapter.send_formatted_output(
        workflow_result=SAMPLE_WORKFLOW_RESULT,
        formatter_func=format_digest_markdown,
        subject="[Test] Daily Digest - Markdown",
        recipient="recipient@example.com",
        save_snapshot=True,
        run_id="demo_markdown"
    )
    logger.info(f"Markdown email sent: {success}")
    
    # Test with plaintext formatter
    logger.info("Sending email with plaintext formatter...")
    success = await email_adapter.send_formatted_output(
        workflow_result=SAMPLE_WORKFLOW_RESULT,
        formatter_func=format_digest_plaintext,
        subject="[Test] Daily Digest - Plaintext",
        recipient="recipient@example.com",
        save_snapshot=True,
        run_id="demo_plaintext"
    )
    logger.info(f"Plaintext email sent: {success}")
    
    # Test with HTML formatter (if available)
    try:
        logger.info("Sending email with HTML formatter...")
        success = await email_adapter.send_formatted_output(
            workflow_result=SAMPLE_WORKFLOW_RESULT,
            formatter_func=format_digest_html,
            subject="[Test] Daily Digest - HTML",
            recipient="recipient@example.com",
            save_snapshot=True,
            run_id="demo_html"
        )
        logger.info(f"HTML email sent: {success}")
    except Exception as e:
        logger.warning(f"HTML formatter not available: {e}")
    
    logger.info("Demo complete. Check the data/logs/output_snapshots/ directory for snapshots.")

if __name__ == "__main__":
    asyncio.run(main())
