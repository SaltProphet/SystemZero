"""Health check system for System//Zero."""
from enum import Enum
from pathlib import Path
from typing import Dict, List, Callable, Optional
from datetime import datetime, timezone
import traceback


class HealthStatus(str, Enum):
    """Health check status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class HealthCheck:
    """Individual health check result."""
    
    def __init__(
        self,
        name: str,
        status: HealthStatus,
        message: str = "",
        details: Optional[Dict] = None
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
        }


class HealthChecker:
    """Performs health checks on system dependencies."""
    
    def __init__(self):
        """Initialize health checker."""
        self._checks: List[Callable[[], HealthCheck]] = []
        
        # Register default checks
        self._register_default_checks()
    
    def _register_default_checks(self) -> None:
        """Register standard system checks."""
        self.register_check(self._check_log_directory)
        self.register_check(self._check_template_directory)
        self.register_check(self._check_api_keys_file)
    
    def register_check(self, check_func: Callable[[], HealthCheck]) -> None:
        """Register a custom health check function.
        
        Args:
            check_func: Function that returns a HealthCheck result
        """
        self._checks.append(check_func)
    
    def run_checks(self) -> Dict:
        """Run all registered health checks.
        
        Returns:
            Dictionary with overall status and individual check results
        """
        results = []
        overall_status = HealthStatus.HEALTHY
        
        for check_func in self._checks:
            try:
                result = check_func()
                results.append(result.to_dict())
                
                # Determine overall status (worst case wins)
                if result.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
                    
            except Exception as e:
                # If check itself fails, mark as unhealthy
                results.append({
                    "name": check_func.__name__,
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": f"Check failed: {str(e)}",
                    "details": {"exception": traceback.format_exc()},
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                overall_status = HealthStatus.UNHEALTHY
        
        return {
            "status": overall_status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": results,
        }
    
    @staticmethod
    def _check_log_directory() -> HealthCheck:
        """Check if log directory is writable."""
        log_dir = Path("logs")
        
        try:
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Try to create a test file
            test_file = log_dir / ".health_check"
            test_file.write_text("test")
            test_file.unlink()
            
            return HealthCheck(
                name="log_directory",
                status=HealthStatus.HEALTHY,
                message="Log directory is writable",
                details={"path": str(log_dir.absolute())}
            )
        except Exception as e:
            return HealthCheck(
                name="log_directory",
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot write to log directory: {e}",
                details={"path": str(log_dir.absolute())}
            )
    
    @staticmethod
    def _check_template_directory() -> HealthCheck:
        """Check if template directory is readable."""
        template_dir = Path("core/baseline/templates")
        
        try:
            if not template_dir.exists():
                return HealthCheck(
                    name="template_directory",
                    status=HealthStatus.DEGRADED,
                    message="Template directory does not exist",
                    details={"path": str(template_dir.absolute())}
                )
            
            # Try to list files
            templates = list(template_dir.glob("*.yaml"))
            
            return HealthCheck(
                name="template_directory",
                status=HealthStatus.HEALTHY,
                message=f"Template directory accessible with {len(templates)} templates",
                details={
                    "path": str(template_dir.absolute()),
                    "template_count": len(templates)
                }
            )
        except Exception as e:
            return HealthCheck(
                name="template_directory",
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot access template directory: {e}",
                details={"path": str(template_dir.absolute())}
            )
    
    @staticmethod
    def _check_api_keys_file() -> HealthCheck:
        """Check if API keys file is loadable."""
        keys_file = Path("config/api_keys.yaml")
        
        try:
            if not keys_file.exists():
                return HealthCheck(
                    name="api_keys_file",
                    status=HealthStatus.DEGRADED,
                    message="API keys file does not exist (expected for fresh install)",
                    details={"path": str(keys_file.absolute())}
                )
            
            # Try to load the file
            import yaml
            with open(keys_file, 'r') as f:
                data = yaml.safe_load(f)
            
            key_count = len(data.get("keys", {})) if isinstance(data, dict) else 0
            
            return HealthCheck(
                name="api_keys_file",
                status=HealthStatus.HEALTHY,
                message=f"API keys file loaded with {key_count} keys",
                details={
                    "path": str(keys_file.absolute()),
                    "key_count": key_count
                }
            )
        except Exception as e:
            return HealthCheck(
                name="api_keys_file",
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot load API keys file: {e}",
                details={"path": str(keys_file.absolute())}
            )


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker
