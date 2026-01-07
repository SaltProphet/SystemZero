"""Match UI trees against baseline templates."""
from typing import Dict, Any, Optional, List, Tuple


class Matcher:
    """Matches captured UI trees against baseline templates.
    
    Matching strategies:
    - Signature matching (exact structure)
    - Required nodes matching (semantic elements present)
    - Similarity scoring (fuzzy matching)
    - Role-based matching (element types present)
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        self.similarity_threshold = similarity_threshold
    
    def match(self, tree: Dict[str, Any], template: Dict[str, Any]) -> bool:
        """Determine if a tree matches a template.
        
        Args:
            tree: Normalized UI tree
            template: Baseline template
            
        Returns:
            True if tree matches template within threshold
        """
        score = self.similarity_score(tree, template)
        return score >= self.similarity_threshold
    
    def similarity_score(self, tree: Dict[str, Any], template: Dict[str, Any]) -> float:
        """Calculate similarity score between tree and template.
        
        Args:
            tree: Normalized UI tree
            template: Baseline template
            
        Returns:
            Similarity score from 0.0 to 1.0
        """
        if not tree or not template:
            return 0.0
        
        scores = []
        
        # Check required nodes (40% weight)
        required_score = self._check_required_nodes(tree, template)
        scores.append((required_score, 0.4))
        
        # Check structure similarity (40% weight)
        structure_score = self._check_structure(tree, template)
        scores.append((structure_score, 0.4))
        
        # Check role distribution (20% weight)
        role_score = self._check_roles(tree, template)
        scores.append((role_score, 0.2))
        
        # Calculate weighted average
        weighted_sum = sum(score * weight for score, weight in scores)
        return weighted_sum
    
    def calculate_score(self, tree: Dict[str, Any], template: Dict[str, Any]) -> float:
        """Alias for similarity_score for backward compatibility.
        
        Args:
            tree: Normalized UI tree
            template: Baseline template
            
        Returns:
            Similarity score from 0.0 to 1.0
        """
        return self.similarity_score(tree, template)
    
    def find_best_match(self, tree: Dict[str, Any], templates: List[Dict[str, Any]]) -> Optional[Tuple[Dict[str, Any], float]]:
        """Find the best matching template for a tree.
        
        Args:
            tree: Normalized UI tree
            templates: List of baseline templates
            
        Returns:
            Tuple of (best_template, score) or None if no good match
        """
        if not templates:
            return None
        
        best_template = None
        best_score = 0.0
        
        for template in templates:
            score = self.similarity_score(tree, template)
            if score > best_score:
                best_score = score
                best_template = template
        
        if best_score >= self.similarity_threshold:
            return (best_template, best_score)
        
        return None
    
    def _check_required_nodes(self, tree: Dict[str, Any], template: Dict[str, Any]) -> float:
        """Check if required nodes are present in the tree."""
        required_nodes = template.get("required_nodes", [])
        if not required_nodes:
            return 1.0
        
        # Extract all node names from tree
        tree_nodes = self._extract_node_names(tree)
        
        # Count how many required nodes are present
        found = sum(1 for node in required_nodes if node in tree_nodes)
        
        return found / len(required_nodes)
    
    def _check_structure(self, tree: Dict[str, Any], template: Dict[str, Any]) -> float:
        """Check structural similarity."""
        # Compare tree depth
        tree_depth = self._calculate_depth(tree.get("root"))
        template_depth = template.get("depth", tree_depth)  # Assume similar if not specified
        
        if tree_depth == 0 and template_depth == 0:
            return 1.0
        
        depth_similarity = 1.0 - abs(tree_depth - template_depth) / max(tree_depth, template_depth)
        
        # Compare node count
        tree_count = self._count_nodes(tree.get("root"))
        template_count = template.get("node_count", tree_count)
        
        if tree_count == 0 and template_count == 0:
            count_similarity = 1.0
        else:
            count_similarity = 1.0 - abs(tree_count - template_count) / max(tree_count, template_count)
        
        return (depth_similarity + count_similarity) / 2
    
    def _check_roles(self, tree: Dict[str, Any], template: Dict[str, Any]) -> float:
        """Check if similar roles are present."""
        tree_roles = self._extract_roles(tree.get("root"))
        template_roles = set(template.get("expected_roles", []))
        
        if not template_roles:
            return 1.0
        
        if not tree_roles:
            return 0.0
        
        intersection = tree_roles & template_roles
        union = tree_roles | template_roles
        
        return len(intersection) / len(union) if union else 1.0
    
    def _extract_node_names(self, obj: Any, names: Optional[set] = None) -> set:
        """Extract all node names from a tree."""
        if names is None:
            names = set()
        
        if isinstance(obj, dict):
            if "name" in obj and obj["name"]:
                names.add(obj["name"])
            if "root" in obj:
                self._extract_node_names(obj["root"], names)
            if "children" in obj:
                for child in obj.get("children", []):
                    self._extract_node_names(child, names)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_node_names(item, names)
        
        return names
    
    def _extract_roles(self, node: Optional[Dict[str, Any]], roles: Optional[set] = None) -> set:
        """Extract all roles from a tree."""
        if roles is None:
            roles = set()
        
        if not isinstance(node, dict):
            return roles
        
        if "role" in node and node["role"]:
            roles.add(node["role"])
        
        for child in node.get("children", []):
            self._extract_roles(child, roles)
        
        return roles
    
    def _calculate_depth(self, node: Optional[Dict[str, Any]], current_depth: int = 0) -> int:
        """Calculate tree depth."""
        if not isinstance(node, dict):
            return current_depth
        
        children = node.get("children", [])
        if not children:
            return current_depth
        
        max_child_depth = max(
            self._calculate_depth(child, current_depth + 1)
            for child in children
        )
        
        return max_child_depth
    
    def _count_nodes(self, node: Optional[Dict[str, Any]]) -> int:
        """Count total nodes in tree."""
        if not isinstance(node, dict):
            return 0
        
        count = 1  # Count this node
        for child in node.get("children", []):
            count += self._count_nodes(child)
        
        return count
