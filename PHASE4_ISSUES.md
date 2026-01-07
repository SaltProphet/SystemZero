# Phase 4 Issue List

Tracking items for Phase 4 (Extension + Template Engine) and remaining Priority 2 enhancements.

## Core Phase 4 Work
- [ ] Recorder & UITreeExport
  - Goal: capture live accessibility trees to disk; export normalized trees for template authoring.
  - Deliverables: CLI entry (`run.py capture`), capture pipeline, saved artifacts under `captures/`, docs on usage.
- [ ] TemplateBuilder
  - Goal: convert captured trees into YAML templates with signatures and required nodes.
  - Deliverables: builder module, CLI entry (`run.py baseline --build`), sample templates, docs.
- [ ] Validators & Exporters
  - Goal: validate generated templates and export logs/templates to common formats (json/csv/html).
  - Deliverables: validator enhancements, exporter utilities, CLI wiring (`run.py export`).

## Priority 2 Enhancements (carryover)
- [ ] Matcher.calculate_score
  - Problem: scoring is stubbed/missing; tests expect similarity scoring per template.
  - Expected: deterministic score combining required nodes, structure, role distribution (per matcher docstring/roadmap 40/40/20 split).
  - Tests: update/enable matcher scoring tests in `tests/test_drift.py` and integration cases.
- [ ] DiffEngine structure outputs
  - Problem: diff currently returns simple dicts; some tests expect richer change objects/consistent schema.
  - Expected: explicit change records with added/removed/modified/moved and property deltas; ensure `diff_summary()` aligns with UI/CLI needs.
  - Tests: cover structural/content diff cases in `tests/test_drift.py` and integration pipelines.
- [ ] NodeClassifier role coverage
  - Problem: incomplete role mappings for interactive/container/static nodes.
  - Expected: map common accessibility roles/types (button, link, input, textarea, menu, list, grid, dialog, etc.); ensure deterministic categories.
  - Tests: expand classification cases in `tests/test_normalization.py` and fixtures.
- [ ] NoiseFilters behavior
  - Problem: filtering for decorative/hidden/transient nodes is incomplete.
  - Expected: implement filters for hidden/aria-hidden, empty labels, decorative icons; preserve focusable/interactable elements.
  - Tests: add filter coverage in `tests/test_normalization.py` and integration drift scenarios.

Notes
- Default log path: `logs/systemzero.log` (UIs also accept `logs/drift.log`).
- Keep outputs deterministic; avoid transient props (`timestamp`, `id`, `focused`) in signatures and comparisons.
