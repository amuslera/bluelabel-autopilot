"""
Tests for the HTML email output formatter.
"""

import unittest
import os
import sys
import tempfile
import webbrowser
from datetime import datetime, timezone, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
from services.email import email_output_formatter

class TestEmailOutputFormatterHTML(unittest.TestCase):
    """Test cases for the HTML email output formatter."""
    
    def setUp(self):
        """Set up test data."""
        self.sample_data = {
            "title": "Test HTML Email",
            "content": "## Section 1\nThis is a test email with **HTML** formatting.\n\n## Section 2\n- Item 1\n- Item 2\n- Item 3\n\n## Section 3\nThis is the final section.",
            "source": {
                "url": "https://example.com/test",
                "tags": ["test", "email", "html"]
            },
            "timestamp": "2025-05-24T10:30:00-07:00"
        }
        
        self.minimal_data = {
            "title": "Minimal Test",
            "content": "This is a minimal test email."
        }
    
    def test_basic_html_generation(self):
        """Test basic HTML email generation."""
        result = email_output_formatter.format_digest_html(self.sample_data)
        
        # Check basic structure
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<html>", result)
        self.assertIn("<head>", result)
        self.assertIn("<body>", result)
        self.assertIn("</body>", result)
        self.assertIn("</html>", result)
        
        # Check title
        self.assertIn("<title>Test HTML Email</title>", result)
        self.assertIn("<h1>Test HTML Email</h1>", result)
        
        # Check content
        self.assertIn("<h2>Section 1</h2>", result)
        self.assertIn("<h2>Section 2</h2>", result)
        self.assertIn("<h2>Section 3</h2>", result)
        
        # Check source and tags
        self.assertIn("https://example.com/test", result)
        self.assertIn("<span class=\"tag\">test</span>", result)
        
        # Check timestamp (using a more flexible check)
        self.assertIn("May 24, 2025", result)
        self.assertIn("10:30 AM", result)
    
    def test_minimal_input(self):
        """Test HTML generation with minimal input."""
        result = email_output_formatter.format_digest_html(self.minimal_data)
        
        # Should still have basic structure
        self.assertIn("<!DOCTYPE html>", result)
        self.assertIn("<h1>Minimal Test</h1>", result)
        self.assertIn("This is a minimal test email.", result)
        
        # Should not have source section
        self.assertNotIn("<div class=\"source\">", result)
    
    def test_html_escaping(self):
        """Test that HTML special characters are properly escaped."""
        test_data = {
            "title": "<script>alert('XSS')</script>",
            "content": "<script>alert('XSS')</script>"
        }
        
        result = email_output_formatter.format_digest_html(test_data)
        
        # Check that script tags are escaped (using the actual HTML entity encoding)
        self.assertIn("&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;", result)
        self.assertNotIn("<script>", result)
    
    def test_preview_html(self):
        """Generate a preview HTML file for manual testing."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(email_output_formatter.format_digest_html(self.sample_data))
            temp_path = f.name
        
        print(f"\nGenerated HTML preview: file://{temp_path}")
        
        # Try to open in default browser
        try:
            webbrowser.open(f"file://{temp_path}")
        except Exception as e:
            print(f"Could not open browser: {e}")
        
        # Don't delete the file so user can view it
        self.assertTrue(True)  # Dummy assertion

if __name__ == "__main__":
    unittest.main()
