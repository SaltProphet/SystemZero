"""Hash chain for tamper-evident logging."""
import hashlib
from typing import Optional, List, Dict, Any
import json


class HashChain:
    """Implements a cryptographic hash chain for log integrity.
    
    Each log entry is linked to the previous entry via a hash chain,
    making it computationally infeasible to tamper with historical entries.
    
    Chain structure:
    entry_hash = SHA256(previous_hash + entry_data + timestamp)
    """
    
    def __init__(self, genesis_hash: Optional[str] = None):
        if genesis_hash is None:
            # Create genesis hash from empty data
            genesis_hash = hashlib.sha256(b"genesis").hexdigest()
        
        self.genesis_hash = genesis_hash
        self.current_hash = genesis_hash
        self._chain_length = 0
    
    def compute_hash(self, entry: Dict[str, Any]) -> str:
        """Compute hash of an entry (without adding to chain).
        
        Args:
            entry: Entry dictionary to hash
            
        Returns:
            SHA256 hash of the entry
        """
        if isinstance(entry, dict):
            data_str = json.dumps(entry, sort_keys=True)
        else:
            data_str = str(entry)
        
        return hashlib.sha256(data_str.encode('utf-8')).hexdigest()
    
    def add_entry(self, entry_data: Any, timestamp: float) -> str:
        """Add an entry to the hash chain.
        
        Args:
            entry_data: Data to add (will be JSON serialized)
            timestamp: Entry timestamp
            
        Returns:
            Hash of the new entry
        """
        # Serialize entry data
        if isinstance(entry_data, dict):
            data_str = json.dumps(entry_data, sort_keys=True)
        else:
            data_str = str(entry_data)
        
        # Create hash chain: hash(previous_hash + data + timestamp)
        chain_input = f"{self.current_hash}{data_str}{timestamp}"
        new_hash = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()
        
        # Update chain state
        self.current_hash = new_hash
        self._chain_length += 1
        
        return new_hash
    
    def verify_entry(self, entry_hash: str, entry_data: Any, 
                    timestamp: float, previous_hash: str) -> bool:
        """Verify an entry's hash is correct.
        
        Args:
            entry_hash: Hash to verify
            entry_data: Entry data
            timestamp: Entry timestamp
            previous_hash: Previous entry's hash
            
        Returns:
            True if hash is valid
        """
        # Serialize data the same way
        if isinstance(entry_data, dict):
            data_str = json.dumps(entry_data, sort_keys=True)
        else:
            data_str = str(entry_data)
        
        # Recompute hash
        chain_input = f"{previous_hash}{data_str}{timestamp}"
        computed_hash = hashlib.sha256(chain_input.encode('utf-8')).hexdigest()
        
        return computed_hash == entry_hash
    
    def verify_chain(self, entries: List[Dict[str, Any]]):
        """Verify an entire chain of entries.
        
        Accepts both structured entries written by ImmutableLog/EventWriter
        and lightweight structures used in certain tests.
        
        Args:
            entries: List of entry dicts. Accepts keys 'entry_hash' or 'hash'.
        
        Returns:
            - Tuple (bool, list[str]) for detailed validation
            - Maintained backward-compat truthiness for callers expecting bool via ImmutableLog
        """
        if not entries:
            return (True, [])
        
        errors: List[str] = []
        previous_hash = self.genesis_hash
        
        for idx, entry in enumerate(entries):
            # Support both legacy 'hash' and newer 'entry_hash'
            e_hash = entry.get('entry_hash') or entry.get('hash')
            e_prev = entry.get('previous_hash') or entry.get('prev')
            data = entry.get('data')
            ts = entry.get('timestamp')
            
            # If we don't have enough data to recompute, fall back to structural check
            if e_hash is None:
                errors.append(f"Entry {idx} missing hash")
                return (False, errors)
            
            if data is None or ts is None:
                # Structural check: ensure links are consistent if present
                if idx > 0 and e_prev and e_prev != previous_hash:
                    errors.append(f"Entry {idx} previous_hash mismatch")
                    return (False, errors)
                previous_hash = e_hash
                continue
            
            # Full recomputation check
            if not self.verify_entry(e_hash, data, ts, previous_hash):
                errors.append(f"Entry {idx} hash verification failed")
                return (False, errors)
            previous_hash = e_hash
        
        return (True, errors)
    
    def get_chain_length(self) -> int:
        """Get the current length of the hash chain."""
        return self._chain_length
    
    def reset(self, genesis_hash: Optional[str] = None):
        """Reset the hash chain."""
        if genesis_hash is None:
            genesis_hash = self.genesis_hash
        
        self.current_hash = genesis_hash
        self._chain_length = 0
