#!/usr/bin/env python3
"""
File locking mechanism for concurrent operations in the orchestration system.

Provides both file-based and directory-based locking to prevent race conditions
when multiple agents or scripts try to modify the same resources.
"""

import os
import time
import fcntl
import contextlib
import hashlib
from pathlib import Path
from typing import Optional, Union
from datetime import datetime, timedelta


class FileLockException(Exception):
    """Exception raised when file locking operations fail."""
    pass


class FileLock:
    """
    A file-based locking mechanism using fcntl for Unix systems.
    
    This lock is process-safe and handles cleanup automatically.
    """
    
    def __init__(self, 
                 lockfile_path: Union[str, Path],
                 timeout: float = 30.0,
                 check_interval: float = 0.1,
                 auto_release: bool = True):
        """
        Initialize a file lock.
        
        Args:
            lockfile_path: Path to the lock file
            timeout: Maximum time to wait for lock acquisition (seconds)
            check_interval: Time between lock acquisition attempts (seconds)
            auto_release: Automatically release lock when object is deleted
        """
        self.lockfile_path = Path(lockfile_path)
        self.timeout = timeout
        self.check_interval = check_interval
        self.auto_release = auto_release
        self._lock_file = None
        self._owns_lock = False
        
        # Ensure lock directory exists
        self.lockfile_path.parent.mkdir(parents=True, exist_ok=True)
    
    def acquire(self, blocking: bool = True) -> bool:
        """
        Acquire the file lock.
        
        Args:
            blocking: If True, wait for lock. If False, return immediately.
            
        Returns:
            True if lock acquired, False if non-blocking and lock unavailable
            
        Raises:
            FileLockException: If timeout exceeded or other locking error
        """
        start_time = time.time()
        
        while True:
            try:
                # Open or create lock file
                self._lock_file = open(self.lockfile_path, 'w')
                
                # Try to acquire exclusive lock
                fcntl.flock(self._lock_file.fileno(), 
                           fcntl.LOCK_EX | (fcntl.LOCK_NB if not blocking else 0))
                
                # Write lock info
                lock_info = {
                    'pid': os.getpid(),
                    'acquired_at': datetime.now().isoformat(),
                    'hostname': os.uname().nodename
                }
                self._lock_file.write(f"{lock_info}\n")
                self._lock_file.flush()
                
                self._owns_lock = True
                return True
                
            except BlockingIOError:
                if not blocking:
                    return False
                
                # Check timeout
                if time.time() - start_time > self.timeout:
                    raise FileLockException(
                        f"Failed to acquire lock on {self.lockfile_path} "
                        f"after {self.timeout} seconds"
                    )
                
                # Wait before retrying
                time.sleep(self.check_interval)
                
            except Exception as e:
                if self._lock_file:
                    self._lock_file.close()
                    self._lock_file = None
                raise FileLockException(f"Lock acquisition failed: {e}")
    
    def release(self):
        """Release the file lock."""
        if self._lock_file and self._owns_lock:
            try:
                # Release the lock
                fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
                self._lock_file.close()
                
                # Remove lock file
                try:
                    self.lockfile_path.unlink()
                except FileNotFoundError:
                    pass
                    
            except Exception as e:
                raise FileLockException(f"Lock release failed: {e}")
            finally:
                self._lock_file = None
                self._owns_lock = False
    
    def is_locked(self) -> bool:
        """Check if the resource is currently locked."""
        try:
            with open(self.lockfile_path, 'w') as f:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                return False
        except:
            return True
    
    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.auto_release and self._owns_lock:
            self.release()


class DirectoryLock:
    """
    Directory-based locking for broader resource protection.
    
    Uses a marker directory to indicate lock status, which works
    across different filesystems and platforms.
    """
    
    def __init__(self,
                 target_path: Union[str, Path],
                 timeout: float = 30.0,
                 check_interval: float = 0.1,
                 lock_suffix: str = ".lock"):
        """
        Initialize a directory lock.
        
        Args:
            target_path: Path to the resource to lock
            timeout: Maximum time to wait for lock acquisition
            check_interval: Time between lock acquisition attempts
            lock_suffix: Suffix for lock directory name
        """
        self.target_path = Path(target_path)
        self.lock_path = self.target_path.parent / f"{self.target_path.name}{lock_suffix}"
        self.timeout = timeout
        self.check_interval = check_interval
        self._owns_lock = False
        
        # Create a unique lock identifier
        self.lock_id = f"{os.getpid()}_{time.time()}"
    
    def acquire(self, blocking: bool = True) -> bool:
        """Acquire the directory lock."""
        start_time = time.time()
        
        while True:
            try:
                # Try to create lock directory
                self.lock_path.mkdir(exist_ok=False)
                
                # Write lock info
                lock_info_path = self.lock_path / "lock_info.json"
                lock_info = {
                    'lock_id': self.lock_id,
                    'pid': os.getpid(),
                    'acquired_at': datetime.now().isoformat(),
                    'target': str(self.target_path)
                }
                
                import json
                with open(lock_info_path, 'w') as f:
                    json.dump(lock_info, f, indent=2)
                
                self._owns_lock = True
                return True
                
            except FileExistsError:
                if not blocking:
                    return False
                
                # Check if lock is stale
                if self._is_lock_stale():
                    self._break_stale_lock()
                    continue
                
                # Check timeout
                if time.time() - start_time > self.timeout:
                    raise FileLockException(
                        f"Failed to acquire lock on {self.target_path} "
                        f"after {self.timeout} seconds"
                    )
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                raise FileLockException(f"Directory lock acquisition failed: {e}")
    
    def release(self):
        """Release the directory lock."""
        if self._owns_lock and self.lock_path.exists():
            try:
                # Verify we own the lock
                lock_info_path = self.lock_path / "lock_info.json"
                if lock_info_path.exists():
                    import json
                    with open(lock_info_path) as f:
                        lock_info = json.load(f)
                    
                    if lock_info.get('lock_id') != self.lock_id:
                        raise FileLockException("Attempting to release lock not owned by this process")
                
                # Remove lock directory and contents
                import shutil
                shutil.rmtree(self.lock_path)
                
            except Exception as e:
                raise FileLockException(f"Directory lock release failed: {e}")
            finally:
                self._owns_lock = False
    
    def _is_lock_stale(self, stale_timeout: float = 300.0) -> bool:
        """Check if existing lock is stale (older than stale_timeout seconds)."""
        try:
            lock_info_path = self.lock_path / "lock_info.json"
            if not lock_info_path.exists():
                return True
            
            import json
            with open(lock_info_path) as f:
                lock_info = json.load(f)
            
            acquired_at = datetime.fromisoformat(lock_info['acquired_at'])
            age = datetime.now() - acquired_at
            
            # Check if process is still alive
            pid = lock_info.get('pid')
            if pid:
                try:
                    os.kill(pid, 0)  # Check if process exists
                except ProcessLookupError:
                    return True  # Process is dead
            
            return age.total_seconds() > stale_timeout
            
        except Exception:
            return True  # Consider corrupted lock as stale
    
    def _break_stale_lock(self):
        """Remove a stale lock."""
        try:
            import shutil
            shutil.rmtree(self.lock_path)
        except Exception:
            pass
    
    def __enter__(self):
        """Context manager entry."""
        self.acquire()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()


@contextlib.contextmanager
def file_transaction(filepath: Union[str, Path], 
                    backup: bool = True,
                    lock_timeout: float = 30.0):
    """
    Context manager for safe file transactions with locking and rollback.
    
    Args:
        filepath: Path to file to modify
        backup: Create backup before modification
        lock_timeout: Timeout for acquiring file lock
        
    Yields:
        Path object for the file to modify
        
    Example:
        with file_transaction('/path/to/file.json') as filepath:
            with open(filepath) as f:
                data = json.load(f)
            data['key'] = 'new_value'
            with open(filepath, 'w') as f:
                json.dump(data, f)
    """
    filepath = Path(filepath)
    lockfile = filepath.parent / f".{filepath.name}.lock"
    backup_file = None
    
    with FileLock(lockfile, timeout=lock_timeout):
        try:
            # Create backup if requested
            if backup and filepath.exists():
                backup_file = filepath.parent / f"{filepath.name}.backup"
                import shutil
                shutil.copy2(filepath, backup_file)
            
            yield filepath
            
            # Success - remove backup
            if backup_file and backup_file.exists():
                backup_file.unlink()
                
        except Exception as e:
            # Rollback on error
            if backup_file and backup_file.exists():
                import shutil
                shutil.copy2(backup_file, filepath)
                backup_file.unlink()
            raise


def with_file_lock(lockfile_path: Union[str, Path], 
                   timeout: float = 30.0):
    """
    Decorator for functions that need file locking.
    
    Args:
        lockfile_path: Path to lock file
        timeout: Lock acquisition timeout
        
    Example:
        @with_file_lock('/tmp/myapp.lock')
        def critical_function():
            # This function will be protected by file lock
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with FileLock(lockfile_path, timeout=timeout):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Convenience functions for common orchestration locks
def get_task_lock(task_id: str) -> FileLock:
    """Get a lock for a specific task."""
    lock_dir = Path("/tmp/orchestration/locks/tasks")
    lock_dir.mkdir(parents=True, exist_ok=True)
    return FileLock(lock_dir / f"{task_id}.lock")


def get_agent_lock(agent_id: str) -> FileLock:
    """Get a lock for a specific agent's operations."""
    lock_dir = Path("/tmp/orchestration/locks/agents")
    lock_dir.mkdir(parents=True, exist_ok=True)
    return FileLock(lock_dir / f"{agent_id}.lock")


def get_resource_lock(resource_path: Union[str, Path]) -> DirectoryLock:
    """Get a lock for a specific resource (file or directory)."""
    return DirectoryLock(resource_path)


if __name__ == "__main__":
    # Example usage
    print("File Lock Example:")
    with FileLock("/tmp/test.lock") as lock:
        print("Lock acquired!")
        time.sleep(2)
    print("Lock released!")
    
    print("\nDirectory Lock Example:")
    with DirectoryLock("/tmp/test_resource") as lock:
        print("Directory lock acquired!")
        time.sleep(2)
    print("Directory lock released!")
    
    print("\nFile Transaction Example:")
    test_file = Path("/tmp/test_transaction.txt")
    test_file.write_text("Original content")
    
    try:
        with file_transaction(test_file) as f:
            f.write_text("Modified content")
            # Simulate error
            # raise Exception("Simulated error")
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"Final content: {test_file.read_text()}")