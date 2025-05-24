"""Ingestion Agent for processing URL and PDF content.

This agent handles the ingestion of content from URLs and PDFs,
extracting text and metadata for further processing.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from pathlib import Path
import aiohttp
import PyPDF2
import io
import re
from urllib.parse import urlparse

from interfaces.agent_models import (
    AgentInput, AgentOutput, AgentCapability, ContentMetadata
)

logger = logging.getLogger(__name__)


class IngestionAgent:
    """Agent that processes URL and PDF content for ingestion."""
    
    def __init__(
        self,
        agent_id: str = "ingestion_agent",
        storage_path: Optional[Path] = None,
        temp_path: Optional[Path] = None
    ):
        """Initialize the IngestionAgent.
        
        Args:
            agent_id: Unique identifier for the agent
            storage_path: Path to content storage (defaults to ./data/knowledge)
            temp_path: Path for temporary files (defaults to ./data/temp)
        """
        self.agent_id = agent_id
        self.name = "Ingestion Agent"
        self.description = "Processes URL and PDF content for ingestion"
        self.version = "1.0.0"
        
        # Set default paths
        self.storage_path = storage_path or Path("./data/knowledge")
        self.temp_path = temp_path or Path("./data/temp")
        
        # Register capabilities
        self._register_capabilities()
        self._initialized = False
        
    def _register_capabilities(self):
        """Register agent capabilities."""
        self.capabilities = [
            AgentCapability(
                name="process_url",
                description="Process content from a URL",
                parameters={
                    "url": "str - URL to process",
                    "extract_metadata": "bool (optional) - Whether to extract metadata",
                    "max_content_length": "int (optional) - Maximum content length to process"
                }
            ),
            AgentCapability(
                name="process_pdf",
                description="Process content from a PDF file",
                parameters={
                    "pdf_data": "bytes - PDF file content",
                    "filename": "str - Original filename",
                    "extract_metadata": "bool (optional) - Whether to extract metadata"
                }
            )
        ]
    
    async def initialize(self) -> None:
        """Initialize the agent and verify dependencies."""
        try:
            # Ensure storage directories exist
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self.temp_path.mkdir(parents=True, exist_ok=True)
            
            self._initialized = True
            logger.info(f"IngestionAgent {self.agent_id} initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing IngestionAgent: {e}")
            raise
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Process the content ingestion request.
        
        Args:
            input_data: Agent input containing content to process
            
        Returns:
            Agent output with processed content
        """
        start_time = datetime.utcnow()
        
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"Processing ingestion request for task: {input_data.task_id}")
            
            # Process based on task type
            if input_data.task_type == "url":
                result = await self._process_url(input_data.content)
            elif input_data.task_type == "pdf":
                result = await self._process_pdf(input_data.content)
            else:
                raise ValueError(f"Unsupported task type: {input_data.task_type}")
            
            # Calculate duration
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                task_id=input_data.task_id,
                status="success",
                result=result,
                metadata={
                    "task_type": input_data.task_type,
                    "source": input_data.source
                },
                duration_ms=duration_ms
            )
            
        except Exception as e:
            logger.error(f"Error processing ingestion request: {e}")
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            return AgentOutput(
                task_id=input_data.task_id,
                status="error",
                error=str(e),
                result={},
                duration_ms=duration_ms
            )
    
    async def _process_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process content from a URL.
        
        Args:
            params: Parameters including URL and processing options
            
        Returns:
            Dictionary with processed content and metadata
        """
        url = params.get("url")
        if not url:
            raise ValueError("URL is required")
            
        extract_metadata = params.get("extract_metadata", True)
        max_length = params.get("max_content_length", 1000000)  # 1MB default
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to fetch URL: {response.status}")
                    
                content_type = response.headers.get("content-type", "")
                
                # Handle PDF content
                if "application/pdf" in content_type:
                    pdf_data = await response.read()
                    return await self._process_pdf({
                        "pdf_data": pdf_data,
                        "filename": urlparse(url).path.split("/")[-1],
                        "extract_metadata": extract_metadata
                    })
                
                # Handle HTML/text content
                text = await response.text()
                if len(text) > max_length:
                    text = text[:max_length]
                
                # Create metadata
                metadata = ContentMetadata(
                    content_id=f"url_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    content_type="url",
                    source=url,
                    title=self._extract_title(text),
                    created_at=datetime.utcnow(),
                    processed_at=datetime.utcnow(),
                    content_length=len(text),
                    additional_metadata={
                        "content_type": content_type
                    }
                )
                
                # Save to storage
                content_data = {
                    "id": metadata.content_id,
                    "type": "url",
                    "content": text,
                    "metadata": metadata.dict(),
                    "created_at": metadata.created_at.isoformat()
                }
                
                self._save_content(content_data)
                
                return {
                    "content_id": metadata.content_id,
                    "content_type": "url",
                    "metadata": metadata.dict(),
                    "content_length": len(text)
                }
    
    async def _process_pdf(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process content from a PDF file.
        
        Args:
            params: Parameters including PDF data and processing options
            
        Returns:
            Dictionary with processed content and metadata
        """
        pdf_data = params.get("pdf_data")
        filename = params.get("filename", "document.pdf")
        extract_metadata = params.get("extract_metadata", True)
        
        if not pdf_data:
            raise ValueError("PDF data is required")
        
        # Process PDF
        pdf_file = io.BytesIO(pdf_data)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        # Create metadata
        additional_metadata = {
            "filename": filename,
            "page_count": len(pdf_reader.pages)
        }
        
        if pdf_reader.metadata:
            additional_metadata.update({
                "title": pdf_reader.metadata.get("/Title"),
                "author": pdf_reader.metadata.get("/Author"),
                "subject": pdf_reader.metadata.get("/Subject"),
                "creator": pdf_reader.metadata.get("/Creator")
            })
        
        metadata = ContentMetadata(
            content_id=f"pdf_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            content_type="pdf",
            source=filename,
            title=additional_metadata.get("title"),
            author=additional_metadata.get("author"),
            created_at=datetime.utcnow(),
            processed_at=datetime.utcnow(),
            content_length=len(text),
            additional_metadata=additional_metadata
        )
        
        # Save to storage
        content_data = {
            "id": metadata.content_id,
            "type": "pdf",
            "content": text,
            "metadata": metadata.dict(),
            "created_at": metadata.created_at.isoformat()
        }
        
        self._save_content(content_data)
        
        return {
            "content_id": metadata.content_id,
            "content_type": "pdf",
            "metadata": metadata.dict(),
            "content_length": len(text)
        }
    
    def _extract_title(self, html_content: str) -> Optional[str]:
        """Extract title from HTML content."""
        title_match = re.search(r"<title>(.*?)</title>", html_content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        return None
    
    def _save_content(self, content_data: Dict[str, Any]) -> None:
        """Save processed content to storage."""
        content_id = content_data["id"]
        file_path = self.storage_path / f"{content_id}.json"
        
        with open(file_path, "w") as f:
            json.dump(content_data, f, indent=2)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return the agent's capabilities."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "initialized": self._initialized,
            "capabilities": [cap.dict() for cap in self.capabilities]
        } 