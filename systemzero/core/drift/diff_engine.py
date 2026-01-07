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
    
    def diff(self, tree_a: Dict[str, Any], tree_b: Dict[str, Any]) -> List[DriftEvent]:
        """Generate a diff between two trees.
        
        Args:
            tree_a: Original tree (baseline)
            tree_b: New tree (current)
            
        Returns:
            List of DriftEvent objects representing:
            - Added nodes (change_type="added")
            - Removed nodes (change_type="removed" or "missing")
            - Modified nodes (change_type="modified" or "changed")
        """
        if not tree_a and not tree_b:
            return []
        
        events = []
        
        if not tree_a:
            events.append(self._create_drift_event(
                "added", tree_b, "root", "info"
            ))
            return events
        
        if not tree_b:
            events.append(self._create_drift_event(
                "removed", tree_a, "root", "warning"
            ))
            return events
        
        # Extract roots
        root_a = tree_a.get("root") if isinstance(tree_a, dict) and "root" in tree_a else tree_a
        root_b = tree_b.get("root") if isinstance(tree_b, dict) and "root" in tree_b else tree_b
        
        # Compare trees recursively
        self._diff_nodes(root_a, root_b, events, "root")
        
        return events
    
    def diff_summary(self, events: List[DriftEvent]) -> str:
        """Generate a human-readable summary of a diff.
        
        Args:
            events: List of DriftEvent objects from diff()
            
        Returns:
            Human-readable summary string
        """
        if not events:
            return "No differences detected"
        
        added = [e for e in events if e.change_type in ("added",)]
        removed = [e for e in events if e.change_type in ("removed", "missing")]
        modified = [e for e in events if e.change_type in ("modified", "changed")]
        
        lines = [
            f"Total changes: {len(events)}",
            f"Added: {len(added)} nodes",
            f"Removed: {len(removed)} nodes",
            f"Modified: {len(modified)} nodes"
        ]
        return "\n".join(lines)
    
    def has_significant_changes(self, events: List[DriftEvent], threshold: int = 5) -> bool:
        """Determine if diff contains significant changes.
        
        Args:
            events: List of DriftEvent objects from diff()
            threshold: Number of changes considered significant
            
        Returns:
            True if number of events exceeds threshold
        """
        return len(events) >= threshold
    
    def _diff_nodes(self, node_a: Any, node_b: Any, events: List[DriftEvent], path: str):
        """Recursively compare nodes."""
        if not isinstance(node_a, dict) or not isinstance(node_b, dict):
            if node_a != node_b:
                if node_a:
                    events.append(self._create_drift_event("removed", node_a, path, "warning"))
                if node_b:
                    events.append(self._create_drift_event("added", node_b, path, "info"))
            return
        
        # Check if nodes are similar (same role/type)
        if not self._nodes_similar(node_a, node_b):
            events.append(self._create_drift_event("removed", node_a, path, "warning"))
            events.append(self._create_drift_event("added", node_b, path, "info"))
            return
        
        # Check for property modifications
        if self._properties_changed(node_a, node_b):
            changes = self._get_property_changes(node_a, node_b)
            events.append(self._create_drift_event("changed", node_b, path, "warning", changes))
        
        # Compare children
        children_a = node_a.get("children", [])
        children_b = node_b.get("children", [])
        
        self._diff_children(children_a, children_b, events, path)
    
    def _diff_children(self, children_a: list, children_b: list, events: List[DriftEvent], parent_path: str):
        """Compare lists of children."""
        # Simple approach: match by position and similarity
        max_len = max(len(children_a), len(children_b))
        
        for i in range(max_len):
            child_a = children_a[i] if i < len(children_a) else None
            child_b = children_b[i] if i < len(children_b) else None
            child_path = f"{parent_path}[{i}]"
            
            if child_a is None:
                events.append(self._create_drift_event("added", child_b, child_path, "info"))
            elif child_b is None:
                events.append(self._create_drift_event("missing", child_a, child_path, "warning"))
            else:
                self._diff_nodes(child_a, child_b, events, child_path)
    
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
