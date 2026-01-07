# System//Zero - Repository Architecture & Organization

## 📊 Repository Structure Analysis

### Overview Statistics
- **Total Python Files**: 74
- **Total YAML Templates**: 7
- **Lines of Code**: ~3,059 (excluding tests)
- **Module Count**: 8 core modules + 3 extensions + 3 interfaces

---

## 🏗️ Architectural Layers

### Layer 1: Core Pipeline (Production Code)
**Location**: `core/`
**Purpose**: Immutable production code for drift detection pipeline

```
core/
├── accessibility/      # System Integration Layer
├── ingestion/         # Raw Data Collection
├── normalization/     # Data Standardization
├── baseline/          # Template Management
├── drift/             # Deviation Detection
├── logging/           # Tamper-Evident Storage
└── utils/             # Shared Utilities
```

### Layer 2: Extensions (Optional Features)
**Location**: `extensions/`
**Purpose**: Pluggable functionality for advanced use cases

```
extensions/
├── capture_mode/      # Screen Recording
├── template_builder/  # YAML Generation
└── modules/           # User-Defined Plugins
```

### Layer 3: Interface Layer (User Interaction)
**Location**: `interface/`
**Purpose**: Multiple access points for operators

```
interface/
├── cli/               # Command-Line Interface
├── api/               # REST API (future)
└── ui/                # Dashboard/Viewer (future)
```

### Layer 4: Testing Infrastructure
**Location**: `tests/`
**Purpose**: Comprehensive test coverage and fixtures

```
tests/
├── fixtures/          # Mock data and scenarios
├── helpers.py         # Integration utilities
└── test_*.py          # Module-specific tests
```

---

## 📦 Module-by-Module Breakdown

### Core Modules (Ordered by Pipeline Flow)

#### 1. **core/accessibility/** - System Event Capture
**Stage**: Input
**Complexity**: 🟡 Medium (278 LOC)
**Status**: ✅ Phase 1 Complete

| File | Lines | Purpose | Dependencies |
|------|-------|---------|-------------|
| `tree_capture.py` | 91 | Capture UI accessibility tree | System APIs |
| `listener.py` | 87 | Listen for accessibility events | EventStream |
| `event_stream.py` | 41 | Queue and distribute events | None |
| `permissions.py` | 17 | Manage accessibility permissions | None |

**Key Pattern**: Mock-based development (returns structured mock data for Linux)

---

#### 2. **core/ingestion/** - Raw Data Collection
**Stage**: Input Processing
**Complexity**: 🟢 Low (95 LOC)
**Status**: ⚪ Stubbed (Phase 0)

| File | Lines | Purpose | Dependencies |
|------|-------|---------|-------------|
| `ui_dump_raw.py` | 46 | Raw accessibility tree dumps | TreeCapture |
| `pixel_capture.py` | 27 | Screen pixel capture (future) | System APIs |
| `screen_transition.py` | 22 | Detect screen changes | None |

**Note**: Minimal implementation - expand in Phase 4+

---

#### 3. **core/normalization/** - Tree Standardization
**Stage**: Data Cleaning
**Complexity**: 🔴 High (468 LOC)
**Status**: ✅ Phase 1 Complete

| File | Lines | Purpose | Key Algorithm |
|------|-------|---------|---------------|
| `signature_generator.py` | 136 | SHA256 fingerprints | Canonical JSON → Hash |
| `noise_filters.py` | 127 | Remove irrelevant elements | Transient prop filtering |
| `node_classifier.py` | 113 | Categorize UI elements | Role-based classification |
| `tree_normalizer.py` | 92 | Standardize tree structure | Property mapping + sorting |

**Critical Pattern**: Deterministic signatures (exclude `timestamp`, `id`, `focused`)

---

#### 4. **core/baseline/** - Template Management
**Stage**: Reference Data
**Complexity**: 🟡 Medium (261 LOC + 7 YAML files)
**Status**: ✅ Phase 1 + Phase 1.5 Complete

| File | Lines | Purpose | Output |
|------|-------|---------|--------|
| `template_validator.py` | 155 | Validate YAML schemas | Error list |
| `template_loader.py` | 106 | Load YAML templates | Template dict |
| `state_machine.py` | Stub | Track screen transitions | State history |

**Templates** (7 YAML files):
- `discord_chat.yaml` - Chat interface baseline
- `doordash_offer.yaml` - Driver offer card
- `gmail_inbox.yaml` - Email interface
- `login_form.yaml` - Authentication screen
- `settings_panel.yaml` - Settings interface
- `manipulative_upsell.yaml` - Dark pattern detection
- `system_default.yaml` - Fallback template

---

#### 5. **core/drift/** - Deviation Detection
**Stage**: Analysis
**Complexity**: 🔴 High (730 LOC)
**Status**: ✅ Phase 1 Complete

| File | Lines | Purpose | Algorithm |
|------|-------|---------|-----------|
| `transition_checker.py` | 206 | Validate state flows | History analysis + loop detection |
| `matcher.py` | 201 | Match trees to templates | Weighted scoring (40/40/20) |
| `diff_engine.py` | 199 | Compare tree structures | Recursive node diff |
| `drift_event.py` | 124 | Represent drift | Event serialization |

**Matching Weights**:
- 40% Required nodes present
- 40% Structure similarity
- 20% Role distribution

---

#### 6. **core/logging/** - Immutable Storage
**Stage**: Output
**Complexity**: 🔴 High (397 LOC)
**Status**: ✅ Phase 1 Complete

| File | Lines | Purpose | Security Feature |
|------|-------|---------|-----------------|
| `immutable_log.py` | 172 | Append-only log | Hash chain verification |
| `event_writer.py` | 112 | Persist events | JSON lines format |
| `hash_chain.py` | 113 | Tamper detection | SHA256 linking |

**Integrity Model**: Each entry links to previous via `previous_hash`

---

#### 7. **core/utils/** - Shared Utilities
**Stage**: Cross-cutting
**Complexity**: 🟢 Low (97 LOC)
**Status**: ✅ Phase 1 Complete

| File | Lines | Purpose |
|------|-------|---------|
| `timestamps.py` | 27 | Unified time handling |
| `constants.py` | 24 | Global constants |
| `hashing.py` | 23 | SHA256 wrapper |
| `config.py` | 23 | Configuration loading |

---

### Extensions (Optional Modules)

#### 1. **extensions/capture_mode/** - Screen Recording
**Complexity**: 🟢 Low (120 LOC)
**Status**: ⚪ Stubbed (Phase 4)

| File | Purpose |
|------|---------|
| `recorder.py` | Capture session management |
| `ui_tree_export.py` | Export trees for analysis |
| `signature_export.py` | Export signatures |

---

#### 2. **extensions/template_builder/** - YAML Generation
**Complexity**: 🟢 Low (105 LOC)
**Status**: ⚪ Stubbed (Phase 4)

| File | Purpose |
|------|---------|
| `builder.py` | Generate templates from captures |
| `exporters.py` | Export to YAML |
| `validators.py` | Validate generated templates |

---

### Interface Layers

#### 1. **interface/cli/** - Command-Line Interface
**Complexity**: 🟡 Medium (201 LOC)
**Status**: 🚧 Phase 1.5 (stubs) → Phase 2 (implementation)

| File | Lines | Purpose | Status |
|------|-------|---------|--------|
| `commands.py` | 110 | CLI command implementations | Stubbed |
| `display.py` | 45 | Output formatting | Stubbed |
| `main.py` | 46 | Entry point | Basic |

**Planned Commands**:
- `sz simulate` - Run pipeline with mock data
- `sz drift` - Display drift events
- `sz replay` - Timeline navigation

---

#### 2. **interface/api/** - REST API
**Complexity**: 🟢 Low (96 LOC)
**Status**: ⚪ Stubbed (Phase 5)

Future HTTP endpoints for remote access.

---

#### 3. **interface/ui/** - Dashboard/Viewer
**Complexity**: 🟢 Low (84 LOC)
**Status**: ⚪ Stubbed (Phase 3)

Future TUI/GUI for operators.

---

### Testing Infrastructure

#### **tests/** - Test Suite
**Complexity**: 🔴 High (868 LOC)
**Status**: ✅ Phase 1.5 Complete

| Component | Files | Lines | Purpose |
|-----------|-------|-------|---------|
| **Fixtures** | 3 | 500 | Mock data library |
| **Helpers** | 1 | 259 | Integration utilities |
| **Test Modules** | 5 | 109 | Unit tests |

**Fixture Breakdown**:
- `mock_trees.py` (179 LOC) - 5 realistic UI trees
- `drift_scenarios.py` (196 LOC) - 5 drift test cases
- `templates.py` (125 LOC) - Template builders

---

## 🔄 Data Flow Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM//ZERO PIPELINE                    │
└─────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │ Accessibility│  1. EVENT CAPTURE
  │   Events     │     • TreeCapture → raw tree
  │              │     • Listener → event stream
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Normalization│  2. DATA CLEANING
  │              │     • TreeNormalizer → remove transients
  │   Filters    │     • NodeClassifier → categorize
  └──────┬───────┘     • SignatureGenerator → SHA256
         │
         ▼
  ┌──────────────┐
  │  Baseline    │  3. TEMPLATE MATCHING
  │  Templates   │     • TemplateLoader → load YAML
  │              │     • Matcher → score similarity (0.0-1.0)
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Drift Engine │  4. DEVIATION DETECTION
  │              │     • DiffEngine → find changes
  │   Analysis   │     • TransitionChecker → validate flow
  └──────┬───────┘     • DriftEvent → generate alert
         │
         ▼
  ┌──────────────┐
  │  Immutable   │  5. TAMPER-EVIDENT LOGGING
  │     Log      │     • HashChain → link entries
  │              │     • EventWriter → persist JSON lines
  └──────────────┘
```

---

## 📈 Complexity & Maturity Matrix

| Module | LOC | Complexity | Status | Next Phase |
|--------|-----|------------|--------|-----------|
| **drift/** | 730 | 🔴 High | ✅ Complete | Phase 2 testing |
| **normalization/** | 468 | 🔴 High | ✅ Complete | Phase 2 testing |
| **logging/** | 397 | 🔴 High | ✅ Complete | Phase 6 signing |
| **accessibility/** | 278 | 🟡 Medium | ✅ Complete | Phase 5 real APIs |
| **baseline/** | 261 | 🟡 Medium | ✅ Complete | Phase 4 versioning |
| **cli/** | 201 | 🟡 Medium | 🚧 Partial | Phase 2 commands |
| **capture_mode/** | 120 | 🟢 Low | ⚪ Stubbed | Phase 4 recording |
| **template_builder/** | 105 | 🟢 Low | ⚪ Stubbed | Phase 4 generation |
| **utils/** | 97 | 🟢 Low | ✅ Complete | - |
| **api/** | 96 | 🟢 Low | ⚪ Stubbed | Phase 5 REST |
| **ingestion/** | 95 | 🟢 Low | ⚪ Stubbed | Phase 5 expansion |
| **ui/** | 84 | 🟢 Low | ⚪ Stubbed | Phase 3 dashboard |

---

## 🎯 Module Dependencies

### Dependency Graph (Production Code)

```
┌─────────────────────────────────────────────────────────────┐
│                     DEPENDENCY LAYERS                        │
└─────────────────────────────────────────────────────────────┘

Layer 1 (No Dependencies):
  • core/utils/

Layer 2 (Utils Only):
  • core/accessibility/
  • core/ingestion/

Layer 3 (L1 + L2):
  • core/normalization/    (uses utils)
  • core/baseline/         (uses utils)
  • core/logging/          (uses utils, hashing)

Layer 4 (L1 + L2 + L3):
  • core/drift/            (uses normalization, baseline, logging)

Layer 5 (Interface):
  • interface/cli/         (uses ALL core)
  • interface/api/         (uses ALL core)
  • interface/ui/          (uses ALL core)

Layer 6 (Extensions):
  • extensions/*           (uses core + interface)

Layer 7 (Testing):
  • tests/                 (uses ALL)
```

### Critical Path (Minimum for Pipeline)
```
utils → accessibility → normalization → baseline → drift → logging
```

---

## 🔐 Security-Critical Files

| File | Risk Level | Why Critical |
|------|-----------|--------------|
| `logging/hash_chain.py` | 🔴 High | Tamper detection mechanism |
| `logging/immutable_log.py` | 🔴 High | Append-only integrity |
| `normalization/signature_generator.py` | 🟡 Medium | Deterministic fingerprints |
| `baseline/template_validator.py` | 🟡 Medium | Prevent malicious templates |
| `drift/transition_checker.py` | 🟡 Medium | Detect forced flows |

---

## 📝 Configuration Files

| File | Purpose | Format | Values |
|------|---------|--------|--------|
| `config/settings.yaml` | System settings | YAML | `log_path` |
| `config/paths.yaml` | File paths | YAML | Directory mappings |
| `config/permissions.yaml` | Access control | YAML | Permission levels |

---

## 🚀 Entry Points

### Primary
- **`run.py`** → `interface.cli.main` → CLI entry point

### Testing
- **`tests/helpers.py`** → `run_pipeline()` → Full pipeline execution
- **`scripts/dev_bootstrap.py`** → Development setup
- **`scripts/run_capture_mode.py`** → Capture mode launcher
- **`scripts/run_replay_demo.py`** → Replay demonstration

---

## 📊 File Size Distribution

```
Large Files (>200 LOC):
  ├── tests/helpers.py                    (259 LOC)
  ├── core/drift/transition_checker.py    (206 LOC)
  └── core/drift/matcher.py               (201 LOC)

Medium Files (100-200 LOC):
  ├── core/drift/diff_engine.py           (199 LOC)
  ├── tests/fixtures/drift_scenarios.py   (196 LOC)
  ├── tests/fixtures/mock_trees.py        (179 LOC)
  ├── core/logging/immutable_log.py       (172 LOC)
  └── ... (11 more files)

Small Files (<100 LOC):
  └── 50+ files
```

---

## 🎨 Naming Conventions

### Patterns Observed
- **Classes**: `PascalCase` (e.g., `TreeNormalizer`, `DriftEvent`)
- **Functions**: `snake_case` (e.g., `run_pipeline`, `verify_log_integrity`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DRIFT_TYPES`, `DISCORD_CHAT_TREE`)
- **Private Methods**: `_leading_underscore` (e.g., `_normalize_node`)
- **Test Functions**: `test_` prefix (e.g., `test_matcher`)

### Module Naming
- **Core**: Singular nouns (e.g., `drift`, `logging`, not `drifts`, `loggings`)
- **Utilities**: Plural for collections (e.g., `utils`, not `util`)
- **Templates**: YAML files use `snake_case` (e.g., `discord_chat.yaml`)

---

## 🔮 Future Organization

### Recommended Additions (Phase 3+)

```
systemzero/
├── docs/                          # User documentation
│   ├── api-reference.md
│   ├── operator-guide.md
│   └── deployment.md
├── examples/                      # Usage examples
│   ├── simple_drift_detection.py
│   └── custom_template.yaml
└── benchmarks/                    # Performance tests
    ├── signature_speed.py
    └── log_integrity_bench.py
```

---

## 📚 Related Documentation

- **[ROADMAP](ROADMAP)** - Development phases
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[.github/copilot-instructions.md](.github/copilot-instructions.md)** - AI agent guidance
- **[tests/README.md](systemzero/tests/README.md)** - Testing strategy

---

## 🏆 Best Practices Encoded

1. **Separation of Concerns**: Core, Extensions, Interface cleanly separated
2. **Immutability**: Logging layer enforces append-only semantics
3. **Determinism**: Signature generation excludes transient properties
4. **Testability**: Comprehensive fixtures and helpers for every module
5. **Modularity**: Each module has single responsibility (SOLID principles)
6. **Documentation**: Docstrings, type hints, and inline comments throughout

---

**Last Updated**: Phase 1.5 Complete (2026-01-07)
**Total Files Analyzed**: 74 Python + 7 YAML + 5 Markdown
**Architecture Status**: ✅ Production-Ready Core | 🚧 Extensions Stubbed
