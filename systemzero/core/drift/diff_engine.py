"""Generate detailed diffs between UI trees."""
from typing import Dict, Any, List, Tuple, Set
import copy
from .drift_event import DriftEvent


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
        self._compare_properties = {"role", "name", "type", "visible", "enabled", "value"}
    
    def diff(self, tree_a: Dict[str, Any], tree_b: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a structured diff between two trees.
        
        Returns a dict with added/removed/modified lists, unchanged count, and similarity score.
        This matches expectations in tests and is easier for UIs to consume.
        """
        if not tree_a and not tree_b:
            return {"added": [], "removed": [], "modified": [], "unchanged": 0, "similarity": 1.0}
        if not tree_a:
            return {"added": [tree_b], "removed": [], "modified": [], "unchanged": 0, "similarity": 0.0}
        if not tree_b:
            return {"added": [], "removed": [tree_a], "modified": [], "unchanged": 0, "similarity": 0.0}

        added: List[Any] = []
        removed: List[Any] = []
        modified: List[Any] = []

        root_a = tree_a.get("root") if isinstance(tree_a, dict) and "root" in tree_a else tree_a
        root_b = tree_b.get("root") if isinstance(tree_b, dict) and "root" in tree_b else tree_b

        unchanged_count = self._diff_nodes(root_a, root_b, added, removed, modified, "root")

        total_changes = len(added) + len(removed) + len(modified)
        total_nodes = total_changes + unchanged_count if (total_changes + unchanged_count) > 0 else 1
        similarity = max(0.0, min(1.0, (total_nodes - total_changes) / total_nodes))

        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged_count,
            "similarity": similarity
        }
    
    def diff_summary(self, result: Dict[str, Any]) -> str:
        """Generate a human-readable summary from structured diff result."""
        if not result:
            return "No differences detected"
        added = len(result.get("added", []))
        removed = len(result.get("removed", []))
        modified = len(result.get("modified", []))
        unchanged = result.get("unchanged", 0)
        similarity = result.get("similarity", 0)
        lines = [
            f"Total changes: {added + removed + modified}",
            f"Added: {added} nodes",
            f"Removed: {removed} nodes",
            f"Modified: {modified} nodes",
            f"Unchanged: {unchanged}",
            f"Similarity: {similarity:.2f}"
        ]
        return "\n".join(lines)
    
    def has_significant_changes(self, diff_result: Dict[str, Any], threshold: float = 0.9) -> bool:
        """Determine if changes exceed a similarity threshold (lower similarity = more change)."""
        similarity = diff_result.get("similarity", 0)
        return similarity < threshold
    
    def _diff_nodes(self, node_a: Any, node_b: Any,
                    added: List[Any], removed: List[Any], modified: List[Any],
                    path: str) -> int:
        """Recursively compare nodes and collect changes.
        Returns number of unchanged nodes encountered.
        """
        unchanged = 0
        if not isinstance(node_a, dict) or not isinstance(node_b, dict):
            if node_a != node_b:
                if node_a:
                    removed.append({"path": path, "node": node_a})
                if node_b:
                    added.append({"path": path, "node": node_b})
            else:
                unchanged += 1
            return unchanged

        if not self._nodes_similar(node_a, node_b):
            removed.append({"path": path, "node": node_a})
            added.append({"path": path, "node": node_b})
            return unchanged

        if self._properties_changed(node_a, node_b):
            changes = self._get_property_changes(node_a, node_b)
            modified.append({"path": path, "changes": changes, "node": node_b})
        else:
            unchanged += 1
        
        children_a = node_a.get("children", [])
        children_b = node_b.get("children", [])
        unchanged += self._diff_children(children_a, children_b, added, removed, modified, path)
        return unchanged
    
    def _diff_children(self, children_a: list, children_b: list,
                       added: List[Any], removed: List[Any], modified: List[Any], parent_path: str) -> int:
        """Compare lists of children. Returns count of unchanged child nodes."""
        unchanged = 0
        max_len = max(len(children_a), len(children_b))
        for i in range(max_len):
            child_a = children_a[i] if i < len(children_a) else None
            child_b = children_b[i] if i < len(children_b) else None
            child_path = f"{parent_path}[{i}]"
            if child_a is None and child_b is not None:
                added.append({"path": child_path, "node": child_b})
            elif child_b is None and child_a is not None:
                removed.append({"path": child_path, "node": child_a})
            else:
                unchanged += self._diff_nodes(child_a, child_b, added, removed, modified, child_path)
        return unchanged
    
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
    
    def _create_drift_event(self, change_type: str, node: Any, location: str, 
                           severity: str, changes: Dict[str, Tuple[Any, Any]] = None) -> DriftEvent:
        """Create a DriftEvent for a detected change.
        
        Args:
            change_type: Type of change (added, removed, modified)
            node: The node that changed
            location: Path to the node in the tree
            severity: Severity level (info, warning, critical)
            changes: Optional property changes for modified nodes
            
        Returns:
            DriftEvent object
        """
        node_summary = self._summarize_node(node)
        
        details = {
            "node": node_summary,
            "location": location
        }
        
        if changes:
            details["changes"] = changes
        
        # Map change_type to drift_type
        if change_type in ("added", "removed", "missing"):
            drift_type = "layout"
        elif change_type in ("modified", "changed"):
            drift_type = "content"
        else:
            drift_type = "layout"
        
        return DriftEvent(
            drift_type=drift_type,
            severity=severity,
            details=details,
            location=location,
            change_type=change_type
        )
