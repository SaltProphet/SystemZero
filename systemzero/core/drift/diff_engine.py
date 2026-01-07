"""Generate detailed diffs between UI trees."""
from typing import Dict, Any, List, Tuple, Set
import copy
from .change import Change


class DiffEngine:
    """Generates detailed structural diffs between UI trees.
    
    Detects:
    - Added nodes
    - Removed nodes
    - Modified nodes (property changes)
    - Moved nodes (structure changes)
    - Content changes
    """
    
    def __init__(self):
        self._compare_properties = {"role", "name", "type", "visible", "enabled"}
    
    def diff(self, tree_a: Dict[str, Any], tree_b: Dict[str, Any]) -> List[Change]:
        """Generate a diff between two trees.
        
        Args:
            tree_a: Original tree (baseline)
            tree_b: New tree (current)
            
        Returns:
            List of Change objects describing differences
        """
        if not tree_a and not tree_b:
            return []
        
        if not tree_a:
            return [Change("added", "/", node=tree_b)]
        
        if not tree_b:
            return [Change("missing", "/", node=tree_a)]
        
        changes = []
        
        # Extract roots
        root_a = tree_a.get("root") if isinstance(tree_a, dict) else tree_a
        root_b = tree_b.get("root") if isinstance(tree_b, dict) else tree_b
        
        # Compare trees recursively
        self._diff_nodes(root_a, root_b, changes, "/")
        
        return changes
    
    def diff_summary(self, changes: List[Change]) -> str:
        """Generate a human-readable summary of changes.
        
        Args:
            changes: List of Change objects
            
        Returns:
            Summary string
        """
        added = [c for c in changes if c.change_type == "added"]
        removed = [c for c in changes if c.change_type == "missing"]
        modified = [c for c in changes if c.change_type == "changed"]
        
        lines = [
            f"Total changes: {len(changes)}",
            f"Added: {len(added)} nodes",
            f"Removed: {len(removed)} nodes",
            f"Modified: {len(modified)} nodes"
        ]
        return "\n".join(lines)
    
    def has_significant_changes(self, changes: List[Change], max_changes: int = 5) -> bool:
        """Determine if changes are significant.
        
        Args:
            changes: List of Change objects
            max_changes: Threshold for significance
            
        Returns:
            True if number of changes exceeds threshold
        """
        return len(changes) >= max_changes
    
    def _diff_nodes(self, node_a: Any, node_b: Any, changes: List[Change], path: str):
        """Recursively compare nodes and collect changes."""
        if not isinstance(node_a, dict) or not isinstance(node_b, dict):
            if node_a != node_b:
                if node_a and not node_b:
                    changes.append(Change("missing", path, node=node_a))
                elif node_b and not node_a:
                    changes.append(Change("added", path, node=node_b))
                else:
                    changes.append(Change("changed", path, old_value=node_a, new_value=node_b))
            return
        
        # Check if nodes are similar (same role/type)
        if not self._nodes_similar(node_a, node_b):
            changes.append(Change("missing", path, node=node_a))
            changes.append(Change("added", path, node=node_b))
            return
        
        # Check for property modifications
        if self._properties_changed(node_a, node_b):
            prop_changes = self._get_property_changes(node_a, node_b)
            for prop, (old_val, new_val) in prop_changes.items():
                changes.append(Change("changed", f"{path}/{prop}", old_value=old_val, new_value=new_val, node=node_b))
        
        # Compare children
        children_a = node_a.get("children", [])
        children_b = node_b.get("children", [])
        
        self._diff_children(children_a, children_b, changes, path)
    
    def _diff_children(self, children_a: list, children_b: list, changes: List[Change], path: str):
        """Compare lists of children."""
        max_len = max(len(children_a), len(children_b))
        
        for i in range(max_len):
            child_a = children_a[i] if i < len(children_a) else None
            child_b = children_b[i] if i < len(children_b) else None
            child_path = f"{path}/child[{i}]"
            
            if child_a is None:
                changes.append(Change("added", child_path, node=child_b))
            elif child_b is None:
                changes.append(Change("missing", child_path, node=child_a))
            else:
                self._diff_nodes(child_a, child_b, changes, child_path)
    
    def _nodes_similar(self, node_a: Dict[str, Any], node_b: Dict[str, Any]) -> bool:
        """Check if two nodes are similar enough to compare."""
        # Nodes are similar if they have the same role or type
        role_a = node_a.get("role", "")
        role_b = node_b.get("role", "")
        type_a = node_a.get("type", "")
        type_b = node_b.get("type", "")
        
        return role_a == role_b or type_a == type_b
    
    def _properties_changed(self, node_a: Dict[str, Any], node_b: Dict[str, Any]) -> bool:
        """Check if any compared properties changed."""
        for prop in self._compare_properties:
            if node_a.get(prop) != node_b.get(prop):
                return True
        return False
    
    def _get_property_changes(self, node_a: Dict[str, Any], node_b: Dict[str, Any]) -> Dict[str, Tuple[Any, Any]]:
        """Get dictionary of property changes."""
        changes = {}
        for prop in self._compare_properties:
            val_a = node_a.get(prop)
            val_b = node_b.get(prop)
            if val_a != val_b:
                changes[prop] = (val_a, val_b)
        return changes
    
    def _summarize_node(self, node: Any) -> Dict[str, Any]:
        """Create a summary of a node for diff output."""
        if not isinstance(node, dict):
            return {"value": node}
        
        return {
            "role": node.get("role"),
            "name": node.get("name"),
            "type": node.get("type")
        }

