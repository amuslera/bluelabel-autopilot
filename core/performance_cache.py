"""
Performance optimization utilities for Bluelabel Autopilot.
Provides caching, connection pooling, and request batching.
"""

import asyncio
import time
from typing import Dict, Any, Optional, Callable, List, TypeVar, Generic
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
import logging
from collections import deque
from threading import Lock

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TTLCache(Generic[T]):
    """Thread-safe Time-To-Live cache implementation."""
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[str, tuple[T, float]] = {}
        self._access_order = deque()
        self._lock = Lock()
        self._hits = 0
        self._misses = 0
        
    def get(self, key: str) -> Optional[T]:
        """Get value from cache if not expired."""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    self._hits += 1
                    # Move to end (LRU)
                    self._access_order.remove(key)
                    self._access_order.append(key)
                    return value
                else:
                    # Expired
                    del self._cache[key]
                    self._access_order.remove(key)
            
            self._misses += 1
            return None
    
    def set(self, key: str, value: T):
        """Set value in cache with TTL."""
        with self._lock:
            expiry = time.time() + self.ttl_seconds
            
            # Remove old entry if exists
            if key in self._cache:
                self._access_order.remove(key)
            
            # Check size limit
            while len(self._cache) >= self.max_size:
                # Remove oldest
                oldest = self._access_order.popleft()
                del self._cache[oldest]
            
            self._cache[key] = (value, expiry)
            self._access_order.append(key)
    
    def clear(self):
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "ttl_seconds": self.ttl_seconds,
                "max_size": self.max_size
            }


class AsyncBatchProcessor:
    """Batch multiple requests for efficient processing."""
    
    def __init__(self, 
                 process_func: Callable,
                 batch_size: int = 10,
                 batch_timeout: float = 0.1):
        self.process_func = process_func
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self._queue = asyncio.Queue()
        self._processor_task = None
        self._running = False
        
    async def start(self):
        """Start the batch processor."""
        if not self._running:
            self._running = True
            self._processor_task = asyncio.create_task(self._process_batches())
            
    async def stop(self):
        """Stop the batch processor."""
        self._running = False
        if self._processor_task:
            await self._processor_task
            
    async def add_request(self, item: Any) -> Any:
        """Add item to batch queue and get result."""
        future = asyncio.Future()
        await self._queue.put((item, future))
        return await future
        
    async def _process_batches(self):
        """Process batches of requests."""
        while self._running:
            batch = []
            futures = []
            
            try:
                # Collect batch
                deadline = time.time() + self.batch_timeout
                
                while len(batch) < self.batch_size and time.time() < deadline:
                    timeout = max(0, deadline - time.time())
                    
                    try:
                        item, future = await asyncio.wait_for(
                            self._queue.get(),
                            timeout=timeout
                        )
                        batch.append(item)
                        futures.append(future)
                    except asyncio.TimeoutError:
                        break
                
                if batch:
                    # Process batch
                    try:
                        results = await self.process_func(batch)
                        
                        # Return results
                        for i, future in enumerate(futures):
                            if i < len(results):
                                future.set_result(results[i])
                            else:
                                future.set_exception(Exception("No result returned"))
                                
                    except Exception as e:
                        # Set error for all futures
                        for future in futures:
                            future.set_exception(e)
                            
            except Exception as e:
                logger.error(f"Batch processor error: {e}")
                await asyncio.sleep(0.1)  # Prevent tight loop on error


class ConnectionPool:
    """Generic connection pool for reusable resources."""
    
    def __init__(self,
                 create_func: Callable,
                 max_size: int = 10,
                 min_size: int = 2):
        self.create_func = create_func
        self.max_size = max_size
        self.min_size = min_size
        self._pool = asyncio.Queue(maxsize=max_size)
        self._size = 0
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize pool with minimum connections."""
        async with self._lock:
            for _ in range(self.min_size):
                conn = await self.create_func()
                await self._pool.put(conn)
                self._size += 1
                
    async def acquire(self):
        """Acquire connection from pool."""
        # Try to get from pool
        try:
            return await asyncio.wait_for(self._pool.get(), timeout=0.1)
        except asyncio.TimeoutError:
            pass
            
        # Create new if under limit
        async with self._lock:
            if self._size < self.max_size:
                conn = await self.create_func()
                self._size += 1
                return conn
                
        # Wait for available connection
        return await self._pool.get()
        
    async def release(self, conn):
        """Return connection to pool."""
        try:
            await self._pool.put(conn)
        except asyncio.QueueFull:
            # Pool full, close connection
            if hasattr(conn, 'close'):
                await conn.close()
            async with self._lock:
                self._size -= 1


def cached(cache: TTLCache, key_func: Optional[Callable] = None):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = {
                    "func": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }
                cache_key = hashlib.md5(
                    json.dumps(key_data, sort_keys=True).encode()
                ).hexdigest()
            
            # Check cache
            result = cache.get(cache_key)
            if result is not None:
                return result
                
            # Call function
            result = await func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result)
            
            return result
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = {
                    "func": func.__name__,
                    "args": args,
                    "kwargs": kwargs
                }
                cache_key = hashlib.md5(
                    json.dumps(key_data, sort_keys=True).encode()
                ).hexdigest()
            
            # Check cache
            result = cache.get(cache_key)
            if result is not None:
                return result
                
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(cache_key, result)
            
            return result
        
        # Return appropriate wrapper
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self._metrics = {}
        self._lock = Lock()
        
    def record_metric(self, name: str, value: float, unit: str = "ms"):
        """Record a performance metric."""
        with self._lock:
            if name not in self._metrics:
                self._metrics[name] = {
                    "values": deque(maxlen=1000),  # Keep last 1000 values
                    "unit": unit,
                    "count": 0,
                    "sum": 0,
                    "min": float('inf'),
                    "max": 0
                }
            
            metric = self._metrics[name]
            metric["values"].append(value)
            metric["count"] += 1
            metric["sum"] += value
            metric["min"] = min(metric["min"], value)
            metric["max"] = max(metric["max"], value)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all performance metrics."""
        with self._lock:
            results = {}
            
            for name, metric in self._metrics.items():
                values = list(metric["values"])
                if values:
                    sorted_values = sorted(values)
                    count = len(values)
                    
                    results[name] = {
                        "unit": metric["unit"],
                        "count": metric["count"],
                        "current_avg": metric["sum"] / metric["count"],
                        "recent_avg": sum(values) / count,
                        "min": metric["min"],
                        "max": metric["max"],
                        "p50": sorted_values[count // 2],
                        "p95": sorted_values[int(count * 0.95)],
                        "p99": sorted_values[int(count * 0.99)]
                    }
                    
            return results
    
    def measure(self, name: str):
        """Context manager for measuring operation time."""
        class TimeMeasurer:
            def __init__(self, monitor, metric_name):
                self.monitor = monitor
                self.metric_name = metric_name
                self.start_time = None
                
            def __enter__(self):
                self.start_time = time.time()
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                duration = (time.time() - self.start_time) * 1000  # Convert to ms
                self.monitor.record_metric(self.metric_name, duration)
                
        return TimeMeasurer(self, name)


# Global instances
workflow_cache = TTLCache[Dict[str, Any]](ttl_seconds=300, max_size=100)
agent_result_cache = TTLCache[Any](ttl_seconds=600, max_size=500)
performance_monitor = PerformanceMonitor()