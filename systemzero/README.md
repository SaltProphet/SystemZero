System//Zero — environment parser

System//Zero watches accessibility trees, normalizes them, matches against YAML baselines, detects drift, and writes tamper-evident logs. Phase 3 is complete with live operator UIs and all tests passing (98/98).

Features
- Core pipeline: capture → normalize → signature → baseline match → drift detection → immutable log
- Hash-chained logging: `ImmutableLog` and `HashChain` maintain tamper-evident records
- Drift insights: structured diffs, severity tagging, transition checks, signature validation
- Operator UIs (Textual): live dashboard, forensic replay viewer, cross-app consistency monitor
- CLI commands: simulate trees, browse drift logs, replay timelines, status checks, launch UIs

Quick start
- Run CLI: `python run.py simulate discord` (default fixture) or `python run.py simulate path/to/tree.json`
- View drift log: `python run.py drift --log logs/systemzero.log`
- Replay log: `python run.py replay --log logs/systemzero.log --start 0 --end 20`
- Launch dashboard: `python run.py dashboard --log logs/systemzero.log`
- Launch forensic viewer: `python run.py forensic --log logs/systemzero.log`
- Launch consistency monitor: `python run.py consistency --log logs/systemzero.log`

Testing
- All tests pass: `pytest -q`
- Key areas covered: normalization, drift matching, logging integrity, CLI flows, UI wiring

Project layout
- config/: paths and settings
- core/: accessibility, normalization, baseline matching, drift detection, logging
- interface/: CLI entrypoint and Textual UIs (dashboard, forensic, consistency)
- extensions/: capture mode and template builder scaffolding
- tests/: fixtures, helpers, and 98 passing tests

Notes
- Default log path for CLI and UIs: `logs/systemzero.log` (UI widgets also accept `logs/drift.log`)
- Baselines live in core/baseline/templates
