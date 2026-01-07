"""UI node classification for semantic analysis."""
from typing import Dict, Any, Set


class NodeClassifier:
    """Classifies UI nodes into semantic categories.
    
    Categories:
    - interactive: Buttons, links, inputs that user can interact with
    - content: Text, images, labels that display information
    - container: Layout elements that group other elements
    - navigation: Menus, tabs, navigation bars
    - input: Text fields, forms, checkboxes
    - decorative: Visual elements with no semantic meaning
    """
    
    def __init__(self):
        self._interactive_roles: Set[str] = {
            "button", "link", "menuitem", "tab", "checkbox",
            "radio", "switch", "slider", "textbox"
        }
        self._content_roles: Set[str] = {
            "text", "label", "heading", "paragraph",
            "image", "icon", "statictext"
        }
        self._container_roles: Set[str] = {
            "window", "pane", "panel", "group",
            "container", "scroll_pane", "splitpane", "frame"
        }
        self._navigation_roles: Set[str] = {
            "menu", "menubar", "toolbar", "tablist",
            "navigation", "tree"
        }
        self._input_roles: Set[str] = {
            "text_field", "textarea", "combobox",
            "spinbutton", "searchbox"
        }
        # Map for backward compatibility
        self._static_roles: Set[str] = self._content_roles
    
    def classify(self, node: Dict[str, Any]) -> str:
        """Classify a UI node into a semantic category.
        
        Args:
            node: Normalized UI node
            
        Returns:
            Classification string (interactive, content, container, etc.)
        """
        if not node or not isinstance(node, dict):
            return "unknown"
        
        role = node.get("role", "").lower()
        node_type = node.get("type", "").lower()
        name = node.get("name", "").lower()
        
        # Check role-based classification first
        if role in self._interactive_roles:
            return "interactive"
        if role in self._content_roles or role in self._static_roles:
            return "content" if role in self._content_roles else "static"
        if role in self._navigation_roles:
            return "navigation"
        if role in self._input_roles:
            return "input"
        if role in self._container_roles:
            return "container"
        
        # Fallback to type-based classification
        if "button" in node_type or "button" in name:
            return "interactive"
        if "text" in node_type or "label" in node_type:
            return "content"
        if "container" in node_type or "pane" in node_type:
            return "container"
        
        # Check properties for hints
        properties = node.get("properties", {})
        if isinstance(properties, dict):
            if properties.get("clickable") or properties.get("focusable"):
                return "interactive"
        
        # Check if decorative (no name, no role, not interactive)
        if not role and not name and not properties.get("enabled"):
            return "decorative"
        
        return "unknown"
    
    def is_significant(self, node: Dict[str, Any]) -> bool:
        """Determine if a node is semantically significant.
        
        Decorative and some container nodes may be filtered as noise.
        """
        classification = self.classify(node)
        return classification not in {"decorative", "unknown"}
    
    def get_interactive_nodes(self, tree: Dict[str, Any]) -> list:
        """Extract all interactive nodes from a tree."""
        interactive = []
        self._collect_by_classification(tree, "interactive", interactive)
        return interactive
    
    def _collect_by_classification(self, node: Any, target_class: str, result: list):
        """Recursively collect nodes of a specific classification."""
        if not isinstance(node, dict):
            return
        
        if self.classify(node) == target_class:
            result.append(node)
        
        # Recurse into children
        children = node.get("children", [])
        if isinstance(children, list):
            for child in children:
                self._collect_by_classification(child, target_class, result)
