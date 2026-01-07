# System//Zero - Quick Reference

**Last Updated**: January 7, 2026  
**Current Status**: Phase 5 Complete → Phase 6 Planning  
**Version**: v0.5.0 (API operational)

---

## 🚀 Quick Start

### Run REST API
```bash
cd /workspaces/SystemZero/systemzero
python run.py server --host 0.0.0.0 --port 8000
# API docs at: http://localhost:8000/docs
```

### Run Tests
```bash
cd /workspaces/SystemZero/systemzero
/workspaces/SystemZero/.venv/bin/python -m pytest
# Expected: 111 passed in ~1.3s
```

### CLI Commands
```bash
python run.py simulate discord       # Run pipeline simulation
python run.py drift                  # View drift events
python run.py capture                # Capture UI tree
python run.py baseline list          # List templates
python run.py export --format html   # Export logs
python run.py server                 # Start API server
```

---

## 📊 Project Status

| Phase | Status | Tests | Docs |
|-------|--------|-------|------|
| 0-5 | ✅ Complete | 111/111 | Current |
| 6 | 🔮 Planning | 134+ target | PHASE6_7_PLAN.md |
| 7 | 🔮 Planning | 150+ target | PHASE6_7_PLAN.md |

---

## 📚 Documentation Index

### High-Level Docs
- **README.md** - Project overview, status, phase breakdown
- **ROADMAP** - All phases with completion status
- **ARCHITECTURE.md** - System design, modules, data flow

### Phase Reports
- **PHASE1_ANALYSIS.md** - Core pipeline implementation
- **PHASE2_PLAN.md** + **PHASE2_DEBRIEF.md** + **PHASE2_SUMMARY.md** - Mock pipeline + tests
- **TESTING_STRATEGY_DEBRIEF.md** - Phase 2.5 testing hardening
- **PHASE3_PLAN.md** - Operator UIs (dashboard, forensic, consistency)
- **PHASE4_COMPLETION.md** - Capture + template engine
- **PHASE5_PLAN.md** + **PHASE5_COMPLETION.md** - REST API + CLI server

### Planning & Analysis
- **PHASE6_7_PLAN.md** - Detailed Phase 6-7 plan (auth, observability, CI/CD, v1.0)
- **PROJECT_ANALYSIS.md** - Current status, risks, technical debt, recommendations
- **VERIFICATION_DEBRIEF.md** - Session summary, test results, next steps

### Other
- **CHANGELOG.md** - All changes by phase
- **SECURITY.md** - Security policy
- **LEGAL.md** - Licensing

---

## 🎯 Next Actions

### Phase 6: Observability + Deployment (8-10 hours)
1. Add API authentication (API keys + roles)
2. Implement structured logging + metrics
3. Create health/readiness probes
4. Build Docker image + docker-compose
5. Add systemd + pm2 service templates
6. Environment config management

### Phase 7: Finalization (6-8 hours)
1. Achieve >90% test coverage
2. Set up GitHub Actions CI/CD
3. Complete operator + developer documentation
4. Run security audit
5. Add performance benchmarks
6. Release v1.0.0

---

## 🧪 Testing

**Test Suite**: 111 tests, 100% passing  
**Coverage**: ~75% overall (>90% target for Phase 7)  
**Run Command**: `pytest` (from systemzero/)

**Test Distribution**:
- Accessibility: 14 tests
- API: 8 tests
- Baseline: 11 tests
- Capture: 2 tests
- Drift: 31 tests
- Integration: 12 tests
- Logging: 12 tests
- Normalization: 18 tests
- Phase 4: 1 test
- Template builder: 2 tests

---

## 🔧 Technical Stack

**Core**: Python 3.12  
**API**: FastAPI + uvicorn  
**CLI**: argparse + rich  
**UI**: Textual (dashboards)  
**Testing**: pytest  
**Logging**: Immutable hash-chained logs  

---

## 📦 API Endpoints

- `GET /` - Service info
- `GET /status` - System status
- `POST /captures` - Create capture
- `GET /templates` - List templates
- `GET /templates/{id}` - Get template
- `POST /templates` - Build template
- `GET /logs` - List log entries
- `GET /logs/export` - Export logs
- `GET /dashboard` - Dashboard data

**Docs**: http://localhost:8000/docs (when server running)

---

## 🐛 Known Issues / Technical Debt

### Critical (Phase 6)
- No API authentication
- No rate limiting
- No structured logging
- No health checks

### Important (Phase 7)
- Test coverage <90%
- No CI/CD
- Incomplete docs (operator guides)
- No security audit

### Backlog (Post-v1.0)
- 21 enhancement tests
- Template versioning
- Performance optimization

---

## 🤝 Contributing

1. Run tests before committing: `pytest`
2. Update CHANGELOG.md for changes
3. Keep documentation current
4. Follow existing code structure
5. Target 100% test pass rate

---

**For detailed information, see individual phase documents and PROJECT_ANALYSIS.md**
