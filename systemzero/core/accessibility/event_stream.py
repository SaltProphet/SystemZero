"""Event stream for accessibility events."""
from collections import deque
from typing import Any, Optional
import threading


class EventStream:
    """Thread-safe event stream for UI accessibility events."""
    
    def __init__(self, maxlen: Optional[int] = 1000):
        self._events = deque(maxlen=maxlen)
        self._lock = threading.Lock()
        self._listeners = []
    
    def push(self, event: Any) -> None:
        """Add an event to the stream."""
        with self._lock:
            self._events.append(event)
            # Notify listeners
            for listener in self._listeners:
                try:
                    listener(event)
                except Exception as e:
                    print(f"EventStream listener error: {e}")
    
    def subscribe(self, callback) -> None:
        """Subscribe a callback to receive events."""
        with self._lock:
            self._listeners.append(callback)
    
    def get_recent(self, count: int = 10) -> list:
        """Get the most recent N events."""
        with self._lock:
            return list(self._events)[-count:]
    
    def clear(self) -> None:
        """Clear all events from the stream."""
        with self._lock:
            self._events.clear()
