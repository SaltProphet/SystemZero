# Operator Guide

This guide helps operators deploy, monitor, and maintain System//Zero in production.

## Deployment
- Docker: see DEPLOYMENT.md for image, compose, and systemd usage.
- Configuration: environment-driven via `SZ_*` variables (see config/settings.yaml and core/utils/config.py).

## Health & Monitoring
- Health: GET /health, GET /readiness
- Metrics: GET /metrics (Prometheus-compatible)
- Logs: JSON structured logs to stdout/file, correlation IDs enabled

## Security
- Auth: API keys + RBAC
- Rate limiting: 60 rpm default, 40 burst (configurable)
- CORS: configure allowed origins via env

## API Documentation
- Swagger UI: /docs
- OpenAPI JSON: /openapi.json
- OpenAPI YAML: /openapi.yaml

## Operations
- Rotate API keys via POST /auth/token (admin role)
- Export logs via GET /logs/export?format=json|csv|html
- Template inventory via GET /templates

## Troubleshooting
- Verify config with /status
- Check hash chain integrity in logs via tests/helpers.verify_log_integrity
- Increase log level with SZ_LOG_LEVEL=DEBUG
