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

from agents.base_agent import AgentInput, AgentOutput
from agents.digest_agent import DigestAgent


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLIRunner:
    """Simple CLI runner for agent operations."""
    
    def __init__(self):
        self.agents = {
            'digest': DigestAgent()
        }
    
    async def run_agent(self, agent_name: str, input_data: Dict[str, Any]) -> AgentOutput:
        """Run a specific agent with the given input."""
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent = self.agents[agent_name]
        agent_input = AgentInput(
            task_id=input_data.get('task_id', 'cli-task'),
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
    run_parser.add_argument('agent', choices=['digest'], help='Agent to run')
    run_parser.add_argument('input', help='JSON input data')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    runner = CLIRunner()
    
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
                print(json.dumps({
                    'status': result.status,
                    'content': result.content,
                    'metadata': result.metadata
                }, indent=2))
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            sys.exit(1)
    
    asyncio.run(execute())


if __name__ == '__main__':
    main()