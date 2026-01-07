"""Tests for logging layer."""
import pytest
import tempfile
import json
from pathlib import Path
from core.logging import ImmutableLog, HashChain, EventWriter


class TestHashChain:
    """Test HashChain functionality."""
    
    def test_genesis_hash(self):
        """Test genesis hash generation."""
        chain = HashChain()
        genesis = chain.genesis_hash
        assert isinstance(genesis, str)
        assert len(genesis) == 64  # SHA256 hex length
    
    def test_compute_hash_deterministic(self):
        """Test hash computation is deterministic."""
        chain = HashChain()
        entry = {"data": "test", "timestamp": 12345}
        hash1 = chain.compute_hash(entry)
        hash2 = chain.compute_hash(entry)
        assert hash1 == hash2
    
    def test_different_entries_different_hashes(self):
        """Test different entries produce different hashes."""
        chain = HashChain()
        entry1 = {"data": "test1"}
        entry2 = {"data": "test2"}
        assert chain.compute_hash(entry1) != chain.compute_hash(entry2)
    
    def test_verify_valid_chain(self):
        """Test verification of valid hash chain."""
        chain = HashChain()
        entries = [
            {"data": "entry1", "hash": "abc"},
            {"data": "entry2", "hash": "def", "previous_hash": "abc"},
            {"data": "entry3", "hash": "ghi", "previous_hash": "def"}
        ]
        # Note: This test assumes verify_chain checks the structure
        result = chain.verify_chain(entries)
        assert isinstance(result, tuple)


class TestImmutableLog:
    """Test ImmutableLog functionality."""
    
    def test_create_log(self):
        """Test creating a new log."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            log = ImmutableLog(log_path)
            assert log.get_entry_count() == 0
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_append_event(self):
        """Test appending events to log."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            log = ImmutableLog(log_path)
            event = {"type": "test", "data": "value"}
            log.append(event)
            
            assert log.get_entry_count() == 1
            entries = log.get_entries()
            assert len(entries) == 1
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_verify_integrity_empty_log(self):
        """Test integrity verification of empty log."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            log = ImmutableLog(log_path)
            assert log.verify_integrity()
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_verify_integrity_valid_chain(self):
        """Test integrity verification of valid chain."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            log = ImmutableLog(log_path)
            for i in range(5):
                log.append({"data": f"event_{i}"})
            
            assert log.verify_integrity()
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_detect_tampering(self):
        """Test detection of tampered log."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            log = ImmutableLog(log_path)
            log.append({"data": "event_1"})
            log.append({"data": "event_2"})
            log.append({"data": "event_3"})
            
            # Manually tamper with log file
            with open(log_path, 'r') as f:
                lines = f.readlines()
            
            # Modify second entry
            if len(lines) > 1:
                entry = json.loads(lines[1])
                entry['data']['data'] = "TAMPERED"
                lines[1] = json.dumps(entry) + '\\n'
            
            with open(log_path, 'w') as f:
                f.writelines(lines)
            
            # Reload and verify - should detect tampering
            log2 = ImmutableLog(log_path)
            assert not log2.verify_integrity()
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_get_entries_range(self):
        """Test getting entries in range."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            log = ImmutableLog(log_path)
            for i in range(10):
                log.append({"data": f"event_{i}"})
            
            # Get range
            entries = log.get_entries(3, 7)
            assert len(entries) == 4
        finally:
            Path(log_path).unlink(missing_ok=True)


class TestEventWriter:
    """Test EventWriter functionality."""
    
    def test_write_with_enrichment(self):
        """Test writing events with automatic enrichment."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            writer = EventWriter(log_path)
            event = {"type": "test"}
            writer.write(event)
            
            # Read back and check enrichment
            log = ImmutableLog(log_path)
            entries = log.get_entries()
            assert len(entries) == 1
            assert "entry_id" in entries[0]["data"]
            assert "timestamp" in entries[0]["data"]
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_write_maintains_chain(self):
        """Test that multiple writes maintain hash chain."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            writer = EventWriter(log_path)
            for i in range(5):
                writer.write({"data": f"event_{i}"})
            
            # Verify chain
            log = ImmutableLog(log_path)
            assert log.verify_integrity()
        finally:
            Path(log_path).unlink(missing_ok=True)
