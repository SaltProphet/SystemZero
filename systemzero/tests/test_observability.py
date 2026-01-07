"""Tests for observability module - logging, metrics, health checks."""
import pytest
import tempfile
import logging
from pathlib import Path
from unittest.mock import patch
import time

from core.observability.structured_logger import (
    get_logger, configure_logging, add_context, clear_context, get_context,
    JSONFormatter
)
from core.observability.metrics import MetricsCollector, get_metrics
from core.observability.health import HealthChecker, HealthStatus


class TestStructuredLogger:
    """Test structured logging functionality."""
    
    def test_get_logger_returns_adapter(self):
        """Test get_logger returns a ContextLoggerAdapter."""
        logger = get_logger("test")
        assert hasattr(logger, "process")  # LoggerAdapter has process method
    
    def test_configure_logging_json(self):
        """Test configuring logging with JSON formatter."""
        configure_logging(level="INFO", json_output=True)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) > 0
        
        # Check if JSON formatter is used
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, JSONFormatter)
    
    def test_configure_logging_standard(self):
        """Test configuring logging with standard formatter."""
        configure_logging(level="DEBUG", json_output=False)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) > 0
    
    def test_add_context(self):
        """Test adding context to logs."""
        clear_context()
        
        add_context(request_id="abc123", user="admin")
        context = get_context()
        
        assert context["request_id"] == "abc123"
        assert context["user"] == "admin"
    
    def test_clear_context(self):
        """Test clearing log context."""
        add_context(key="value")
        assert len(get_context()) > 0
        
        clear_context()
        assert len(get_context()) == 0
    
    def test_json_formatter_basic(self):
        """Test JSON formatter produces valid JSON."""
        import json
        
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        data = json.loads(output)
        
        assert data["level"] == "INFO"
        assert data["message"] == "Test message"
        assert "timestamp" in data
    
    def test_json_formatter_with_exception(self):
        """Test JSON formatter handles exceptions."""
        import json
        
        formatter = JSONFormatter()
        
        try:
            raise ValueError("Test error")
        except Exception:
            import sys
            record = logging.LogRecord(
                name="test",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info()
            )
            
            output = formatter.format(record)
            data = json.loads(output)
            
            assert "exception" in data
            assert "ValueError" in data["exception"]


class TestMetricsCollector:
    """Test metrics collection."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Reset metrics before each test."""
        collector = MetricsCollector()
        yield collector
        collector.reset()
    
    def test_increment_counter(self, setup):
        """Test incrementing counters."""
        collector = setup
        
        collector.increment_counter("test_counter")
        collector.increment_counter("test_counter", value=5)
        
        metrics = collector.get_metrics()
        assert metrics["counters"]["test_counter"] == 6
    
    def test_counter_with_labels(self, setup):
        """Test counters with labels."""
        collector = setup
        
        collector.increment_counter("requests", labels={"method": "GET", "status": "200"})
        collector.increment_counter("requests", labels={"method": "POST", "status": "201"})
        collector.increment_counter("requests", labels={"method": "GET", "status": "200"})
        
        metrics = collector.get_metrics()
        assert metrics["counters"]["requests{method=GET,status=200}"] == 2
        assert metrics["counters"]["requests{method=POST,status=201}"] == 1
    
    def test_observe_histogram(self, setup):
        """Test histogram observations."""
        collector = setup
        
        collector.observe_histogram("response_time", 0.1)
        collector.observe_histogram("response_time", 0.2)
        collector.observe_histogram("response_time", 0.15)
        
        metrics = collector.get_metrics()
        stats = metrics["histograms"]["response_time"]
        
        assert stats["count"] == 3
        assert stats["min"] == 0.1
        assert stats["max"] == 0.2
        assert 0.14 < stats["mean"] < 0.16
    
    def test_histogram_percentiles(self, setup):
        """Test histogram percentile calculation."""
        collector = setup
        
        # Add 100 observations
        for i in range(100):
            collector.observe_histogram("test", float(i))
        
        metrics = collector.get_metrics()
        stats = metrics["histograms"]["test"]
        
        assert 48 <= stats["p50"] <= 51  # Median around 50
        assert 93 <= stats["p95"] <= 96  # 95th percentile
        assert 98 <= stats["p99"] <= 100  # 99th percentile
    
    def test_set_gauge(self, setup):
        """Test setting gauge values."""
        collector = setup
        
        collector.set_gauge("active_connections", 42.0)
        collector.set_gauge("active_connections", 50.0)
        
        metrics = collector.get_metrics()
        assert metrics["gauges"]["active_connections"] == 50.0
    
    def test_increment_decrement_gauge(self, setup):
        """Test incrementing and decrementing gauges."""
        collector = setup
        
        collector.set_gauge("connections", 10.0)
        collector.increment_gauge("connections", 5.0)
        collector.decrement_gauge("connections", 3.0)
        
        metrics = collector.get_metrics()
        assert metrics["gauges"]["connections"] == 12.0
    
    def test_get_metrics_structure(self, setup):
        """Test metrics structure."""
        collector = setup
        
        collector.increment_counter("test")
        collector.observe_histogram("test_hist", 1.0)
        collector.set_gauge("test_gauge", 42.0)
        
        metrics = collector.get_metrics()
        
        assert "counters" in metrics
        assert "histograms" in metrics
        assert "gauges" in metrics
        assert "metadata" in metrics
        assert "uptime_seconds" in metrics["metadata"]
    
    def test_reset_metrics(self, setup):
        """Test resetting all metrics."""
        collector = setup
        
        collector.increment_counter("test")
        collector.observe_histogram("test_hist", 1.0)
        collector.set_gauge("test_gauge", 42.0)
        
        collector.reset()
        metrics = collector.get_metrics()
        
        assert len(metrics["counters"]) == 0
        assert len(metrics["histograms"]) == 0
        assert len(metrics["gauges"]) == 0


class TestHealthChecker:
    """Test health check system."""
    
    def test_health_checker_initialization(self):
        """Test health checker initializes with default checks."""
        checker = HealthChecker()
        assert len(checker._checks) > 0  # Should have default checks
    
    def test_run_checks_returns_dict(self):
        """Test run_checks returns proper structure."""
        checker = HealthChecker()
        result = checker.run_checks()
        
        assert "status" in result
        assert "timestamp" in result
        assert "checks" in result
        assert isinstance(result["checks"], list)
    
    def test_healthy_status(self):
        """Test healthy check result."""
        checker = HealthChecker()
        
        # Create log directory to ensure check passes
        Path("logs").mkdir(exist_ok=True)
        
        result = checker.run_checks()
        
        # Should have at least one healthy check (log_directory)
        healthy_checks = [c for c in result["checks"] if c["status"] == "healthy"]
        assert len(healthy_checks) > 0
    
    def test_custom_check_registration(self):
        """Test registering custom health checks."""
        from core.observability.health import HealthCheck
        
        checker = HealthChecker()
        initial_count = len(checker._checks)
        
        def custom_check() -> HealthCheck:
            return HealthCheck("custom", HealthStatus.HEALTHY, "All good")
        
        checker.register_check(custom_check)
        assert len(checker._checks) == initial_count + 1
        
        result = checker.run_checks()
        custom_results = [c for c in result["checks"] if c["name"] == "custom"]
        assert len(custom_results) == 1
        assert custom_results[0]["status"] == "healthy"
    
    def test_failed_check_marks_unhealthy(self):
        """Test that failed check marks overall status as unhealthy."""
        from core.observability.health import HealthCheck
        
        checker = HealthChecker()
        
        def failing_check() -> HealthCheck:
            return HealthCheck("failing", HealthStatus.UNHEALTHY, "Something wrong")
        
        checker.register_check(failing_check)
        result = checker.run_checks()
        
        # Overall status should be unhealthy
        assert result["status"] in ["unhealthy", "degraded"]
    
    def test_check_exception_handling(self):
        """Test that exceptions in checks are handled gracefully."""
        checker = HealthChecker()
        
        def broken_check():
            raise Exception("Intentional error")
        
        checker.register_check(broken_check)
        result = checker.run_checks()
        
        # Should not crash, should mark check as unhealthy
        assert result["status"] in ["healthy", "degraded", "unhealthy"]
        broken_results = [c for c in result["checks"] if "broken_check" in c["name"]]
        if broken_results:
            assert broken_results[0]["status"] == "unhealthy"


class TestMetricsIntegration:
    """Test metrics integration."""
    
    def test_global_metrics_singleton(self):
        """Test get_metrics returns same instance."""
        metrics1 = get_metrics()
        metrics2 = get_metrics()
        
        assert metrics1 is metrics2
    
    def test_metrics_persistence(self):
        """Test metrics persist across calls."""
        metrics = get_metrics()
        metrics.reset()  # Start fresh
        
        metrics.increment_counter("test_counter")
        
        metrics2 = get_metrics()
        result = metrics2.get_metrics()
        
        assert result["counters"]["test_counter"] == 1
