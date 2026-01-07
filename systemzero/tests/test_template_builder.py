import json
from pathlib import Path

from extensions.template_builder.builder import TemplateBuilder


def _sample_capture():
    return {
        "captured_at": "2026-01-07T13:25:00Z",
        "raw": {},
        "normalized": {
            "root": {
                "role": "window",
                "name": "TestWindow",
                "type": "container",
                "children": [
                    {"role": "button", "name": "OK", "type": "control", "children": []},
                    {"role": "text", "name": "Message", "type": "static", "children": []}
                ],
            }
        },
        "signatures": {
            "full": "abc123",
            "structural": "struct456",
            "content": "content789"
        }
    }


def test_template_builder_from_capture(tmp_path):
    """Test building a template from a capture file."""
    capture_file = tmp_path / "test_capture.json"
    with open(capture_file, "w", encoding="utf-8") as f:
        json.dump(_sample_capture(), f)

    builder = TemplateBuilder()
    template = builder.build_from_capture(capture_file, "test_screen", "test_app")

    assert template["screen_id"] == "test_screen"
    assert "OK" in template["required_nodes"]
    assert template["metadata"]["app"] == "test_app"
    assert template["structure_signature"] == "struct456"


def test_template_builder_save_yaml(tmp_path):
    """Test saving template to YAML."""
    capture_file = tmp_path / "test_capture.json"
    with open(capture_file, "w", encoding="utf-8") as f:
        json.dump(_sample_capture(), f)

    builder = TemplateBuilder()
    template = builder.build_from_capture(capture_file, "test_screen", "test_app")
    
    yaml_path = tmp_path / "test.yaml"
    saved_path = builder.save_yaml(template, yaml_path)

    assert saved_path.exists()
    with open(saved_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "test_screen" in content
    assert "OK" in content
