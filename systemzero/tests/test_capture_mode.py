import json
from pathlib import Path

from extensions.capture_mode.recorder import Recorder
from interface.cli.commands import cmd_capture


def _sample_tree():
    return {
        "root": {
            "role": "window",
            "name": "Root",
            "type": "container",
            "children": [
                {"role": "button", "name": "OK", "type": "control", "children": []}
            ],
        }
    }


def test_recorder_writes_capture(tmp_path):
    out_file = tmp_path / "cap.json"
    recorder = Recorder()
    result = recorder.record(out_file, _sample_tree())

    assert out_file.exists()
    with open(out_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    assert payload.get("normalized", {}).get("root", {}).get("role") == "window"
    assert "full" in payload.get("signatures", {})
    assert Path(result["path"]).exists()


def test_cli_capture_with_tree_file(tmp_path):
    tree_path = tmp_path / "tree.json"
    out_file = tmp_path / "cli_cap.json"
    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump(_sample_tree(), f)

    cmd_capture(str(out_file), str(tree_path))

    assert out_file.exists()
    with open(out_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    assert payload.get("normalized", {}).get("root", {}).get("name") == "Root"
    assert "structural" in payload.get("signatures", {})
