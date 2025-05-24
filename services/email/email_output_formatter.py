"""
Email Output Formatter

This module provides functions to format workflow output into email-friendly formats.
It supports both markdown and plaintext output for maximum compatibility.
"""

from datetime import datetime
from typing import Dict, Any, Optional
import textwrap

def format_timestamp(timestamp: Optional[str] = None) -> str:
    """Format a timestamp for display.
    
    Args:
        timestamp: ISO format timestamp string. If None, uses current time.
        
    Returns:
        Formatted date and time string.
    """
    if timestamp:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    else:
        dt = datetime.utcnow()
    
    return dt.strftime('%A, %B %d, %Y at %I:%M %p %Z')

def format_digest_markdown(digest_data: Dict[str, Any]) -> str:
    """Format digest data into markdown for email.
    
    Args:
        digest_data: Dictionary containing digest information with keys:
                   - title: (str) Title of the digest
                   - content: (str) Main content
                   - source: (dict, optional) Source information
                     - url: (str, optional) Source URL
                     - tags: (list[str], optional) List of tags
                   - timestamp: (str, optional) ISO format timestamp
                   
    Returns:
        Formatted markdown string ready for email.
    """
    # Extract data with defaults
    title = digest_data.get('title', 'Untitled Digest')
    content = digest_data.get('content', '')
    source = digest_data.get('source', {})
    timestamp = digest_data.get('timestamp')
    
    # Build markdown sections
    sections = [f"# {title}\n"]
    
    # Add timestamp if available
    if timestamp:
        sections.append(f"*Generated on {format_timestamp(timestamp)}*\n")
    
    # Add content
    sections.append("## Summary\n" + content + "\n")
    
    # Add source information if available
    if source:
        source_info = []
        if 'url' in source:
            source_info.append(f"[Source]({source['url']})")
        if 'tags' in source and source['tags']:
            tags = ' '.join(f'`{tag}`' for tag in source['tags'])
            source_info.append(f"Tags: {tags}")
            
        if source_info:
            sections.append("### Source\n" + "  \n".join(source_info) + "\n")
    
    return "\n".join(sections)

def format_digest_plaintext(digest_data: Dict[str, Any], line_width: int = 72) -> str:
    """Format digest data into plaintext for email.
    
    Args:
        digest_data: Dictionary containing digest information (same as markdown version)
        line_width: Maximum line width for text wrapping
        
    Returns:
        Formatted plaintext string ready for email.
    """
    # Extract data with defaults
    title = digest_data.get('title', 'Untitled Digest')
    content = digest_data.get('content', '')
    source = digest_data.get('source', {})
    timestamp = digest_data.get('timestamp')
    
    # Build plaintext sections
    sections = [f"{title}", "=" * len(title), ""]
    
    # Add timestamp if available
    if timestamp:
        sections.append(f"Generated on {format_timestamp(timestamp)}\n")
    
    # Add content with text wrapping
    wrapped_content = textwrap.fill(content, width=line_width)
    sections.extend(["SUMMARY", "-------", wrapped_content, ""])
    
    # Add source information if available
    if source:
        source_info = []
        if 'url' in source:
            source_info.append(f"Source: {source['url']}")
        if 'tags' in source and source['tags']:
            tags = ', '.join(source['tags'])
            source_info.append(f"Tags: {tags}")
            
        if source_info:
            sections.extend(["SOURCE", "-----", "\n".join(source_info)])
    
    return "\n".join(sections)
