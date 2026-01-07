"""Export helpers for UI tree captures."""
import json
from pathlib import Path
from typing import Dict, Any


def export_tree(tree: Dict[str, Any], path: Path) -> Path:
    """Persist a UI tree (raw or normalized) to disk as JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tree or {}, f, indent=2)
    return path
