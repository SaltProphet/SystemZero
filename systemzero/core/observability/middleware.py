"""Request logging and metrics middleware for FastAPI."""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from core.observability.structured_logger import get_logger, add_context, clear_context
from core.observability.metrics import get_metrics


logger = get_logger(__name__)
metrics = get_metrics()


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests with timing and context."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add logging/metrics."""
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Add context for structured logging
        add_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else "unknown"
        )
        
        # Extract user from API key metadata if available
        user_role = None
        if hasattr(request.state, "api_key_metadata"):
            user_role = request.state.api_key_metadata.get("role")
            add_context(user_role=user_role)
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={"extra_fields": {
                "query_params": dict(request.query_params),
                "path_params": dict(request.path_params),
            }}
        )
        
        # Increment active requests gauge
        metrics.increment_gauge("http_requests_active")
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            metrics.increment_counter(
                "http_requests_total",
                labels={
                    "method": request.method,
                    "path": request.url.path,
                    "status": str(response.status_code)
                }
            )
            
            metrics.observe_histogram(
                "http_request_duration_seconds",
                duration,
                labels={
                    "method": request.method,
                    "path": request.url.path
                }
            )
            
            # Log response
            logger.info(
                f"Response {response.status_code}",
                extra={"extra_fields": {
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                }}
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            
            metrics.increment_counter(
                "http_requests_total",
                labels={
                    "method": request.method,
                    "path": request.url.path,
                    "status": "500"
                }
            )
            
            metrics.increment_counter(
                "http_errors_total",
                labels={
                    "method": request.method,
                    "path": request.url.path,
                    "exception": type(e).__name__
                }
            )
            
            # Log error
            logger.error(
                f"Request failed: {e}",
                exc_info=True,
                extra={"extra_fields": {
                    "duration_ms": round(duration * 1000, 2),
                    "exception_type": type(e).__name__,
                }}
            )
            
            raise
            
        finally:
            # Decrement active requests gauge
            metrics.decrement_gauge("http_requests_active")
            
            # Clear context for next request
            clear_context()


def configure_request_logging(app: ASGIApp) -> None:
    """Configure request logging middleware for a FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(RequestLoggingMiddleware)
