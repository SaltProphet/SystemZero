"""Generate deterministic signatures from UI trees."""
import hashlib
import json
from typing import Dict, Any, List, Set


class SignatureGenerator:
    """Generates deterministic cryptographic signatures from normalized UI trees.
    
    Signatures are used to:
    - Quickly compare tree structures
    - Detect layout drift
    - Match against baseline templates
    - Create forensic audit trails
    """
    
    def __init__(self):
        self._ignore_properties: Set[str] = {
            "timestamp", "id", "instance_id", "focused"
        }
    
    def generate(self, normalized_tree: Dict[str, Any]) -> str:
        """Generate a SHA256 signature from a normalized tree.
        
        Args:
            normalized_tree: Normalized UI tree
            
        Returns:
            Hex string of SHA256 hash
        """
        if not normalized_tree:
            return hashlib.sha256(b"").hexdigest()
        
        # Create a canonical representation
        canonical = self._canonicalize(normalized_tree)
        
        # Convert to deterministic JSON
        json_str = json.dumps(canonical, sort_keys=True, separators=(',', ':'))
        
        # Generate hash
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def generate_structural(self, normalized_tree: Dict[str, Any]) -> str:
        """Generate signature based only on structure, ignoring content.
        
        This is useful for detecting layout changes while ignoring text changes.
        """
        if not normalized_tree:
            return hashlib.sha256(b"").hexdigest()
        
        structure = self._extract_structure(normalized_tree)
        json_str = json.dumps(structure, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def generate_content(self, normalized_tree: Dict[str, Any]) -> str:
        """Generate signature based only on content, ignoring structure.
        
        This is useful for detecting content changes while ignoring layout.
        """
        if not normalized_tree:
            return hashlib.sha256(b"").hexdigest()
        
        content = self._extract_content(normalized_tree)
        content_str = '|'.join(sorted(content))
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()
    
    def _canonicalize(self, obj: Any) -> Any:
        """Create a canonical representation for hashing."""
        if isinstance(obj, dict):
            canonical = {}
            for key, value in obj.items():
                # Skip ignored properties
                if key in self._ignore_properties:
                    continue
                canonical[key] = self._canonicalize(value)
            return canonical
        elif isinstance(obj, list):
            return [self._canonicalize(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)
    
    def _extract_structure(self, obj: Any, depth: int = 0) -> Any:
        """Extract only structural information (types, roles, hierarchy)."""
        if isinstance(obj, dict):
            structure = {
                "type": obj.get("type"),
                "role": obj.get("role")
            }
            if "children" in obj and isinstance(obj["children"], list):
                structure["children"] = [
                    self._extract_structure(child, depth + 1)
                    for child in obj["children"]
                ]
            return structure
        elif isinstance(obj, list):
            return [self._extract_structure(item, depth) for item in obj]
        else:
            return None
    
    def _extract_content(self, obj: Any, content: List[str] = None) -> List[str]:
        """Extract all text content from the tree."""
        if content is None:
            content = []
        
        if isinstance(obj, dict):
            # Extract name/text content
            if "name" in obj and obj["name"]:
                content.append(str(obj["name"]))
            
            # Recurse into children
            if "children" in obj and isinstance(obj["children"], list):
                for child in obj["children"]:
                    self._extract_content(child, content)
        elif isinstance(obj, list):
            for item in obj:
                self._extract_content(item, content)
        
        return content
    
    def compare_signatures(self, sig1: str, sig2: str) -> bool:
        """Compare two signatures for equality."""
        return sig1 == sig2
    
    def generate_multi(self, normalized_tree: Dict[str, Any]) -> Dict[str, str]:
        """Generate all signature types at once.
        
        Returns:
            Dict with keys: full, structural, content
        """
        return {
            "full": self.generate(normalized_tree),
            "structural": self.generate_structural(normalized_tree),
            "content": self.generate_content(normalized_tree)
        }
