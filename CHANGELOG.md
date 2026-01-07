# System//Zero Changelog

All notable changes to this project will be documented in this file.

## [Phase 1.5] - 2026-01-07 - Pre-Phase 2 Foundation ✓ COMPLETE

### Added - Test Infrastructure & Fixtures

#### Test Fixtures Library
- **tests/fixtures/mock_trees.py** - Comprehensive mock UI trees
  - `DISCORD_CHAT_TREE` - Complete Discord chat interface
  - `DOORDASH_OFFER_TREE` - DoorDash driver offer card
  - `GMAIL_INBOX_TREE` - Gmail inbox layout
  - `SETTINGS_PANEL_TREE` - Settings panel with sections
  - `LOGIN_FORM_TREE` - Standard login form

- **tests/fixtures/drift_scenarios.py** - Pre-built drift test cases
  - `MISSING_BUTTON_DRIFT` - Layout drift with removed button
  - `TEXT_CHANGE_DRIFT` - Content drift with text modifications
  - `LAYOUT_SHIFT_DRIFT` - Structural changes
  - `MANIPULATIVE_PATTERN_DRIFT` - Dark pattern detection
  - `SEQUENCE_VIOLATION_DRIFT` - Invalid state transition

- **tests/fixtures/templates.py** - Programmatic template generation
  - `build_template()` - Create templates from trees
  - `template_from_tree()` - Auto-generate templates
  - Template builders for all mock trees

#### Integration Test Helpers
- **tests/helpers.py** - Full pipeline test utilities
  - `run_pipeline()` - Execute complete normalization → matching → drift pipeline
  - `verify_log_integrity()` - Validate hash chain integrity
  - `create_temp_log()` - Isolated test log creation
  - `assert_drift_detected()` - Semantic drift assertions
  - `compare_trees()` - Tree diff with DiffEngine
  - `load_all_test_templates()` - Load all test templates
  - `validate_template()` - Template validation
  - `simulate_drift_detection_pipeline()` - Full drift detection flow

#### CLI Command Stubs
- **interface/cli/commands.py** - Phase 2 command placeholders
  - `cmd_simulate()` - Run pipeline with mock tree
  - `cmd_drift()` - Display drift events from log
  - `cmd_replay()` - Replay events with timeline

#### Baseline Template Gallery
- **core/baseline/templates/discord_chat.yaml** - Completed with real signatures
- **core/baseline/templates/doordash_offer.yaml** - Completed with real signatures
- **core/baseline/templates/system_default.yaml** - Completed with real signatures
- **core/baseline/templates/gmail_inbox.yaml** - NEW: Gmail inbox template
- **core/baseline/templates/settings_panel.yaml** - NEW: Settings panel template
- **core/baseline/templates/login_form.yaml** - NEW: Login form template
- **core/baseline/templates/manipulative_upsell.yaml** - NEW: Dark pattern detection template

#### Documentation
- **tests/README.md** - Comprehensive test strategy guide
  - Expected pipeline behaviors
  - Hash chain verification procedures
  - Template matching edge cases
  - CLI output examples
  - Drift type documentation

### Summary
- 5 comprehensive mock UI trees for realistic testing
- 5 pre-built drift scenarios covering all drift types
- 8 integration helper functions for pipeline testing
- 7 YAML baseline templates with real signatures
- Complete test documentation for Phase 2 development

All materials verified and tested. Ready for Phase 2 implementation.

---

## [Phase 0] - 2026-01-07 - Baseline Confirmation ✓ COMPLETE

### Added - Initial Scaffolding (74 files)

#### Core Modules
- **core/accessibility/** - Accessibility event capture system
  - `__init__.py` - Package exports
  - `event_stream.py` - EventStream class for event queueing
  - `listener.py` - AccessibilityListener for system events
  - `permissions.py` - PermissionManager for access control
  - `tree_capture.py` - TreeCapture for UI tree snapshots

- **core/ingestion/** - Raw data ingestion layer
  - `__init__.py` - Package exports
  - `pixel_capture.py` - PixelCapture for screen captures
  - `screen_transition.py` - ScreenTransition detection
  - `ui_dump_raw.py` - UIDumpRaw for accessibility tree dumps

- **core/normalization/** - Tree normalization pipeline
  - `__init__.py` - Package exports
  - `node_classifier.py` - NodeClassifier for element categorization
  - `noise_filters.py` - NoiseFilters for irrelevant element removal
  - `signature_generator.py` - SignatureGenerator for layout fingerprinting
  - `tree_normalizer.py` - TreeNormalizer for tree standardization

- **core/baseline/** - Template and state management
  - `__init__.py` - Package exports
  - `state_machine.py` - StateMachine for state tracking
  - `template_loader.py` - TemplateLoader for YAML templates
  - `template_validator.py` - TemplateValidator for template verification
  - `templates/discord_chat.yaml` - Discord chat screen baseline
  - `templates/doordash_offer.yaml` - DoorDash offer card baseline
  - `templates/system_default.yaml` - Default fallback template

- **core/drift/** - Drift detection and analysis
  - `__init__.py` - Package exports
  - `diff_engine.py` - DiffEngine for tree comparison
  - `drift_event.py` - DriftEvent class for drift representation
  - `matcher.py` - Matcher for baseline matching
  - `transition_checker.py` - TransitionChecker for valid transitions

- **core/logging/** - Immutable logging system
  - `__init__.py` - Package exports
  - `event_writer.py` - EventWriter for log persistence
  - `hash_chain.py` - HashChain for tamper-evidence
  - `immutable_log.py` - ImmutableLog for append-only logs

- **core/utils/** - Shared utilities
  - `__init__.py` - Package exports
  - `config.py` - CONFIG dictionary
  - `constants.py` - DRIFT_TYPES constants
  - `hashing.py` - sha256 utility function
  - `timestamps.py` - now() utility function

#### Extensions
- **extensions/capture_mode/** - Screen capture mode
  - `__init__.py` - Package exports
  - `recorder.py` - Recorder for capture sessions
  - `signature_export.py` - SignatureExport utility
  - `ui_tree_export.py` - UITreeExport utility

- **extensions/template_builder/** - Template creation tools
  - `__init__.py` - Package exports
  - `builder.py` - TemplateBuilder for template generation
  - `exporters.py` - Exporters utility
  - `validators.py` - Validators utility

- **extensions/modules/** - User-defined modules directory
  - `README.md` - Module documentation
  - `__init__.py` - Package init

#### Interface Layer
- **interface/api/** - REST API
  - `__init__.py` - Package exports
  - `routes.py` - API routes placeholder
  - `serializers.py` - Serializer classes
  - `server.py` - start_server function

- **interface/cli/** - Command-line interface
  - `__init__.py` - Package exports
  - `commands.py` - cmd_status, cmd_drift, cmd_replay commands
  - `display.py` - display utility function
  - `main.py` - main() CLI entry point

- **interface/ui/** - User interface components
  - `__init__.py` - Package exports
  - `dashboard.py` - render_dashboard function
  - `drift_viewer.py` - DriftViewer class
  - `log_viewer.py` - LogViewer class

#### Configuration & Testing
- **config/** - Configuration files
  - `paths.yaml` - Path configuration
  - `permissions.yaml` - Permission configuration
  - `settings.yaml` - System settings

- **tests/** - Test suite
  - `__init__.py` - Package init
  - `test_accessibility.py` - Accessibility tests
  - `test_baseline.py` - Baseline tests
  - `test_drift.py` - Drift detection tests
  - `test_logging.py` - Logging tests
  - `test_normalization.py` - Normalization tests

- **scripts/** - Utility scripts
  - `__init__.py` - Package init
  - `dev_bootstrap.py` - bootstrap() function
  - `run_capture_mode.py` - Capture mode script
  - `run_replay_demo.py` - Replay demo script

#### Root Files
- `run.py` - Main entry point (calls interface.cli.main)
- `README.md` - Project documentation
- `.gitignore` - Git ignore rules

### Verified
- CLI entry point functional: `python systemzero/run.py` → "System//Zero CLI - placeholder"
- All 74 files created successfully
- 3 YAML baseline templates with valid content
- Drift engine classes (DriftEvent) initialized
- Logging classes (ImmutableLog, HashChain) initialized

---

## [Phase 1] - 2026-01-07 - Core Pipeline Implementation ✓ COMPLETE

### Goal
Build the ingestion → normalization → matching → logging pipeline

### Completed

#### 1. AccessibilityListener and TreeCapture ✓
- **core/accessibility/event_stream.py**
  - Thread-safe event queue with deque
  - Subscribe/publish pattern for listeners
  - Event history with configurable maxlen
  - `push()`, `subscribe()`, `get_recent()`, `clear()` methods

- **core/accessibility/tree_capture.py**
  - Platform-agnostic UI tree capture (Linux/macOS/Windows ready)
  - Recursive tree traversal with depth limits
  - Captures: timestamp, platform, active_window, root node
  - Mock implementation with accessibility roles (window, pane, button, text_field, etc.)
  - Structured node format: type, role, name, properties, bounds, children

- **core/accessibility/listener.py**
  - Background thread for continuous event monitoring
  - Configurable poll interval
  - Event enrichment with timestamps and metadata
  - Custom callback support
  - Lifecycle management: `start()`, `stop()`
  - Mock event generation (ready for OS API integration)

**Verified**: All modules import successfully, TreeCapture returns structured 4-key tree with platform detection

#### 2. TreeNormalizer, NodeClassifier, NoiseFilters ✓

- **core/normalization/tree_normalizer.py**
  - Removes transient properties (timestamps, IDs)
  - Standardizes property names across platforms
  - Sorts children for deterministic comparison
  - Recursive node normalization
  - Property mapping (label→name, title→name, etc.)

- **core/normalization/node_classifier.py**
  - Semantic classification: interactive, content, container, navigation, input, decorative
  - Role-based classification with extensive role sets
  - Significance detection for noise filtering
  - Extract interactive nodes from tree
  - Fallback to type and name-based classification

- **core/normalization/noise_filters.py**
  - Filters invisible/hidden elements
  - Removes zero-size elements
  - Filters transient status indicators (spinners, progress bars)
  - Removes decorative elements
  - Configurable filter settings
  - Extensible noise role/name lists

#### 3. SignatureGenerator ✓

- **core/normalization/signature_generator.py**
  - SHA256 signatures for normalized trees
  - Three signature types:
    - Full: Complete tree signature
    - Structural: Layout-only (ignores content)
    - Content: Text-only (ignores structure)
  - Deterministic JSON canonicalization
  - Ignores transient properties
  - `generate_multi()` for all signature types at once
  - Signature comparison utilities

**Verified**: Generates 64-char hex signatures (e.g., 138caa94ce580c58...)

#### 4. TemplateLoader and TemplateValidator ✓

- **core/baseline/template_loader.py**
  - YAML template loading with caching
  - Load single or all templates
  - Template lookup by screen_id
  - Automatic template directory detection
  - Reload functionality
  - List available templates

- **core/baseline/template_validator.py**
  - Validates required fields: screen_id, required_nodes, structure_signature
  - Type checking for all fields
  - Transition format validation (screen_a -> screen_b)
  - Detailed error reporting with `validate_with_errors()`
  - Batch validation for multiple templates
  - Screen ID uniqueness checking

**Verified**: Successfully loaded 3 templates (discord_chat, doordash_offer_card, system_default), all validated as True

#### 5. BaselineMatcher (Matcher), DiffEngine, TransitionChecker ✓

- **core/drift/matcher.py**
  - Similarity scoring with weighted metrics:
    - Required nodes matching (40%)
    - Structure similarity (40%)
    - Role distribution (20%)
  - Configurable similarity threshold (default 0.8)
  - Find best matching template from list
  - Tree depth and node count comparison
  - Role intersection analysis

- **core/drift/diff_engine.py**
  - Detailed tree comparison
  - Detects: added, removed, modified, unchanged nodes
  - Calculates similarity scores
  - Human-readable diff summaries
  - Property change tracking
  - Significance threshold for change detection
  - Recursive node comparison

- **core/drift/transition_checker.py**
  - Validates state transitions against templates
  - Transition history tracking (max 100)
  - Loop detection for dark pattern analysis
  - Forced flow detection (limited navigation)
  - Transition graph validation
  - Invalid transition reporting with expected alternatives

#### 6. Enhanced DriftEvent ✓

- **core/drift/drift_event.py**
  - Event types: layout, content, sequence, manipulative
  - Severity levels: info, warning, critical
  - Unique event IDs (SHA256-based)
  - Timestamp tracking
  - Serialization with `to_dict()`
  - Human-readable summaries
  - Factory methods:
    - `create_layout_drift()`
    - `create_content_drift()`
    - `create_sequence_drift()`
    - `create_manipulative_drift()`

#### 7. EventWriter, HashChain, ImmutableLog ✓

- **core/logging/hash_chain.py**
  - Cryptographic hash chain for tamper detection
  - SHA256-based entry linking
  - Genesis hash initialization
  - Entry verification: `verify_entry()`, `verify_chain()`
  - Chain length tracking
  - Computationally infeasible to tamper with history

- **core/logging/event_writer.py**
  - JSON line format (one JSON object per line)
  - Append-only writes
  - Auto-flush support
  - Batch write operations
  - Write count tracking
  - Context manager support
  - Error handling and logging

- **core/logging/immutable_log.py**
  - Append-only log with hash chain integrity
  - Automatic integrity verification
  - Entry search by hash or criteria
  - Load existing logs with verification
  - In-memory entry cache
  - Entry count and range queries
  - Context manager support

**Verified**: All logging components import and initialize successfully

### Summary
All 7 Phase 1 tasks completed successfully:
- [x] Implement AccessibilityListener and TreeCapture
- [x] Normalize UI trees via TreeNormalizer, NodeClassifier, NoiseFilters
- [x] Generate layout signatures with SignatureGenerator
- [x] Load and validate templates with TemplateLoader and TemplateValidator
- [x] Compare trees to baselines using BaselineMatcher, DiffEngine, TransitionChecker
- [x] Generate DriftEvent objects
- [x] Write to ImmutableLog with EventWriter and HashChain

**Total files implemented**: 13 core modules fully implemented
**Verification**: All imports successful, templates loaded and validated, signature generation tested

---
