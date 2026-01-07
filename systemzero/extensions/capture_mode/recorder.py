"""Capture UI trees and persist normalized snapshots."""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from core.accessibility import TreeCapture
from core.normalization import TreeNormalizer, SignatureGenerator


class Recorder:
    """Captures UI accessibility trees and saves normalized output.
    
    Pipeline: capture raw tree → normalize → generate signatures → persist to disk.
    """

    def __init__(
        self,
        capture: Optional[TreeCapture] = None,
        normalizer: Optional[TreeNormalizer] = None,
        signature_generator: Optional[SignatureGenerator] = None,
    ) -> None:
        self.capture_source = capture or TreeCapture()
        self.normalizer = normalizer or TreeNormalizer()
        self.signature_generator = signature_generator or SignatureGenerator()

    def record(self, output_path: Optional[Path] = None, tree: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Capture and persist a snapshot.
        
        Args:
            output_path: Where to write the capture (defaults to captures/capture_<ts>.json)
            tree: Optional pre-supplied tree (primarily for tests); if omitted, capture live
        Returns:
            Dict payload containing raw, normalized, and signatures
        """
        raw_tree = tree or self.capture_source.capture()
        normalized = self.normalizer.normalize(raw_tree)
        signatures = self.signature_generator.generate_multi(normalized)

        payload = {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "raw": raw_tree,
            "normalized": normalized,
            "signatures": signatures,
        }

        path = self._resolve_output_path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return {"path": str(path), **payload}

    def _resolve_output_path(self, output_path: Optional[Path]) -> Path:
        """Compute output path, defaulting to captures/ with timestamped filename."""
        if output_path:
            return Path(output_path)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        return Path("captures") / f"capture_{timestamp}.json"
