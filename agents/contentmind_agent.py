"""Content Mind Agent for generating content summaries.

This agent processes content from the knowledge store and generates
concise summaries using prompt templates.
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


class ContentMindAgent(BaseAgent):
    """Agent that generates summaries from ingested content."""
    
    def __init__(
        self,
        agent_id: str = "contentmind_agent",
        storage_path: Optional[Path] = None,
        prompt_template_path: Optional[Path] = None
    ):
        """Initialize the ContentMindAgent.
        
        Args:
            agent_id: Unique identifier for the agent
            storage_path: Path to content storage (defaults to ./data/knowledge)
            prompt_template_path: Path to prompt templates (defaults to ./prompts)
        """
        super().__init__(
            name="Content Mind Agent",
            description="Generates summaries from ingested content",
            agent_id=agent_id,
            version="1.0.0"
        )
        
        # Set default paths
        self.storage_path = storage_path or Path("./data/knowledge")
        self.prompt_template_path = prompt_template_path or Path("./prompts")
        
        # Register capabilities
        self._register_capabilities()
        
    def _register_capabilities(self):
        """Register agent capabilities."""
        self.add_capability(AgentCapability(
            name="generate_summary",
            description="Generate a summary from ingested content",
            parameters={
                "content_id": "str - ID of content to summarize",
                "max_length": "int (optional) - Maximum summary length",
                "format": "str (optional) - Output format: 'markdown', 'html', 'json'"
            }
        ))
        
        self.add_capability(AgentCapability(
            name="query_content",
            description="Query stored content",
            parameters={
                "content_type": "str (optional) - Filter by content type",
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
            logger.info(f"ContentMindAgent {self.agent_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing ContentMindAgent: {e}")
            raise
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process the request to generate a summary.
        
        Args:
            input_data: Agent input containing parameters for summary generation
            
        Returns:
            Agent output with the generated summary
        """
        start_time = datetime.utcnow()
        
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Processing summary request for task: {input_data.task_id}")
            
            # Extract parameters
            action = input_data.content.get("action", "generate_summary")
            params = input_data.content.get("parameters", {})
            
            if action == "generate_summary":
                result = await self._generate_summary(params)
            elif action == "query_content":
                result = await self._query_content(params)
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
            logger.error(f"Error processing summary request: {e}")
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                task_id=input_data.task_id,
                status="error",
                error=str(e),
                result={},
                duration_ms=duration_ms
            )
    
    async def _generate_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary from ingested content.
        
        Args:
            params: Parameters including content_id, max_length, format
            
        Returns:
            Dictionary with summary content and metadata
        """
        content_id = params.get("content_id")
        if not content_id:
            raise ValueError("content_id is required")
            
        # Load content from storage
        content_file = self.storage_path / f"{content_id}.json"
        if not content_file.exists():
            raise ValueError(f"Content not found: {content_id}")
            
        with open(content_file, 'r') as f:
            content_data = json.load(f)
            
        # Generate summary using prompt template
        summary = await self._summarize_content(
            content_data["content"],
            max_length=params.get("max_length", 500)
        )
        
        # Format output
        output_format = params.get("format", "markdown")
        if output_format == "markdown":
            formatted_summary = self._format_markdown_summary(summary, content_data)
        elif output_format == "html":
            formatted_summary = self._format_html_summary(summary, content_data)
        elif output_format == "json":
            formatted_summary = {
                "summary": summary,
                "content_id": content_id,
                "metadata": content_data.get("metadata", {})
            }
        else:
            formatted_summary = self._format_markdown_summary(summary, content_data)
            
        # Save summary to storage
        summary_data = {
            "id": f"summary_{content_id}",
            "content_id": content_id,
            "summary": summary,
            "formatted_summary": formatted_summary,
            "format": output_format,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": content_data.get("metadata", {})
        }
        
        self._save_summary(summary_data)
        
        return {
            "summary": formatted_summary,
            "content_id": content_id,
            "format": output_format,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def _query_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query content based on parameters.
        
        Args:
            params: Query parameters
            
        Returns:
            Dictionary with content and metadata
        """
        content_list = []
        
        # Read all JSON files in storage directory
        for json_file in self.storage_path.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Apply filters
                if params.get("content_type") and data.get("type") != params["content_type"]:
                    continue
                    
                if params.get("date_from"):
                    created_at = datetime.fromisoformat(data.get("created_at", ""))
                    if created_at < datetime.fromisoformat(params["date_from"]):
                        continue
                        
                if params.get("date_to"):
                    created_at = datetime.fromisoformat(data.get("created_at", ""))
                    if created_at > datetime.fromisoformat(params["date_to"]):
                        continue
                        
                if params.get("tags") and not any(tag in data.get("tags", []) for tag in params["tags"]):
                    continue
                    
                content_list.append(data)
                    
            except Exception as e:
                logger.error(f"Error reading content file {json_file}: {e}")
                continue
                
        return {
            "content": content_list,
            "count": len(content_list),
            "query_params": params
        }
    
    async def _summarize_content(self, content: str, max_length: int = 500) -> str:
        """Generate a summary of the content.
        
        Args:
            content: The content to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Generated summary
        """
        # TODO: Implement actual summarization using LLM
        # For now, return a simple truncation
        if len(content) <= max_length:
            return content
            
        return content[:max_length] + "..."
    
    def _format_markdown_summary(self, summary: str, content_data: Dict[str, Any]) -> str:
        """Format summary in markdown.
        
        Args:
            summary: The generated summary
            content_data: Original content data
            
        Returns:
            Formatted markdown
        """
        metadata = content_data.get("metadata", {})
        title = metadata.get("title", "Untitled")
        
        return f"""# {title}

{summary}

---
*Source: {metadata.get("source", "Unknown")}*
*Generated: {datetime.utcnow().isoformat()}*
"""
    
    def _format_html_summary(self, summary: str, content_data: Dict[str, Any]) -> str:
        """Format summary in HTML.
        
        Args:
            summary: The generated summary
            content_data: Original content data
            
        Returns:
            Formatted HTML
        """
        metadata = content_data.get("metadata", {})
        title = metadata.get("title", "Untitled")
        
        return f"""<div class="summary">
    <h1>{title}</h1>
    <div class="content">{summary}</div>
    <div class="metadata">
        <p>Source: {metadata.get("source", "Unknown")}</p>
        <p>Generated: {datetime.utcnow().isoformat()}</p>
    </div>
</div>"""
    
    def _save_summary(self, summary_data: Dict[str, Any]) -> None:
        """Save summary to storage.
        
        Args:
            summary_data: Summary data to save
        """
        summary_file = self.storage_path / f"{summary_data['id']}.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary_data, f, indent=2) 