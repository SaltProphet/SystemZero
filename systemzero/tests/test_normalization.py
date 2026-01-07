"""Tests for normalization layer."""
import pytest
from core.normalization import TreeNormalizer, NodeClassifier, NoiseFilters, SignatureGenerator
from tests.fixtures.mock_trees import DISCORD_CHAT_TREE, DOORDASH_OFFER_TREE


class TestTreeNormalizer:
    """Test TreeNormalizer functionality."""
    
    def test_removes_transient_properties(self):
        """Test that transient properties are removed."""
        normalizer = TreeNormalizer()
        tree = {
            "root": {
                "role": "window",
                "name": "test",
                "timestamp": 12345,
                "id": "abc123",
                "focused": True,
                "children": []
            }
        }
        normalized = normalizer.normalize(tree)
        assert "timestamp" not in normalized["root"]
        assert "id" not in normalized["root"]
        assert "focused" not in normalized["root"]
    
    def test_property_mapping(self):
        """Test that label/title/text map to name."""
        normalizer = TreeNormalizer()
        tree = {
            "root": {
                "role": "button",
                "label": "Click me",
                "children": []
            }
        }
        normalized = normalizer.normalize(tree)
        assert normalized["root"]["name"] == "Click me"
        assert "label" not in normalized["root"]
    
    def test_child_sorting(self):
        """Test that children are sorted deterministically."""
        normalizer = TreeNormalizer()
        tree = {
            "root": {
                "role": "window",
                "children": [
                    {"role": "button", "name": "c"},
                    {"role": "button", "name": "a"},
                    {"role": "button", "name": "b"}
                ]
            }
        }
        normalized = normalizer.normalize(tree)
        names = [child["name"] for child in normalized["root"]["children"]]
        assert names == ["a", "b", "c"]
    
    def test_normalize_full_tree(self):
        """Test normalizing a full mock tree."""
        normalizer = TreeNormalizer()
        normalized = normalizer.normalize(DISCORD_CHAT_TREE)
        assert normalized is not None
        assert "root" in normalized


class TestNodeClassifier:
    """Test NodeClassifier functionality."""
    
    def test_classify_interactive(self):
        """Test classification of interactive elements."""
        classifier = NodeClassifier()
        assert classifier.classify({"role": "button"}) == "interactive"
        assert classifier.classify({"role": "textbox"}) == "interactive"
        assert classifier.classify({"role": "link"}) == "interactive"
    
    def test_classify_container(self):
        """Test classification of container elements."""
        classifier = NodeClassifier()
        assert classifier.classify({"role": "panel"}) == "container"
        assert classifier.classify({"role": "window"}) == "container"
        assert classifier.classify({"role": "frame"}) == "container"
    
    def test_classify_static(self):
        """Test classification of static elements."""
        classifier = NodeClassifier()
        assert classifier.classify({"role": "label"}) == "static"
        assert classifier.classify({"role": "text"}) == "static"
        assert classifier.classify({"role": "image"}) == "static"
    
    def test_classify_unknown(self):
        """Test fallback to unknown."""
        classifier = NodeClassifier()
        assert classifier.classify({"role": "weird_element"}) == "unknown"


class TestNoiseFilters:
    """Test NoiseFilters functionality."""
    
    def test_filters_decorative(self):
        """Test removal of decorative elements."""
        filters = NoiseFilters()
        tree = {
            "root": {
                "role": "window",
                "children": [
                    {"role": "button", "name": "ok"},
                    {"role": "decoration", "name": "border"},
                    {"role": "separator"}
                ]
            }
        }
        filtered = filters.filter(tree)
        assert len(filtered["root"]["children"]) == 1
        assert filtered["root"]["children"][0]["name"] == "ok"
    
    def test_filters_hidden(self):
        """Test removal of hidden elements."""
        filters = NoiseFilters()
        tree = {
            "root": {
                "role": "window",
                "children": [
                    {"role": "button", "name": "visible", "visible": True},
                    {"role": "button", "name": "hidden", "visible": False}
                ]
            }
        }
        filtered = filters.filter(tree)
        assert len(filtered["root"]["children"]) == 1


class TestSignatureGenerator:
    """Test SignatureGenerator functionality."""
    
    def test_deterministic_signature(self):
        """Test that same tree produces same signature."""
        generator = SignatureGenerator()
        tree = {"root": {"role": "window", "name": "test"}}
        sig1 = generator.generate(tree)
        sig2 = generator.generate(tree)
        assert sig1 == sig2
    
    def test_different_trees_different_signatures(self):
        """Test that different trees produce different signatures."""
        generator = SignatureGenerator()
        tree1 = {"root": {"role": "window", "name": "test1"}}
        tree2 = {"root": {"role": "window", "name": "test2"}}
        assert generator.generate(tree1) != generator.generate(tree2)
    
    def test_structural_signature(self):
        """Test structural signature ignores content."""
        generator = SignatureGenerator()
        tree1 = {"root": {"role": "window", "name": "test1"}}
        tree2 = {"root": {"role": "window", "name": "test2"}}
        # Structural signatures should be same (same structure, different content)
        sig1 = generator.generate_structural(tree1)
        sig2 = generator.generate_structural(tree2)
        assert sig1 == sig2
    
    def test_content_signature(self):
        """Test content signature captures text."""
        generator = SignatureGenerator()
        tree1 = {"root": {"role": "window", "name": "test1"}}
        tree2 = {"root": {"role": "window", "name": "test2"}}
        # Content signatures should differ
        sig1 = generator.generate_content(tree1)
        sig2 = generator.generate_content(tree2)
        assert sig1 != sig2
