# Release Notes (Draft)

## v1.0.0 (Target)

### Highlights
- Production-ready release with documented API, operator and developer guides
- Performance baselines and benchmarks for core endpoints
- Hardened CI/CD with security scans and reproducible builds

### New
- OpenAPI YAML at `/openapi.yaml`; export script added
- API Reference (generated from OpenAPI): `docs/API_REFERENCE.md`
- Operator Guide: `docs/OPERATOR_GUIDE.md`
- Developer Guide: `docs/DEVELOPER_GUIDE.md`
- Performance Guide: `docs/PERFORMANCE.md`
- Kubernetes manifests under `deployment/k8s/`

### Improvements
- Code hygiene pass completed (naming/exports, no backups)
- Requirements pinned via `requirements-lock.txt`
- README quick links for discoverability

### Security
- CI workflows scanning repository and Docker image with Trivy
- Rate limiting defaults: 60 rpm, 40 burst (configurable)

### Breaking Changes
- None; all changes are backward compatible

### Upgrade Notes
- No migrations required
- Optional: set `SZ_RATE_LIMIT_RPM` if higher throughput needed

### Known Issues
- Dashboard Textual version is pinned to 0.58.1; upgrade planned post-1.0.0

---

## v0.7.0
- Phase 6 complete + Phase 7 starting
- See CHANGELOG for details
