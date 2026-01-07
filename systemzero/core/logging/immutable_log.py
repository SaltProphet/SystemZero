"""Immutable append-only log with hash chain integrity."""
from typing import Optional, List, Dict, Any
import json
from pathlib import Path
import time

from .hash_chain import HashChain
from .event_writer import EventWriter


class ImmutableLog:
    """Immutable append-only log with cryptographic integrity.
    
    Features:
    - Append-only (no modifications or deletions)
    - Hash chain for tamper detection
    - JSON line format for easy parsing
    - Automatic integrity verification
    """
    
    def __init__(self, path: str, verify_on_load: bool = True):
        self.path = Path(path)
        self.verify_on_load = verify_on_load
        self._load_error = False
        
        # Initialize hash chain
        self.hash_chain = HashChain()
        
        # Initialize writer
        self.writer = EventWriter(str(self.path), auto_flush=True)
        
        # Load existing entries if file exists
        self._entries: List[Dict[str, Any]] = []
        if self.path.exists():
            self._load_existing()
    
    def append(self, event: Any) -> str:
        """Append an event to the log.
        
        Args:
            event: Event to append (will be converted to dict)
            
        Returns:
            Hash of the appended entry
        """
        # Convert event to dict
        if hasattr(event, 'to_dict'):
            event_dict = event.to_dict()
        elif isinstance(event, dict):
            event_dict = event
        else:
            event_dict = {"data": str(event)}
        
        # Get timestamp
        timestamp = event_dict.get('timestamp', time.time())
        
        # Generate hash chain entry
        previous_hash = self.hash_chain.current_hash
        entry_hash = self.hash_chain.add_entry(event_dict, timestamp)
        
        # Create log entry with hash
        log_entry = {
            "entry_hash": entry_hash,
            "previous_hash": previous_hash if self._entries else self.hash_chain.genesis_hash,
            "timestamp": timestamp,
            "data": event_dict
        }
        
        # Write to file
        self.writer.write(log_entry)
        
        # Add to in-memory cache
        self._entries.append(log_entry)
        
        return entry_hash
    
    def verify_integrity(self) -> bool:
        """Verify the integrity of the entire log.
        
        Returns:
            True if log integrity is valid
        """
        if self._load_error:
            return False
        result = self.hash_chain.verify_chain(self._entries)
        if isinstance(result, tuple):
            return bool(result[0])
        return bool(result)
    
    def get_entries(self, start: int = 0, end: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get log entries.
        
        Args:
            start: Start index
            end: End index (None = all)
            
        Returns:
            List of log entries
        """
        if end is None:
            return self._entries[start:]
        return self._entries[start:end]
    
    def get_entry_by_hash(self, entry_hash: str) -> Optional[Dict[str, Any]]:
        """Find an entry by its hash.
        
        Args:
            entry_hash: Hash to search for
            
        Returns:
            Entry dict or None if not found
        """
        for entry in self._entries:
            if entry.get('entry_hash') == entry_hash:
                return entry
        return None
    
    def get_entry_count(self) -> int:
        """Get total number of entries in log."""
        return len(self._entries)
    
    def search(self, **criteria) -> List[Dict[str, Any]]:
        """Search log entries by criteria.
        
        Args:
            **criteria: Key-value pairs to match in event data
            
        Returns:
            List of matching entries
        """
        matches = []
        for entry in self._entries:
            event_data = entry.get('data', {})
            if all(event_data.get(k) == v for k, v in criteria.items()):
                matches.append(entry)
        return matches
    
    def _load_existing(self):
        """Load existing log entries from file."""
        if not self.path.exists():
            return
        
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        entry = json.loads(line)
                        # Normalize: if raw event dict (no 'data' key), wrap it
                        if isinstance(entry, dict) and 'data' not in entry:
                            normalized = {"data": entry}
                        else:
                            normalized = entry
                        self._entries.append(normalized)
                        
                        # Update hash chain state
                        if 'entry_hash' in normalized:
                            self.hash_chain.current_hash = normalized['entry_hash']
                            self.hash_chain._chain_length += 1
                    
                    except json.JSONDecodeError as e:
                        print(f"Error parsing log entry: {e}")
                        self._load_error = True
            
            # Verify integrity if requested
            if self.verify_on_load and not self.verify_integrity():
                print(f"WARNING: Log integrity verification failed for {self.path}")
        
        except Exception as e:
            print(f"Error loading log: {e}")

    def read_all(self) -> List[Dict[str, Any]]:
        """Return all log entries in order.
        
        Provided for UI components expecting a simple accessor.
        """
        return list(self._entries)
    
    def close(self):
        """Close the log."""
        self.writer.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
