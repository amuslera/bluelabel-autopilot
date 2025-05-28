"""
Performance optimization utilities for workflow execution.

Provides caching, connection pooling, and performance monitoring.
"""

import asyncio
import time
import functools
from typing import Dict, Any, Optional, Callable, TypeVar, Union
from datetime import datetime, timedelta
import hashlib
import json
import logging
from pathlib import Path


logger = logging.getLogger(__name__)

T = TypeVar('T')


class WorkflowCache:
    """In-memory cache for workflow results with TTL support."""
    
    def __init__(self, ttl_seconds: int = 300):
        """Initialize cache with TTL in seconds."""
        self.cache: Dict[str, tuple[Any, datetime]] = {}
        self.ttl_seconds = ttl_seconds
        self.hits = 0
        self.misses = 0
        
    def _make_key(self, workflow_path: str, input_data: Optional[Dict[str, Any]] = None) -> str:
        """Create cache key from workflow path and input."""
        key_data = {
            'workflow': workflow_path,
            'input': input_data or {}
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, workflow_path: str, input_data: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        """Get cached result if available and not expired."""
        key = self._make_key(workflow_path, input_data)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            if datetime.utcnow() - timestamp < timedelta(seconds=self.ttl_seconds):
                self.hits += 1
                logger.debug(f"Cache hit for {workflow_path}")
                return result
            else:
                # Expired
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, workflow_path: str, result: Any, input_data: Optional[Dict[str, Any]] = None):
        """Store result in cache."""
        key = self._make_key(workflow_path, input_data)
        self.cache[key] = (result, datetime.utcnow())
        logger.debug(f"Cached result for {workflow_path}")
    
    def clear(self):
        """Clear all cached results."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'ttl_seconds': self.ttl_seconds
        }


class ConnectionPool:
    """Connection pool for HTTP/database connections."""
    
    def __init__(self, max_connections: int = 10):
        """Initialize connection pool."""
        self.max_connections = max_connections
        self.pool: asyncio.Queue = asyncio.Queue(maxsize=max_connections)
        self.active_connections = 0
        self._lock = asyncio.Lock()
        
    async def acquire(self) -> Any:
        """Acquire a connection from the pool."""
        try:
            # Try to get existing connection
            connection = self.pool.get_nowait()
            logger.debug("Reused connection from pool")
            return connection
        except asyncio.QueueEmpty:
            # Create new connection if under limit
            async with self._lock:
                if self.active_connections < self.max_connections:
                    self.active_connections += 1
                    connection = await self._create_connection()
                    logger.debug(f"Created new connection ({self.active_connections}/{self.max_connections})")
                    return connection
            
            # Wait for available connection
            logger.debug("Waiting for available connection")
            connection = await self.pool.get()
            return connection
    
    async def release(self, connection: Any):
        """Release connection back to pool."""
        try:
            self.pool.put_nowait(connection)
            logger.debug("Released connection to pool")
        except asyncio.QueueFull:
            # Pool is full, close connection
            await self._close_connection(connection)
            async with self._lock:
                self.active_connections -= 1
    
    async def _create_connection(self) -> Any:
        """Create a new connection (override in subclasses)."""
        # Placeholder - actual implementation depends on connection type
        return {'id': self.active_connections, 'created': datetime.utcnow()}
    
    async def _close_connection(self, connection: Any):
        """Close a connection (override in subclasses)."""
        # Placeholder - actual implementation depends on connection type
        logger.debug(f"Closed connection {connection.get('id')}")
    
    async def close_all(self):
        """Close all connections in the pool."""
        while not self.pool.empty():
            try:
                connection = self.pool.get_nowait()
                await self._close_connection(connection)
            except asyncio.QueueEmpty:
                break
        
        self.active_connections = 0


def with_cache(cache: WorkflowCache):
    """Decorator to cache workflow execution results."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, workflow_path: Path, **kwargs):
            # Check cache
            initial_input = kwargs.get('initial_input')
            cached_result = cache.get(str(workflow_path), initial_input)
            
            if cached_result is not None:
                logger.info(f"Using cached result for {workflow_path}")
                return cached_result
            
            # Execute and cache
            result = await func(self, workflow_path, **kwargs)
            
            # Only cache successful results
            if result.status.value == "success":
                cache.set(str(workflow_path), result, initial_input)
            
            return result
        
        return wrapper
    return decorator


def measure_performance(name: str):
    """Decorator to measure function execution time."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.info(f"{name} completed in {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"{name} failed after {duration:.2f}ms: {e}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = (time.time() - start_time) * 1000
                logger.info(f"{name} completed in {duration:.2f}ms")
                return result
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                logger.error(f"{name} failed after {duration:.2f}ms: {e}")
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, list] = {}
        
    def record(self, metric_name: str, value: float):
        """Record a performance metric."""
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].append({
            'value': value,
            'timestamp': datetime.utcnow()
        })
        
        # Keep only last 1000 entries per metric
        if len(self.metrics[metric_name]) > 1000:
            self.metrics[metric_name] = self.metrics[metric_name][-1000:]
    
    def get_stats(self, metric_name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if metric_name not in self.metrics:
            return {}
        
        values = [m['value'] for m in self.metrics[metric_name]]
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values),
            'last': values[-1]
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics."""
        return {
            metric: self.get_stats(metric)
            for metric in self.metrics
        }


# Global instances
workflow_cache = WorkflowCache(ttl_seconds=300)  # 5 minute cache
performance_monitor = PerformanceMonitor()