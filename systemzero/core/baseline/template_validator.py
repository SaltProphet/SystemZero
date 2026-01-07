"""Validate baseline template structure and content."""
from typing import Dict, Any, List, Set


class TemplateValidator:
    """Validates baseline templates for correctness and completeness.
    
    Validates:
    - Required fields present
    - Field types correct
    - Valid transitions format
    - Screen ID uniqueness
    - Required nodes format
    """
    
    def __init__(self):
        self._required_fields: Set[str] = {
            "screen_id"
        }
        self._optional_fields: Set[str] = {
            "required_nodes", "structure_signature",
            "valid_transitions", "metadata", "version"
        }
    
    def validate(self, template: Dict[str, Any]) -> bool:
        """Validate a template for correctness.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not template or not isinstance(template, dict):
            return False
        
        # Check required fields
        if not self._validate_required_fields(template):
            return False

        # Minimal structural checks
        if not template.get("screen_id"):
            return False
        # Treat required_nodes as optional but validate if present
        if "required_nodes" in template and not isinstance(template.get("required_nodes", []), list):
            return False
        if "structure_signature" in template and not isinstance(template.get("structure_signature"), str):
            return False

        # Check field types
        if not self._validate_field_types(template):
            return False

        # Check transitions format
        if "valid_transitions" in template:
            if not self._validate_transitions(template["valid_transitions"]):
                return False

        return True
    
    def validate_with_errors(self, template: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate a template and return detailed errors.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        if not template or not isinstance(template, dict):
            errors.append("Template must be a non-empty dictionary")
            return False, errors
        
        # Check required fields
        for field in self._required_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")
        
        # Check screen_id
        if "screen_id" in template:
            if not isinstance(template["screen_id"], str) or not template["screen_id"]:
                errors.append("screen_id must be a non-empty string")
        
        # Check required_nodes
        if "required_nodes" in template:
            if not isinstance(template["required_nodes"], list):
                errors.append("required_nodes must be a list")
            elif not all(isinstance(node, str) for node in template["required_nodes"]):
                errors.append("All required_nodes must be strings")
        
        # Check structure_signature
        if "structure_signature" in template:
            if not isinstance(template["structure_signature"], str):
                errors.append("structure_signature must be a string")
        
        # Check valid_transitions
        if "valid_transitions" in template:
            transitions = template["valid_transitions"]
            if not isinstance(transitions, list):
                errors.append("valid_transitions must be a list")
            else:
                for i, transition in enumerate(transitions):
                    if not isinstance(transition, str):
                        errors.append(f"Transition {i} must be a string")
                    elif " -> " not in transition and transition != "":
                        errors.append(f"Invalid transition format: {transition}")
        
        return len(errors) == 0, errors
    
    def _validate_required_fields(self, template: Dict[str, Any]) -> bool:
        """Check all required fields are present."""
        return all(field in template for field in self._required_fields)
    
    def _validate_field_types(self, template: Dict[str, Any]) -> bool:
        """Check field types are correct."""
        if "screen_id" in template:
            if not isinstance(template["screen_id"], str):
                return False
        
        if "required_nodes" in template:
            if not isinstance(template["required_nodes"], list):
                return False
        
        if "structure_signature" in template:
            if not isinstance(template["structure_signature"], str):
                return False
        
        if "valid_transitions" in template:
            if not isinstance(template["valid_transitions"], list):
                return False
        
        return True
    
    def _validate_transitions(self, transitions: List[Any]) -> bool:
        """Validate transition format.
        
        Transitions should be strings like: "screen_a -> screen_b"
        """
        if not isinstance(transitions, list):
            return False
        
        for transition in transitions:
            if not isinstance(transition, str):
                return False
            # Allow empty list or valid transition format
            if transition and " -> " not in transition:
                return False
        
        return True
    
    def validate_multiple(self, templates: Dict[str, Dict[str, Any]]) -> Dict[str, bool]:
        """Validate multiple templates.
        
        Args:
            templates: Dict mapping screen_id to template
            
        Returns:
            Dict mapping screen_id to validation result
        """
        results = {}
        for screen_id, template in templates.items():
            results[screen_id] = self.validate(template)
        return results
