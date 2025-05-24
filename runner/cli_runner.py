#!/usr/bin/env python3
"""
CLI Runner for Bluelabel Autopilot
A simple command-line interface for running agents and processing content.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import models from single source of truth
from interfaces.agent_models import AgentInput, AgentOutput
from agents.digest_agent import DigestAgent
from agents.ingestion_agent import IngestionAgent


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLIRunner:
    """Simple CLI runner for agent operations."""
    
    def __init__(self, storage_path: Optional[Path] = None, temp_path: Optional[Path] = None):
        """Initialize the CLI runner.
        
        Args:
            storage_path: Path to content storage directory
            temp_path: Path to temporary files directory
        """
        self.storage_path = storage_path or Path("./data/knowledge")
        self.temp_path = temp_path or Path("./data/temp")
        
        # Initialize agents
        self.agents = {
            'digest': DigestAgent(),
            'ingestion': IngestionAgent(
                storage_path=self.storage_path,
                temp_path=self.temp_path
            )
        }
    
    async def run_agent(self, agent_name: str, input_data: Dict[str, Any]) -> AgentOutput:
        """Run a specific agent with the given input.
        
        Args:
            agent_name: Name of the agent to run
            input_data: Input data dictionary
            
        Returns:
            AgentOutput from the agent
            
        Raises:
            ValueError: If agent name is unknown
        """
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent = self.agents[agent_name]
        
        # Create AgentInput based on agent type
        if agent_name == 'ingestion':
            agent_input = AgentInput(
                task_id=input_data.get('task_id', 'cli-task'),
                task_type=input_data.get('task_type', 'url'),
                source='cli',
                content=input_data.get('content', {}),
                metadata=input_data.get('metadata', {}),
                context=input_data.get('context', {})
            )
        else:
            agent_input = AgentInput(
                task_id=input_data.get('task_id', 'cli-task'),
                source='cli',
                content=input_data.get('content', {}),
                metadata=input_data.get('metadata', {})
            )
        
        logger.info(f"Running {agent_name} agent with task_id: {agent_input.task_id}")
        result = await agent.process(agent_input)
        logger.info(f"Agent completed with status: {result.status}")
        
        return result
    
    async def generate_digest(self, output_format: str = 'markdown', limit: Optional[int] = None):
        """Generate a digest from stored summaries."""
        input_data = {
            'task_id': 'digest-generation',
            'content': {
                'action': 'generate_digest',
                'format': output_format,
                'limit': limit
            }
        }
        
        result = await self.run_agent('digest', input_data)
        return result
    
    async def add_summary(self, source: str, summary: str, url: Optional[str] = None):
        """Add a new summary to the digest store."""
        input_data = {
            'task_id': 'add-summary',
            'content': {
                'action': 'add_summary',
                'source': source,
                'summary': summary,
                'url': url
            }
        }
        
        result = await self.run_agent('digest', input_data)
        return result


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description='Bluelabel Autopilot CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Digest command
    digest_parser = subparsers.add_parser('digest', help='Generate content digest')
    digest_parser.add_argument('--format', choices=['markdown', 'html', 'json'], 
                             default='markdown', help='Output format')
    digest_parser.add_argument('--limit', type=int, help='Limit number of items')
    
    # Add summary command
    add_parser = subparsers.add_parser('add-summary', help='Add a summary to the digest')
    add_parser.add_argument('source', help='Source of the content')
    add_parser.add_argument('summary', help='Summary text')
    add_parser.add_argument('--url', help='Optional URL for the source')
    
    # Run agent command (generic)
    run_parser = subparsers.add_parser('run', help='Run an agent with JSON input')
    run_parser.add_argument('agent', choices=['digest', 'ingestion'], help='Agent to run')
    run_parser.add_argument('input', help='JSON input data')
    
    # Common options
    parser.add_argument('--storage-path', type=Path, default='./data/knowledge',
                       help='Path to content storage directory')
    parser.add_argument('--temp-path', type=Path, default='./data/temp',
                       help='Path to temporary files directory')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    runner = CLIRunner(
        storage_path=args.storage_path,
        temp_path=args.temp_path
    )
    
    async def execute():
        try:
            if args.command == 'digest':
                result = await runner.generate_digest(args.format, args.limit)
                print(result.content)
                
            elif args.command == 'add-summary':
                result = await runner.add_summary(args.source, args.summary, args.url)
                print(f"Summary added successfully: {result.status}")
                
            elif args.command == 'run':
                input_data = json.loads(args.input)
                result = await runner.run_agent(args.agent, input_data)
                
                # Print results in a structured format
                print("\nProcessing Results:")
                print("------------------")
                print(f"Task ID: {result.task_id}")
                print(f"Status: {result.status}")
                print(f"Duration: {result.duration_ms}ms")
                
                if result.status == "success":
                    if args.agent == 'ingestion':
                        print("\nContent Details:")
                        print(f"Content ID: {result.result['content_id']}")
                        print(f"Content Type: {result.result['content_type']}")
                        print(f"Content Length: {result.result['content_length']} characters")
                        
                        if result.result.get('metadata'):
                            print("\nMetadata:")
                            for key, value in result.result['metadata'].items():
                                if key != 'additional_metadata':
                                    print(f"{key}: {value}")
                    else:
                        print("\nResult:")
                        print(json.dumps(result.result, indent=2))
                else:
                    print(f"\nError: {result.error}")
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            sys.exit(1)
    
    asyncio.run(execute())


if __name__ == '__main__':
    main()