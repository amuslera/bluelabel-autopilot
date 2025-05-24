#!/usr/bin/env python3
"""
Create a reasonably large PDF for stress testing (1-2MB).
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import random

def create_test_pdf(filename, num_pages=100):
    """Create a test PDF with the specified number of pages."""
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    print(f"Creating test PDF with {num_pages} pages...")
    
    for page_num in range(1, num_pages + 1):
        # Add page title
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, f"Test Page {page_num}")
        
        # Add metadata
        c.setFont("Helvetica", 12)
        c.drawString(50, height - 80, f"Stress Test Document for Agent Execution Pipeline")
        c.drawString(50, height - 100, f"Page {page_num} of {num_pages}")
        
        # Add lots of text content
        y = height - 150
        c.setFont("Helvetica", 10)
        
        # Generate 30-40 lines of text per page
        for line_num in range(random.randint(30, 40)):
            if y < 50:
                break
                
            # Generate random text line
            words = ["lorem", "ipsum", "dolor", "sit", "amet", "consectetur", 
                    "adipiscing", "elit", "sed", "do", "eiusmod", "tempor"]
            line = " ".join(random.choices(words, k=random.randint(8, 15)))
            c.drawString(50, y, f"{line_num + 1}. {line}")
            y -= 15
        
        # Add page number at bottom
        c.drawString(width / 2 - 20, 30, f"- {page_num} -")
        
        # New page
        c.showPage()
        
        if page_num % 20 == 0:
            print(f"  Generated {page_num} pages...")
    
    c.save()
    
    import os
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    print(f"Created {filename} ({size_mb:.2f}MB)")
    
    return filename, size_mb

if __name__ == "__main__":
    # Create a moderately large PDF
    create_test_pdf("tests/stress_test_100pages.pdf", 100)
    create_test_pdf("tests/stress_test_200pages.pdf", 200)