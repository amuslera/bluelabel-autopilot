"""
API middleware for logging, monitoring, and error handling.

Provides request/response logging and performance tracking.
"""

import time
import logging
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import traceback
from datetime import datetime


logger = logging.getLogger(__name__)


async def log_requests(request: Request, call_next: Callable) -> Response:
    """Log all API requests with timing information."""
    # Generate request ID
    request_id = f"{datetime.utcnow().timestamp()}-{hash(request)}"
    
    # Start timer
    start_time = time.time()
    
    # Log request
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = (time.time() - start_time) * 1000
    
    # Log response
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"completed in {duration:.2f}ms with status {response.status_code}"
    )
    
    # Add timing header
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{duration:.2f}ms"
    
    return response


async def handle_errors(request: Request, call_next: Callable) -> Response:
    """Global error handler for unhandled exceptions."""
    try:
        return await call_next(request)
    except Exception as e:
        # Log full traceback
        logger.error(f"Unhandled exception: {e}\n{traceback.format_exc()}")
        
        # Return standardized error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(e),
                "path": request.url.path,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


class MetricsMiddleware:
    """Collect API metrics for monitoring."""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0
        self.endpoint_stats = {}
    
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Track metrics for each request."""
        endpoint = f"{request.method} {request.url.path}"
        start_time = time.time()
        
        # Increment request count
        self.request_count += 1
        
        try:
            # Process request
            response = await call_next(request)
            
            # Track errors
            if response.status_code >= 400:
                self.error_count += 1
            
            # Track response time
            duration = (time.time() - start_time) * 1000
            self.total_response_time += duration
            
            # Track per-endpoint stats
            if endpoint not in self.endpoint_stats:
                self.endpoint_stats[endpoint] = {
                    "count": 0,
                    "total_time": 0,
                    "errors": 0
                }
            
            self.endpoint_stats[endpoint]["count"] += 1
            self.endpoint_stats[endpoint]["total_time"] += duration
            
            if response.status_code >= 400:
                self.endpoint_stats[endpoint]["errors"] += 1
            
            return response
            
        except Exception as e:
            self.error_count += 1
            raise
    
    def get_metrics(self) -> dict:
        """Get current metrics."""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": self.error_count / self.request_count if self.request_count > 0 else 0,
            "avg_response_time_ms": avg_response_time,
            "endpoints": self.endpoint_stats
        }


# Global metrics instance
metrics = MetricsMiddleware()