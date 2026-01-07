# Phase 4: Capture & Automation Engine - Development Roadmap

**Status**: 🛠️ PLANNED  
**Prerequisites**: ✅ Phase 3 Complete (81.3% test coverage, dashboards operational)  
**Target Completion**: TBD  
**Estimated Duration**: 12-15 hours implementation + 4-6 hours testing

---

## Executive Summary

Phase 4 expands System//Zero from a **monitoring tool** into a **recording and template generation platform**. Users will be able to capture UI sessions in real-time, automatically generate baseline templates, and build a library of reusable screen definitions without manual YAML authoring.

### Key Deliverables
1. **Capture Mode** - Record UI state sequences with auto-drift detection
2. **Template Builder** - Generate YAML baselines from captured trees
3. **Advanced Alerting** - Configurable thresholds and notifications
4. **Session Replay** - Playback captures with frame-by-frame navigation
5. **Template Versioning** - Track changes and rollback support

---

## Strategic Context

### Why Phase 4 Matters
- **Current State**: 10 hand-authored YAML templates, manual creation process
- **Limitation**: Requires technical expertise to define baselines
- **Opportunity**: Auto-generate templates from live captures → democratize usage
- **Impact**: Enable non-technical users to build their own monitoring baselines

### Success Metrics
| Metric | Target | Measurement |
|--------|--------|-------------|
| Template Generation Speed | <30 seconds per screen | Time from capture → YAML export |
| Auto-Detection Accuracy | >85% correct node classification | Manual review of generated templates |
| Capture Session Storage | <5MB per 1000 events | Disk usage for recorded sessions |
| Template Version Control | 100% rollback success | Git-based version tracking |
| User Adoption | 3+ new templates/week | Community contributions |

---

## Phase 4A: Capture Mode (Core Recording)

### Goal
Enable users to record UI sessions with automatic tree capture, normalization, and signature generation at configurable intervals.

### Components

#### 1. Recorder (`extensions/capture_mode/recorder.py`)
**Current State**: Stub class (`def start(): pass`)  
**Target State**: Full recording session manager

**Implementation**:
```python
class Recorder:
    """Manages capture sessions with background monitoring."""
    
    def __init__(self, interval: float = 2.0, output_dir: str = "captures/"):
        self.interval = interval
        self.output_dir = output_dir
        self.session_id = None
        self.is_recording = False
        self.captured_trees = []
        self.drift_events = []
        
    def start(self) -> str:
        """Start capture session, returns session_id."""
        # Generate unique session ID (timestamp-based)
        # Initialize capture directory
        # Start background TreeCapture loop
        # Enable auto-normalization and signature generation
        
    def stop(self) -> Dict[str, Any]:
        """Stop capture, return session summary."""
        # Halt background capture
        # Save captured_trees to disk
        # Generate session report (drift count, unique signatures)
        # Return metadata
        
    def pause(self) -> None:
        """Pause recording without stopping session."""
        
    def resume(self) -> None:
        """Resume paused session."""
        
    def export_session(self, format: str = "json") -> str:
        """Export session data (json, yaml, csv)."""
        
    def add_annotation(self, text: str, timestamp: float = None) -> None:
        """Add manual annotation to timeline."""
```

**Key Features**:
- Configurable capture interval (0.5s-10s)
- Auto-drift detection during recording (compare each frame to last)
- Memory-efficient: write trees to disk every 50 captures
- Session annotations for marking key moments
- Export formats: JSON (full data), YAML (templates), CSV (metrics)

**Testing**:
```python
# tests/test_capture_mode.py
def test_recorder_starts_and_stops():
    recorder = Recorder(interval=1.0)
    session_id = recorder.start()
    assert recorder.is_recording == True
    time.sleep(3)  # Capture for 3 seconds
    summary = recorder.stop()
    assert summary["total_captures"] >= 2
    assert summary["session_id"] == session_id
    
def test_drift_detection_during_capture():
    recorder = Recorder()
    recorder.start()
    # Simulate UI change (inject different mock tree)
    recorder.stop()
    assert len(recorder.drift_events) > 0
```

**Files Modified**:
- `extensions/capture_mode/recorder.py` (~250 lines)
- `tests/test_capture_mode.py` (new, ~150 lines)

---

#### 2. UITreeExport (`extensions/capture_mode/ui_tree_export.py`)
**Current State**: Stub  
**Target State**: Multi-format tree export utility

**Implementation**:
```python
class UITreeExport:
    """Export captured trees in various formats."""
    
    @staticmethod
    def to_json(tree: Dict[str, Any], filepath: str) -> None:
        """Export tree as JSON with pretty formatting."""
        
    @staticmethod
    def to_yaml(tree: Dict[str, Any], filepath: str) -> None:
        """Export tree as YAML (human-readable)."""
        
    @staticmethod
    def to_csv(trees: List[Dict[str, Any]], filepath: str) -> None:
        """Export tree metrics as CSV (timestamp, node_count, signature)."""
        
    @staticmethod
    def to_markdown(tree: Dict[str, Any], filepath: str) -> None:
        """Export tree as markdown (documentation)."""
        
    @staticmethod
    def export_diff(tree1: Dict, tree2: Dict, filepath: str) -> None:
        """Export diff between two trees (visual comparison)."""
```

**Use Cases**:
- Export session for external analysis (JSON)
- Human-readable documentation (Markdown)
- Data science pipeline (CSV metrics)
- Template generation (YAML)

**Testing**:
```python
def test_export_to_json():
    tree = create_mock_discord_tree()
    UITreeExport.to_json(tree, "/tmp/test.json")
    loaded = json.load(open("/tmp/test.json"))
    assert loaded == tree
    
def test_export_diff():
    tree1 = create_mock_discord_tree()
    tree2 = create_mock_discord_tree_modified()
    UITreeExport.export_diff(tree1, tree2, "/tmp/diff.md")
    # Verify diff contains "added", "removed", "changed" sections
```

**Files Modified**:
- `extensions/capture_mode/ui_tree_export.py` (~180 lines)
- `tests/test_ui_tree_export.py` (new, ~120 lines)

---

#### 3. SignatureExport (`extensions/capture_mode/signature_export.py`)
**Current State**: Stub  
**Target State**: Signature analysis and export

**Implementation**:
```python
class SignatureExport:
    """Export and analyze UI signatures."""
    
    @staticmethod
    def export_timeline(sessions: List[Dict], filepath: str) -> None:
        """Export signature timeline (CSV: timestamp, signature, screen_id)."""
        
    @staticmethod
    def find_duplicates(signatures: List[str]) -> Dict[str, List[int]]:
        """Find duplicate signatures (detect repeated screens)."""
        
    @staticmethod
    def cluster_signatures(signatures: List[str], threshold: float = 0.9) -> Dict[str, List[str]]:
        """Cluster similar signatures (group related screens)."""
        
    @staticmethod
    def export_heatmap(signatures: List[str], filepath: str) -> None:
        """Generate signature frequency heatmap (HTML/PNG)."""
```

**Use Cases**:
- Identify unique screens in session (deduplicate)
- Detect loops (repeated signature sequences)
- Cluster similar screens (e.g., all chat interfaces)
- Visual timeline of state changes

**Files Modified**:
- `extensions/capture_mode/signature_export.py` (~150 lines)
- `tests/test_signature_export.py` (new, ~100 lines)

---

#### 4. CLI Integration
**Commands**:
```bash
# Start capture session
python run.py capture --interval 2.0 --output captures/

# Stop active session (via signal or separate command)
python run.py capture --stop

# Export session
python run.py capture --export SESSION_ID --format yaml

# List all sessions
python run.py sessions --list

# Replay session
python run.py replay --session SESSION_ID
```

**Implementation**:
```python
# interface/cli/commands.py
def cmd_capture(interval: float = 2.0, output: str = "captures/", stop: bool = False, export: str = None):
    """Manage capture sessions."""
    if stop:
        # Stop active recorder
    elif export:
        # Export specified session
    else:
        # Start new capture
        
def cmd_sessions(list: bool = False, delete: str = None):
    """Manage capture sessions."""
```

**Files Modified**:
- `interface/cli/commands.py` (+80 lines)
- `interface/cli/main.py` (+25 lines for argparse)

---

## Phase 4B: Template Builder (Auto-Generation)

### Goal
Convert captured UI trees into valid YAML baseline templates without manual authoring.

### Components

#### 1. TemplateBuilder (`extensions/template_builder/builder.py`)
**Current State**: `def build(capture): return {"template": "yaml"}`  
**Target State**: Intelligent template generator

**Implementation**:
```python
class TemplateBuilder:
    """Generate baseline templates from captured trees."""
    
    def __init__(self, min_confidence: float = 0.7):
        self.min_confidence = min_confidence
        self.normalizer = TreeNormalizer()
        self.signature_gen = SignatureGenerator()
        self.classifier = NodeClassifier()
        
    def build_from_tree(self, tree: Dict[str, Any], screen_id: str = None) -> Dict[str, Any]:
        """Generate template from single tree."""
        # Normalize tree
        # Extract required nodes (interactive elements)
        # Generate structure signature
        # Infer valid transitions (if session context available)
        # Return complete template dict
        
    def build_from_session(self, session: List[Dict], auto_detect: bool = True) -> List[Dict[str, Any]]:
        """Generate multiple templates from session (one per unique screen)."""
        # Cluster trees by signature similarity
        # For each cluster, generate representative template
        # Auto-detect transitions (sequence of screen_ids)
        # Return list of templates
        
    def suggest_required_nodes(self, tree: Dict[str, Any]) -> List[str]:
        """Suggest which nodes should be required (semantic importance)."""
        # Use NodeClassifier to find interactive elements
        # Prioritize: buttons, textboxes, links
        # Exclude: static labels, decorative elements
        
    def infer_transitions(self, session: List[Dict]) -> Dict[str, List[str]]:
        """Infer valid transitions from session sequence."""
        # Track screen_id sequence
        # Build transition graph
        # Return {screen_id: [valid_next_screens]}
```

**Key Features**:
- **Smart Node Selection**: Prioritize interactive elements for `required_nodes`
- **Auto-Naming**: Generate screen_id from dominant text or role composition
- **Transition Inference**: Detect allowed state flows from session sequences
- **Confidence Scoring**: Mark low-confidence templates for manual review

**Example Output**:
```yaml
# Generated from capture
screen_id: auto_discord_chat_2026_01_07
required_nodes:
  - send_button
  - message_input
  - channel_list
  - settings_icon
structure_signature: a3f9b2e8c1d4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0
valid_transitions:
  - auto_discord_settings_2026_01_07
  - auto_discord_dm_2026_01_07
confidence: 0.85
metadata:
  generated: 2026-01-07T10:30:00Z
  source: capture_session_20260107_103000
  reviewed: false
```

**Testing**:
```python
def test_build_from_tree():
    tree = create_mock_discord_tree()
    builder = TemplateBuilder()
    template = builder.build_from_tree(tree, screen_id="discord_test")
    assert "screen_id" in template
    assert len(template["required_nodes"]) > 0
    assert "structure_signature" in template
    
def test_suggest_required_nodes():
    tree = create_mock_discord_tree()
    builder = TemplateBuilder()
    suggested = builder.suggest_required_nodes(tree)
    assert "send_button" in suggested
    assert "message_input" in suggested
    # Static labels should NOT be suggested
    assert "app_title" not in suggested
```

**Files Modified**:
- `extensions/template_builder/builder.py` (~300 lines)
- `tests/test_template_builder.py` (new, ~200 lines)

---

#### 2. Exporters (`extensions/template_builder/exporters.py`)
**Current State**: Stub  
**Target State**: YAML export with validation

**Implementation**:
```python
class Exporters:
    """Export templates in various formats."""
    
    @staticmethod
    def to_yaml(template: Dict, filepath: str, validate: bool = True) -> None:
        """Export template as YAML with validation."""
        if validate:
            validator = TemplateValidator()
            assert validator.validate(template), "Invalid template"
        # Write YAML with proper formatting
        
    @staticmethod
    def to_json(template: Dict, filepath: str) -> None:
        """Export template as JSON (for programmatic use)."""
        
    @staticmethod
    def batch_export(templates: List[Dict], output_dir: str) -> None:
        """Export multiple templates to directory."""
        
    @staticmethod
    def export_with_metadata(template: Dict, filepath: str, metadata: Dict) -> None:
        """Export template with generation metadata (source, confidence, etc.)."""
```

**Files Modified**:
- `extensions/template_builder/exporters.py` (~120 lines)
- `tests/test_exporters.py` (new, ~80 lines)

---

#### 3. Validators (`extensions/template_builder/validators.py`)
**Current State**: Stub  
**Target State**: Template quality checks

**Implementation**:
```python
class Validators:
    """Validate generated templates for quality."""
    
    @staticmethod
    def check_completeness(template: Dict) -> Tuple[bool, List[str]]:
        """Check if template has all required fields."""
        
    @staticmethod
    def check_node_coverage(template: Dict, tree: Dict) -> float:
        """Check what % of tree nodes are represented in template."""
        
    @staticmethod
    def check_transition_validity(template: Dict, all_templates: List[Dict]) -> bool:
        """Check if valid_transitions reference existing templates."""
        
    @staticmethod
    def suggest_improvements(template: Dict) -> List[str]:
        """Suggest improvements (missing nodes, weak signatures, etc.)."""
```

**Use Cases**:
- Pre-export validation (catch errors before writing YAML)
- Quality scoring (flag low-quality auto-generated templates)
- Improvement suggestions (guide manual review)

**Files Modified**:
- `extensions/template_builder/validators.py` (~150 lines)
- `tests/test_validators.py` (new, ~100 lines)

---

#### 4. CLI Integration
**Commands**:
```bash
# Generate template from capture
python run.py build-template --session SESSION_ID --output templates/

# Generate from single tree (JSON file)
python run.py build-template --tree tree.json --screen-id my_screen

# Batch generate from session (auto-detect screens)
python run.py build-template --session SESSION_ID --auto-detect

# Validate generated template
python run.py validate-template --file templates/my_template.yaml
```

**Implementation**:
```python
# interface/cli/commands.py
def cmd_build_template(session: str = None, tree: str = None, screen_id: str = None, auto_detect: bool = False):
    """Generate baseline templates from captures."""
    
def cmd_validate_template(file: str):
    """Validate template quality and completeness."""
```

**Files Modified**:
- `interface/cli/commands.py` (+60 lines)
- `interface/cli/main.py` (+20 lines)

---

## Phase 4C: Advanced Alerting & Automation

### Goal
Enable proactive notifications and automated responses to drift events.

### Components

#### 1. Alert System (`core/utils/alerts.py` - NEW)
**Implementation**:
```python
class AlertConfig:
    """Alert configuration."""
    drift_types: List[str]  # Which types trigger alert
    severity_threshold: str  # Minimum severity ("info", "warning", "critical")
    channels: List[str]  # Where to send ("console", "email", "webhook")
    cooldown: int  # Seconds between repeat alerts
    
class AlertManager:
    """Manage drift alerts."""
    
    def __init__(self, config: AlertConfig):
        self.config = config
        self.last_alert = {}  # Track cooldowns
        
    def check_alert(self, drift_event: DriftEvent) -> bool:
        """Check if event should trigger alert."""
        
    def send_alert(self, drift_event: DriftEvent) -> None:
        """Send alert via configured channels."""
        # Console: Rich formatted output
        # Email: SMTP send (optional)
        # Webhook: POST to URL (Slack, Discord, etc.)
        
    def load_config(self, filepath: str) -> AlertConfig:
        """Load alert config from YAML."""
```

**Config Example** (`config/alerts.yaml`):
```yaml
alerts:
  - name: critical_layout_changes
    drift_types: [layout, manipulative]
    severity_threshold: critical
    channels: [console, webhook]
    webhook_url: https://hooks.slack.com/...
    cooldown: 60
    
  - name: content_monitoring
    drift_types: [content]
    severity_threshold: warning
    channels: [console]
    cooldown: 300
```

**Files Created**:
- `core/utils/alerts.py` (~200 lines)
- `config/alerts.yaml` (new)
- `tests/test_alerts.py` (new, ~120 lines)

---

#### 2. Automation Hooks (`core/utils/automation.py` - NEW)
**Implementation**:
```python
class AutomationHook:
    """Execute actions on drift detection."""
    
    def __init__(self, trigger: str, action: str, params: Dict = None):
        self.trigger = trigger  # Drift type or severity
        self.action = action    # "capture", "export", "notify", "script"
        self.params = params or {}
        
    def execute(self, drift_event: DriftEvent) -> None:
        """Execute automation action."""
        if self.action == "capture":
            # Start capture session
        elif self.action == "export":
            # Export current state
        elif self.action == "script":
            # Run custom script
```

**Example Use**:
```yaml
# config/automation.yaml
hooks:
  - trigger: manipulative_drift
    action: capture
    params:
      duration: 30  # Capture for 30 seconds
      
  - trigger: critical_severity
    action: script
    params:
      script: /path/to/emergency_handler.sh
```

**Files Created**:
- `core/utils/automation.py` (~150 lines)
- `config/automation.yaml` (new)
- `tests/test_automation.py` (new, ~100 lines)

---

## Phase 4D: Template Versioning & Management

### Goal
Track template changes over time, enable rollback, and manage template library.

### Components

#### 1. Template Versioning (`core/baseline/version_control.py` - NEW)
**Implementation**:
```python
class TemplateVersion:
    """Represents a template version."""
    version: str  # Semantic version (1.0.0)
    template: Dict[str, Any]
    timestamp: str
    author: str
    changelog: str
    
class TemplateVersionControl:
    """Manage template versions."""
    
    def __init__(self, templates_dir: str = "core/baseline/templates/"):
        self.templates_dir = templates_dir
        self.versions = {}  # {template_id: [versions]}
        
    def save_version(self, template: Dict, changelog: str = "") -> str:
        """Save new version of template."""
        # Increment version number
        # Save to disk with version suffix (template_v1.0.0.yaml)
        # Update version registry
        
    def load_version(self, template_id: str, version: str = "latest") -> Dict:
        """Load specific version of template."""
        
    def list_versions(self, template_id: str) -> List[TemplateVersion]:
        """List all versions of template."""
        
    def rollback(self, template_id: str, version: str) -> None:
        """Rollback to previous version."""
        
    def diff_versions(self, template_id: str, v1: str, v2: str) -> Dict:
        """Diff two versions of template."""
```

**Files Created**:
- `core/baseline/version_control.py` (~250 lines)
- `tests/test_version_control.py` (new, ~150 lines)

---

#### 2. Template Manager UI (`interface/ui/template_manager.py` - NEW)
**TUI Dashboard** for template management (using Textual):
```python
class TemplateManagerApp(App):
    """Interactive template library manager."""
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield TemplateList()  # List all templates
        yield VersionHistory()  # Show versions for selected template
        yield TemplateDiff()  # Diff viewer
        yield Footer()
        
    # Actions: load, save, delete, rollback, diff, export
```

**Features**:
- Browse template library
- View version history
- Compare versions side-by-side
- Rollback to previous version
- Export/import templates

**Files Created**:
- `interface/ui/template_manager.py` (~300 lines)
- `tests/test_template_manager.py` (new, ~120 lines)

---

## Phase 4E: Session Replay Enhancements

### Goal
Enhance existing replay functionality with frame-by-frame navigation and visual diff.

### Enhancements to `cmd_replay`
**Current**: Log entry replay with hash verification  
**Enhanced**: Session capture replay with UI navigation

**New Features**:
1. **Frame Navigation**: `←→` keys to step through captures
2. **Visual Diff**: Show changes between frames (red=removed, green=added)
3. **Signature Timeline**: Display signature changes over time
4. **Playback Speed**: Adjustable (0.5x, 1x, 2x, 5x)
5. **Bookmarks**: Mark key moments for quick jump

**Implementation**:
```python
def cmd_replay_enhanced(session: str, start: int = 0, speed: float = 1.0):
    """Enhanced replay with navigation."""
    # Load session captures
    # Build signature timeline
    # Launch Textual app with frame viewer
    
class ReplayViewerApp(App):
    """Interactive replay viewer."""
    # Left panel: Frame list with signatures
    # Center: Current frame tree visualization
    # Right: Diff from previous frame
    # Bottom: Timeline scrubber
```

**Files Modified**:
- `interface/cli/commands.py` (+150 lines)
- `interface/ui/replay_viewer.py` (new, ~400 lines)
- `tests/test_replay_viewer.py` (new, ~150 lines)

---

## Implementation Strategy

### Phase 4A: Capture Mode (Week 1)
**Priority**: HIGH - Foundation for all other features  
**Effort**: 6-8 hours

1. Implement `Recorder` class (3 hours)
2. Build `UITreeExport` and `SignatureExport` (2 hours)
3. Wire CLI commands (1 hour)
4. Write tests (2 hours)

**Deliverable**: Working capture sessions with export

---

### Phase 4B: Template Builder (Week 2)
**Priority**: HIGH - Core value proposition  
**Effort**: 6-8 hours

1. Implement `TemplateBuilder` (4 hours)
2. Build `Exporters` and `Validators` (2 hours)
3. Wire CLI commands (1 hour)
4. Write tests (2 hours)

**Deliverable**: Auto-generated YAML templates from captures

---

### Phase 4C: Advanced Alerting (Week 3)
**Priority**: MEDIUM - Enhances usability  
**Effort**: 3-4 hours

1. Build `AlertManager` (2 hours)
2. Implement `AutomationHook` (1 hour)
3. Write tests (1 hour)

**Deliverable**: Proactive drift notifications

---

### Phase 4D: Template Versioning (Week 4)
**Priority**: MEDIUM - Quality of life  
**Effort**: 4-5 hours

1. Implement `TemplateVersionControl` (3 hours)
2. Build `TemplateManagerApp` UI (2 hours)
3. Write tests (1 hour)

**Deliverable**: Template library management with rollback

---

### Phase 4E: Replay Enhancements (Week 4)
**Priority**: LOW - Nice to have  
**Effort**: 3-4 hours

1. Build `ReplayViewerApp` (2 hours)
2. Enhance `cmd_replay` (1 hour)
3. Write tests (1 hour)

**Deliverable**: Interactive session replay

---

## Testing Strategy

### Unit Tests
- Each new module (Recorder, TemplateBuilder, AlertManager, etc.) gets dedicated test file
- Target: 90%+ coverage for Phase 4 modules
- Mock external dependencies (filesystem, webhooks, email)

### Integration Tests
```python
# tests/test_phase4_integration.py
def test_capture_to_template_workflow():
    """End-to-end: Capture → Build Template → Validate → Export."""
    # 1. Start capture session
    recorder = Recorder()
    session_id = recorder.start()
    
    # 2. Simulate UI changes
    time.sleep(5)
    
    # 3. Stop and export
    recorder.stop()
    
    # 4. Build template from session
    builder = TemplateBuilder()
    templates = builder.build_from_session(session_id)
    
    # 5. Validate generated templates
    for template in templates:
        assert TemplateValidator().validate(template)
        
    # 6. Export to YAML
    Exporters.batch_export(templates, "test_output/")
```

### Manual Testing Checklist
- [ ] Capture session starts and stops cleanly
- [ ] Generated templates load without errors
- [ ] Alerts trigger on configured drift types
- [ ] Template rollback restores previous version
- [ ] Replay viewer navigates frames smoothly

---

## Dependencies & Prerequisites

### New Dependencies
```txt
# requirements.txt additions
pyyaml>=6.0          # Already installed (YAML handling)
watchdog>=3.0.0      # File system monitoring (optional)
requests>=2.31.0     # Webhook alerts (optional)
```

### No Breaking Changes
- All Phase 4 features are **additive** (extensions)
- Core modules (drift, logging, normalization) unchanged
- Existing CLI commands remain functional

---

## Risk Assessment

### Technical Risks
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Capture performance impact | Medium | Medium | Configurable intervals, background threads |
| Template generation quality | High | High | Confidence scoring, manual review workflow |
| Session storage growth | Medium | Low | Compression, auto-cleanup old sessions |
| Alert fatigue | Medium | Medium | Cooldown timers, severity thresholds |

### Mitigation Strategies
1. **Performance**: Profile `Recorder` with 1000+ capture sessions, optimize tree serialization
2. **Quality**: Implement template review dashboard, flag low-confidence generations
3. **Storage**: Add session pruning (delete after 30 days), compression for large trees
4. **Alerts**: Default to conservative thresholds, encourage user customization

---

## Success Criteria

### Must-Have (MVP)
- ✅ Capture sessions work for 5+ minute recordings
- ✅ Template generation produces valid YAML 80%+ of time
- ✅ CLI commands integrated and documented
- ✅ 85%+ test coverage for new modules

### Nice-to-Have (Polish)
- ✅ Alert webhooks (Slack, Discord integration)
- ✅ Template versioning with Git-like interface
- ✅ Replay viewer with frame navigation
- ✅ Template manager UI dashboard

### Phase 4 Complete When:
1. User can record UI session with single command
2. Generated templates load successfully in Phase 1 pipeline
3. Alert system notifies on critical drift
4. Template library has 20+ auto-generated templates
5. Documentation updated (README, examples, CLI help text)

---

## Documentation Requirements

### New Documentation
1. **CAPTURE_MODE.md** - How to record sessions, export formats
2. **TEMPLATE_BUILDER.md** - Auto-generation guide, quality tips
3. **ALERTING.md** - Alert configuration, webhook setup
4. **VERSIONING.md** - Template version control, rollback guide

### Updated Documentation
- **README.md** - Add Phase 4 features to quick start
- **ROADMAP** - Mark Phase 4 complete, outline Phase 5
- **CHANGELOG.md** - Add v0.4.0 release notes

---

## Next Steps After Phase 4

### Phase 5: Deployment & Operator Tooling
- REST API with FastAPI
- Background service (systemd integration)
- Multi-user dashboards
- Remote monitoring capabilities

### Phase 6: Security & Integrity
- Template signature verification
- Cryptographic audit trails
- Environment tamper detection
- Zero-knowledge logging (optional)

---

## Appendix: File Changes Summary

### New Files (18 total)
```
extensions/capture_mode/
  recorder.py (250 lines)
  
extensions/template_builder/
  builder.py (300 lines)
  exporters.py (120 lines)
  validators.py (150 lines)
  
core/utils/
  alerts.py (200 lines)
  automation.py (150 lines)
  
core/baseline/
  version_control.py (250 lines)
  
interface/ui/
  template_manager.py (300 lines)
  replay_viewer.py (400 lines)
  
config/
  alerts.yaml (new)
  automation.yaml (new)
  
docs/
  CAPTURE_MODE.md (new)
  TEMPLATE_BUILDER.md (new)
  ALERTING.md (new)
  VERSIONING.md (new)
  
tests/
  test_capture_mode.py (150 lines)
  test_ui_tree_export.py (120 lines)
  test_signature_export.py (100 lines)
  test_template_builder.py (200 lines)
  test_exporters.py (80 lines)
  test_validators.py (100 lines)
  test_alerts.py (120 lines)
  test_automation.py (100 lines)
  test_version_control.py (150 lines)
  test_template_manager.py (120 lines)
  test_replay_viewer.py (150 lines)
  test_phase4_integration.py (200 lines)
```

### Modified Files (4 total)
```
interface/cli/commands.py (+300 lines)
interface/cli/main.py (+80 lines)
README.md (Phase 4 section)
ROADMAP (Phase 4 completion)
```

### Total LOC Added: ~4,500 lines
### Estimated Test Coverage: 88-92%

---

## Questions for Stakeholder Review

1. **Capture Intervals**: Default 2 seconds acceptable? Should we support <1 second?
2. **Template Auto-Naming**: Prefer timestamp-based IDs or semantic names (extracted from UI text)?
3. **Alert Channels**: Priority for webhook integrations (Slack, Discord, email)?
4. **Template Review**: Build review dashboard in Phase 4 or defer to Phase 5?
5. **Storage Strategy**: Keep all sessions indefinitely or auto-prune after X days?

---

**Last Updated**: 2026-01-07  
**Author**: System//Zero Development Team  
**Status**: READY FOR IMPLEMENTATION
