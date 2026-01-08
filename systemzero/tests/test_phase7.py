"""Phase 7 coverage and hardening tests."""
from pathlib import Path

from fastapi.testclient import TestClient

from core.drift.diff_engine import DiffEngine
from core.logging import ImmutableLog
from core.observability.metrics import MetricsCollector
from interface.api.security import RateLimiter
from interface.api.server import app


client = TestClient(app)


def test_diff_engine_deep_nested_changes():
    engine = DiffEngine()
    tree_a = {
        "root": {
            "role": "window",
            "name": "A",
            "children": [
                {"role": "button", "name": "save", "children": []},
                {
                    "role": "container",
                    "name": "panel",
                    "children": [
                        {"role": "label", "name": "v1", "value": "old"},
                        {"role": "input", "name": "field", "value": "abc"},
                    ],
                },
            ],
        }
    }
    tree_b = {
        "root": {
            "role": "window",
            "name": "A",
            "children": [
                {"role": "button", "name": "save", "children": []},
                {
                    "role": "container",
                    "name": "panel",
                    "children": [
                        {"role": "label", "name": "v1", "value": "new"},
                        {"role": "input", "name": "field", "value": "abcd"},
                        {"role": "button", "name": "extra", "value": None},
                    ],
                },
            ],
        }
    }

    result = engine.diff(tree_a, tree_b)
    assert result["unchanged"] >= 1
    assert len(result["modified"]) >= 1
    assert len(result["added"]) >= 1
    assert result["similarity"] < 1.0
    summary = engine.diff_summary(result)
    assert "Added:" in summary and "Modified:" in summary


def test_metrics_histogram_cap_and_percentiles():
    metrics = MetricsCollector()
    for i in range(10050):
        metrics.observe_histogram("latency", float(i))
    data = metrics.get_metrics()["histograms"].get("latency")
    assert data["count"] == 10000  # capped
    assert data["min"] == 50.0
    assert data["max"] == 10049.0
    assert data["p99"] >= 9949


def test_rate_limiter_burst_blocking():
    limiter = RateLimiter(requests_per_minute=10, burst_size=2)
    allowed, _ = limiter.check_rate_limit("client")
    allowed2, _ = limiter.check_rate_limit("client")
    allowed3, msg3 = limiter.check_rate_limit("client")
    assert allowed and allowed2
    assert not allowed3
    assert "requests per 5 seconds" in (msg3 or "")


def test_logs_export_success_and_cleanup():
    log_path = Path("logs/systemzero.log")
    backup_bytes = None
    if log_path.exists():
        backup_bytes = log_path.read_bytes()
        log_path.unlink()

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log = ImmutableLog(str(log_path))
    log.append({"event_type": "test", "drift_type": "layout", "severity": "info"})

    response = client.get("/logs/export?format=json")
    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("application/json")

    # Cleanup: remove created export files in /tmp
    for file in Path("/tmp").glob("export_*.json"):
        try:
            file.unlink()
        except OSError as exc:
            # Do not fail the test on cleanup issues, but surface the problem for debugging.
            print(f"Warning: failed to delete temp export file {file}: {exc}")

    if log_path.exists():
        log_path.unlink()
    if backup_bytes is not None:
        log_path.write_bytes(backup_bytes)


def test_logs_export_invalid_format():
    """Test export endpoint rejects invalid formats."""
    invalid = client.get("/logs/export?format=xml")
    assert invalid.status_code == 422