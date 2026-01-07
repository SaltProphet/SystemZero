# System//Zero – AI Coding Agent Instructions

## Project Overview
System//Zero is an environment parser that monitors UI state, detects drift from baseline expectations, and maintains tamper-evident audit logs. It's designed for situational awareness and manipulation detection in GUI environments.

**Core Pipeline Flow**: Accessibility Events → Tree Capture → Normalization → Signature Generation → Baseline Matching → Drift Detection → Immutable Logging

## Architecture

### Module Boundaries
- **core/accessibility/** - System event capture (EventStream, AccessibilityListener, TreeCapture)
- **core/normalization/** - Tree standardization (TreeNormalizer removes transient props, NodeClassifier categorizes elements, SignatureGenerator creates SHA256 fingerprints)
- **core/baseline/** - Template management (TemplateLoader reads YAML, TemplateValidator ensures structure)
- **core/drift/** - Deviation detection (Matcher compares trees, DiffEngine finds changes, TransitionChecker validates state flows)
- **core/logging/** - Immutable records (ImmutableLog uses HashChain for tamper-evidence, EventWriter handles persistence)
- **extensions/** - Optional features (capture_mode for recording new screens, template_builder for YAML generation)
- **interface/** - User interaction (cli/main.py entry point, api/server.py REST endpoints, ui/ for dashboards)

### Key Design Patterns
1. **Immutable Logging**: All events appended to hash-chained log (see [core/logging/immutable_log.py](core/logging/immutable_log.py#L11-L36)). NEVER modify existing entries.
2. **Deterministic Signatures**: SignatureGenerator excludes transient properties (`timestamp`, `id`, `focused`) for consistent hashing. Structure and content signatures computed separately.
3. **Template-Based Matching**: YAML templates in [core/baseline/templates/](core/baseline/templates/) define expected screens. Match scoring: 40% required nodes, 40% structure, 20% role distribution (see [core/drift/matcher.py](core/drift/matcher.py#L34-L59)).
4. **Tree Normalization Pipeline**: Raw tree → remove transients → map alternative prop names → sort children → generate signature. Property mappings: `label/title/text` → `name` (see [core/normalization/tree_normalizer.py](core/normalization/tree_normalizer.py#L18-L22)).

### Data Flow Example
```python
# Typical pipeline usage
tree = TreeCapture().capture()                    # Raw accessibility tree
normalized = TreeNormalizer().normalize(tree)     # Remove noise
sig = SignatureGenerator().generate(normalized)   # SHA256 fingerprint
templates = TemplateLoader().load_all()           # Baseline expectations
matcher = Matcher()
match, score = matcher.find_best_match(normalized, list(templates.values()))
if not match or score < 0.8:
    drift = DriftEvent("layout", "warning", {"score": score})
    ImmutableLog("logs/drift.log").append(drift)
```

## Development Workflow

### Running the System
```bash
# Main entry point
cd /workspaces/SystemZero/systemzero && python3 run.py

# Validate all Phase 1 imports
python3 -c "from core.normalization import TreeNormalizer, NodeClassifier, NoiseFilters, SignatureGenerator; ..."

# Run specific test modules
pytest tests/test_drift.py -v
```

### Project Status (per ROADMAP)
- ✅ Phase 0: Complete – scaffold with 74 files, core modules stubbed
- 🚧 Phase 1: IN PROGRESS – implementing core pipeline (ingestion → drift → logging)
- Upcoming: Phase 2 (mock testing), Phase 3 (operator dashboards), Phase 4 (template builder)

### Testing Conventions
- Tests in `tests/` mirror `core/` structure (e.g., `test_drift.py` covers `core/drift/`)
- All classes have placeholder tests (`assert True` stubs) – expand with real test cases
- Test templates available in [core/baseline/templates/](core/baseline/templates/) (discord_chat.yaml, doordash_offer.yaml)

## Critical Conventions

### 1. DriftEvent Structure
```python
# Drift types: "layout", "content", "sequence", "manipulative"
# Severity: "info", "warning", "critical"
drift = DriftEvent("layout", "critical", {
    "expected_sig": "abc123...",
    "actual_sig": "def456...",
    "missing_nodes": ["send_button"]
})
```

### 2. Hash Chain Integrity
Every log entry MUST include `previous_hash` linking to prior entry. Genesis hash is SHA256 of empty string. See [core/logging/hash_chain.py](core/logging/hash_chain.py#L17-L26).

### 3. Template YAML Schema
```yaml
screen_id: unique_identifier          # Required
required_nodes: [list, of, names]     # Semantic elements
structure_signature: "sha256_hash"    # Expected layout
valid_transitions: [other_screen_ids] # Allowed next states
```

### 4. Module Exports
Each `__init__.py` explicitly exports classes for clean imports (e.g., `from core.drift import DriftEvent` not `from core.drift.drift_event import DriftEvent`).

## Common Pitfalls
- ❌ Don't include transient props in signatures (`timestamp`, `id`, `focused`) – leads to false drift
- ❌ Don't validate YAML templates without TemplateValidator – missing `screen_id` breaks matching
- ❌ Don't modify ImmutableLog entries – breaks hash chain verification
- ❌ Don't assume TreeCapture returns normalized trees – always pipe through TreeNormalizer first
- ❌ Don't hardcode paths – use [config/paths.yaml](config/paths.yaml) or [config/settings.yaml](config/settings.yaml)

## When Implementing New Features
1. **Adding drift types**: Update [core/utils/constants.py](core/utils/constants.py) `DRIFT_TYPES` constant
2. **New templates**: Place in [core/baseline/templates/](core/baseline/templates/) with `.yaml` extension
3. **CLI commands**: Add to [interface/cli/commands.py](interface/cli/commands.py) and wire in [interface/cli/main.py](interface/cli/main.py)
4. **Extensions**: Create subdirectory under `extensions/` with `__init__.py`, `README.md`, and main module

## Integration Points
- **Accessibility APIs**: TreeCapture interfaces with system accessibility (currently mocked for Linux dev container)
- **File System**: Templates in YAML, logs in JSON lines format ([config/settings.yaml](config/settings.yaml) defines `log_path`)
- **CLI Entry**: [run.py](run.py) → [interface/cli/main.py](interface/cli/main.py) (single point of entry)

## Quick Reference
- **Import all Phase 1 modules**: See terminal history for validation command
- **Signature types**: `generate()` (full), `generate_structural()` (layout only), `generate_content()` (text only)
- **Matcher threshold**: Default 0.8 (80% similarity), configurable in constructor
- **Log verification**: `ImmutableLog.verify_integrity()` checks entire hash chain
