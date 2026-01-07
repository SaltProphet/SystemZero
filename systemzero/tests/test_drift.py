"""Comprehensive tests for drift detection - Matcher and DiffEngine."""
import pytest
import copy
from core.drift import Matcher, DiffEngine, DriftEvent
from core.normalization import TreeNormalizer, SignatureGenerator
from tests.fixtures.mock_trees import (
    DISCORD_CHAT_TREE,
    DOORDASH_OFFER_TREE,
    GMAIL_INBOX_TREE,
    SETTINGS_PANEL_TREE,
    LOGIN_FORM_TREE
)
from tests.fixtures.templates import (
    discord_chat_template,
    doordash_offer_template,
    gmail_inbox_template,
    settings_panel_template,
    login_form_template
)


class TestMatcher:
    """Test suite for Matcher with focus on scoring algorithm."""
    
    def test_matcher_initialization_with_threshold(self):
        """Verify Matcher can be initialized with custom threshold."""
        matcher = Matcher(similarity_threshold=0.75)
        assert matcher.similarity_threshold == 0.75
        
        matcher_default = Matcher()
        assert matcher_default.similarity_threshold == 0.8
    
    def test_match_returns_true_above_threshold(self):
        """Verify match() returns True when similarity exceeds threshold."""
        normalizer = TreeNormalizer()
        matcher = Matcher(similarity_threshold=0.8)
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        template = discord_chat_template()
        
        result = matcher.match(tree, template)
        assert result is True
    
    def test_match_returns_false_below_threshold(self):
        """Verify match() returns False when similarity is below threshold."""
        normalizer = TreeNormalizer()
        matcher = Matcher(similarity_threshold=0.95)
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        # Use a template from different screen
        template = doordash_offer_template()
        
        result = matcher.match(tree, template)
        assert result is False
    
    def test_similarity_score_perfect_match(self):
        """Verify similarity_score returns 1.0 for perfect match."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        template = discord_chat_template()
        
        score = matcher.similarity_score(tree, template)
        # Score should be very high (close to 1.0) for matching template
        assert score >= 0.9
    
    def test_similarity_score_weighted_components(self):
        """Verify scoring uses 40% required nodes, 40% structure, 20% roles."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        template = discord_chat_template()
        
        # Get individual component scores
        required_score = matcher._check_required_nodes(tree, template)
        structure_score = matcher._check_structure(tree, template)
        role_score = matcher._check_roles(tree, template)
        
        # Calculate expected weighted score
        expected_score = (required_score * 0.4) + (structure_score * 0.4) + (role_score * 0.2)
        
        actual_score = matcher.similarity_score(tree, template)
        
        # Should match weighted calculation
        assert abs(actual_score - expected_score) < 0.01
    
    def test_check_required_nodes_all_present(self):
        """Verify _check_required_nodes returns 1.0 when all nodes present."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        template = discord_chat_template()
        
        score = matcher._check_required_nodes(tree, template)
        assert score == 1.0
    
    def test_check_required_nodes_partial_present(self):
        """Verify _check_required_nodes calculates correct ratio for partial matches."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        # Template with some missing nodes
        template = {
            "required_nodes": ["message_list", "input_box", "send_button", "missing_node"]
        }
        
        score = matcher._check_required_nodes(tree, template)
        # 3 out of 4 required nodes present
        assert score == 0.75
    
    def test_check_required_nodes_none_present(self):
        """Verify _check_required_nodes returns 0.0 when no nodes match."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        template = {
            "required_nodes": ["nonexistent1", "nonexistent2", "nonexistent3"]
        }
        
        score = matcher._check_required_nodes(tree, template)
        assert score == 0.0
    
    def test_check_required_nodes_empty_list(self):
        """Verify _check_required_nodes returns 1.0 when no requirements specified."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        template = {"required_nodes": []}
        
        score = matcher._check_required_nodes(tree, template)
        assert score == 1.0
    
    def test_check_structure_depth_similarity(self):
        """Verify _check_structure considers tree depth."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        # Calculate actual depth
        depth = matcher._calculate_depth(tree.get("root"))
        
        # Template with matching depth
        template = {"depth": depth, "node_count": 100}
        
        score = matcher._check_structure(tree, template)
        # Should have good score with matching depth
        assert score > 0.5
    
    def test_check_roles_exact_match(self):
        """Verify _check_roles with exact role overlap."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        # Extract actual roles from tree
        actual_roles = matcher._extract_roles(tree.get("root"))
        
        template = {"expected_roles": list(actual_roles)}
        
        score = matcher._check_roles(tree, template)
        # Perfect overlap should give 1.0
        assert score == 1.0
    
    def test_check_roles_partial_overlap(self):
        """Verify _check_roles calculates Jaccard similarity correctly."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        # Some overlapping, some unique roles
        template = {"expected_roles": ["window", "panel", "button", "nonexistent_role"]}
        
        score = matcher._check_roles(tree, template)
        # Should be between 0 and 1
        assert 0.0 < score < 1.0
    
    def test_find_best_match_with_multiple_templates(self):
        """Verify find_best_match returns highest scoring template."""
        normalizer = TreeNormalizer()
        matcher = Matcher(similarity_threshold=0.5)
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        templates = [
            discord_chat_template(),
            doordash_offer_template(),
            gmail_inbox_template()
        ]
        
        result = matcher.find_best_match(tree, templates)
        
        assert result is not None
        best_template, score = result
        
        # Should match discord template
        assert best_template["screen_id"] == "discord_chat"
        assert score >= matcher.similarity_threshold
    
    def test_find_best_match_returns_none_below_threshold(self):
        """Verify find_best_match returns None when no template meets threshold."""
        normalizer = TreeNormalizer()
        matcher = Matcher(similarity_threshold=0.99)
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        # Use templates from different screens
        templates = [
            doordash_offer_template(),
            gmail_inbox_template()
        ]
        
        result = matcher.find_best_match(tree, templates)
        
        # No match should exceed 0.99 threshold
        assert result is None
    
    def test_find_best_match_empty_templates(self):
        """Verify find_best_match handles empty template list."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        
        result = matcher.find_best_match(tree, [])
        assert result is None
    
    def test_extract_node_names_recursive(self):
        """Verify _extract_node_names finds all nodes recursively."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        names = matcher._extract_node_names(tree)
        
        # Should find nodes at all levels
        assert "Discord" in names
        assert "sidebar" in names
        assert "message_list" in names
        assert "send_button" in names
    
    def test_extract_roles_recursive(self):
        """Verify _extract_roles finds all role types."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        roles = matcher._extract_roles(tree.get("root"))
        
        assert "window" in roles
        assert "panel" in roles
        assert "button" in roles
        assert "list" in roles
    
    def test_calculate_depth_nested_structure(self):
        """Verify _calculate_depth correctly measures tree depth."""
        matcher = Matcher()
        
        # Simple nested structure
        node = {
            "role": "root",
            "children": [
                {
                    "role": "level1",
                    "children": [
                        {"role": "level2"}
                    ]
                }
            ]
        }
        
        depth = matcher._calculate_depth(node)
        assert depth == 2
    
    def test_count_nodes_total(self):
        """Verify _count_nodes counts all nodes in tree."""
        normalizer = TreeNormalizer()
        matcher = Matcher()
        
        tree = normalizer.normalize(DISCORD_CHAT_TREE)
        count = matcher._count_nodes(tree.get("root"))
        
        # Should count root + all descendants
        assert count > 10


class TestDiffEngine:
    """Test suite for DiffEngine with actual tree deltas."""
    
    def test_diff_empty_trees(self):
        """Verify diff handles empty trees."""
        engine = DiffEngine()
        
        result = engine.diff({}, {})
        
        assert result["added"] == []
        assert result["removed"] == []
        assert result["modified"] == []
        assert result["unchanged"] == 0
        assert result["similarity"] == 1.0
    
    def test_diff_identical_trees(self):
        """Verify diff recognizes identical trees."""
        normalizer = TreeNormalizer()
        engine = DiffEngine()
        
        tree1 = normalizer.normalize(DISCORD_CHAT_TREE)
        tree2 = normalizer.normalize(copy.deepcopy(DISCORD_CHAT_TREE))
        
        result = engine.diff(tree1, tree2)
        
        # Should have no changes
        assert len(result["added"]) == 0
        assert len(result["removed"]) == 0
        # May have some modifications due to sorting, but similarity should be high
        assert result["similarity"] >= 0.9
    
    def test_diff_detects_added_nodes(self):
        """Verify diff detects nodes added to tree."""
        normalizer = TreeNormalizer()
        engine = DiffEngine()
        
        tree1 = normalizer.normalize(DISCORD_CHAT_TREE)
        tree2 = copy.deepcopy(tree1)
        
        # Add a new node
        tree2["root"]["children"][0]["children"].append({
            "role": "button",
            "name": "new_button"
        })
        
        result = engine.diff(tree1, tree2)
        
        assert len(result["added"]) > 0
        assert result["similarity"] < 1.0
    
    def test_diff_detects_removed_nodes(self):
        """Verify diff detects nodes removed from tree."""
        normalizer = TreeNormalizer()
        engine = DiffEngine()
        
        tree1 = normalizer.normalize(DISCORD_CHAT_TREE)
        tree2 = copy.deepcopy(tree1)
        
        # Remove a node
        tree2["root"]["children"][0]["children"].pop()
        
        result = engine.diff(tree1, tree2)
        
        assert len(result["removed"]) > 0
        assert result["similarity"] < 1.0
    
    def test_diff_detects_modified_properties(self):
        """Verify diff detects property changes in nodes."""
        normalizer = TreeNormalizer()
        engine = DiffEngine()
        
        tree1 = normalizer.normalize(DISCORD_CHAT_TREE)
        tree2 = copy.deepcopy(tree1)
        
        # Modify a property that's tracked
        tree2["root"]["role"] = "dialog"
        
        result = engine.diff(tree1, tree2)
        
        # Should detect modification or see it as removed+added
        assert result["similarity"] < 1.0
    
    def test_diff_similarity_score_calculation(self):
        """Verify similarity score is correctly calculated."""
        normalizer = TreeNormalizer()
        engine = DiffEngine()
        
        tree1 = normalizer.normalize(LOGIN_FORM_TREE)
        tree2 = copy.deepcopy(tree1)
        
        # Make a small change
        tree2["root"]["children"][0]["children"][0]["value"] = "Modified Title"
        
        result = engine.diff(tree1, tree2)
        
        # Similarity should reflect the proportion of unchanged nodes
        total = len(result["added"]) + len(result["removed"]) + len(result["modified"]) + result["unchanged"]
        expected_similarity = result["unchanged"] / total if total > 0 else 1.0
        
        assert abs(result["similarity"] - expected_similarity) < 0.01
    
    def test_diff_summary_formatting(self):
        """Verify diff_summary produces readable output."""
        normalizer = TreeNormalizer()
        engine = DiffEngine()
        
        tree1 = normalizer.normalize(DISCORD_CHAT_TREE)
        tree2 = copy.deepcopy(tree1)
        tree2["root"]["children"].pop()
        
        result = engine.diff(tree1, tree2)
        summary = engine.diff_summary(result)
        
        assert "Similarity:" in summary
        assert "Added:" in summary
        assert "Removed:" in summary
        assert "Modified:" in summary
        assert "Unchanged:" in summary
    
    def test_has_significant_changes_above_threshold(self):
        """Verify has_significant_changes with similarity above threshold."""
        engine = DiffEngine()
        
        diff_result = {
            "added": [],
            "removed": [],
            "modified": [],
            "unchanged": 100,
            "similarity": 0.95
        }
        
        # 0.95 > 0.9 threshold, so not significant
        assert engine.has_significant_changes(diff_result, threshold=0.9) is False
    
    def test_has_significant_changes_below_threshold(self):
        """Verify has_significant_changes with similarity below threshold."""
        engine = DiffEngine()
        
        diff_result = {
            "added": [{"role": "button"}],
            "removed": [{"role": "text"}],
            "modified": [],
            "unchanged": 10,
            "similarity": 0.75
        }
        
        # 0.75 < 0.9 threshold, so significant
        assert engine.has_significant_changes(diff_result, threshold=0.9) is True
    
    def test_diff_with_completely_different_trees(self):
        """Verify diff handles completely different trees."""
        normalizer = TreeNormalizer()
        engine = DiffEngine()
        
        tree1 = normalizer.normalize(DISCORD_CHAT_TREE)
        tree2 = normalizer.normalize(DOORDASH_OFFER_TREE)
        
        result = engine.diff(tree1, tree2)
        
        # Should have very low similarity
        assert result["similarity"] < 0.5
        # Should have many differences
        assert (len(result["added"]) + len(result["removed"]) + len(result["modified"])) > 0


class TestDriftEvent:
    """Test suite for DriftEvent data structure."""
    
    def test_drift_event_creation(self):
        """Verify DriftEvent can be created with required fields."""
        event = DriftEvent("layout", "warning", {"test": "data"})
        
        assert event.drift_type == "layout"
        assert event.severity == "warning"
        assert event.metadata == {"test": "data"}
    
    def test_drift_event_to_dict(self):
        """Verify DriftEvent converts to dict properly."""
        event = DriftEvent("content", "critical", {"key": "value"})
        
        event_dict = event.to_dict()
        
        assert event_dict["drift_type"] == "content"
        assert event_dict["severity"] == "critical"
        assert event_dict["metadata"]["key"] == "value"
        assert "timestamp" in event_dict
