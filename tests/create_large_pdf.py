#!/usr/bin/env python3
"""
Create a large PDF file for stress testing the agent execution pipeline.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
import random
import string
import os

def generate_lorem_ipsum_paragraph():
    """Generate a random paragraph of lorem ipsum text."""
    words = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing", 
        "elit", "sed", "do", "eiusmod", "tempor", "incididunt", "ut", "labore",
        "et", "dolore", "magna", "aliqua", "enim", "ad", "minim", "veniam",
        "quis", "nostrud", "exercitation", "ullamco", "laboris", "nisi", "ut",
        "aliquip", "ex", "ea", "commodo", "consequat", "duis", "aute", "irure",
        "dolor", "in", "reprehenderit", "voluptate", "velit", "esse", "cillum",
        "dolore", "eu", "fugiat", "nulla", "pariatur", "excepteur", "sint",
        "occaecat", "cupidatat", "non", "proident", "sunt", "culpa", "qui",
        "officia", "deserunt", "mollit", "anim", "id", "est", "laborum"
    ]
    
    # Generate 5-10 sentences
    paragraph = []
    for _ in range(random.randint(5, 10)):
        sentence_length = random.randint(8, 20)
        sentence = " ".join(random.choices(words, k=sentence_length))
        sentence = sentence.capitalize() + "."
        paragraph.append(sentence)
    
    return " ".join(paragraph)

def create_large_pdf(filename, target_size_mb=5):
    """Create a large PDF file with random text content."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Text parameters
    margin = 50
    text_width = width - 2 * margin
    y_position = height - margin
    line_height = 14
    font_size = 11
    
    c.setFont("Helvetica", font_size)
    
    # Track file size
    page_count = 0
    total_text = []
    
    print(f"Creating large PDF (target: {target_size_mb}MB)...")
    
    while True:
        # Add title on each page
        if y_position == height - margin:
            page_count += 1
            c.setFont("Helvetica-Bold", 16)
            c.drawString(margin, y_position, f"Stress Test Document - Page {page_count}")
            y_position -= 30
            c.setFont("Helvetica", font_size)
            
            # Add page metadata
            c.drawString(margin, y_position, f"Generated for agent execution stress testing")
            y_position -= 20
            c.drawString(margin, y_position, f"Target size: {target_size_mb}MB")
            y_position -= 30
        
        # Generate and add paragraph
        paragraph = generate_lorem_ipsum_paragraph()
        total_text.append(paragraph)
        
        # Split paragraph into lines
        lines = simpleSplit(paragraph, "Helvetica", font_size, text_width)
        
        for line in lines:
            if y_position < margin + line_height:
                # New page
                c.showPage()
                y_position = height - margin
                continue
                
            c.drawString(margin, y_position, line)
            y_position -= line_height
        
        y_position -= line_height  # Extra space between paragraphs
        
        # Check file size periodically
        if page_count % 10 == 0:
            c.save()
            current_size = os.path.getsize(filename) / (1024 * 1024)  # MB
            print(f"  Pages: {page_count}, Size: {current_size:.2f}MB")
            
            if current_size >= target_size_mb:
                break
                
            # Recreate canvas to continue
            c = canvas.Canvas(filename, pagesize=letter)
            c.setFont("Helvetica", font_size)
    
    # Final save
    c.save()
    
    final_size = os.path.getsize(filename) / (1024 * 1024)
    print(f"Created {filename}")
    print(f"  Final size: {final_size:.2f}MB")
    print(f"  Pages: {page_count}")
    print(f"  Total paragraphs: {len(total_text)}")
    print(f"  Estimated words: {sum(len(p.split()) for p in total_text)}")
    
    return filename, final_size, page_count

if __name__ == "__main__":
    # Create PDFs of different sizes
    sizes = [
        ("tests/large_pdf_5mb.pdf", 5),
        ("tests/large_pdf_10mb.pdf", 10)
    ]
    
    for filename, size_mb in sizes:
        create_large_pdf(filename, size_mb)
        print()