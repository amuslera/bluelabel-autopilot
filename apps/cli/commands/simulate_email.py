"""CLI command for simulating email triggers with PDF attachments.

This module provides a command-line interface for manually triggering
the email-to-DAG workflow with PDF files.
"""

import asyncio
import click
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from services.email.email_dag_connector import EmailDAGConnector

logger = logging.getLogger(__name__)

@click.command()
@click.option('--file', '-f', required=True, type=click.Path(exists=True),
              help='Path to PDF file to simulate as email attachment')
@click.option('--subject', '-s', default='Simulated Email',
              help='Email subject line')
@click.option('--from', '-f', 'from_email', default='simulator@example.com',
              help='Sender email address')
@click.option('--to', '-t', default='recipient@example.com',
              help='Recipient email address')
def simulate_email(file: str, subject: str, from_email: str, to: str):
    """Simulate receiving an email with a PDF attachment.
    
    This command triggers the email-to-DAG workflow by simulating
    an email event with the specified PDF file as an attachment.
    """
    try:
        # Validate PDF file
        pdf_path = Path(file)
        if not pdf_path.suffix.lower() == '.pdf':
            raise click.BadParameter('File must be a PDF')
            
        # Create email event data
        email_data = {
            'from': from_email,
            'to': to,
            'subject': subject,
            'timestamp': datetime.now().isoformat(),
            'attachments': [{
                'filename': pdf_path.name,
                'content_type': 'application/pdf',
                'file_path': str(pdf_path)
            }]
        }
        
        # Initialize connector and process event
        connector = EmailDAGConnector()
        dag_id = asyncio.run(connector.process_email_event(email_data))
        
        if dag_id:
            click.echo(f"✅ Successfully triggered DAG: {dag_id}")
            click.echo(f"📁 PDF saved to: {connector.input_base_path / dag_id / 'source.pdf'}")
            click.echo(f"📝 Metadata saved to: {connector.input_base_path / dag_id / 'metadata.json'}")
        else:
            click.echo("❌ Failed to trigger DAG - no PDF attachment found")
            
    except Exception as e:
        logger.error(f"Error simulating email: {e}")
        raise click.ClickException(str(e))

if __name__ == '__main__':
    simulate_email() 