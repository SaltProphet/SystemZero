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
    
    def verify_chain(self, entries: List[Dict[str, Any]]) -> bool:
        """Verify an entire chain of entries.
        
        Args:
            entries: List of entry dicts with 'entry_hash', 'data', 'timestamp'
            
        Returns:
            True if entire chain is valid
        """
        if not entries:
            return True
        
        previous_hash = self.genesis_hash
        
        for entry in entries:
            if not self.verify_entry(
                entry['entry_hash'],
                entry['data'],
                entry['timestamp'],
                previous_hash
            ):
                return False
            previous_hash = entry['entry_hash']
        
        return True
    
    def get_chain_length(self) -> int:
        """Get the current length of the hash chain."""
        return self._chain_length
    
    def reset(self, genesis_hash: Optional[str] = None):
        """Reset the hash chain."""
        if genesis_hash is None:
            genesis_hash = self.genesis_hash
        
        self.current_hash = genesis_hash
        self._chain_length = 0
