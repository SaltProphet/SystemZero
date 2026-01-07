"""Export helpers for signature artifacts."""
import json
from pathlib import Path
from typing import Dict


def export_signatures(signatures: Dict[str, str], path: Path) -> Path:
    """Persist signature map to disk as JSON."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(signatures or {}, f, indent=2)
    return path
