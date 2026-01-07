"""Change dataclass for diff results."""
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Change:
    """Represents a single change detected between two UI trees.
    
    Attributes:
        change_type: Type of change (missing, added, changed, moved)
        path: Path to the changed node in the tree
        old_value: Previous value (for changed/removed nodes)
        new_value: New value (for changed/added nodes)
        node: Reference to the affected node
    """
    change_type: str
    path: str
    old_value: Optional[Any] = None
    new_value: Optional[Any] = None
    node: Optional[Dict[str, Any]] = None
    
    def __str__(self) -> str:
        """Human-readable representation."""
        if self.change_type == "missing":
            return f"Missing node at {self.path}"
        elif self.change_type == "added":
            return f"Added node at {self.path}"
        elif self.change_type == "changed":
            return f"Changed {self.path}: {self.old_value} -> {self.new_value}"
        elif self.change_type == "moved":
            return f"Moved node from {self.old_value} to {self.new_value}"
        else:
            return f"{self.change_type} at {self.path}"
