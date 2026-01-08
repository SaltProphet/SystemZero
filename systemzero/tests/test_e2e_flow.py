"""End-to-end test: capture → normalize → template → match → log workflow."""
import pytest
from pathlib import Path
import json

from core.accessibility import TreeCapture
from core.normalization import TreeNormalizer, SignatureGenerator
from core.baseline import TemplateLoader, TemplateValidator
from core.drift import Matcher, DriftEvent
from core.logging import ImmutableLog
from extensions.template_builder.builder import TemplateBuilder


class TestE2EFlow:
    """Test complete workflow from capture to logging."""
    
    def test_full_capture_to_log_workflow(self, tmp_path):
        """Test: capture tree → normalize → match template → detect drift → log event."""
        # Step 1: Capture (mock)
        tree_capture = TreeCapture()
        raw_tree = tree_capture.capture()
        assert raw_tree is not None
        assert 'root' in raw_tree  # TreeCapture returns dict with 'root' key
        
        # Step 2: Normalize
        normalizer = TreeNormalizer()
        normalized_tree = normalizer.normalize(raw_tree['root'])
        assert 'name' in normalized_tree
        
        # Step 3: Generate signature
        sig_gen = SignatureGenerator()
        signature = sig_gen.generate(normalized_tree)
        assert len(signature) == 64  # SHA256 hex length
        
        # Step 4: Load templates
        loader = TemplateLoader()
        templates = loader.load_all()
        assert len(templates) > 0
        
        # Step 5: Match against templates
        matcher = Matcher(similarity_threshold=0.7)
        best_match, score = matcher.find_best_match(normalized_tree, list(templates.values()))
        
        # Step 6: Detect drift if no match
        if best_match is None or score < 0.8:
            drift_event = DriftEvent(
                "layout",
                "warning",
                {"signature": signature, "score": score if score else 0.0}
            )
            
            # Step 7: Log to immutable log
            log_path = tmp_path / "test_e2e.log"
            log = ImmutableLog(str(log_path))
            log.append(drift_event.to_dict())
            
            # Verify log integrity
            entries = log.get_entries(0, 1)
            assert len(entries) == 1
            assert entries[0]['data']['drift_type'] == "layout"
            
            # Verify hash chain
            is_valid = log.verify_integrity()
            assert is_valid
    
    def test_template_building_workflow(self, tmp_path):
        """Test: capture → build template → validate → match."""
        # Step 1: Create sample capture with proper structure
        capture_data = {
            "normalized": {
                "root": {
                    "name": "test_app",
                    "role": "window",
                    "children": [
                        {"name": "button_submit", "role": "button"},
                        {"name": "input_field", "role": "textbox"}
                    ]
                }
            },
            "signatures": {
                "structural": "abc123"
            }
        }
        
        # Step 2: Build template using capture file
        capture_path = tmp_path / "test_capture.json"
        import json
        capture_path.write_text(json.dumps(capture_data))
        
        builder = TemplateBuilder()
        from pathlib import Path
        template = builder.build_from_capture(Path(capture_path), "test_screen")
        assert template['screen_id'] == "test_screen"
        assert len(template['required_nodes']) > 0
        
        # Step 3: Validate template
        validator = TemplateValidator()
        is_valid = validator.validate(template)
        assert is_valid
        
        # Step 4: Match new capture against template
        normalizer = TreeNormalizer()
        normalized = normalizer.normalize(capture_data["normalized"]["root"])
        
        matcher = Matcher(similarity_threshold=0.8)
        match_result = matcher.match(normalized, template)
        assert match_result  # Should match its own template
    
    def test_multi_step_drift_detection(self, tmp_path):
        """Test: sequence of captures with drift injection."""
        log_path = tmp_path / "drift_sequence.log"
        log = ImmutableLog(str(log_path))
        
        base_tree = {
            "name": "app",
            "role": "window",
            "children": [
                {"name": "btn1", "role": "button"},
                {"name": "btn2", "role": "button"}
            ]
        }
        
        # Capture 1: baseline
        normalizer = TreeNormalizer()
        sig_gen = SignatureGenerator()
        tree1 = normalizer.normalize(base_tree)
        sig1 = sig_gen.generate(tree1)
        
        # Capture 2: modified (drift)
        drifted_tree = {
            "name": "app",
            "role": "window",
            "children": [
                {"name": "btn1", "role": "button"},
                {"name": "btn3", "role": "button"}  # Changed!
            ]
        }
        tree2 = normalizer.normalize(drifted_tree)
        sig2 = sig_gen.generate(tree2)
        
        # Detect drift
        assert sig1 != sig2
        
        drift_event = DriftEvent(
            "content",
            "warning",
            {
                "expected_sig": sig1,
                "actual_sig": sig2,
                "modified_nodes": ["btn2 → btn3"]
            }
        )
        log.append(drift_event.to_dict())
        
        # Verify log
        entries = log.get_entries(0, 1)
        assert len(entries) == 1
        assert entries[0]['data']['drift_type'] == "content"
        
        # Verify integrity
        is_valid = log.verify_integrity()
        assert is_valid
