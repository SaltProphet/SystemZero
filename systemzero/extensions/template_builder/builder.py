"""Convert captured trees to YAML baseline templates."""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

import yaml

from core.baseline import TemplateValidator
from core.normalization import SignatureGenerator


class TemplateBuilder:
    """Build YAML templates from normalized UI tree captures.
    
    Pipeline: load capture JSON → extract required nodes → generate signatures → write YAML.
    """

    def __init__(self, signature_generator: Optional[SignatureGenerator] = None):
        self.signature_generator = signature_generator or SignatureGenerator()
        self.validator = TemplateValidator()

    def build_from_capture(
        self, capture_path: Path, screen_id: str, app: Optional[str] = None
    ) -> Dict[str, Any]:
        """Load a capture file and build a template.
        
        Args:
            capture_path: Path to capture JSON (from Recorder)
            screen_id: Unique template identifier
            app: Optional app name for metadata
            
        Returns:
            Template dict ready for YAML export
        """
        with open(capture_path, "r", encoding="utf-8") as f:
            capture = json.load(f)

        normalized = capture.get("normalized", {})
        root = normalized.get("root", {})

        # Extract required nodes (names of interactive/semantic elements)
        required_nodes = self._extract_required_nodes(root)

        # Use signatures from capture or regenerate
        sigs = capture.get("signatures", {})
        structure_signature = sigs.get("structural", "")

        template = {
            "screen_id": screen_id,
            "required_nodes": sorted(required_nodes),
            "structure_signature": structure_signature,
            "valid_transitions": [],
            "metadata": {
                "app": app or "unknown",
                "version": "1.0",
                "source": str(capture_path),
            },
        }

        # Validate before returning
        is_valid, errors = self.validator.validate_with_errors(template)
        if not is_valid:
            raise ValueError(f"Template validation failed: {errors}")

        return template

    def _extract_required_nodes(self, node: Optional[Dict[str, Any]]) -> List[str]:
        """Extract names of interactive/semantic nodes."""
        nodes = []
        if not node or not isinstance(node, dict):
            return nodes

        # Consider interactive roles and container roles as "required"
        interactive_roles = {
            "button",
            "link",
            "menuitem",
            "checkbox",
            "radio",
            "textbox",
            "text",
            "spinbutton",
            "combobox",
            "tab",
            "tablist",
        }
        container_roles = {"window", "dialog", "form", "menu", "list", "grid"}

        role = node.get("role", "").lower()
        name = node.get("name", "")

        if role in interactive_roles or role in container_roles:
            if name:
                nodes.append(name)

        # Recurse into children
        children = node.get("children", [])
        for child in children:
            nodes.extend(self._extract_required_nodes(child))

        return nodes

    def save_yaml(self, template: Dict[str, Any], output_path: Path) -> Path:
        """Write template to YAML file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)

        return output_path
