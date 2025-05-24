"""
Email Output Snapshot Utility

This module provides functionality to save rendered email outputs (HTML, plaintext, markdown)
as static files for debugging, auditing, and historical reference.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)

class EmailSnapshot:
    """Handles saving email output snapshots to disk."""
    
    def __init__(self, base_dir: str = "data/logs/output_snapshots"):
        """Initialize the EmailSnapshot utility.
        
        Args:
            base_dir: Base directory where snapshots will be stored
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_snapshot(
        self,
        run_id: str,
        content: Dict[str, str],
        metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """Save email output snapshots for a workflow run.
        
        Args:
            run_id: Unique identifier for the workflow run
            content: Dictionary containing output formats with keys:
                   - 'markdown': Markdown formatted content
                   - 'plaintext': Plaintext formatted content
                   - 'html': HTML formatted content (optional)
            metadata: Additional metadata to include in the snapshot
            
        Returns:
            Dictionary with paths to saved files
        """
        if not run_id:
            raise ValueError("run_id is required")
        
        # Create run-specific directory
        run_dir = self.base_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        saved_paths = {}
        
        # Save each content type
        for content_type, content_data in content.items():
            if not content_data:
                continue
                
            # Determine file extension
            ext = {
                'markdown': 'md',
                'plaintext': 'txt',
                'html': 'html'
            }.get(content_type, 'txt')
            
            # Create filename with timestamp and workflow info
            filename = f"email_output.{ext}"
            filepath = run_dir / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content_data)
                saved_paths[content_type] = str(filepath)
                logger.debug(f"Saved {content_type} snapshot to {filepath}")
            except Exception as e:
                logger.error(f"Failed to save {content_type} snapshot: {e}")
        
        # Save metadata
        if metadata is None:
            metadata = {}
            
        metadata.update({
            'run_id': run_id,
            'snapshot_timestamp': datetime.utcnow().isoformat(),
            'saved_paths': saved_paths
        })
        
        try:
            metadata_path = run_dir / 'metadata.json'
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            logger.debug(f"Saved metadata to {metadata_path}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
        
        return saved_paths


def save_email_snapshot(
    run_id: str,
    content: Dict[str, str],
    metadata: Optional[Dict[str, str]] = None,
    base_dir: str = "data/logs/output_snapshots"
) -> Dict[str, str]:
    """Convenience function to save email snapshots.
    
    Args:
        run_id: Unique identifier for the workflow run
        content: Dictionary of content to save (markdown, plaintext, html)
        metadata: Optional metadata to include
        base_dir: Base directory for snapshots
        
    Returns:
        Dictionary of saved file paths
    """
    snapshot = EmailSnapshot(base_dir=base_dir)
    return snapshot.save_snapshot(run_id, content, metadata)
