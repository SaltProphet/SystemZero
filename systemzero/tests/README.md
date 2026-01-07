# System//Zero Test Strategy

This directory contains comprehensive test infrastructure for System//Zero Phase 2 development.

## Test Structure

### Fixtures (`fixtures/`)
Reusable test data for consistent testing:

- **`mock_trees.py`** - UI tree structures
  - `DISCORD_CHAT_TREE` - Messaging interface
  - `DOORDASH_OFFER_TREE` - Delivery offer card
  - `GMAIL_INBOX_TREE` - Email inbox
  - `SETTINGS_PANEL_TREE` - Settings interface
  - `LOGIN_FORM_TREE` - Authentication form

- **`drift_scenarios.py`** - Pre-built drift cases
  - `MISSING_BUTTON_DRIFT` - Critical element removed (layout)
  - `TEXT_CHANGE_DRIFT` - Content modified (content)
  - `LAYOUT_SHIFT_DRIFT` - UI reordered (layout)
  - `MANIPULATIVE_PATTERN_DRIFT` - Dark pattern detected (manipulative)
  - `SEQUENCE_VIOLATION_DRIFT` - Invalid state transition (sequence)

- **`templates.py`** - Template generators
  - `build_template()` - Create template from tree
  - `template_from_tree()` - Auto-extract required nodes
  - Pre-built: `discord_chat_template()`, `doordash_offer_template()`, etc.

### Helpers (`helpers.py`)
Integration test utilities:

- **`run_pipeline(tree, templates)`** - Execute full pipeline (normalize → match → detect)
- **`verify_log_integrity(log_path)`** - Check hash chain validity
- **`create_temp_log()`** - Isolated test log instance
- **`assert_drift_detected(tree, template, type, severity)`** - Semantic drift assertions
- **`compare_trees(tree_a, tree_b)`** - Diff summary with added/removed/modified nodes
- **`simulate_drift_detection_pipeline()`** - End-to-end simulation with logging

## Expected Behaviors

### Drift Detection
System//Zero detects 4 types of drift:

1. **Layout Drift** - Structural changes
   - Missing required nodes → `severity: critical`
   - Element reordering → `severity: warning`
   - Added/removed containers → `severity: info`

2. **Content Drift** - Text/data changes
   - Required field value changed → `severity: warning`
   - Non-critical text updated → `severity: info`

3. **Sequence Drift** - Invalid state transitions
   - Transition not in `valid_transitions` → `severity: warning`
   - Rapid back-and-forth (loops) → `severity: info`

4. **Manipulative Drift** - Dark patterns
   - Hidden decline options → `severity: critical`
   - Deceptive element sizing/coloring → `severity: critical`
   - Forced flows (no exit path) → `severity: critical`

### Template Matching
Match scoring algorithm (see [core/drift/matcher.py](../core/drift/matcher.py)):
- **40%** - Required nodes present
- **40%** - Structure similarity
- **20%** - Role distribution

**Thresholds**:
- `≥ 0.8` - Valid match (no drift logged)
- `0.5 - 0.8` - Partial match (warning drift)
- `< 0.5` - No match (critical drift)

### Hash Chain Verification
Every log entry contains:
```json
{
  "event_id": "abc123...",
  "drift_type": "layout",
  "previous_hash": "def456...",  // Links to prior entry
  "entry_hash": "ghi789..."      // Hash of this entry
}
```

**Verification rules**:
1. Genesis hash = `sha256("")` = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
2. Each `entry_hash` must match recomputed hash of entry data
3. Each `previous_hash` must equal prior entry's `entry_hash`
4. Any mismatch = tamper detected

## Test Patterns

### Basic Pipeline Test
```python
from tests.fixtures import DISCORD_CHAT_TREE
from tests.helpers import run_pipeline, load_all_test_templates

templates = load_all_test_templates()
result = run_pipeline(DISCORD_CHAT_TREE, templates)

assert result["best_match"]["screen_id"] == "discord_chat"
assert result["match_score"] >= 0.8
assert len(result["drift_events"]) == 0
```

### Drift Detection Test
```python
from tests.fixtures import MISSING_BUTTON_DRIFT
from tests.helpers import assert_drift_detected, load_all_test_templates

original, drifted = MISSING_BUTTON_DRIFT
templates = load_all_test_templates()

assert_drift_detected(drifted, templates[0], "layout", "critical")
```

### Log Integrity Test
```python
from tests.helpers import create_temp_log, verify_log_integrity
from core.drift import DriftEvent

log_path, log = create_temp_log()

# Append events
for i in range(10):
    log.append(DriftEvent("layout", "info", {"index": i}))

# Verify chain
is_valid, error = verify_log_integrity(log_path)
assert is_valid, f"Hash chain broken: {error}"
```

## CLI Test Commands (Phase 2)

### `sz simulate`
```bash
# Run pipeline with mock tree
sz simulate tests/fixtures/discord_tree.json --template discord_chat

# Expected output:
# ✓ Tree normalized
# ✓ Signature: 269217da...
# ✓ Matched: discord_chat (score: 0.95)
# ✓ No drift detected
```

### `sz drift`
```bash
# View all drift events
sz drift logs/test.log

# Filter by type
sz drift logs/test.log --filter layout

# Expected output:
# | Timestamp | Type    | Severity | Details
# | 12:34:56  | layout  | warning  | Missing: send_button
# | 12:35:10  | content | info     | Text changed: payout
```

### `sz replay`
```bash
# Replay events with timeline
sz replay logs/test.log --start 0 --end 50

# Expected output:
# [0] 12:34:56 - Layout drift (warning)
# [1] 12:35:10 - Content drift (info)
# ...
```

## Edge Cases to Test

1. **Empty tree** → Should match `system_default` template
2. **Null/missing fields** → Normalizer removes transient props
3. **Duplicate children** → Sorted deterministically
4. **Circular references** → Not expected (tree structure)
5. **Extremely deep trees** → Signature generation handles recursion
6. **No templates loaded** → Returns critical drift (no match)
7. **Log file doesn't exist** → Creates new log with genesis hash
8. **Corrupted log entry** → `verify_integrity()` returns False

## Performance Benchmarks

Target performance for Phase 2:
- Tree normalization: < 10ms
- Signature generation: < 5ms
- Template matching (10 templates): < 50ms
- Log append: < 2ms
- Hash chain verification (1000 entries): < 100ms

## Next Steps (Phase 2)

1. ✅ Fixtures created
2. ✅ Helpers implemented
3. ✅ CLI stubs defined
4. ⏳ Implement `cmd_simulate()` - Execute pipeline with JSON tree
5. ⏳ Implement `cmd_drift()` - Display filtered log entries
6. ⏳ Implement `cmd_replay()` - Timeline viewer
7. ⏳ Write pytest suite for all scenarios
8. ⏳ Validate hash chain end-to-end

---

**Maintainer Note**: Update this README when adding new fixtures, helpers, or test patterns. Keep examples current with actual implementation.
