# Phase 2: Mock Pipeline + Test Harness - Detailed Implementation Plan

## Overview
**Goal**: Simulate events and validate pipeline behavior with comprehensive testing infrastructure

**Status**: Ready to begin (Phase 1 complete, Phase 1.5 fixtures ready)

**Timeline**: Estimated 3-5 development sessions

---

## Current State Analysis

### ✅ What We Have (Phase 1 Complete)
1. **Core Pipeline Components**
   - ✓ TreeCapture - captures UI trees (mock implementation ready for OS APIs)
   - ✓ TreeNormalizer - removes transient properties, maps alternative names
   - ✓ NodeClassifier - categorizes nodes (interactive, static, container, etc.)
   - ✓ NoiseFilters - removes irrelevant elements
   - ✓ SignatureGenerator - creates SHA256 fingerprints (structural + content + full)
   - ✓ TemplateLoader - loads YAML templates with validation
   - ✓ TemplateValidator - validates template structure (screen_id, required_nodes, etc.)
   - ✓ Matcher - compares trees to baselines with scoring algorithm
   - ✓ DiffEngine - finds differences between trees
   - ✓ TransitionChecker - validates state transitions
   - ✓ DriftEvent - represents drift occurrences
   - ✓ ImmutableLog - append-only logging
   - ✓ HashChain - tamper-evident hash chaining
   - ✓ EventWriter - writes events to disk

2. **Test Infrastructure (Phase 1.5)**
   - ✓ Mock UI trees: DISCORD_CHAT_TREE, DOORDASH_OFFER_TREE, LOGIN_FORM_TREE, etc.
   - ✓ Drift scenarios: MISSING_BUTTON_DRIFT, CONTENT_CHANGE_DRIFT, etc.
   - ✓ Template fixtures with real signatures
   - ✓ Integration test helpers: `run_pipeline()`, `create_test_log()`, etc.

3. **CLI Skeleton**
   - ✓ cmd_simulate() - stubbed
   - ✓ cmd_drift() - stubbed
   - ✓ cmd_replay() - stubbed
   - ✓ cmd_status() - stubbed

### ❌ What We Need (Phase 2 Objectives)

1. **Functional CLI Commands**
   - Interactive simulation mode (`sz simulate <tree.json>`)
   - Drift event viewer (`sz drift --filter=layout`)
   - Log replay with timeline (`sz replay --start=0 --end=100`)
   - System status dashboard (`sz status`)

2. **End-to-End Pipeline Testing**
   - Automated test suite running full pipeline
   - Validation of each pipeline stage
   - Hash chain integrity verification
   - Template matching accuracy tests

3. **Mock Event Generation**
   - Simulate accessibility events without OS dependencies
   - Generate event sequences for various scenarios
   - Test state transitions and edge cases

4. **Log Analysis Tools**
   - Parse and display log entries
   - Verify hash chain integrity
   - Filter and search drift events
   - Export reports

---

## Phase 2 Tasks Breakdown

### Task 1: Implement `cmd_simulate` - Pipeline Simulation CLI
**Priority**: HIGH | **Estimated Time**: 1-2 hours

**Objective**: Run the full pipeline on mock trees and display results

**Implementation Steps**:
1. Read JSON tree from file or use fixture
2. Run through normalization → signature → matching → drift detection
3. Display results in terminal with Rich formatting:
   - Tree structure preview
   - Normalization changes
   - Signature (truncated)
   - Best template match + score
   - Detected drift events
   - Log entry created

**Files to Modify**:
- `interface/cli/commands.py` - Implement `cmd_simulate()`
- `interface/cli/display.py` - Add Rich display utilities
- `interface/cli/main.py` - Wire simulate command with argparse

**Dependencies**: Rich library for terminal formatting

**Test Cases**:
- Simulate with DISCORD_CHAT_TREE → should match discord_chat template
- Simulate with MISSING_BUTTON_DRIFT → should detect layout drift
- Simulate with unknown tree → should return low match scores

**Deliverable**: `python run.py simulate tests/fixtures/mock_trees.json --template=discord_chat`

---

### Task 2: Implement `cmd_drift` - Drift Event Viewer
**Priority**: HIGH | **Estimated Time**: 1 hour

**Objective**: Display and filter drift events from immutable log

**Implementation Steps**:
1. Load log file (default: logs/systemzero.log)
2. Parse JSON entries
3. Filter by drift type if specified
4. Display in formatted table with columns:
   - Index | Timestamp | Type | Severity | Details
5. Support pagination for large logs
6. Show summary statistics (counts by type)

**Files to Modify**:
- `interface/cli/commands.py` - Implement `cmd_drift()`
- `interface/cli/display.py` - Add table formatting
- `core/logging/immutable_log.py` - Add `read_entries()` method

**Test Cases**:
- View all drift events
- Filter by type: `sz drift --filter=layout`
- Filter by severity: `sz drift --severity=critical`
- Empty log handling

**Deliverable**: `python run.py drift --filter=layout --severity=warning`

---

### Task 3: Implement `cmd_replay` - Log Replay Viewer
**Priority**: MEDIUM | **Estimated Time**: 1-2 hours

**Objective**: Replay logged events with timeline navigation

**Implementation Steps**:
1. Load log entries from file
2. Display in chronological order with timeline
3. For each entry show:
   - Entry number / total
   - Timestamp (relative and absolute)
   - Event type and data
   - Drift events if present
   - Hash chain link (previous hash)
4. Support range selection (--start, --end)
5. Add interactive mode with arrow key navigation (optional for Phase 2)

**Files to Modify**:
- `interface/cli/commands.py` - Implement `cmd_replay()`
- `interface/cli/display.py` - Add timeline formatting

**Test Cases**:
- Replay all events: `sz replay`
- Replay range: `sz replay --start=10 --end=20`
- Replay single event: `sz replay --entry=15`
- Verify hash chain during replay

**Deliverable**: `python run.py replay logs/systemzero.log --start=0 --end=50`

---

### Task 4: Implement `cmd_status` - System Status Dashboard
**Priority**: LOW | **Estimated Time**: 30 minutes

**Objective**: Display current system state and configuration

**Implementation Steps**:
1. Show configuration summary:
   - Log path and size
   - Template count and locations
   - Pipeline module status
2. Show recent activity:
   - Last N events
   - Drift summary (counts by type)
   - Log integrity status
3. Format as dashboard with Rich panels

**Files to Modify**:
- `interface/cli/commands.py` - Implement `cmd_status()`
- `interface/cli/display.py` - Add dashboard layout

**Test Cases**:
- Status with empty log
- Status with active log
- Status with templates loaded

**Deliverable**: `python run.py status`

---

### Task 5: Build Automated Test Suite
**Priority**: HIGH | **Estimated Time**: 2-3 hours

**Objective**: Comprehensive pytest suite for pipeline validation

**Implementation Areas**:

#### 5.1 Normalization Tests (`tests/test_normalization.py`)
- Test TreeNormalizer removes transient properties
- Test property mapping (label→name, title→name)
- Test NodeClassifier categorization
- Test NoiseFilters removes noise nodes
- Test signature determinism (same tree = same signature)

#### 5.2 Baseline Tests (`tests/test_baseline.py`)
- Test TemplateLoader loads all YAML files
- Test TemplateValidator catches invalid templates
- Test template matching with mock trees
- Test scoring algorithm accuracy

#### 5.3 Drift Tests (`tests/test_drift.py`)
- Test Matcher finds best match
- Test DiffEngine detects differences
- Test TransitionChecker validates transitions
- Test all drift scenarios from fixtures:
  - MISSING_BUTTON_DRIFT → layout drift
  - CONTENT_CHANGE_DRIFT → content drift
  - INVALID_TRANSITION_DRIFT → sequence drift

#### 5.4 Logging Tests (`tests/test_logging.py`)
- Test ImmutableLog append operation
- Test HashChain integrity
- Test hash verification
- Test EventWriter persistence
- Test log reading and parsing
- Test tampering detection

#### 5.5 Integration Tests (`tests/test_integration.py`)
- Test full pipeline: capture → normalize → match → log
- Test with all fixture trees
- Test drift detection end-to-end
- Test log replay accuracy

**Files to Modify**:
- `tests/test_normalization.py` - Expand with real tests
- `tests/test_baseline.py` - Expand with real tests
- `tests/test_drift.py` - Expand with real tests
- `tests/test_logging.py` - Expand with real tests
- `tests/test_integration.py` - Create new file

**Test Execution**:
```bash
pytest tests/ -v                    # Run all tests
pytest tests/test_drift.py -v      # Run specific module
pytest tests/ -k "signature"       # Run tests matching keyword
pytest tests/ --cov=core           # With coverage report
```

**Deliverable**: 50+ passing tests with >80% coverage

---

### Task 6: Mock Event Generation System
**Priority**: MEDIUM | **Estimated Time**: 1-2 hours

**Objective**: Generate realistic accessibility event sequences for testing

**Implementation Steps**:
1. Create event generator in `tests/fixtures/event_generator.py`:
   - Generate window focus events
   - Generate element click events
   - Generate text input events
   - Generate screen transition events
2. Create event sequences for scenarios:
   - Normal user flow (login → chat → logout)
   - Drift injection (normal → manipulative upsell)
   - State transition tests
3. Integrate with AccessibilityListener mock mode

**Files to Create**:
- `tests/fixtures/event_generator.py` - EventGenerator class
- `tests/fixtures/event_sequences.py` - Pre-built sequences

**Test Cases**:
- Generate 100 events → all have proper structure
- Generate with drift injection → drift detected
- Generate invalid transition → TransitionChecker catches

**Deliverable**: Reusable event generator for all testing scenarios

---

### Task 7: Hash Chain Validation Tests
**Priority**: HIGH | **Estimated Time**: 1 hour

**Objective**: Ensure immutable log tamper-evidence works correctly

**Implementation Steps**:
1. Create log with multiple entries
2. Verify each entry links to previous
3. Test tampering detection:
   - Modify log entry → verify_integrity() fails
   - Delete log entry → missing link detected
   - Reorder entries → chain breaks
4. Test genesis hash (first entry)
5. Test hash chain reconstruction

**Files to Modify**:
- `tests/test_logging.py` - Add chain validation tests
- `core/logging/immutable_log.py` - Add `verify_integrity()` method

**Test Cases**:
- Valid chain with 100 entries → passes
- Modified entry at position 50 → fails at 51
- Missing entry → gap detected
- Reordered entries → hash mismatch

**Deliverable**: Bulletproof tamper detection system

---

### Task 8: CLI Integration and Argument Parsing
**Priority**: HIGH | **Estimated Time**: 1 hour

**Objective**: Wire all CLI commands with proper argument parsing

**Implementation Steps**:
1. Update `interface/cli/main.py` with argparse:
   ```python
   parser = argparse.ArgumentParser(prog='sz')
   subparsers = parser.add_subparsers()
   
   # simulate command
   sim_parser = subparsers.add_parser('simulate')
   sim_parser.add_argument('tree_path')
   sim_parser.add_argument('--template', '-t')
   
   # drift command
   drift_parser = subparsers.add_parser('drift')
   drift_parser.add_argument('--filter', choices=['layout', 'content', 'sequence', 'manipulative'])
   drift_parser.add_argument('--severity', choices=['info', 'warning', 'critical'])
   
   # ... etc
   ```
2. Add command aliases (sz = systemzero)
3. Add --help documentation for all commands
4. Add --version flag

**Files to Modify**:
- `interface/cli/main.py` - Implement full argparse
- `run.py` - Support direct command invocation

**Test Cases**:
- `python run.py --help` → shows all commands
- `python run.py simulate --help` → shows simulate usage
- Invalid command → helpful error message

**Deliverable**: Professional CLI with full argument support

---

## Success Criteria

Phase 2 is complete when:

1. ✅ **CLI Commands Work**
   - `sz simulate <tree>` runs full pipeline and displays results
   - `sz drift` displays and filters drift events from log
   - `sz replay` replays log entries with timeline
   - `sz status` shows system dashboard

2. ✅ **Test Suite Passes**
   - 50+ pytest tests passing
   - >80% code coverage on core modules
   - All drift scenarios detected correctly
   - Hash chain validation works

3. ✅ **Mock Event System Works**
   - Can generate realistic event sequences
   - Events properly trigger pipeline
   - Drift injection works as expected

4. ✅ **Documentation Complete**
   - All commands documented with --help
   - Test fixtures documented
   - CHANGELOG updated with Phase 2 changes

5. ✅ **Validation Complete**
   - End-to-end pipeline tested with all fixtures
   - Log integrity verified
   - Template matching accuracy validated
   - No critical bugs remaining

---

## Dependencies & Tools

### Required Python Packages
```bash
pip install rich pytest pytest-cov pyyaml
```

### Development Tools
- pytest - test framework
- pytest-cov - coverage reporting
- Rich - terminal formatting
- GitHub Actions - CI/CD (optional for Phase 2)

---

## Risk Assessment

### Low Risk
- CLI command implementation (straightforward)
- Test suite expansion (infrastructure exists)
- Display formatting (Rich library well-documented)

### Medium Risk
- Mock event generation (need realistic sequences)
- Hash chain validation edge cases
- Performance with large logs

### Mitigation Strategies
- Start with simple event sequences, expand gradually
- Test hash chain with various tampering scenarios
- Add pagination/streaming for large log files

---

## Next Steps

1. **Immediate**: Start with Task 1 (cmd_simulate) - highest value, enables testing
2. **Then**: Task 5 (test suite) - validates implementation quality
3. **Then**: Task 2 & 3 (drift/replay viewers) - completes CLI
4. **Finally**: Tasks 4, 6, 7, 8 - polish and validation

**Estimated Total Time**: 10-15 hours of development work

---

## Phase 2 Checklist

```markdown
Phase 2: Mock Pipeline + Test Harness

[ ] Task 1: cmd_simulate implementation
  [ ] Read JSON tree files
  [ ] Run full pipeline
  [ ] Display results with Rich
  [ ] Test with all fixture trees

[ ] Task 2: cmd_drift implementation
  [ ] Load and parse log files
  [ ] Filter by type and severity
  [ ] Display in formatted table
  [ ] Show summary statistics

[ ] Task 3: cmd_replay implementation
  [ ] Load log entries
  [ ] Display with timeline
  [ ] Support range selection
  [ ] Verify hash chain during replay

[ ] Task 4: cmd_status implementation
  [ ] Show configuration summary
  [ ] Display recent activity
  [ ] Format as dashboard

[ ] Task 5: Automated test suite
  [ ] Normalization tests
  [ ] Baseline tests
  [ ] Drift detection tests
  [ ] Logging tests
  [ ] Integration tests
  [ ] Achieve >80% coverage

[ ] Task 6: Mock event generation
  [ ] Create EventGenerator
  [ ] Build event sequences
  [ ] Integrate with listener

[ ] Task 7: Hash chain validation
  [ ] Implement verify_integrity()
  [ ] Test tampering detection
  [ ] Test chain reconstruction

[ ] Task 8: CLI integration
  [ ] Full argparse implementation
  [ ] Command aliases
  [ ] Help documentation
  [ ] Version flag

[ ] Documentation
  [ ] Update CHANGELOG
  [ ] Document CLI usage
  [ ] Document test fixtures
  [ ] Update ROADMAP

[ ] Final validation
  [ ] All tests passing
  [ ] End-to-end pipeline verified
  [ ] No critical bugs
  [ ] Ready for Phase 3
```

---

**Phase 2 Goal**: Transform System//Zero from scaffolding into a fully testable, validated, and interactive tool for drift detection.
