"""
Tests for the email snapshot functionality.
"""

import os
import tempfile
import shutil
import unittest
from pathlib import Path

# Add the project root to the Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.email.email_snapshot import EmailSnapshot, save_email_snapshot

class TestEmailSnapshot(unittest.TestCase):
    """Test cases for the EmailSnapshot class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp(prefix="email_snapshot_test_")
        self.snapshot = EmailSnapshot(base_dir=self.test_dir)
        
        # Sample content
        self.run_id = "test_run_123"
        self.content = {
            'markdown': '# Test Email\n\nThis is a **test** email in markdown.',
            'plaintext': 'TEST EMAIL\n\nThis is a test email in plaintext.',
            'html': '<h1>Test Email</h1><p>This is a <strong>test</strong> email in HTML.</p>'
        }
        self.metadata = {
            'workflow': 'test_workflow',
            'sender': 'test@example.com',
            'recipient': 'user@example.com'
        }
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_save_snapshot(self):
        """Test saving a snapshot with all content types."""
        # Save the snapshot
        saved_paths = self.snapshot.save_snapshot(
            run_id=self.run_id,
            content=self.content,
            metadata=self.metadata
        )
        
        # Check that all files were saved
        self.assertEqual(len(saved_paths), 3)
        self.assertIn('markdown', saved_paths)
        self.assertIn('plaintext', saved_paths)
        self.assertIn('html', saved_paths)
        
        # Check that files exist
        for path in saved_paths.values():
            self.assertTrue(os.path.exists(path))
        
        # Check metadata file
        metadata_path = Path(self.test_dir) / self.run_id / 'metadata.json'
        self.assertTrue(metadata_path.exists())
        
        # Check metadata content
        with open(metadata_path, 'r') as f:
            metadata = f.read()
            self.assertIn(self.run_id, metadata)
            self.assertIn('test_workflow', metadata)
            self.assertIn('test@example.com', metadata)
    
    def test_save_snapshot_missing_content(self):
        """Test saving a snapshot with missing content types."""
        # Save with only markdown content
        saved_paths = self.snapshot.save_snapshot(
            run_id=self.run_id,
            content={'markdown': self.content['markdown']},
            metadata=self.metadata
        )
        
        # Only markdown should be saved
        self.assertEqual(len(saved_paths), 1)
        self.assertIn('markdown', saved_paths)
        self.assertTrue(os.path.exists(saved_paths['markdown']))
    
    def test_save_snapshot_invalid_run_id(self):
        """Test saving with an invalid run_id."""
        with self.assertRaises(ValueError):
            self.snapshot.save_snapshot(
                run_id='',
                content=self.content,
                metadata=self.metadata
            )
    
    def test_convenience_function(self):
        """Test the save_email_snapshot convenience function."""
        saved_paths = save_email_snapshot(
            run_id=self.run_id,
            content=self.content,
            metadata=self.metadata,
            base_dir=self.test_dir
        )
        
        # Check that files were saved
        self.assertEqual(len(saved_paths), 3)
        for path in saved_paths.values():
            self.assertTrue(os.path.exists(path))


if __name__ == '__main__':
    unittest.main()
