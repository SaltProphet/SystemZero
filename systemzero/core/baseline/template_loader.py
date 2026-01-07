"""Load and manage YAML baseline templates."""
import yaml
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class TemplateLoader:
    """Loads baseline templates from YAML files.
    
    Templates define expected UI structures for known screens/states.
    Each template contains:
    - screen_id: Unique identifier
    - required_nodes: List of expected UI elements
    - structure_signature: Expected layout signature
    - valid_transitions: Allowed state transitions
    """
    
    def __init__(self, templates_dir: Optional[str] = None):
        if templates_dir is None:
            # Default to templates directory relative to this file
            current_dir = Path(__file__).parent
            templates_dir = current_dir / "templates"
        
        self.templates_dir = Path(templates_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._loaded = False
    
    def load(self, path: str) -> Dict[str, Any]:
        """Load a single template from a file path.
        
        Args:
            path: Absolute or relative path to YAML template
            
        Returns:
            Parsed template dictionary
        """
        file_path = Path(path)
        
        # Try relative to templates_dir if not absolute
        if not file_path.is_absolute():
            file_path = self.templates_dir / file_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Template not found: {file_path}")
        
        with open(file_path, 'r') as f:
            template = yaml.safe_load(f)
        
        # Cache by screen_id if available
        if template and "screen_id" in template:
            self._cache[template["screen_id"]] = template
        
        return template or {}
    
    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """Load all templates from the templates directory.
        
        Returns:
            Dict mapping screen_id to template data
        """
        if self._loaded and self._cache:
            return self._cache
        
        if not self.templates_dir.exists():
            return {}
        
        # Load all YAML files
        for yaml_file in self.templates_dir.glob("*.yaml"):
            try:
                template = self.load(str(yaml_file))
                if template and "screen_id" in template:
                    self._cache[template["screen_id"]] = template
            except Exception as e:
                print(f"Error loading template {yaml_file}: {e}")
        
        self._loaded = True
        return self._cache
    
    def get(self, screen_id: str) -> Optional[Dict[str, Any]]:
        """Get a template by screen_id.
        
        Args:
            screen_id: Unique screen identifier
            
        Returns:
            Template dict or None if not found
        """
        # Load all templates if not already loaded
        if not self._loaded:
            self.load_all()
        
        return self._cache.get(screen_id)
    
    def list_templates(self) -> List[str]:
        """List all available template screen IDs."""
        if not self._loaded:
            self.load_all()
        
        return list(self._cache.keys())
    
    def reload(self):
        """Clear cache and reload all templates."""
        self._cache.clear()
        self._loaded = False
        self.load_all()
