#!/usr/bin/env python3
"""
CLI Runner for Bluelabel Autopilot
A simple command-line interface for running agents and processing content.

Examples:
    # Process URL content with IngestionAgent
    python cli_runner.py run ingestion '{
        "task_id": "test-url",
        "task_type": "url",
        "content": {
            "url": "https://example.com/sample-article"
        }
    }'

    # Process PDF content with IngestionAgent
    python cli_runner.py run ingestion '{
        "task_id": "test-pdf",
        "task_type": "pdf",
        "content": {
            "file_path": "tests/sample.pdf"
        }
    }'

    # Generate digest with DigestAgent
    python cli_runner.py run digest '{
        "task_id": "test-digest",
        "content": {
            "content_id": "digest_abc123",
            "content_type": "article",
            "text": "Sample text to digest..."
        }
    }'

    # Generate formatted digest
    python cli_runner.py digest --format markdown --limit 5

    # Add a summary to the digest
    python cli_runner.py add-summary "Test Source" "Sample summary text" --url "https://example.com"
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
import logging
from pydantic import ValidationError

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
    
    def validate_input(self, agent_name: str, input_data: Dict[str, Any]) -> AgentInput:
        """Validate input data against the AgentInput schema.
        
        Args:
            agent_name: Name of the agent to run
            input_data: Input data dictionary
            
        Returns:
            Validated AgentInput object
            
        Raises:
            ValueError: If validation fails
        """
        try:
            # Add source field if not present
            if 'source' not in input_data:
                input_data['source'] = 'cli'
            
            # Validate using Pydantic model
            agent_input = AgentInput.parse_obj(input_data)
            
            # Additional agent-specific validation
            if agent_name == 'ingestion':
                if not agent_input.task_type:
                    raise ValueError("task_type is required for ingestion agent")
                if agent_input.task_type == 'pdf':
                    file_path = agent_input.content.get('file_path')
                    if not file_path:
                        raise ValueError("file_path is required in content for PDF processing")
                    if not Path(file_path).exists():
                        raise ValueError(f"PDF file not found: {file_path}")
            
            return agent_input
            
        except ValidationError as e:
            # Format validation errors for better readability
            error_messages = []
            for error in e.errors():
                field = " -> ".join(str(x) for x in error["loc"])
                message = error["msg"]
                error_messages.append(f"{field}: {message}")
            
            raise ValueError(
                "Input validation failed:\n" + 
                "\n".join(error_messages) + 
                "\n\nExample valid input:\n" +
                json.dumps({
                    "task_id": "example-task",
                    "task_type": "url",
                    "source": "cli",
                    "content": {
                        "url": "https://example.com"
                    },
                    "metadata": {},
                    "context": {}
                }, indent=2)
            )
    
    async def run_agent(self, agent_name: str, input_data: Dict[str, Any]) -> AgentOutput:
        """Run a specific agent with the given input.
        
        Args:
            agent_name: Name of the agent to run
            input_data: Input data dictionary
            
        Returns:
            AgentOutput from the agent
            
        Raises:
            ValueError: If agent name is unknown or input validation fails
        """
        if agent_name not in self.agents:
            raise ValueError(f"Unknown agent: {agent_name}")
        
        agent = self.agents[agent_name]
        
        # Validate input data
        agent_input = self.validate_input(agent_name, input_data)
        
        logger.info(f"Running {agent_name} agent with task_id: {agent_input.task_id}")
        result = await agent.process(agent_input)
        logger.info(f"Agent completed with status: {result.status}")
        
        return result
    
    async def generate_digest(self, output_format: str = 'markdown', limit: Optional[int] = None):
        """Generate a digest from stored summaries."""
        input_data = {
            'task_id': 'digest-generation',
            'source': 'cli',
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
            'source': 'cli',
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
    parser = argparse.ArgumentParser(
        description='Bluelabel Autopilot CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Available Agents:
  - ingestion: Process URL and PDF content
  - digest: Generate and manage content digests

Sample Input Files:
  - tests/sample_url_input.json: Example URL processing input
  - tests/sample_pdf_input.json: Example PDF processing input
  - tests/sample_digest_input.json: Example digest generation input

For more examples and detailed usage, see the script's docstring.
"""
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Digest command
    digest_parser = subparsers.add_parser('digest', help='Generate content digest')
    digest_parser.add_argument('--format', choices=['markdown', 'html', 'json'], 
                             default='markdown', help='Output format (default: markdown)')
    digest_parser.add_argument('--limit', type=int, help='Limit number of items in output')
    
    # Add summary command
    add_parser = subparsers.add_parser('add-summary', help='Add a summary to the digest')
    add_parser.add_argument('source', help='Source of the content (e.g., website name)')
    add_parser.add_argument('summary', help='Summary text to add')
    add_parser.add_argument('--url', help='Optional URL for the source content')
    
    # Run agent command (generic)
    run_parser = subparsers.add_parser('run', help='Run an agent with JSON input')
    run_parser.add_argument('agent', choices=['digest', 'ingestion'], 
                          help='Agent to run (digest or ingestion)')
    run_parser.add_argument('input', help='JSON input data or path to input file')
    
    # Common options
    parser.add_argument('--storage-path', type=Path, default='./data/knowledge',
                       help='Path to content storage directory (default: ./data/knowledge)')
    parser.add_argument('--temp-path', type=Path, default='./data/temp',
                       help='Path to temporary files directory (default: ./data/temp)')
    
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
                # Check if input is a file path
                input_path = Path(args.input)
                if input_path.exists():
                    with open(input_path) as f:
                        input_data = json.load(f)
                else:
                    try:
                        input_data = json.loads(args.input)
                    except json.JSONDecodeError:
                        print(f"Error: Invalid JSON input. Please provide valid JSON or a path to a JSON file.")
                        print("\nExample input format:")
                        print(json.dumps({
                            "task_id": "example-task",
                            "task_type": "url",
                            "source": "cli",
                            "content": {
                                "url": "https://example.com"
                            },
                            "metadata": {},
                            "context": {}
                        }, indent=2))
                        sys.exit(1)
                
                try:
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
                        
                except ValueError as e:
                    print(f"\nError: {str(e)}")
                    sys.exit(1)
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            sys.exit(1)
    
    asyncio.run(execute())


if __name__ == '__main__':
    main()