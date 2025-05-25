"""
PDF Stream Handler for processing large PDF files without loading them entirely into memory.

This module provides utilities for streaming PDF content to prevent memory exhaustion
with large files.
"""

import io
import logging
from pathlib import Path
from typing import Iterator, Optional, Tuple
import PyPDF2

logger = logging.getLogger(__name__)


class PDFStreamHandler:
    """Handles streaming operations for large PDF files."""
    
    # Default chunk size for streaming (10MB)
    DEFAULT_CHUNK_SIZE = 10 * 1024 * 1024
    
    # Maximum file size for direct loading (50MB)
    MAX_DIRECT_LOAD_SIZE = 50 * 1024 * 1024
    
    def __init__(self, file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE):
        """
        Initialize PDF stream handler.
        
        Args:
            file_path: Path to the PDF file
            chunk_size: Size of chunks for streaming operations
        """
        self.file_path = Path(file_path)
        self.chunk_size = chunk_size
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        self.file_size = self.file_path.stat().st_size
        logger.info(f"Initialized PDFStreamHandler for {file_path} ({self.file_size} bytes)")
    
    def should_stream(self) -> bool:
        """
        Determine if the file should be streamed based on size.
        
        Returns:
            True if file should be streamed, False if it can be loaded directly
        """
        return self.file_size > self.MAX_DIRECT_LOAD_SIZE
    
    def extract_text_streaming(self) -> str:
        """
        Extract text from PDF using streaming to handle large files.
        
        Returns:
            Extracted text content
        """
        logger.info(f"Extracting text from PDF using streaming method")
        
        text_content = []
        
        try:
            with open(self.file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)
                
                total_pages = len(pdf_reader.pages)
                logger.info(f"Processing {total_pages} pages")
                
                # Process pages in chunks to manage memory
                for i, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                        
                        # Log progress every 100 pages
                        if (i + 1) % 100 == 0:
                            logger.info(f"Processed {i + 1}/{total_pages} pages")
                            
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {i}: {e}")
                        continue
            
            full_text = '\n'.join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from PDF")
            return full_text
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def extract_text_chunked(self, max_chars: Optional[int] = None) -> Iterator[str]:
        """
        Extract text from PDF in chunks, yielding text as it's processed.
        
        Args:
            max_chars: Maximum characters to extract (None for all)
            
        Yields:
            Text chunks as they are extracted
        """
        logger.info(f"Extracting text from PDF in chunks")
        
        total_chars = 0
        
        try:
            with open(self.file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)
                
                for i, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        
                        if page_text:
                            # Check character limit
                            if max_chars and total_chars + len(page_text) > max_chars:
                                remaining = max_chars - total_chars
                                if remaining > 0:
                                    yield page_text[:remaining]
                                logger.info(f"Reached character limit at page {i}")
                                return
                            
                            yield page_text
                            total_chars += len(page_text)
                            
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {i}: {e}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def get_metadata(self) -> dict:
        """
        Extract metadata from PDF without loading full content.
        
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with open(self.file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file, strict=False)
                
                metadata = {
                    'page_count': len(pdf_reader.pages),
                    'file_size': self.file_size,
                    'file_name': self.file_path.name,
                }
                
                # Extract document info if available
                if pdf_reader.metadata:
                    doc_info = pdf_reader.metadata
                    metadata.update({
                        'title': doc_info.get('/Title', ''),
                        'author': doc_info.get('/Author', ''),
                        'subject': doc_info.get('/Subject', ''),
                        'creator': doc_info.get('/Creator', ''),
                        'producer': doc_info.get('/Producer', ''),
                        'creation_date': str(doc_info.get('/CreationDate', '')),
                        'modification_date': str(doc_info.get('/ModDate', '')),
                    })
                
                return metadata
                
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            return {
                'file_size': self.file_size,
                'file_name': self.file_path.name,
                'error': str(e)
            }
    
    def validate_pdf(self) -> Tuple[bool, Optional[str]]:
        """
        Validate that the file is a valid PDF.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(self.file_path, 'rb') as pdf_file:
                # Check PDF header
                header = pdf_file.read(5)
                if header != b'%PDF-':
                    return False, "Invalid PDF header"
                
                # Try to create reader
                pdf_file.seek(0)
                PyPDF2.PdfReader(pdf_file, strict=False)
                
                return True, None
                
        except Exception as e:
            return False, f"Invalid PDF: {str(e)}"


def process_pdf_safely(file_path: str, max_size: int = 100 * 1024 * 1024) -> dict:
    """
    Process a PDF file safely with size limits and streaming.
    
    Args:
        file_path: Path to the PDF file
        max_size: Maximum file size to process (default 100MB)
        
    Returns:
        Dictionary containing extracted content and metadata
    """
    handler = PDFStreamHandler(file_path)
    
    # Validate file size
    if handler.file_size > max_size:
        raise ValueError(f"PDF file too large: {handler.file_size} bytes (max: {max_size})")
    
    # Validate PDF
    is_valid, error = handler.validate_pdf()
    if not is_valid:
        raise ValueError(error)
    
    # Get metadata
    metadata = handler.get_metadata()
    
    # Extract text based on file size
    if handler.should_stream():
        logger.info("Using streaming extraction for large PDF")
        text = handler.extract_text_streaming()
    else:
        logger.info("Using direct extraction for small PDF")
        # For smaller files, we can still use the regular method
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = '\n'.join(page.extract_text() for page in pdf_reader.pages)
    
    return {
        'content': text,
        'metadata': metadata,
        'file_size': handler.file_size,
        'extraction_method': 'streaming' if handler.should_stream() else 'direct'
    }