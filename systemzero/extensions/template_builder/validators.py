"""Enhanced validators for templates and captures."""
from typing import Dict, Any, List, Tuple


class TemplateMetadataValidator:
    """Validate template metadata and versioning."""

    def validate_metadata(self, template: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check metadata completeness and version compatibility."""
        errors = []
        metadata = template.get("metadata", {})

        # Check version
        version = metadata.get("version")
        if version is None:
            errors.append("metadata.version is missing")
        elif isinstance(version, str):
            try:
                parts = version.split(".")
                if len(parts) != 3:
                    errors.append(f"version must be semver (e.g., 1.0.0), got: {version}")
            except:
                errors.append(f"version format invalid: {version}")

        # Check app
        app = metadata.get("app")
        if not app:
            errors.append("metadata.app is recommended")

        return len(errors) == 0, errors


class CaptureValidator:
    """Validate capture file structure."""

    def validate_capture(self, capture: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Check capture has required fields."""
        errors = []

        required = ["captured_at", "raw", "normalized", "signatures"]
        for field in required:
            if field not in capture:
                errors.append(f"Missing required field: {field}")

        # Check signatures structure
        sigs = capture.get("signatures", {})
        for sig_type in ["full", "structural", "content"]:
            if sig_type not in sigs:
                errors.append(f"Missing signature type: {sig_type}")

        return len(errors) == 0, errors
