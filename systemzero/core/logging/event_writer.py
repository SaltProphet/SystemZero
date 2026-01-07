"""Write events to immutable log."""
from typing import Any, Optional, TextIO
import json
import time


class EventWriter:
    """Writes events to a log file with optional formatting.
    
    Supports:
    - JSON line format (one JSON object per line)
    - Append-only writes
    - Automatic flushing
    - Buffering for performance
    """
    
    def __init__(self, log_file: Optional[str] = None, auto_flush: bool = True):
        self.log_file = log_file
        self.auto_flush = auto_flush
        self._file_handle: Optional[TextIO] = None
        self._write_count = 0
        
        if log_file:
            self._open_file()
    
    def _open_file(self):
        """Open log file in append mode."""
        if self.log_file:
            self._file_handle = open(self.log_file, 'a', encoding='utf-8')
    
    def write(self, event: Any) -> bool:
        """Write an event to the log.
        
        Args:
            event: Event object to write (must be serializable)
            
        Returns:
            True if write successful
        """
        if not self._file_handle and not self.log_file:
            # No file configured, skip
            return False
        
        if not self._file_handle:
            self._open_file()
        
        try:
            # Convert event to dict if it has to_dict method
            if hasattr(event, 'to_dict'):
                event_dict = event.to_dict()
            elif isinstance(event, dict):
                event_dict = event
            else:
                event_dict = {"data": str(event), "timestamp": time.time()}
            
            # Enrich with timestamp and entry_id if missing
            if isinstance(event_dict, dict):
                if 'timestamp' not in event_dict:
                    event_dict['timestamp'] = time.time()
                if 'entry_id' not in event_dict:
                    # Use a simple incrementing id for this writer instance
                    event_dict['entry_id'] = f"evt_{self._write_count+1}"
            
            # Write as JSON line
            json_line = json.dumps(event_dict, separators=(',', ':'))
            self._file_handle.write(json_line + '\n')
            
            self._write_count += 1
            
            if self.auto_flush:
                self._file_handle.flush()
            
            return True
        
        except Exception as e:
            print(f"EventWriter error: {e}")
            return False
    
    def write_batch(self, events: list) -> int:
        """Write multiple events.
        
        Args:
            events: List of events to write
            
        Returns:
            Number of events successfully written
        """
        success_count = 0
        for event in events:
            if self.write(event):
                success_count += 1
        return success_count
    
    def flush(self):
        """Flush buffered writes to disk."""
        if self._file_handle:
            self._file_handle.flush()
    
    def close(self):
        """Close the log file."""
        if self._file_handle:
            self._file_handle.flush()
            self._file_handle.close()
            self._file_handle = None
    
    def get_write_count(self) -> int:
        """Get number of events written."""
        return self._write_count
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def __del__(self):
        """Cleanup on deletion."""
        self.close()
