"""Security middleware for System//Zero API: CORS, rate limiting, request validation."""
import time
from typing import Dict, Optional, List
from collections import defaultdict, deque
from datetime import datetime, timezone

from fastapi import Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """Rate limiter using sliding window algorithm."""
    
    def __init__(
        self,
        requests_per_minute: int = 100,
        burst_size: int = 20
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Max requests per minute per client
            burst_size: Max requests in a short burst
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.window_size = 60  # 60 seconds
        
        # Track requests per client (IP or API key)
        self._requests: Dict[str, deque] = defaultdict(deque)
    
    def _cleanup_old_requests(self, client_id: str, current_time: float) -> None:
        """Remove requests outside the time window."""
        queue = self._requests[client_id]
        cutoff_time = current_time - self.window_size
        
        while queue and queue[0] < cutoff_time:
            queue.popleft()
    
    def check_rate_limit(self, client_id: str) -> tuple[bool, Optional[str]]:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Unique client identifier (IP or API key)
            
        Returns:
            Tuple of (allowed, error_message)
        """
        current_time = time.time()
        
        # Clean up old requests
        self._cleanup_old_requests(client_id, current_time)
        
        queue = self._requests[client_id]
        request_count = len(queue)
        
        # Check burst limit (last 5 seconds)
        recent_cutoff = current_time - 5
        recent_count = sum(1 for t in queue if t > recent_cutoff)
        
        if recent_count >= self.burst_size:
            return False, f"Rate limit exceeded: max {self.burst_size} requests per 5 seconds"
        
        # Check per-minute limit
        if request_count >= self.requests_per_minute:
            return False, f"Rate limit exceeded: max {self.requests_per_minute} requests per minute"
        
        # Record this request
        queue.append(current_time)
        return True, None
    
    def get_stats(self, client_id: str) -> Dict[str, int]:
        """Get rate limit stats for a client."""
        current_time = time.time()
        self._cleanup_old_requests(client_id, current_time)
        
        queue = self._requests[client_id]
        recent_cutoff = current_time - 5
        recent_count = sum(1 for t in queue if t > recent_cutoff)
        
        return {
            "requests_last_minute": len(queue),
            "requests_last_5_seconds": recent_count,
            "limit_per_minute": self.requests_per_minute,
            "burst_limit": self.burst_size,
            "remaining": max(0, self.requests_per_minute - len(queue))
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting."""
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 100,
        burst_size: int = 20,
        enabled: bool = True
    ):
        super().__init__(app)
        self.limiter = RateLimiter(requests_per_minute, burst_size)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        if not self.enabled:
            return await call_next(request)
        
        # Get client identifier (API key > IP address)
        client_id = request.headers.get("X-API-Key")
        if not client_id:
            client_id = request.client.host if request.client else "unknown"
        
        # Check rate limit
        allowed, error_msg = self.limiter.check_rate_limit(client_id)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=error_msg,
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.limiter.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        
        stats = self.limiter.get_stats(client_id)
        response.headers["X-RateLimit-Limit"] = str(stats["limit_per_minute"])
        response.headers["X-RateLimit-Remaining"] = str(stats["remaining"])
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit request body size."""
    
    def __init__(self, app, max_size_mb: int = 10):
        super().__init__(app)
        self.max_size = max_size_mb * 1024 * 1024  # Convert to bytes
    
    async def dispatch(self, request: Request, call_next):
        """Check request size before processing."""
        content_length = request.headers.get("content-length")
        
        if content_length and int(content_length) > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Request body too large. Max size: {self.max_size // (1024*1024)}MB"
            )
        
        return await call_next(request)


def configure_cors(
    app,
    allowed_origins: Optional[List[str]] = None,
    allow_credentials: bool = True,
    allow_methods: Optional[List[str]] = None,
    allow_headers: Optional[List[str]] = None
):
    """
    Configure CORS middleware for the FastAPI app.
    
    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins (default: ["*"])
        allow_credentials: Whether to allow credentials
        allow_methods: Allowed HTTP methods (default: all)
        allow_headers: Allowed headers (default: all)
    """
    if allowed_origins is None:
        allowed_origins = ["*"]
    
    if allow_methods is None:
        allow_methods = ["*"]
    
    if allow_headers is None:
        allow_headers = ["*"]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]
    )


def configure_security(
    app,
    cors_origins: Optional[List[str]] = None,
    rate_limit_rpm: int = 100,
    rate_limit_burst: int = 20,
    max_request_size_mb: int = 10,
    enable_rate_limiting: bool = True,
    trusted_hosts: Optional[List[str]] = None
):
    """
    Configure all security middleware for the app.
    
    Args:
        app: FastAPI application
        cors_origins: Allowed CORS origins
        rate_limit_rpm: Requests per minute limit
        rate_limit_burst: Burst size limit
        max_request_size_mb: Max request body size in MB
        enable_rate_limiting: Whether to enable rate limiting
        trusted_hosts: List of trusted host patterns
    """
    # CORS
    configure_cors(app, allowed_origins=cors_origins)
    
    # Rate limiting
    if enable_rate_limiting:
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=rate_limit_rpm,
            burst_size=rate_limit_burst,
            enabled=True
        )
    
    # Request size limits
    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_size_mb=max_request_size_mb
    )
    
    # Trusted hosts (optional)
    if trusted_hosts:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=trusted_hosts
        )


# Security configuration defaults
DEFAULT_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000"
]

DEFAULT_RATE_LIMITS = {
    "requests_per_minute": 100,
    "burst_size": 20
}

DEFAULT_MAX_REQUEST_SIZE_MB = 10
