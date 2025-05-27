"""
Persistent storage for DAGRun states.

This module provides file-based storage for DAG execution states,
supporting CRUD operations and query capabilities.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from filelock import FileLock

from .dag_run_tracker import DAGRun, DAGRunStatus
from shared.schemas.dag_trace_schema import DAGRunTrace, StepTraceEntry, TraceEventType

logger = logging.getLogger(__name__)


class DAGRunStore:
    """Persistent storage interface for DAGRun instances."""
    
    def __init__(self, storage_path: str = "data/dag_runs"):
        """
        Initialize DAGRun store.
        
        Args:
            storage_path: Base directory for storing DAGRun data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Index file for quick lookups
        self.index_file = self.storage_path / "dag_runs_index.json"
        self.index_lock = FileLock(str(self.index_file) + ".lock")
        
        # Initialize index if it doesn't exist
        if not self.index_file.exists():
            self._save_index({})
    
    def _get_run_file(self, run_id: str) -> Path:
        """Get file path for a specific run."""
        return self.storage_path / f"run_{run_id}.json"
    
    def _get_trace_file(self, run_id: str) -> Path:
        """Get file path for a specific run's trace."""
        return self.storage_path / f"trace_{run_id}.json"
    
    def _load_index(self) -> Dict[str, Any]:
        """Load the run index."""
        try:
            with self.index_lock:
                if self.index_file.exists():
                    with open(self.index_file, 'r') as f:
                        return json.load(f)
        except Exception as e:
            logger.error(f"Error loading index: {e}")
        return {}
    
    def _save_index(self, index: Dict[str, Any]) -> None:
        """Save the run index."""
        try:
            with self.index_lock:
                with open(self.index_file, 'w') as f:
                    json.dump(index, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def create(self, dag_run: DAGRun) -> str:
        """
        Create a new DAGRun in storage.
        
        Args:
            dag_run: DAGRun instance to persist
            
        Returns:
            run_id of the created run
        """
        run_file = self._get_run_file(dag_run.run_id)
        
        # Save run data
        try:
            with open(run_file, 'w') as f:
                json.dump(dag_run.to_dict(), f, indent=2)
            
            # Update index
            index = self._load_index()
            index[dag_run.run_id] = {
                'dag_id': dag_run.dag_id,
                'status': dag_run.status.value,
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat(),
                'file': str(run_file.relative_to(self.storage_path))
            }
            self._save_index(index)
            
            logger.info(f"Created DAGRun {dag_run.run_id} for DAG {dag_run.dag_id}")
            return dag_run.run_id
            
        except Exception as e:
            logger.error(f"Error creating DAGRun: {e}")
            raise
    
    def update(self, dag_run: DAGRun) -> None:
        """
        Update an existing DAGRun.
        
        Args:
            dag_run: Updated DAGRun instance
        """
        run_file = self._get_run_file(dag_run.run_id)
        
        if not run_file.exists():
            raise ValueError(f"DAGRun {dag_run.run_id} not found")
        
        try:
            # Update run data
            with open(run_file, 'w') as f:
                json.dump(dag_run.to_dict(), f, indent=2)
            
            # Update index
            index = self._load_index()
            if dag_run.run_id in index:
                index[dag_run.run_id]['status'] = dag_run.status.value
                index[dag_run.run_id]['updated_at'] = datetime.utcnow().isoformat()
                self._save_index(index)
            
            logger.info(f"Updated DAGRun {dag_run.run_id}")
            
        except Exception as e:
            logger.error(f"Error updating DAGRun: {e}")
            raise
    
    def get(self, run_id: str) -> Optional[DAGRun]:
        """
        Retrieve a DAGRun by ID.
        
        Args:
            run_id: The run ID to retrieve
            
        Returns:
            DAGRun instance or None if not found
        """
        run_file = self._get_run_file(run_id)
        
        if not run_file.exists():
            logger.warning(f"DAGRun {run_id} not found")
            return None
        
        try:
            with open(run_file, 'r') as f:
                data = json.load(f)
            return DAGRun.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading DAGRun {run_id}: {e}")
            return None
    
    def delete(self, run_id: str) -> bool:
        """
        Delete a DAGRun.
        
        Args:
            run_id: The run ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        run_file = self._get_run_file(run_id)
        
        if not run_file.exists():
            return False
        
        try:
            # Delete file
            run_file.unlink()
            
            # Delete associated trace if exists
            self.delete_trace(run_id)
            
            # Update index
            index = self._load_index()
            if run_id in index:
                del index[run_id]
                self._save_index(index)
            
            logger.info(f"Deleted DAGRun {run_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting DAGRun {run_id}: {e}")
            return False
    
    def list_runs(self, dag_id: Optional[str] = None, 
                  status: Optional[DAGRunStatus] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        List DAGRuns with optional filtering.
        
        Args:
            dag_id: Filter by DAG ID
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of run summaries
        """
        index = self._load_index()
        results = []
        
        for run_id, info in index.items():
            # Apply filters
            if dag_id and info['dag_id'] != dag_id:
                continue
            if status and info['status'] != status.value:
                continue
            
            results.append({
                'run_id': run_id,
                'dag_id': info['dag_id'],
                'status': info['status'],
                'created_at': info.get('created_at'),
                'updated_at': info.get('updated_at')
            })
        
        # Sort by updated_at descending
        results.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return results[:limit]
    
    def get_active_runs(self) -> List[DAGRun]:
        """
        Get all currently active (running) DAGRuns.
        
        Returns:
            List of active DAGRun instances
        """
        active_runs = []
        
        for run_info in self.list_runs(status=DAGRunStatus.RUNNING):
            run = self.get(run_info['run_id'])
            if run and run.is_running:
                active_runs.append(run)
        
        return active_runs
    
    def cleanup_old_runs(self, days: int = 30) -> int:
        """
        Clean up old completed runs.
        
        Args:
            days: Delete runs older than this many days
            
        Returns:
            Number of runs deleted
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        index = self._load_index()
        deleted_count = 0
        
        for run_id, info in list(index.items()):
            # Only clean up completed runs
            if info['status'] not in ['success', 'failed', 'cancelled']:
                continue
            
            # Check age
            updated_at = datetime.fromisoformat(info.get('updated_at', ''))
            if updated_at < cutoff_date:
                if self.delete(run_id):
                    deleted_count += 1
        
        logger.info(f"Cleaned up {deleted_count} old DAGRuns")
        return deleted_count
    
    def get_statistics(self, dag_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get execution statistics.
        
        Args:
            dag_id: Optional DAG ID to filter by
            
        Returns:
            Dictionary of statistics
        """
        index = self._load_index()
        
        # Count by status
        status_counts = {}
        total_runs = 0
        
        for run_id, info in index.items():
            if dag_id and info['dag_id'] != dag_id:
                continue
            
            status = info['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            total_runs += 1
        
        return {
            'total_runs': total_runs,
            'by_status': status_counts,
            'success_rate': (
                (status_counts.get('success', 0) / total_runs * 100)
                if total_runs > 0 else 0
            )
        }
    
    def save_trace(self, run_id: str, trace: DAGRunTrace) -> None:
        """
        Save execution trace for a DAGRun.
        
        Args:
            run_id: The run ID
            trace: The execution trace to save
        """
        trace_file = self._get_trace_file(run_id)
        
        try:
            # Convert trace to dict for JSON serialization
            trace_data = {
                'run_id': trace.run_id,
                'dag_id': trace.dag_id,
                'start_time': trace.start_time.isoformat() if trace.start_time else None,
                'end_time': trace.end_time.isoformat() if trace.end_time else None,
                'trace_entries': [entry.to_dict() for entry in trace.trace_entries],
                'summary': trace.summary
            }
            
            with open(trace_file, 'w') as f:
                json.dump(trace_data, f, indent=2)
            
            logger.info(f"Saved trace for DAGRun {run_id}")
            
        except Exception as e:
            logger.error(f"Error saving trace for DAGRun {run_id}: {e}")
            raise
    
    def get_trace(self, run_id: str) -> Optional[DAGRunTrace]:
        """
        Retrieve execution trace for a DAGRun.
        
        Args:
            run_id: The run ID
            
        Returns:
            DAGRunTrace instance or None if not found
        """
        trace_file = self._get_trace_file(run_id)
        
        if not trace_file.exists():
            logger.debug(f"No trace found for DAGRun {run_id}")
            return None
        
        try:
            with open(trace_file, 'r') as f:
                trace_data = json.load(f)
            
            # Convert back to DAGRunTrace using from_dict
            trace = DAGRunTrace.from_dict(trace_data)
            
            return trace
            
        except Exception as e:
            logger.error(f"Error loading trace for DAGRun {run_id}: {e}")
            return None
    
    def delete_trace(self, run_id: str) -> bool:
        """
        Delete execution trace for a DAGRun.
        
        Args:
            run_id: The run ID
            
        Returns:
            True if deleted, False if not found
        """
        trace_file = self._get_trace_file(run_id)
        
        if not trace_file.exists():
            return False
        
        try:
            trace_file.unlink()
            logger.info(f"Deleted trace for DAGRun {run_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting trace for DAGRun {run_id}: {e}")
            return False