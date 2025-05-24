#!/usr/bin/env python3
"""
Create a large PDF by repeating text content many times.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os

def create_large_pdf(filename, target_mb=5):
    """Create a large PDF file with repeated text content."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Large block of text to repeat
    base_text = """
    This is a comprehensive stress test document designed to evaluate the performance 
    of the Bluelabel Autopilot agent execution pipeline when processing large PDF files. 
    The document contains extensive amounts of text data that will challenge the 
    ingestion, processing, and digest generation capabilities of the system.
    
    The agent pipeline consists of multiple components working together:
    1. The IngestionAgent that reads and extracts content from PDF files
    2. The text processing and chunking mechanisms
    3. The DigestAgent that summarizes and formats the extracted content
    4. The workflow orchestration layer that coordinates these agents
    
    Performance considerations for large documents include:
    - Memory usage during PDF parsing and text extraction
    - Processing time for content analysis and summarization
    - File I/O operations and temporary storage requirements
    - Network latency if content needs to be transmitted
    - CPU usage during text processing operations
    
    This test document will help identify potential bottlenecks, memory leaks,
    timeout issues, and other performance-related problems that may not be
    apparent when processing smaller files. By stress testing the system with
    documents of various sizes, we can ensure robust performance under real-world
    conditions where users may submit large reports, books, or other substantial
    PDF documents for processing.
    
    Additional considerations include error handling, graceful degradation,
    and the ability to process documents in chunks or batches if necessary.
    The system should be able to handle edge cases such as corrupted PDFs,
    password-protected files, and documents with complex formatting or
    embedded images without crashing or hanging indefinitely.
    """
    
    print(f"Creating large PDF (target: {target_mb}MB)...")
    
    # Add title page
    title = Paragraph("Stress Test Document", styles['Title'])
    subtitle = Paragraph(f"Target Size: {target_mb}MB", styles['Heading2'])
    story.extend([title, Spacer(1, 0.5*inch), subtitle, PageBreak()])
    
    # Calculate how many times to repeat the text
    # Rough estimate: each page ~2KB, so for 5MB need ~2500 pages
    pages_needed = int((target_mb * 1024 * 1024) / 2048)
    
    print(f"Generating approximately {pages_needed} pages...")
    
    for page_num in range(pages_needed):
        # Add page header
        header = Paragraph(f"Page {page_num + 1} of {pages_needed}", styles['Heading3'])
        story.append(header)
        story.append(Spacer(1, 0.2*inch))
        
        # Add the text content
        para = Paragraph(base_text, styles['BodyText'])
        story.append(para)
        
        # Add page break
        if page_num < pages_needed - 1:
            story.append(PageBreak())
        
        if (page_num + 1) % 100 == 0:
            print(f"  Generated {page_num + 1} pages...")
    
    # Build the PDF
    print("Building PDF file...")
    doc.build(story)
    
    # Check actual size
    actual_size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"Created {filename}")
    print(f"  Size: {actual_size_mb:.2f}MB")
    print(f"  Pages: {pages_needed}")
    
    return filename, actual_size_mb

if __name__ == "__main__":
    # Create PDFs of different sizes
    create_large_pdf("tests/stress_test_5mb.pdf", 5)
    # create_large_pdf("tests/stress_test_10mb.pdf", 10)  # Uncomment if needed