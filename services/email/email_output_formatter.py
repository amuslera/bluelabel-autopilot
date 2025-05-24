"""
Email Output Formatter

This module provides functions to format workflow output into email-friendly formats.
It supports HTML, markdown, and plaintext output for maximum compatibility.
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
import textwrap
import html

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


def format_digest_html(digest_data: Dict[str, Any]) -> str:
    """Format digest data into HTML for email.
    
    Args:
        digest_data: Dictionary containing digest information with keys:
                   - title: (str) Title of the digest
                   - content: (str) Main content (can contain markdown)
                   - source: (dict, optional) Source information
                     - url: (str, optional) Source URL
                     - tags: (list[str], optional) List of tags
                   - timestamp: (str, optional) ISO format timestamp
                   
    Returns:
        Formatted HTML string ready for email.
    """
    # Extract data with defaults
    title = digest_data.get('title', 'Untitled Digest')
    content = digest_data.get('content', '')
    source = digest_data.get('source', {})
    timestamp = digest_data.get('timestamp')
    
    # Escape all content to prevent XSS
    safe_title = html.escape(title)
    safe_content = html.escape(content)
    
    # Convert markdown-like formatting to HTML
    # Start with the escaped content
    html_content = safe_content
    
    # Convert markdown headers (## -> h2, ### -> h3, etc.)
    lines = html_content.split('\n')
    in_list = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('## '):
            lines[i] = f'<h2>{line[3:]}</h2>'
        elif line.startswith('### '):
            lines[i] = f'<h3>{line[4:]}</h3>'
        elif line.startswith(('* ', '- ')):
            if not in_list:
                lines[i] = f'<ul>\n  <li>{line[2:]}</li>'
                in_list = True
            else:
                lines[i] = f'  <li>{line[2:]}</li>'
        elif in_list and line == '':
            lines[i] = '</ul>\n'
            in_list = False
        elif line != '':
            lines[i] = f'<p>{line}</p>'
    
    # Close any open list
    if in_list:
        lines.append('</ul>')
    
    html_content = '\n'.join(lines)
    
    # Convert remaining newlines to <br> tags within paragraphs
    html_content = html_content.replace('\n', '<br>\n')
    
    # Fix any double <br> before closing tags
    html_content = html_content.replace('<br>\n</', '</')
    
    # Build HTML email
    html_parts = [
        '<!DOCTYPE html>',
        '<html>',
        '<head>',
        '  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">',
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f'  <title>{safe_title}</title>',
        '  <style type="text/css">',
        '    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }',
        '    h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }',
        '    h2 { color: #3498db; margin-top: 20px; }',
        '    h3 { color: #7f8c8d; }',
        '    .timestamp { color: #7f8c8d; font-style: italic; margin-bottom: 20px; }',
        '    .source { margin-top: 30px; padding-top: 15px; border-top: 1px solid #eee; }',
        '    .tags { margin-top: 10px; }',
        '    .tag { display: inline-block; background: #f1f1f1; padding: 2px 8px; border-radius: 3px; ', 
        '           font-size: 0.9em; margin-right: 5px; color: #555; }',
        '    a { color: #3498db; text-decoration: none; }',
        '    a:hover { text-decoration: underline; }',
        '    @media only screen and (max-width: 600px) {',
        '      body { padding: 10px; }',
        '      h1 { font-size: 1.5em; }',
        '    }',
        '  </style>',
        '</head>',
        '<body>',
        f'<h1>{safe_title}</h1>'
    ]
    
    # Add timestamp if available
    if timestamp:
        html_parts.append(f'<div class="timestamp">Generated on {format_timestamp(timestamp)}</div>')
    
    # Add content
    html_parts.append(f'<div class="content">{html_content}</div>')
    
    # Add source information if available
    if source:
        source_html = []
        if 'url' in source:
            safe_url = html.escape(source['url'])
            source_html.append(f'<div><strong>Source:</strong> <a href="{safe_url}">{safe_url}</a></div>')
        
        if 'tags' in source and source['tags']:
            tags_html = [f'<span class="tag">{html.escape(tag)}</span>' for tag in source['tags']]
            source_html.append(f'<div class="tags"><strong>Tags:</strong> {" ".join(tags_html)}</div>')
        
        if source_html:
            html_parts.append('<div class="source">' + '\n'.join(source_html) + '</div>')
    
    # Close HTML
    html_parts.extend(['</body>', '</html>'])
    
    return '\n'.join(html_parts)
