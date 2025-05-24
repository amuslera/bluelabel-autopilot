"""
Tests for the email output formatter module.
"""

import unittest
from datetime import datetime, timezone, timedelta
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.email import email_output_formatter

class TestEmailOutputFormatter(unittest.TestCase):
    """Test cases for the email output formatter."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_timestamp = "2025-05-24T10:30:00-07:00"
        
        # Sample 1: Basic summary
        self.summary_data = {
            "title": "Daily News Digest",
            "content": "Here's what happened today in the world of technology...",
            "timestamp": self.sample_timestamp,
            "source": {
                "url": "https://example.com/daily-news",
                "tags": ["news", "daily"]
            }
        }
        
        # Sample 2: Long-form digest
        self.digest_data = {
            "title": "Weekly Research Report",
            "content": (
                "## Key Findings\n\n"
                "1. Market trends show a 15% increase in AI adoption.\n"
                "2. New regulations will impact data privacy practices.\n"
                "3. Emerging technologies to watch in Q3.\n\n"
                "## Analysis\n\n"
                "The technology sector continues to evolve rapidly..."
            ),
            "timestamp": self.sample_timestamp,
            "source": {
                "url": "https://research.example.com/weekly/2025-05-24",
                "tags": ["research", "weekly", "analysis"]
            }
        }
        
        # Sample 3: Minimal data
        self.minimal_data = {
            "title": "Quick Update",
            "content": "Just a quick note with minimal information."
        }
    
    def test_format_digest_markdown_summary(self):
        """Test markdown formatting with summary data."""
        result = email_output_formatter.format_digest_markdown(self.summary_data)
        
        # Check title
        self.assertIn("# Daily News Digest", result)
        
        # Check timestamp (using a more flexible check for the timestamp format)
        self.assertIn("*Generated on ", result)
        self.assertIn("May 24, 2025", result)  # Check for the date part
        
        # Check content
        self.assertIn("Here's what happened today", result)
        
        # Check source
        self.assertIn("### Source", result)
        self.assertIn("[Source](https://example.com/daily-news)", result)
        self.assertIn("`news` `daily`", result)
    
    def test_format_digest_plaintext_digest(self):
        """Test plaintext formatting with digest data."""
        result = email_output_formatter.format_digest_plaintext(self.digest_data)
        
        # Check title
        self.assertIn("Weekly Research Report", result)
        self.assertIn("=====================", result)
        
        # Check content sections
        self.assertIn("SUMMARY", result)
        self.assertIn("Key Findings", result)
        self.assertIn("1. Market trends", result)
        
        # Check source
        self.assertIn("SOURCE", result)
        self.assertIn("Source: https://research.example.com/weekly/2025-05-24", result)
        self.assertIn("Tags: research, weekly, analysis", result)
    
    def test_format_minimal_data(self):
        """Test formatting with minimal input data."""
        # Test markdown
        md_result = email_output_formatter.format_digest_markdown(self.minimal_data)
        self.assertIn("# Quick Update", md_result)
        self.assertIn("Just a quick note", md_result)
        
        # Test plaintext
        txt_result = email_output_formatter.format_digest_plaintext(self.minimal_data)
        self.assertIn("Quick Update", txt_result)
        self.assertIn("Just a quick note", txt_result)
    
    def test_line_wrapping_plaintext(self):
        """Test that plaintext output respects line width."""
        test_data = {
            "title": "Line Wrapping Test",
            "content": "This is a very long line that should be wrapped to fit within the specified line width when converted to plaintext format."
        }
        
        result = email_output_formatter.format_digest_plaintext(test_data, line_width=40)
        lines = result.split('\n')
        
        # Check that no line exceeds the specified width
        for line in lines:
            if line.strip() and not line.startswith('=') and not line in ['SUMMARY', '-----']:
                self.assertLessEqual(len(line), 40)

if __name__ == "__main__":
    unittest.main()
