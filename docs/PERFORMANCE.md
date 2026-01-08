# Performance Baselines

Baseline latency metrics for key API endpoints, measured in-process via httpx.

## How to Run
```bash
python -m systemzero.scripts.bench_api
```

## Target SLOs
- p95 latency < 100ms
- Error rate < 0.1%

## Recording Results
- Capture output and commit to this document under a dated section.

## Latest Results (placeholder)
- GET /status: min=1.2ms avg=2.4ms p95=3.1ms max=7.8ms
- GET /health: min=1.1ms avg=2.2ms p95=3.0ms max=6.9ms
- GET /templates: min=2.0ms avg=4.1ms p95=5.2ms max=9.3ms
- GET /dashboard: min=2.3ms avg=4.5ms p95=5.5ms max=10.2ms
