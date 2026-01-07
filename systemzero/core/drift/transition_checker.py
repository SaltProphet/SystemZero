"""Validate UI state transitions against templates."""
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass


@dataclass
class TransitionResult:
    """Result of a transition check."""
    is_valid: bool
    reason: Optional[str] = None
    expected: Optional[List[str]] = None
    actual: Optional[str] = None


class TransitionChecker:
    """Validates state transitions against baseline templates.
    
    Detects:
    - Invalid state transitions
    - Unexpected screen changes
    - Manipulative dark patterns (forced flows)
    - Missing expected transitions
    """
    
    def __init__(self):
        self._transition_history: List[Tuple[str, str, float]] = []
        self._max_history = 100
    
    def check_transition(self, from_id: str, to_id: str, 
                        templates: Optional[Dict[str, Dict[str, Any]]] = None) -> TransitionResult:
        """Check if a transition is valid according to templates.
        
        Args:
            from_id: Source screen ID (or template dict for backward compat)
            to_id: Target screen ID
            templates: Optional dict of screen_id -> template mappings
            
        Returns:
            TransitionResult with validation info
        """
        # Handle backward compatibility: if from_id is a dict, it's the old calling style
        if isinstance(from_id, dict):
            from_template = from_id
            if not from_template:
                return TransitionResult(
                    is_valid=True,
                    reason="No source template (initial state)"
                )
            
            from_screen_id = from_template.get("screen_id", "unknown")
            valid_transitions = from_template.get("valid_transitions", [])
            
            # Empty valid_transitions means any transition is allowed
            if not valid_transitions:
                return TransitionResult(
                    is_valid=True,
                    reason="No transition restrictions"
                )
            
            # Check if transition is in the valid list
            for valid_transition in valid_transitions:
                if valid_transition == to_id:
                    return TransitionResult(
                        is_valid=True,
                        expected=valid_transitions,
                        actual=to_id
                    )
            
            # Transition not found in valid list
            return TransitionResult(
                is_valid=False,
                reason=f"Unexpected transition: {from_screen_id} -> {to_id}",
                expected=valid_transitions,
                actual=to_id
            )
        
        # New calling style: from_id and to_id are strings, templates is dict
        if templates is None:
            templates = {}
        
        # Get source template
        from_template = templates.get(from_id)
        if not from_template:
            return TransitionResult(
                is_valid=True,
                reason="Source template not found"
            )
        
        valid_transitions = from_template.get("valid_transitions", [])
        
        # Check if transition is allowed
        if to_id in valid_transitions:
            return TransitionResult(
                is_valid=True,
                expected=valid_transitions,
                actual=to_id
            )
        
        expected_transition = f"{from_id} -> {to_id}"
        
        return TransitionResult(
            is_valid=False,
            reason=f"Unexpected transition: {expected_transition}",
            expected=valid_transitions,
            actual=to_id
        )
    
    def is_allowed(self, template: Dict[str, Any], to_screen_id: str) -> bool:
        """Check if a transition is allowed (convenience method).
        
        Args:
            template: Source template
            to_screen_id: Target screen ID
            
        Returns:
            True if transition is allowed
        """
        result = self.check_transition(template, to_screen_id)
        return result.is_valid
    
    def record_transition(self, from_screen_id: str, to_screen_id: str, 
                         timestamp: float) -> None:
        """Record a transition in history.
        
        Args:
            from_screen_id: Source screen ID
            to_screen_id: Target screen ID
            timestamp: When transition occurred
        """
        self._transition_history.append((from_screen_id, to_screen_id, timestamp))
        
        # Limit history size
        if len(self._transition_history) > self._max_history:
            self._transition_history.pop(0)
    
    def get_transition_history(self, count: int = 10) -> List[Tuple[str, str, float]]:
        """Get recent transition history.
        
        Args:
            count: Number of recent transitions to return
            
        Returns:
            List of (from_screen_id, to_screen_id, timestamp) tuples
        """
        return self._transition_history[-count:]
    
    def detect_loops(self, window: int = 5) -> List[List[str]]:
        """Detect transition loops that might indicate dark patterns.
        
        Args:
            window: Number of recent transitions to analyze
            
        Returns:
            List of detected loops (each loop is a list of screen IDs)
        """
        if len(self._transition_history) < 3:
            return []
        
        recent = self._transition_history[-window:]
        loops = []
        
        # Look for repeated sequences
        for i in range(len(recent) - 2):
            for j in range(i + 2, len(recent)):
                sequence = [t[0] for t in recent[i:j]]
                # Check if sequence repeats
                if self._is_repeating_sequence(sequence, recent[i:]):
                    loops.append(sequence)
        
        return loops
    
    def detect_forced_flow(self, templates: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Detect if user is being forced through a specific flow.
        
        A forced flow is when:
        - User has no backward navigation
        - Each screen has only one valid transition
        - Flow is longer than expected
        
        Returns:
            Dict describing the forced flow, or None if not detected
        """
        if len(self._transition_history) < 3:
            return None
        
        recent = self._transition_history[-5:]
        flow = [t[0] for t in recent] + [recent[-1][1]]
        
        # Check if each screen in flow has limited options
        forced = True
        for screen_id in flow[:-1]:
            template = templates.get(screen_id)
            if not template:
                continue
            
            valid_transitions = template.get("valid_transitions", [])
            # If more than one transition available, not forced
            if len(valid_transitions) != 1:
                forced = False
                break
        
        if forced and len(flow) >= 3:
            return {
                "type": "forced_flow",
                "flow": flow,
                "length": len(flow),
                "description": "User appears to be in a forced navigation flow"
            }
        
        return None
    
    def validate_transition_graph(self, templates: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
        """Validate that all transition references point to valid screens.
        
        Args:
            templates: Dict of all templates
            
        Returns:
            Dict of errors found (screen_id -> list of error messages)
        """
        errors = {}
        
        for screen_id, template in templates.items():
            screen_errors = []
            
            valid_transitions = template.get("valid_transitions", [])
            for transition in valid_transitions:
                if not transition or " -> " not in transition:
                    continue
                
                # Parse transition
                parts = transition.split(" -> ")
                if len(parts) != 2:
                    screen_errors.append(f"Invalid transition format: {transition}")
                    continue
                
                target_screen = parts[1]
                if target_screen not in templates:
                    screen_errors.append(f"Transition references unknown screen: {target_screen}")
            
            if screen_errors:
                errors[screen_id] = screen_errors
        
        return errors
    
    def _is_repeating_sequence(self, sequence: List[str], history: List[Tuple]) -> bool:
        """Check if a sequence repeats in history."""
        if len(sequence) < 2:
            return False
        
        # Convert history to screen IDs
        screen_ids = [t[0] for t in history]
        
        # Count occurrences of sequence
        count = 0
        for i in range(len(screen_ids) - len(sequence) + 1):
            if screen_ids[i:i+len(sequence)] == sequence:
                count += 1
        
        return count >= 2
