"""Digest Agent for generating content summaries and daily digests.

This agent processes content from a knowledge store and generates
formatted digests using prompt templates.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path

# Import BaseAgent from local module, models from single source of truth
from agents.base_agent import BaseAgent
from interfaces.agent_models import AgentInput, AgentOutput, AgentCapability

logger = logging.getLogger(__name__)


class DigestAgent(BaseAgent):
    """Agent that generates digests from stored content summaries."""
    
    def __init__(
        self,
        agent_id: str = "digest_agent",
        storage_path: Optional[Path] = None,
        prompt_template_path: Optional[Path] = None
    ):
        """Initialize the DigestAgent.
        
        Args:
            agent_id: Unique identifier for the agent
            storage_path: Path to content storage (defaults to ./data/knowledge)
            prompt_template_path: Path to prompt templates (defaults to ./prompts)
        """
        super().__init__(
            name="Digest Agent",
            description="Generates formatted digests from content summaries",
            agent_id=agent_id,
            version="2.0.0"
        )
        
        # Set default paths
        self.storage_path = storage_path or Path("./data/knowledge")
        self.prompt_template_path = prompt_template_path or Path("./prompts")
        
        # Register capabilities
        self._register_capabilities()
        
    def _register_capabilities(self):
        """Register agent capabilities."""
        self.add_capability(AgentCapability(
            name="generate_digest",
            description="Generate a formatted digest from content summaries",
            parameters={
                "user_id": "str (optional) - Filter by user",
                "limit": "int (optional) - Maximum summaries to include",
                "format": "str (optional) - Output format: 'markdown', 'html', 'json'"
            }
        ))
        
        self.add_capability(AgentCapability(
            name="query_summaries",
            description="Query stored content summaries",
            parameters={
                "user_id": "str (optional) - Filter by user",
                "date_from": "str (optional) - ISO date string",
                "date_to": "str (optional) - ISO date string",
                "tags": "List[str] (optional) - Filter by tags"
            }
        ))
    
    async def initialize(self) -> None:
        """Initialize the agent and verify dependencies."""
        try:
            # Ensure storage directory exists
            self.storage_path.mkdir(parents=True, exist_ok=True)
            
            # Verify prompt templates exist
            if not self.prompt_template_path.exists():
                logger.warning(f"Prompt template path does not exist: {self.prompt_template_path}")
            
            self._initialized = True
            logger.info(f"DigestAgent {self.agent_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing DigestAgent: {e}")
            raise
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process the request to generate a digest.
        
        Args:
            input_data: Agent input containing parameters for digest generation
            
        Returns:
            Agent output with the generated digest
        """
        start_time = datetime.utcnow()
        
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Processing digest request for task: {input_data.task_id}")
            
            # Extract parameters
            action = input_data.content.get("action", "generate_digest")
            params = input_data.content.get("parameters", {})
            
            if action == "generate_digest":
                result = await self._generate_digest(params)
            elif action == "query_summaries":
                result = await self._query_summaries(params)
            else:
                raise ValueError(f"Unknown action: {action}")
            
            # Calculate duration
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                task_id=input_data.task_id,
                status="success",
                result=result,
                metadata={
                    "action": action,
                    "parameters": params
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            logger.error(f"Error processing digest request: {e}")
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                task_id=input_data.task_id,
                status="error",
                error=str(e),
                result={},
                duration_ms=duration_ms
            )
    
    async def _generate_digest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a digest from stored summaries.
        
        Args:
            params: Parameters including user_id, limit, format
            
        Returns:
            Dictionary with digest content and metadata
        """
        # Query summaries
        summaries = await self._query_summaries_internal(
            user_id=params.get("user_id"),
            limit=params.get("limit", 10)
        )
        
        if not summaries:
            return {
                "digest": "No content available for digest generation.",
                "summary_count": 0,
                "format": params.get("format", "markdown")
            }
        
        # Generate digest based on format
        output_format = params.get("format", "markdown")
        
        if output_format == "markdown":
            digest_content = self._format_markdown_digest(summaries)
        elif output_format == "html":
            digest_content = self._format_html_digest(summaries)
        elif output_format == "json":
            digest_content = summaries  # Already in JSON format
        else:
            digest_content = self._format_markdown_digest(summaries)
        
        return {
            "digest": digest_content,
            "summary_count": len(summaries),
            "format": output_format,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _query_summaries(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query summaries based on parameters.
        
        Args:
            params: Query parameters
            
        Returns:
            Dictionary with summaries and metadata
        """
        summaries = await self._query_summaries_internal(
            user_id=params.get("user_id"),
            date_from=params.get("date_from"),
            date_to=params.get("date_to"),
            tags=params.get("tags"),
            limit=params.get("limit", 50)
        )
        
        return {
            "summaries": summaries,
            "count": len(summaries),
            "query_params": params
        }
    
    async def _query_summaries_internal(
        self,
        user_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Internal method to query summaries from storage.
        
        For MVP, this reads from JSON files in the storage directory.
        """
        summaries = []
        
        # Read all JSON files in storage directory
        for json_file in self.storage_path.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Apply filters
                if user_id and data.get("user_id") != user_id:
                    continue
                    
                if date_from:
                    created_at = datetime.fromisoformat(data.get("created_at", ""))
                    if created_at < datetime.fromisoformat(date_from):
                        continue
                        
                if date_to:
                    created_at = datetime.fromisoformat(data.get("created_at", ""))
                    if created_at > datetime.fromisoformat(date_to):
                        continue
                        
                if tags and not any(tag in data.get("tags", []) for tag in tags):
                    continue
                    
                summaries.append(data)
                
                if len(summaries) >= limit:
                    break
                    
            except Exception as e:
                logger.warning(f"Error reading {json_file}: {e}")
                continue
        
        # Sort by created_at descending
        summaries.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return summaries[:limit]
    
    def _format_markdown_digest(self, summaries: List[Dict[str, Any]]) -> str:
        """Format summaries as a Markdown digest."""
        lines = [
            "# Content Digest",
            f"\n*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}*",
            f"\n**Total items: {len(summaries)}**\n",
            "---\n"
        ]
        
        for i, summary in enumerate(summaries, 1):
            lines.append(f"## {i}. {summary.get('title', 'Untitled')}")
            
            # Metadata
            if summary.get('source'):
                lines.append(f"\n**Source:** {summary['source']}")
            if summary.get('created_at'):
                lines.append(f"**Date:** {summary['created_at']}")
            if summary.get('tags'):
                lines.append(f"**Tags:** {', '.join(summary['tags'])}")
            
            # Content
            lines.append(f"\n{summary.get('summary', summary.get('content', 'No content available'))}")
            
            # Key points if available
            if summary.get('key_points'):
                lines.append("\n**Key Points:**")
                for point in summary['key_points']:
                    lines.append(f"- {point}")
            
            lines.append("\n---\n")
        
        return "\n".join(lines)
    
    def _format_html_digest(self, summaries: List[Dict[str, Any]]) -> str:
        """Format summaries as HTML digest."""
        html_parts = [
            "<html><head><title>Content Digest</title></head><body>",
            "<h1>Content Digest</h1>",
            f"<p><em>Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</em></p>",
            f"<p><strong>Total items: {len(summaries)}</strong></p>",
            "<hr>"
        ]
        
        for i, summary in enumerate(summaries, 1):
            html_parts.append(f"<h2>{i}. {summary.get('title', 'Untitled')}</h2>")
            
            # Metadata
            metadata = []
            if summary.get('source'):
                metadata.append(f"<strong>Source:</strong> {summary['source']}")
            if summary.get('created_at'):
                metadata.append(f"<strong>Date:</strong> {summary['created_at']}")
            if summary.get('tags'):
                metadata.append(f"<strong>Tags:</strong> {', '.join(summary['tags'])}")
            
            if metadata:
                html_parts.append("<p>" + " | ".join(metadata) + "</p>")
            
            # Content
            html_parts.append(f"<p>{summary.get('summary', summary.get('content', 'No content available'))}</p>")
            
            # Key points if available
            if summary.get('key_points'):
                html_parts.append("<p><strong>Key Points:</strong></p><ul>")
                for point in summary['key_points']:
                    html_parts.append(f"<li>{point}</li>")
                html_parts.append("</ul>")
            
            html_parts.append("<hr>")
        
        html_parts.append("</body></html>")
        
        return "\n".join(html_parts)