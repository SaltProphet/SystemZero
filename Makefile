.PHONY: help install docs-api bench load openapi

VENV?=.venv
PY?=$(VENV)/bin/python
PIP?=$(VENV)/bin/pip
HOST?=http://localhost:8000

help:
	@echo "Targets: install, docs-api, bench, load, openapi"

install:
	$(PIP) install -r requirements.txt

openapi:
	$(PY) -m systemzero.scripts.export_openapi --out openapi.yaml

docs-api: openapi
	$(PY) -m systemzero.scripts.generate_api_reference --out docs/API_REFERENCE.md

bench:
	$(PY) -m systemzero.scripts.bench_api

load:
	@command -v locust >/dev/null 2>&1 || { echo "Locust not installed. Install with: pip install -r requirements-dev.txt"; exit 1; }
	LOCUST_HOST=$(HOST) locust -f load/locustfile.py --headless -u 100 -r 10 -t 2m
