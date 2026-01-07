"""Phase 4 integration tests."""
import json
from pathlib import Path

from extensions.capture_mode.recorder import Recorder
from extensions.template_builder.builder import TemplateBuilder
from extensions.template_builder.exporters import LogExporter
from core.drift import DriftEvent
from core.logging import ImmutableLog


def test_phase4_full_workflow(tmp_path):
    """Test complete Phase 4 workflow: capture → build template → export."""

    # Step 1: Capture
    sample_tree = {
        "root": {
            "role": "window",
            "name": "TestApp",
            "type": "container",
            "children": [
                {"role": "button", "name": "Submit", "type": "control", "children": []}
            ],
        }
    }
    
    recorder = Recorder()
    capture_file = tmp_path / "workflow_capture.json"
    capture_result = recorder.record(capture_file, sample_tree)
    assert capture_file.exists()

    # Step 2: Build template
    builder = TemplateBuilder()
    template = builder.build_from_capture(capture_file, "workflow_screen", "workflow_app")
    template_file = tmp_path / "workflow_template.yaml"
    builder.save_yaml(template, template_file)
    assert template_file.exists()
    assert "workflow_screen" in template["screen_id"]

    # Step 3: Create and export log
    log_file = tmp_path / "workflow.log"
    log = ImmutableLog(str(log_file))
    
    drift1 = DriftEvent("layout", "warning", {"test": "data1"})
    drift2 = DriftEvent("content", "info", {"test": "data2"})
    
    log.append(drift1)
    log.append(drift2)
    
    # Step 4: Export log to JSON
    entries = log.get_entries()
    exporter = LogExporter()
    
    export_json = tmp_path / "export.json"
    exporter.to_json(entries, export_json)
    assert export_json.exists()
    
    with open(export_json, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) >= 2

    # Step 5: Export to CSV
    export_csv = tmp_path / "export.csv"
    exporter.to_csv(entries, export_csv)
    assert export_csv.exists()

    # Step 6: Export to HTML
    export_html = tmp_path / "export.html"
    exporter.to_html(entries, export_html, title="Phase 4 Test")
    assert export_html.exists()
    assert b"Phase 4 Test" in export_html.read_bytes()
