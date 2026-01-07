"""Drift event data structure for UI changes."""
from typing import Dict, Any, Optional
import time


class DriftEvent:
    """Represents a detected drift from baseline expectations.
    
    Drift types:
    - layout: Structural changes to UI
    - content: Text or data changes
    - sequence: Unexpected state transitions
    - manipulative: Dark patterns detected
    
    Severity levels:
    - info: Minor expected variation
    - warning: Noteworthy change
    - critical: Significant drift or manipulation
    """
    
    def __init__(self, drift_type: str, severity: str, details: Dict[str, Any], 
                 location: Optional[str] = None, change_type: Optional[str] = None):
        self.drift_type = drift_type
        self.severity = severity
        self.details = details
        self.location = location
        self.change_type = change_type
        self.timestamp = time.time()
        self.event_id = self._generate_event_id()
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID."""
        import hashlib
        data = f"{self.drift_type}:{self.severity}:{self.timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        result = {
            "event_id": self.event_id,
            "drift_type": self.drift_type,
            "severity": self.severity,
            "details": self.details,
            "timestamp": self.timestamp
        }
        if self.location is not None:
            result["location"] = self.location
        if self.change_type is not None:
            result["change_type"] = self.change_type
        return result
    
    def __repr__(self) -> str:
        return f"DriftEvent({self.drift_type}, {self.severity}, id={self.event_id})"
    
    def is_critical(self) -> bool:
        """Check if event is critical severity."""
        return self.severity == "critical"
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the event."""
        summary_parts = [
            f"[{self.severity.upper()}]",
            f"Drift Type: {self.drift_type}"
        ]
        
        # Add key details
        if "screen_id" in self.details:
            summary_parts.append(f"Screen: {self.details['screen_id']}")
        
        if "transition" in self.details:
            summary_parts.append(f"Transition: {self.details['transition']}")
        
        if "similarity" in self.details:
            similarity = self.details['similarity']
            summary_parts.append(f"Similarity: {similarity:.1%}")
        
        return " | ".join(summary_parts)
    
    @classmethod
    def create_layout_drift(cls, screen_id: str, similarity: float, 
                           diff_summary: str) -> 'DriftEvent':
        """Create a layout drift event."""
        severity = "critical" if similarity < 0.7 else "warning" if similarity < 0.9 else "info"
        
        return cls(
            drift_type="layout",
            severity=severity,
            details={
                "screen_id": screen_id,
                "similarity": similarity,
                "diff_summary": diff_summary
            }
        )
    
    @classmethod
    def create_content_drift(cls, screen_id: str, changes: Dict[str, Any]) -> 'DriftEvent':
        """Create a content drift event."""
        return cls(
            drift_type="content",
            severity="info",
            details={
                "screen_id": screen_id,
                "changes": changes
            }
        )
    
    @classmethod
    def create_sequence_drift(cls, invalid_transition: str, 
                             expected: list) -> 'DriftEvent':
        """Create a sequence/transition drift event."""
        return cls(
            drift_type="sequence",
            severity="warning",
            details={
                "invalid_transition": invalid_transition,
                "expected_transitions": expected
            }
        )
    
    @classmethod
    def create_manipulative_drift(cls, pattern_type: str, 
                                 description: str, flow: list) -> 'DriftEvent':
        """Create a manipulative pattern drift event."""
        return cls(
            drift_type="manipulative",
            severity="critical",
            details={
                "pattern_type": pattern_type,
                "description": description,
                "flow": flow
            }
        )
