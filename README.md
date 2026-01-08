
---

# System//Zero  
**A local-first protocol for logging, pattern detection, and system behavior analysis.**

## Overview  
System//Zero is a tactical clarity tool for tracking how systems behave — platforms, processes, or people. It is built in phases, with each phase delivering a functional, testable layer. The protocol is designed for operators who need visibility, not assumptions.

---

## Current Status: Phase 7  
Phase 6 is complete. Phase 7 has started with API documentation and performance groundwork. FastAPI REST API + CLI server with 166/166 tests passing; container, systemd, PM2 options, and CI/CD are in place. New: `/openapi.yaml`, operator/developer guides, security scan workflow, and requirements lock.

---

## Repository Structure

| Path | Purpose |
|------|---------|
| **`systemzero/`** | Core logic, scripts, and modules for logging and analysis |
| **`.vscode/`** | Editor config for consistent development |
| **`.github/`** | GitHub workflows and issue templates |
| **`README.md`** | This file |
| **`ROADMAP`** | High-level development plan across phases |
| **`ARCHITECTURE.md`** | System design, module layout, and data flow |
| **`PHASE1_ANALYSIS.md`** | Postmortem and findings from Phase 1 |
| **`PHASE2_PLAN.md`** | Objectives and scope for Phase 2 |
| **`PHASE2_DEBRIEF.md`** | Mid-phase analysis and adjustments |
| **`PHASE2_SUMMARY.md`** | Summary of Phase 2 outcomes |
| **`PHASE3_PLAN.md`** | Draft plan for Phase 3 (UI and automation) |
| **`TESTING_STRATEGY_DEBRIEF.md`** | Notes on testing methodology and results |
| **`CHANGELOG.md`** | Commit-level change tracking |
| **`LEGAL.md`** | Licensing and usage terms |
| **`SECURITY.md`** | Security policy and disclosure process |
| **`docs/`** | Operator, developer, performance guides, and API reference |

---

## Phase Breakdown

### ✅ Phase 1: Baseline Logging  
- Manual offer logging (timestamp, type, outcome)  
- Local-only storage  
- No UI, CLI-only  
- Initial breach tracking logic  
- Analysis of suppression patterns

### ✅ Phase 2: Pattern Detection + Feedback  
- Real-time logging interface (CLI)  
- Pattern recognition (decline clusters, offer gaps, system behavior)  
- Operator feedback loop: log → analyze → adjust  
- Debrief and recalibration modules  
- Prep for UI scaffolding

### ✅ Phase 3: UI + Automation  

### 🚀 Phase 7: v1.0.0 Readiness (in progress)
- OpenAPI YAML route (`/openapi.yaml`) + export script
- Docs: Operator, Developer, Performance guides
- Benchmark script for core endpoints
- Security workflow: Trivy FS/image scans in CI
- Pinned requirements for reproducible builds

Quick links:
- API Docs (Swagger): /docs
- OpenAPI YAML: /openapi.yaml
- API Reference: [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- Operator Guide: [docs/OPERATOR_GUIDE.md](docs/OPERATOR_GUIDE.md)
- Developer Guide: [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md)
- Local-first Textual UIs for dashboard, replay, consistency monitor  
- Immutable log views with filtering and diff summaries  
- Operator-defined filters and triggers  
- Exportable logs and summaries

### ✅ Phase 4: Capture + Template Engine  
- Recorder + UI tree export, TemplateBuilder, validators, exporters  
- CLI capture/baseline/export commands; full capture-to-template flow  
- 103/103 tests passing

### ✅ Phase 5: REST API + CLI Server  
- FastAPI app exposing status, captures, templates, logs, dashboard  
- CLI `server` command to launch API (`run.py server --host --port --reload`)  
- API tests in place; 111/111 tests passing

### 🔮 Phase 6: Observability + Deployment Hardening (planning)  
- AuthZ/authN for API, metrics, health probes, container packaging

---

## Usage (Phase 5)

1. **Run REST API**  
   `python run.py server --host 0.0.0.0 --port 8000 --reload`
2. **Capture and build templates**  
   `python run.py capture` then `python run.py baseline --build <capture>`  
3. **Query via API**  
   Use `/status`, `/captures`, `/templates`, `/logs`, `/dashboard` (see `tests/test_api.py` for examples).  
4. **Export logs**  
   `python run.py export --format html` or GET `/logs/export?format=html`

---

## License  
This protocol is for personal use only. Redistribution or repackaging without consent is not permitted. See `LEGAL.md` for details.

---

