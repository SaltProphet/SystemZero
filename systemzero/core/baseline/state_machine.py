"""State machine for managing UI state transitions."""
from typing import List, Dict, Any, Optional, Tuple


class StateMachine:
    """Manages UI state transitions and validates state flows.
    
    Tracks state history and validates transitions against template definitions.
    """
    
    def __init__(self):
        """Initialize state machine."""
        self.current_state: Optional[str] = None
        self.state_history: List[Tuple[str, str]] = []
    
    def transition(self, from_id: str, to_id: str) -> None:
        """Record a state transition.
        
        Args:
            from_id: Source state ID
            to_id: Target state ID
        """
        self.state_history.append((from_id, to_id))
        self.current_state = to_id
    
    def is_valid_transition(self, template: Dict[str, Any], to_screen_id: str) -> bool:
        """Check if a transition is valid according to template.
        
        Args:
            template: Template dictionary with valid_transitions
            to_screen_id: Target screen ID to validate
            
        Returns:
            True if transition is valid
        """
        if not template:
            return True
        
        valid_transitions = template.get("valid_transitions", [])
        
        # Empty list means any transition is allowed
        if not valid_transitions:
            return True
        
        # Check if target is in valid transitions
        return to_screen_id in valid_transitions
    
    def get_history(self, count: int = 10) -> List[Tuple[str, str]]:
        """Get recent state history.
        
        Args:
            count: Number of recent transitions to return
            
        Returns:
            List of (from_id, to_id) tuples
        """
        return self.state_history[-count:]
    
    def reset(self) -> None:
        """Reset state machine to initial state."""
        self.current_state = None
        self.state_history = []
    
    # Alias for compatibility
    @property
    def history(self):
        """Alias for state_history for test compatibility."""
        return self.state_history
