"""CLI runner for testing the IngestionAgent.

This script provides a command-line interface for testing the IngestionAgent
with sample URL and PDF inputs.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import click
from datetime import datetime

from agents.ingestion_agent import IngestionAgent
from interfaces.agent_models import AgentInput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_input_file(file_path: str) -> Dict[str, Any]:
    """Load and validate input JSON file.
    
    Args:
        file_path: Path to input JSON file
        
    Returns:
        Dictionary containing input data
        
    Raises:
        click.ClickException: If file cannot be loaded or is invalid
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            
        # Validate required fields
        required_fields = ['task_id', 'task_type', 'content']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise click.ClickException(
                f"Input file missing required fields: {', '.join(missing_fields)}"
            )
            
        return data
        
    except json.JSONDecodeError:
        raise click.ClickException(f"Invalid JSON in input file: {file_path}")
    except FileNotFoundError:
        raise click.ClickException(f"Input file not found: {file_path}")


async def run_agent(agent: IngestionAgent, input_data: Dict[str, Any]) -> None:
    """Run the agent with the provided input data.
    
    Args:
        agent: Initialized IngestionAgent instance
        input_data: Input data dictionary
    """
    try:
        # Create AgentInput
        agent_input = AgentInput(
            task_id=input_data['task_id'],
            task_type=input_data['task_type'],
            source='cli',
            content=input_data['content'],
            metadata=input_data.get('metadata', {}),
            context=input_data.get('context', {})
        )
        
        # Process input
        output = await agent.process(agent_input)
        
        # Print results
        print("\nProcessing Results:")
        print("------------------")
        print(f"Task ID: {output.task_id}")
        print(f"Status: {output.status}")
        print(f"Duration: {output.duration_ms}ms")
        
        if output.status == "success":
            print("\nContent Details:")
            print(f"Content ID: {output.result['content_id']}")
            print(f"Content Type: {output.result['content_type']}")
            print(f"Content Length: {output.result['content_length']} characters")
            
            if output.result.get('metadata'):
                print("\nMetadata:")
                for key, value in output.result['metadata'].items():
                    if key != 'additional_metadata':
                        print(f"{key}: {value}")
        else:
            print(f"\nError: {output.error}")
            
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        raise click.ClickException(str(e))


@click.command()
@click.option(
    '--agent',
    type=click.Choice(['ingestion']),
    required=True,
    help='Agent to test'
)
@click.option(
    '--input',
    type=click.Path(exists=True),
    required=True,
    help='Path to input JSON file'
)
@click.option(
    '--storage-path',
    type=click.Path(),
    default='./data/knowledge',
    help='Path to content storage directory'
)
@click.option(
    '--temp-path',
    type=click.Path(),
    default='./data/temp',
    help='Path to temporary files directory'
)
def main(agent: str, input: str, storage_path: str, temp_path: str):
    """Run agent tests from the command line."""
    try:
        # Load input data
        input_data = load_input_file(input)
        
        # Initialize agent
        if agent == 'ingestion':
            agent_instance = IngestionAgent(
                storage_path=Path(storage_path),
                temp_path=Path(temp_path)
            )
        else:
            raise click.ClickException(f"Unsupported agent: {agent}")
            
        # Run agent
        asyncio.run(run_agent(agent_instance, input_data))
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 