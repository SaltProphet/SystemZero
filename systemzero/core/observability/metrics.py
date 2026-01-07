"""Metrics collection for System//Zero - counters, histograms, gauges."""
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional
import threading


class MetricsCollector:
    """In-memory metrics collector for API observability."""
    
    def __init__(self):
        """Initialize metrics storage."""
        self._lock = threading.Lock()
        
        # Counters: incrementing values
        self._counters: Dict[str, int] = defaultdict(int)
        
        # Histograms: list of observations for percentile calculation
        self._histograms: Dict[str, List[float]] = defaultdict(list)
        
        # Gauges: current value (can increase/decrease)
        self._gauges: Dict[str, float] = {}
        
        # Metadata
        self._start_time = datetime.now(timezone.utc)
    
    def increment_counter(self, name: str, value: int = 1, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric.
        
        Args:
            name: Counter name (e.g., "http_requests_total")
            value: Amount to increment by (default 1)
            labels: Optional labels dict (e.g., {"method": "GET", "status": "200"})
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._counters[key] += value
    
    def observe_histogram(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Record a histogram observation.
        
        Args:
            name: Histogram name (e.g., "http_request_duration_seconds")
            value: Observed value
            labels: Optional labels dict
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._histograms[key].append(value)
            
            # Limit histogram size to prevent memory issues
            if len(self._histograms[key]) > 10000:
                self._histograms[key] = self._histograms[key][-10000:]
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric to a specific value.
        
        Args:
            name: Gauge name (e.g., "active_connections")
            value: Current value
            labels: Optional labels dict
        """
        key = self._make_key(name, labels)
        with self._lock:
            self._gauges[key] = value
    
    def increment_gauge(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment a gauge metric.
        
        Args:
            name: Gauge name
            value: Amount to increment by
            labels: Optional labels dict
        """
        key = self._make_key(name, labels)
        with self._lock:
            current = self._gauges.get(key, 0.0)
            self._gauges[key] = current + value
    
    def decrement_gauge(self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Decrement a gauge metric.
        
        Args:
            name: Gauge name
            value: Amount to decrement by
            labels: Optional labels dict
        """
        self.increment_gauge(name, -value, labels)
    
    def get_metrics(self) -> Dict[str, any]:
        """Get all metrics as a dictionary.
        
        Returns:
            Dictionary with counters, histograms (with stats), gauges, and metadata
        """
        with self._lock:
            # Calculate histogram statistics
            histogram_stats = {}
            for key, observations in self._histograms.items():
                if observations:
                    sorted_obs = sorted(observations)
                    histogram_stats[key] = {
                        "count": len(observations),
                        "sum": sum(observations),
                        "min": sorted_obs[0],
                        "max": sorted_obs[-1],
                        "mean": sum(observations) / len(observations),
                        "p50": self._percentile(sorted_obs, 0.50),
                        "p95": self._percentile(sorted_obs, 0.95),
                        "p99": self._percentile(sorted_obs, 0.99),
                    }
            
            uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
            
            return {
                "counters": dict(self._counters),
                "histograms": histogram_stats,
                "gauges": dict(self._gauges),
                "metadata": {
                    "start_time": self._start_time.isoformat(),
                    "uptime_seconds": uptime,
                }
            }
    
    def reset(self) -> None:
        """Reset all metrics (useful for testing)."""
        with self._lock:
            self._counters.clear()
            self._histograms.clear()
            self._gauges.clear()
            self._start_time = datetime.now(timezone.utc)
    
    @staticmethod
    def _make_key(name: str, labels: Optional[Dict[str, str]]) -> str:
        """Create a unique key from name and labels."""
        if not labels:
            return name
        
        # Sort labels for consistent keys
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    @staticmethod
    def _percentile(sorted_data: List[float], p: float) -> float:
        """Calculate percentile from sorted data."""
        if not sorted_data:
            return 0.0
        
        k = (len(sorted_data) - 1) * p
        f = int(k)
        c = k - f
        
        if f + 1 < len(sorted_data):
            return sorted_data[f] + c * (sorted_data[f + 1] - sorted_data[f])
        else:
            return sorted_data[f]


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Get the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector
