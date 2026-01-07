"""Accessibility event listener for UI changes."""
import threading
import time
from typing import Optional, Callable


class AccessibilityListener:
    """Listens for accessibility events and forwards them to an event stream.
    
    This monitors system accessibility events like:
    - Window focus changes
    - UI element state changes
    - Text content changes
    - Layout modifications
    """
    
    def __init__(self, event_stream, poll_interval: float = 0.5):
        self.event_stream = event_stream
        self.poll_interval = poll_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._on_event_callback: Optional[Callable] = None
    
    def start(self) -> None:
        """Start listening for accessibility events."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop listening for accessibility events."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def on_event(self, raw_event: dict) -> None:
        """Process and forward a raw accessibility event.
        
        Args:
            raw_event: Raw event data from accessibility API
        """
        # Enrich event with metadata
        enriched_event = {
            "type": raw_event.get("type", "unknown"),
            "timestamp": time.time(),
            "source": raw_event.get("source", "accessibility_api"),
            "data": raw_event
        }
        
        # Push to event stream
        self.event_stream.push(enriched_event)
        
        # Call custom callback if registered
        if self._on_event_callback:
            try:
                self._on_event_callback(enriched_event)
            except Exception as e:
                print(f"Event callback error: {e}")
    
    def set_callback(self, callback: Callable) -> None:
        """Register a callback to be called on each event."""
        self._on_event_callback = callback
    
    def _listen_loop(self) -> None:
        """Main listening loop (runs in background thread).
        
        In a real implementation, this would register with the
        system accessibility API. For now, it generates mock events.
        """
        while self._running:
            try:
                # Mock event generation
                # Real implementation would poll/listen to OS accessibility events
                mock_event = {
                    "type": "window_focus",
                    "source": "accessibility_api",
                    "window_title": "Mock Application"
                }
                self.on_event(mock_event)
                
                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"Listener loop error: {e}")
                time.sleep(1.0)
