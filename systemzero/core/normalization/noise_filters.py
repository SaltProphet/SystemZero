"""Filters for removing noise from UI trees."""
from typing import Dict, Any, Optional, Set
import copy


class NoiseFilters:
    """Filters out irrelevant UI elements that create false drift signals.
    
    Filters:
    - Invisible/hidden elements
    - Zero-size elements
    - Transient status indicators (loading spinners, etc.)
    - Dynamic timestamps and counters
    - Decorative elements with no semantic value
    """
    
    def __init__(self):
        self._noise_roles: Set[str] = {
            "scrollbar", "separator", "statusbar",
            "progressbar", "spinner"
        }
        self._noise_names: Set[str] = {
            "loading", "spinner", "dots", "ellipsis"
        }
        self.filter_invisible = True
        self.filter_zero_size = True
        self.filter_decorative = True
    
    def filter(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """Apply all noise filters to a UI tree.
        
        Args:
            tree: Normalized UI tree
            
        Returns:
            Filtered tree with noise elements removed
        """
        if not tree:
            return tree
        
        filtered = copy.deepcopy(tree)
        
        # Filter the root node and its children
        if "root" in filtered:
            filtered["root"] = self._filter_node(filtered["root"])
        
        return filtered
    
    def _filter_node(self, node: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Recursively filter a single node."""
        if not node or not isinstance(node, dict):
            return node
        
        # Apply filter rules
        if self._should_filter(node):
            return None
        
        # Filter children recursively
        if "children" in node and isinstance(node["children"], list):
            filtered_children = [
                self._filter_node(child) for child in node["children"]
            ]
            # Remove None entries
            node["children"] = [c for c in filtered_children if c is not None]
        
        return node
    
    def _should_filter(self, node: Dict[str, Any]) -> bool:
        """Determine if a node should be filtered out."""
        role = node.get("role", "").lower()
        name = node.get("name", "").lower()
        properties = node.get("properties", {})
        bounds = node.get("bounds", {})
        
        # Filter by role
        if role in self._noise_roles:
            return True
        
        # Filter by name patterns
        if any(noise in name for noise in self._noise_names):
            return True
        
        # Filter invisible elements
        if self.filter_invisible and isinstance(properties, dict):
            if not properties.get("visible", True):
                return True
        
        # Filter zero-size elements
        if self.filter_zero_size and isinstance(bounds, dict):
            width = bounds.get("width", 0)
            height = bounds.get("height", 0)
            if width <= 0 or height <= 0:
                return True
        
        # Filter decorative elements (no role, no name, not enabled)
        if self.filter_decorative:
            has_role = bool(role)
            has_name = bool(name)
            is_enabled = properties.get("enabled", False) if isinstance(properties, dict) else False
            
            if not has_role and not has_name and not is_enabled:
                return True
        
        return False
    
    def configure(self, **kwargs):
        """Configure filter settings.
        
        Args:
            filter_invisible: Filter invisible elements
            filter_zero_size: Filter zero-size elements
            filter_decorative: Filter decorative elements
        """
        if "filter_invisible" in kwargs:
            self.filter_invisible = kwargs["filter_invisible"]
        if "filter_zero_size" in kwargs:
            self.filter_zero_size = kwargs["filter_zero_size"]
        if "filter_decorative" in kwargs:
            self.filter_decorative = kwargs["filter_decorative"]
    
    def add_noise_role(self, role: str):
        """Add a role to the noise filter list."""
        self._noise_roles.add(role.lower())
    
    def add_noise_name(self, name: str):
        """Add a name pattern to the noise filter list."""
        self._noise_names.add(name.lower())
