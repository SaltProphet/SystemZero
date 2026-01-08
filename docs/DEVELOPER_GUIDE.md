# Developer Guide

This guide covers local development, testing, and extension building.

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
```bash
cd systemzero
python run.py
```

## Tests
```bash
pytest tests/ -v --cov
```

## Export OpenAPI
```bash
python -m systemzero.scripts.export_openapi --out openapi.yaml
```

## Benchmark Endpoints
```bash
python -m systemzero.scripts.bench_api
```

## Coding Standards
- See CONVENTIONS.md for naming and structure
- Use type hints everywhere
- Keep functions small and focused

## Building Extensions
- Add under extensions/<your_module>
- Provide __init__.py re-exports and README
- Include tests under tests/ to validate behavior
