"""UI tree normalization for consistent comparison."""
from typing import Dict, Any, List, Optional
import copy


class TreeNormalizer:
    """Normalizes UI trees for consistent baseline comparison.
    
    Normalization includes:
    - Removing transient properties (timestamps, IDs)
    - Standardizing property names across platforms
    - Sorting children for deterministic comparison
    - Flattening redundant wrapper nodes
    """
    
    def __init__(self):
        self._transient_props = {"timestamp", "id", "instance_id", "hash"}
        self._property_mappings = {
            "label": "name",
            "title": "name",
            "text": "name",
            "description": "name"
        }
    
    def normalize(self, tree: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a UI tree for comparison.
        
        Args:
            tree: Raw UI tree from TreeCapture
            
        Returns:
            Normalized tree with consistent structure
        """
        if not tree:
            return {}
        
        normalized = copy.deepcopy(tree)
        
        # Extract and normalize the root node
        if "root" in normalized:
            normalized["root"] = self._normalize_node(normalized["root"])
        
        # Remove transient top-level properties
        for prop in list(normalized.keys()):
            if prop in self._transient_props:
                del normalized[prop]
        
        return normalized
    
    def _normalize_node(self, node: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Recursively normalize a single node."""
        if not node or not isinstance(node, dict):
            return node
        
        normalized = {}
        
        # Normalize property names
        for key, value in node.items():
            if key in self._transient_props:
                continue
            
            # Map alternative property names to standard names
            standard_key = self._property_mappings.get(key, key)
            
            if key == "children" and isinstance(value, list):
                # Recursively normalize children
                normalized_children = [
                    self._normalize_node(child) for child in value
                ]
                # Filter out None values and sort for determinism
                normalized_children = [c for c in normalized_children if c]
                normalized["children"] = self._sort_children(normalized_children)
            elif isinstance(value, dict):
                normalized[standard_key] = self._normalize_node(value)
            else:
                normalized[standard_key] = value
        
        return normalized
    
    def _sort_children(self, children: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort children for deterministic comparison.
        
        Sorts by: role > name > type
        """
        def sort_key(node):
            return (
                node.get("role", ""),
                node.get("name", ""),
                node.get("type", "")
            )
        
        return sorted(children, key=sort_key)
