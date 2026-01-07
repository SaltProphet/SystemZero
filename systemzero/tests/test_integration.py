"""Integration tests for full pipeline."""
import pytest
import tempfile
from pathlib import Path
from tests.helpers import run_pipeline, create_test_log, verify_log_integrity
from tests.fixtures.mock_trees import DISCORD_CHAT_TREE, DOORDASH_OFFER_TREE, LOGIN_FORM_TREE
from tests.fixtures.drift_scenarios import MISSING_BUTTON_DRIFT, CONTENT_CHANGE_DRIFT
from core.logging import ImmutableLog, EventWriter


class TestFullPipeline:
    """Test complete end-to-end pipeline."""
    
    def test_pipeline_with_discord_tree(self):
        """Test pipeline with Discord chat tree."""
        results = run_pipeline(DISCORD_CHAT_TREE)
        
        assert results is not None
        assert "normalized_tree" in results
        assert "signature" in results
        assert len(results["signature"]) == 64  # SHA256 length
    
    def test_pipeline_with_doordash_tree(self):
        """Test pipeline with DoorDash tree."""
        results = run_pipeline(DOORDASH_OFFER_TREE)
        
        assert results is not None
        assert results["normalized_tree"] is not None
    
    def test_pipeline_detects_drift(self):
        """Test pipeline detects drift in modified tree."""
        original, modified = MISSING_BUTTON_DRIFT
        
        results = run_pipeline(modified)
        
        # Should have low match score or detect drift
        assert "match_score" in results
    
    def test_pipeline_generates_signature(self):
        """Test pipeline generates signatures."""
        results = run_pipeline(LOGIN_FORM_TREE)
        
        assert "signature" in results
        sig = results["signature"]
        assert isinstance(sig, str)
        assert len(sig) == 64
    
    def test_pipeline_with_templates(self):
        """Test pipeline with template matching."""
        from tests.fixtures.templates import generate_template
        
        template = generate_template(DISCORD_CHAT_TREE, "discord_chat")
        results = run_pipeline(DISCORD_CHAT_TREE, templates=[template])
        
        assert "best_match" in results
        assert "match_score" in results
        if results["best_match"]:
            assert results["match_score"] > 0.5


class TestLogIntegration:
    """Test log writing and reading integration."""
    
    def test_write_and_read_log(self):
        """Test writing events and reading them back."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            # Create log and write events
            log = create_test_log(log_path, event_count=10)
            
            # Read back
            entries = log.get_entries()
            assert len(entries) == 10
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_log_integrity_verification(self):
        """Test hash chain integrity verification."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            log = create_test_log(log_path, event_count=5)
            
            # Verify integrity
            is_valid = verify_log_integrity(log_path)
            assert is_valid
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_event_writer_integration(self):
        """Test EventWriter with hash chain."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            writer = EventWriter(log_path)
            
            # Write multiple events
            for i in range(5):
                writer.write({"event_type": "test", "id": i})
            
            # Verify chain
            log = ImmutableLog(log_path)
            assert log.verify_integrity()
            assert log.get_entry_count() == 5
        finally:
            Path(log_path).unlink(missing_ok=True)


class TestDriftDetectionIntegration:
    """Test drift detection in full pipeline."""
    
    def test_missing_button_detection(self):
        """Test detection of missing UI elements."""
        original, modified = MISSING_BUTTON_DRIFT
        from tests.fixtures.templates import generate_template
        
        # Create template from original
        template = generate_template(original, "original")
        
        # Run pipeline on modified
        results = run_pipeline(modified, templates=[template])
        
        # Should detect drift or have low match score
        assert results["match_score"] < 1.0
    
    def test_content_change_detection(self):
        """Test detection of content changes."""
        original, modified = CONTENT_CHANGE_DRIFT
        from tests.fixtures.templates import generate_template
        from core.normalization import SignatureGenerator
        
        # Generate signatures
        gen = SignatureGenerator()
        sig_original = gen.generate_content(original)
        sig_modified = gen.generate_content(modified)
        
        # Content signatures should differ
        assert sig_original != sig_modified


class TestEndToEnd:
    """Full end-to-end system tests."""
    
    def test_capture_normalize_match_log(self):
        """Test complete flow: capture → normalize → match → log."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            from core.accessibility import TreeCapture
            from core.normalization import TreeNormalizer, SignatureGenerator
            from core.baseline import TemplateLoader
            from core.drift import Matcher
            from core.logging import EventWriter
            
            # 1. Capture (use mock)
            capture = TreeCapture()
            tree = capture.capture()
            
            # 2. Normalize
            normalizer = TreeNormalizer()
            normalized = normalizer.normalize(tree)
            
            # 3. Generate signature
            sig_gen = SignatureGenerator()
            signature = sig_gen.generate(normalized)
            
            # 4. Match against templates
            loader = TemplateLoader()
            templates = loader.load_all()
            if templates:
                matcher = Matcher()
                best_match, score = matcher.find_best_match(normalized, list(templates.values()))
            
            # 5. Log event
            writer = EventWriter(log_path)
            writer.write({
                "event_type": "tree_captured",
                "signature": signature,
                "timestamp": tree["timestamp"]
            })
            
            # Verify log
            log = ImmutableLog(log_path)
            assert log.get_entry_count() == 1
            assert log.verify_integrity()
        finally:
            Path(log_path).unlink(missing_ok=True)
    
    def test_multiple_captures_with_drift(self):
        """Test multiple captures with drift injection."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_path = f.name
        
        try:
            writer = EventWriter(log_path)
            
            # Capture normal tree
            results1 = run_pipeline(DISCORD_CHAT_TREE)
            writer.write({"capture": 1, "signature": results1["signature"]})
            
            # Capture modified tree (with drift)
            _, modified = MISSING_BUTTON_DRIFT
            results2 = run_pipeline(modified)
            writer.write({"capture": 2, "signature": results2["signature"]})
            
            # Verify log integrity
            log = ImmutableLog(log_path)
            assert log.get_entry_count() == 2
            assert log.verify_integrity()
            
            # Signatures should differ
            entries = log.get_entries()
            assert entries[0]["data"]["signature"] != entries[1]["data"]["signature"]
        finally:
            Path(log_path).unlink(missing_ok=True)
