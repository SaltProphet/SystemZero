"""Generate detailed diffs between UI trees."""
from typing import Dict, Any, List, Tuple, Set
import copy


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
    
    def diff(self, tree_a: Dict[str, Any], tree_b: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a diff between two trees.
        
        Args:
            tree_a: Original tree (baseline)
            tree_b: New tree (current)
            
        Returns:
            Dict containing:
            - added: List of nodes in tree_b but not tree_a
            - removed: List of nodes in tree_a but not tree_b
            - modified: List of nodes with property changes
            - unchanged: Count of unchanged nodes
            - similarity: Overall similarity score
        """
        if not tree_a and not tree_b:
            return self._empty_diff()
        
        if not tree_a:
            return {
                "added": [tree_b],
                "removed": [],
                "modified": [],
                "unchanged": 0,
                "similarity": 0.0
            }
        
        if not tree_b:
            return {
                "added": [],
                "removed": [tree_a],
                "modified": [],
                "unchanged": 0,
                "similarity": 0.0
            }
        
        added = []
        removed = []
        modified = []
        unchanged_count = 0
        
        # Extract roots
        root_a = tree_a.get("root") if isinstance(tree_a, dict) else tree_a
        root_b = tree_b.get("root") if isinstance(tree_b, dict) else tree_b
        
        # Compare trees recursively
        self._diff_nodes(root_a, root_b, added, removed, modified, [unchanged_count])
        
        total_nodes = len(added) + len(removed) + len(modified) + unchanged_count
        similarity = unchanged_count / total_nodes if total_nodes > 0 else 1.0
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged_count,
            "similarity": similarity
        }
    
    def diff_summary(self, diff: Dict[str, Any]) -> str:
        """Generate a human-readable summary of a diff."""
        lines = [
            f"Similarity: {diff['similarity']:.1%}",
            f"Added: {len(diff['added'])} nodes",
            f"Removed: {len(diff['removed'])} nodes",
            f"Modified: {len(diff['modified'])} nodes",
            f"Unchanged: {diff['unchanged']} nodes"
        ]
        return "\n".join(lines)
    
    def has_significant_changes(self, diff: Dict[str, Any], threshold: float = 0.9) -> bool:
        """Determine if diff contains significant changes.
        
        Args:
            diff: Diff result from diff()
            threshold: Similarity threshold (below = significant)
            
        Returns:
            True if similarity is below threshold
        """
        return diff.get("similarity", 1.0) < threshold
    
    def _diff_nodes(self, node_a: Any, node_b: Any, added: list, removed: list, 
                    modified: list, unchanged: list):
        """Recursively compare nodes."""
        if not isinstance(node_a, dict) or not isinstance(node_b, dict):
            if node_a != node_b:
                if node_a:
                    removed.append(node_a)
                if node_b:
                    added.append(node_b)
            else:
                unchanged[0] += 1
            return
        
        # Check if nodes are similar (same role/type)
        if not self._nodes_similar(node_a, node_b):
            removed.append(self._summarize_node(node_a))
            added.append(self._summarize_node(node_b))
            return
        
        # Check for property modifications
        if self._properties_changed(node_a, node_b):
            modified.append({
                "node": self._summarize_node(node_b),
                "changes": self._get_property_changes(node_a, node_b)
            })
        else:
            unchanged[0] += 1
        
        # Compare children
        children_a = node_a.get("children", [])
        children_b = node_b.get("children", [])
        
        self._diff_children(children_a, children_b, added, removed, modified, unchanged)
    
    def _diff_children(self, children_a: list, children_b: list, added: list, 
                      removed: list, modified: list, unchanged: list):
        """Compare lists of children."""
        # Simple approach: match by position and similarity
        max_len = max(len(children_a), len(children_b))
        
        for i in range(max_len):
            child_a = children_a[i] if i < len(children_a) else None
            child_b = children_b[i] if i < len(children_b) else None
            
            if child_a is None:
                added.append(self._summarize_node(child_b))
            elif child_b is None:
                removed.append(self._summarize_node(child_a))
            else:
                self._diff_nodes(child_a, child_b, added, removed, modified, unchanged)
    
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
    
    def _empty_diff(self) -> Dict[str, Any]:
        """Return an empty diff result."""
        return {
            "added": [],
            "removed": [],
            "modified": [],
            "unchanged": 0,
            "similarity": 1.0
        }
