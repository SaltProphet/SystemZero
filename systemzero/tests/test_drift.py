"""Tests for drift detection."""
import pytest
from core.drift import Matcher, DiffEngine, DriftEvent, TransitionChecker
from core.normalization import TreeNormalizer
from tests.fixtures.mock_trees import DISCORD_CHAT_TREE, DOORDASH_OFFER_TREE
from tests.fixtures.drift_scenarios import MISSING_BUTTON_DRIFT, CONTENT_CHANGE_DRIFT
from tests.fixtures.templates import generate_template


class TestMatcher:
    """Test Matcher functionality."""
    
    def test_perfect_match(self):
        """Test matching identical tree to template."""
        matcher = Matcher()
        normalizer = TreeNormalizer()
        
        # Normalize tree
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        # Create template from same tree
        template = generate_template(DISCORD_CHAT_TREE, "discord_chat")
        
        # Match should be very high
        score = matcher.calculate_score(tree, template)
        assert score > 0.8
    
    def test_no_match(self):
        """Test matching completely different trees."""
        matcher = Matcher()
        normalizer = TreeNormalizer()
        
        tree1 = normalizer.normalize(DISCORD_CHAT_TREE)
        template = generate_template(DOORDASH_OFFER_TREE, "doordash_offer")
        
        # Score should be low
        score = matcher.calculate_score(tree1, template)
        assert score < 0.5
    
    def test_find_best_match(self):
        """Test finding best match from multiple templates."""
        matcher = Matcher()
        normalizer = TreeNormalizer()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        templates = [
            generate_template(DISCORD_CHAT_TREE, "discord_chat"),
            generate_template(DOORDASH_OFFER_TREE, "doordash_offer")
        ]
        
        best, score = matcher.find_best_match(tree, templates)
        assert best["screen_id"] == "discord_chat"
        assert score > 0.8


class TestDiffEngine:
    """Test DiffEngine functionality."""
    
    def test_detects_missing_node(self):
        """Test detection of missing nodes."""
        engine = DiffEngine()
        original, modified = MISSING_BUTTON_DRIFT
        
        diffs = engine.diff(original, modified)
        assert len(diffs) > 0
        # Should detect missing send_button
        missing = [d for d in diffs if d.change_type == "missing"]
        assert len(missing) > 0
    
    def test_detects_content_change(self):
        """Test detection of content changes."""
        engine = DiffEngine()
        original, modified = CONTENT_CHANGE_DRIFT
        
        diffs = engine.diff(original, modified)
        assert len(diffs) > 0
        # Should detect changed text
        changes = [d for d in diffs if d.change_type == "changed"]
        assert len(changes) > 0
    
    def test_no_diff_identical_trees(self):
        """Test that identical trees have no diffs."""
        engine = DiffEngine()
        diffs = engine.diff(DISCORD_CHAT_TREE, DISCORD_CHAT_TREE)
        assert len(diffs) == 0


class TestDriftEvent:
    """Test DriftEvent functionality."""
    
    def test_create_layout_drift(self):
        """Test creating layout drift event."""
        drift = DriftEvent("layout", "critical", {"missing": ["send_button"]})
        assert drift.drift_type == "layout"
        assert drift.severity == "critical"
        assert "missing" in drift.details
    
    def test_create_content_drift(self):
        """Test creating content drift event."""
        drift = DriftEvent("content", "warning", {"changed": "text_value"})
        assert drift.drift_type == "content"
        assert drift.severity == "warning"
    
    def test_drift_serialization(self):
        """Test drift event can be serialized."""
        drift = DriftEvent("sequence", "info", {"from": "A", "to": "B"})
        drift_dict = drift.to_dict()
        assert isinstance(drift_dict, dict)
        assert "drift_type" in drift_dict
        assert "severity" in drift_dict


class TestTransitionChecker:
    """Test TransitionChecker functionality."""
    
    def test_valid_transition(self):
        """Test validation of allowed transition."""
        checker = TransitionChecker()
        template = {
            "screen_id": "screen_a",
            "valid_transitions": ["screen_b", "screen_c"]
        }
        assert checker.is_allowed(template, "screen_b")
    
    def test_invalid_transition(self):
        """Test detection of invalid transition."""
        checker = TransitionChecker()
        template = {
            "screen_id": "screen_a",
            "valid_transitions": ["screen_b"]
        }
        assert not checker.is_allowed(template, "screen_x")
    
    def test_check_transition_sequence(self):
        """Test checking sequence of transitions."""
        checker = TransitionChecker()
        templates = {
            "screen_a": {"screen_id": "screen_a", "valid_transitions": ["screen_b"]},
            "screen_b": {"screen_id": "screen_b", "valid_transitions": ["screen_c"]},
            "screen_c": {"screen_id": "screen_c", "valid_transitions": []}
        }
        
        # Valid sequence
        result = checker.check_transition("screen_a", "screen_b", templates)
        assert result.is_valid
        
        # Invalid sequence
        result = checker.check_transition("screen_a", "screen_c", templates)
        assert not result.is_valid
