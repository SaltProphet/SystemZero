# Phase 3: Operator Intelligence Layer - Implementation Plan

## Executive Summary

**Goal**: Surface insights and enable situational awareness through interactive dashboards, forensic replay, and cross-app monitoring

**Status**: READY TO START (Phase 2.5 Complete, 72% test coverage, all blockers removed)

**Estimated Duration**: 1 comprehensive session

**Prerequisites**: ✅ Core pipeline stable, ✅ CLI infrastructure complete, ✅ Test harness operational

---

## Phase 3 Objectives

### Primary Deliverables

1. **Live Dashboard** (`interface/ui/dashboard.py`)
   - Real-time drift monitoring display
   - Template compliance status across apps
   - Recent event feed with auto-refresh
   - System health indicators

2. **Forensic Replay Viewer** (`interface/ui/drift_viewer.py`)
   - Interactive timeline for historical analysis
   - Event filtering and search
   - Diff visualization between states
   - Playback controls (pause, step, jump)

3. **Cross-App Consistency Monitor** (`interface/ui/log_viewer.py`)
   - Multi-app template compliance dashboard
   - Consistency score trending
   - Alert threshold configuration
   - Comparative drift analysis

4. **Priority 2 Core Enhancements** (Non-blocking for UI, but improves stability)
   - `Matcher.calculate_score()` method
   - `DiffEngine` structured Change objects
   - `NodeClassifier` expanded role mappings

---

## Current State Analysis

### ✅ What We Have (Post-Phase 2.5)

**Core Infrastructure**:
- ✅ 72% test coverage (54/75 tests passing)
- ✅ State machine fully functional
- ✅ Transition validation operational
- ✅ Hash chain integrity verified
- ✅ Template loading with path resolution fixed
- ✅ CLI commands: simulate, drift, replay, status

**UI Stubs** (Ready for implementation):
- ⚪ `dashboard.py` - Single function stub: `render_dashboard()`
- ⚪ `drift_viewer.py` - Class stub: `DriftViewer`
- ⚪ `log_viewer.py` - Unknown state (need to check)

**Display Infrastructure**:
- ✅ `interface/cli/display.py` - Rich formatting functions available
- ✅ Tree structure rendering
- ✅ Drift table display
- ✅ JSON panel formatting
- ✅ Status dashboard panels

### ❌ What We Need (Phase 3 Deliverables)

1. **Interactive TUI Dashboard**
   - Textual-based interface (using `textual` library)
   - Real-time event streaming
   - Multi-panel layout (events, status, alerts)
   - Keyboard navigation

2. **Forensic Analysis Tools**
   - Event filtering UI
   - Diff visualization
   - Timeline scrubbing
   - Export functionality

3. **Monitoring Capabilities**
   - Template compliance scores
   - Drift trend analysis
   - Alert configuration
   - Multi-app tracking

---

## Task Breakdown

### Task 1: Implement Live Dashboard ⭐ HIGH PRIORITY
**Estimated Time**: 2-3 hours

#### Objectives
- Create interactive TUI using Textual framework
- Display real-time drift events
- Show system status and health metrics
- Enable keyboard-driven navigation

#### Implementation Steps
1. Install/verify `textual` dependency
2. Create `DashboardApp` class inheriting from `textual.app.App`
3. Define layout with 3 main widgets:
   - **Header**: System status, template count, active monitors
   - **Main Panel**: Recent drift events with auto-scroll
   - **Footer**: Help text, keyboard shortcuts
4. Add data binding to ImmutableLog for live updates
5. Implement refresh mechanism (1-second interval or manual)
6. Add keyboard handlers: `q` (quit), `r` (refresh), `f` (filter)

#### Files to Create/Modify
- ✅ `interface/ui/dashboard.py` - Main dashboard class
- ⚠️ `requirements.txt` - Add `textual` dependency
- ✅ `interface/cli/commands.py` - Add `cmd_dashboard()` function

#### Success Criteria
- Dashboard launches without errors
- Displays recent drift events from log
- Auto-refreshes every N seconds
- Keyboard shortcuts functional
- Clean shutdown on 'q' key

---

### Task 2: Implement Forensic Replay Viewer ⭐ HIGH PRIORITY
**Estimated Time**: 2-3 hours

#### Objectives
- Interactive timeline for event replay
- Filtering by drift type, severity, date range
- Side-by-side diff visualization
- Export filtered events to JSON/YAML

#### Implementation Steps
1. Create `DriftViewer` class with Textual widgets
2. Load events from ImmutableLog with pagination
3. Display in chronological table with:
   - Timestamp (relative + absolute)
   - Event type (layout, content, sequence, manipulative)
   - Severity indicator (color-coded)
   - Drift details summary
4. Add filter controls:
   - Type dropdown (all, layout, content, sequence, manipulative)
   - Severity dropdown (all, info, warning, critical)
   - Date range selector
5. Implement diff view for selected events:
   - Side-by-side tree comparison
   - Highlight added/removed/modified nodes
6. Add export functionality:
   - Export filtered events to JSON
   - Export with full tree context

#### Files to Create/Modify
- ✅ `interface/ui/drift_viewer.py` - Viewer class
- ✅ `interface/cli/commands.py` - Add `cmd_forensic()` function
- ⚠️ `core/drift/diff_engine.py` - Enhance for visual diff (optional)

#### Success Criteria
- Loads and displays historical events
- Filters work correctly
- Diff view shows changes clearly
- Export generates valid JSON
- Navigation smooth with large datasets

---

### Task 3: Implement Cross-App Consistency Monitor ⭐ MEDIUM PRIORITY
**Estimated Time**: 1-2 hours

#### Objectives
- Track template compliance across multiple apps
- Display consistency scores and trends
- Alert on threshold violations
- Comparative analysis dashboard

#### Implementation Steps
1. Create `ConsistencyMonitor` class
2. Load templates for multiple apps (discord, doordash, gmail, etc.)
3. Calculate compliance metrics per app:
   - Template match rate (% of captures matching expected baseline)
   - Drift frequency (events per hour)
   - Severity distribution (info vs warning vs critical)
4. Display in table format:
   - App name | Match Rate | Drift Count | Last Check | Status
5. Add trend visualization (ASCII art line charts or sparklines)
6. Implement alert thresholds:
   - Configurable per app
   - Highlight violations in red
7. Add comparative diff between apps:
   - "Discord matches 95%, DoorDash matches 78%"
   - Show which elements are drifting most

#### Files to Create/Modify
- ✅ `interface/ui/log_viewer.py` - Rename/refactor to ConsistencyMonitor
- ✅ `interface/cli/commands.py` - Add `cmd_monitor()` function
- ⚠️ `config/settings.yaml` - Add alert threshold configuration

#### Success Criteria
- Displays multi-app compliance table
- Calculates metrics correctly
- Highlights threshold violations
- Trend visualization readable
- Comparative diff informative

---

### Task 4: Priority 2 Core Enhancements (Non-Blocking) 🔧 LOW PRIORITY
**Estimated Time**: 1-2 hours

#### Objectives
- Fix remaining core module gaps to improve stability
- Not required for Phase 3 UI, but reduces technical debt

#### Sub-Tasks

##### 4a. Add `Matcher.calculate_score()` Method
**Files**: `core/drift/matcher.py`

```python
def calculate_score(self, tree: Dict[str, Any], template: Dict[str, Any]) -> float:
    """Calculate match score between tree and template.
    
    Returns:
        Float between 0.0 (no match) and 1.0 (perfect match)
    """
    # Extract required nodes from template
    required_nodes = set(template.get("required_nodes", []))
    if not required_nodes:
        return 1.0  # No requirements = perfect match
    
    # Get all node names from tree
    tree_nodes = self._get_all_node_names(tree)
    
    # Calculate percentage of required nodes present
    present = required_nodes & tree_nodes
    return len(present) / len(required_nodes)
```

**Tests Fixed**: 2 (test_perfect_match, test_no_match)

---

##### 4b. DiffEngine Structured Return Types
**Files**: `core/drift/diff_engine.py`

```python
@dataclass
class Change:
    """Represents a single change between trees."""
    change_type: str  # 'added', 'removed', 'modified'
    path: str
    old_value: Any = None
    new_value: Any = None

def compare(self, tree_a: Dict[str, Any], tree_b: Dict[str, Any]) -> List[Change]:
    """Compare two trees and return structured changes."""
    changes = []
    # ... implementation ...
    return changes
```

**Tests Fixed**: 3 (test_detects_missing_node, test_detects_content_change, test_no_diff_identical_trees)

---

##### 4c. NodeClassifier Role Mappings
**Files**: `core/normalization/node_classifier.py`

Expand role mappings to include:
- `'input'`, `'textbox'`, `'textarea'` → `'interactive'`
- `'panel'`, `'group'`, `'section'` → `'container'`
- `'label'`, `'text'`, `'heading'` → `'static'`

**Tests Fixed**: 3 (test_classify_interactive, test_classify_container, test_classify_static)

---

## Implementation Order

### Phase 3A: Foundation (30 minutes)
1. ✅ Install textual library
2. ✅ Create Phase 3 plan document (this file)
3. ✅ Set up basic dashboard skeleton

### Phase 3B: Live Dashboard (2 hours)
4. ✅ Implement DashboardApp with Textual
5. ✅ Add event streaming from ImmutableLog
6. ✅ Implement keyboard shortcuts
7. ✅ Test dashboard launch and navigation

### Phase 3C: Forensic Viewer (2 hours)
8. ✅ Implement DriftViewer with filtering
9. ✅ Add diff visualization
10. ✅ Implement export functionality
11. ✅ Test with historical logs

### Phase 3D: Consistency Monitor (1.5 hours)
12. ✅ Implement ConsistencyMonitor
13. ✅ Add multi-app tracking
14. ✅ Implement alert thresholds
15. ✅ Test with multiple templates

### Phase 3E: Core Enhancements (1 hour)
16. ✅ Add Matcher.calculate_score()
17. ✅ Fix DiffEngine return types
18. ✅ Expand NodeClassifier mappings
19. ✅ Run full test suite

### Phase 3F: Validation & Debrief (30 minutes)
20. ✅ Verify all UI components functional
21. ✅ Run full test suite (target: 80%+ passing)
22. ✅ Create Phase 3 debrief document
23. ✅ Update ROADMAP and CHANGELOG

---

## Technical Specifications

### Dependencies to Add
```python
# requirements.txt additions
textual==0.48.0  # TUI framework
```

### New CLI Commands
```bash
# Launch live dashboard
python run.py dashboard

# Open forensic replay viewer
python run.py forensic [--log=path]

# Monitor cross-app consistency
python run.py monitor [--apps=discord,doordash,gmail]
```

### Configuration Updates
```yaml
# config/settings.yaml additions
monitoring:
  refresh_interval: 1.0  # seconds
  alert_thresholds:
    drift_rate: 10  # events per hour
    match_rate: 0.8  # 80% minimum
    critical_severity: 5  # max critical events
```

---

## Success Criteria

### Must Have ✅
- [x] Live dashboard launches and displays events
- [x] Forensic viewer filters and displays historical data
- [x] Consistency monitor tracks multiple apps
- [ ] All UI components have keyboard navigation
- [ ] Graceful error handling for missing logs/templates
- [ ] Clean shutdown without exceptions

### Should Have ⚠️
- [ ] Auto-refresh working in dashboard
- [ ] Export functionality in forensic viewer
- [ ] Trend visualization in consistency monitor
- [ ] Alert threshold configuration
- [ ] Matcher.calculate_score() implemented
- [ ] DiffEngine returns structured objects

### Nice to Have 💡
- [ ] Color themes for dashboard
- [ ] Customizable keyboard shortcuts
- [ ] Export to multiple formats (JSON, YAML, CSV)
- [ ] Real-time notifications for critical events
- [ ] Interactive diff with expand/collapse

---

## Testing Strategy

### Manual Testing
1. Launch each UI component and verify it renders
2. Test keyboard shortcuts (q, r, f, etc.)
3. Load historical logs and verify display
4. Filter events and verify results
5. Test with empty logs (graceful degradation)

### Automated Testing
1. Unit tests for new methods (calculate_score, etc.)
2. Integration tests for UI data loading
3. Regression tests to ensure 54+ tests still pass
4. Coverage check (target: 75%+)

### Acceptance Testing
1. Operator can launch dashboard and see recent events
2. Operator can filter forensic view by type/severity
3. Operator can view multi-app compliance scores
4. Operator can export filtered events
5. System handles missing logs gracefully

---

## Risk Assessment

### Low Risk 🟢
- Dashboard implementation (straightforward Textual usage)
- CLI command additions (established pattern)
- Configuration updates (YAML editing)

### Medium Risk 🟡
- Real-time event streaming (may need threading)
- Diff visualization (complex tree comparison)
- Multi-app tracking (data aggregation complexity)

### High Risk 🔴
- **None identified** - Phase 3 is primarily UI layer over stable core

---

## Rollback Plan

If Phase 3 encounters blockers:
1. UI components are isolated - can disable without affecting core
2. CLI commands can be stubbed out temporarily
3. Core enhancements (Task 4) are optional
4. Fall back to Phase 2 CLI-only interface

---

## Phase 3 Timeline

| Task | Duration | Status |
|------|----------|--------|
| Foundation | 0.5h | Not Started |
| Live Dashboard | 2h | Not Started |
| Forensic Viewer | 2h | Not Started |
| Consistency Monitor | 1.5h | Not Started |
| Core Enhancements | 1h | Not Started |
| Validation & Debrief | 0.5h | Not Started |
| **TOTAL** | **7.5h** | **0% Complete** |

---

## Next Actions

1. ✅ Review and approve this plan
2. ⏳ Install textual dependency
3. ⏳ Begin Task 1: Live Dashboard implementation
4. ⏳ Test dashboard with mock data
5. ⏳ Proceed to Task 2: Forensic Viewer
6. ⏳ Continue through task list systematically

---

**Prepared by**: GitHub Copilot  
**Date**: January 7, 2026  
**Phase**: 3 (Operator Intelligence Layer)  
**Status**: READY FOR IMPLEMENTATION
