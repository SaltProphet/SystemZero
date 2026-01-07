"""Comprehensive tests for tree normalization and signature generation."""
import pytest
import hashlib
import copy
from core.normalization import TreeNormalizer, SignatureGenerator
from tests.fixtures.mock_trees import (
    DISCORD_CHAT_TREE,
    DOORDASH_OFFER_TREE,
    GMAIL_INBOX_TREE,
    SETTINGS_PANEL_TREE,
    LOGIN_FORM_TREE
)


class TestTreeNormalizer:
    """Test suite for TreeNormalizer."""
    
    def test_normalize_removes_transient_properties(self):
        """Verify that transient properties like timestamp, id, instance_id are removed."""
        tree_with_transients = {
            "root": {
                "role": "window",
                "name": "Test",
                "timestamp": "2024-01-01T00:00:00",
                "id": "abc123",
                "instance_id": "xyz789",
                "children": [
                    {
                        "role": "button",
                        "name": "submit",
                        "id": "btn_001",
                        "timestamp": "2024-01-01T00:00:01"
                    }
                ]
            },
            "timestamp": "2024-01-01T00:00:00"
        }
        
        normalizer = TreeNormalizer()
        normalized = normalizer.normalize(tree_with_transients)
        
        # Check root level
        assert "timestamp" not in normalized
        assert "root" in normalized
        
        # Check root node
        root = normalized["root"]
        assert "timestamp" not in root
        assert "id" not in root
        assert "instance_id" not in root
        assert root["role"] == "window"
        assert root["name"] == "Test"
        
        # Check child node
        child = root["children"][0]
        assert "timestamp" not in child
        assert "id" not in child
        assert child["role"] == "button"
        assert child["name"] == "submit"
    
    def test_normalize_maps_alternative_property_names(self):
        """Verify that alternative property names (label, title, text) map to 'name'."""
        tree_with_alternatives = {
            "root": {
                "role": "window",
                "title": "Main Window",
                "children": [
                    {"role": "button", "label": "Submit"},
                    {"role": "text", "text": "Description"}
                ]
            }
        }
        
        normalizer = TreeNormalizer()
        normalized = normalizer.normalize(tree_with_alternatives)
        
        root = normalized["root"]
        assert root["name"] == "Main Window"
        assert "title" not in root
        
        assert normalized["root"]["children"][0]["name"] == "Submit"
        assert "label" not in normalized["root"]["children"][0]
        
        assert normalized["root"]["children"][1]["name"] == "Description"
        assert "text" not in normalized["root"]["children"][1]
    
    def test_normalize_sorts_children_deterministically(self):
        """Verify that children are sorted for deterministic comparison."""
        tree_unsorted = {
            "root": {
                "role": "window",
                "name": "Test",
                "children": [
                    {"role": "textbox", "name": "input_z"},
                    {"role": "button", "name": "submit"},
                    {"role": "button", "name": "cancel"},
                    {"role": "text", "name": "label_a"}
                ]
            }
        }
        
        normalizer = TreeNormalizer()
        normalized = normalizer.normalize(tree_unsorted)
        
        children = normalized["root"]["children"]
        # Should be sorted by role > name > type
        assert children[0]["role"] == "button"
        assert children[0]["name"] == "cancel"
        assert children[1]["role"] == "button"
        assert children[1]["name"] == "submit"
        assert children[2]["role"] == "text"
        assert children[3]["role"] == "textbox"
    
    def test_normalize_handles_empty_tree(self):
        """Verify normalization handles empty trees gracefully."""
        normalizer = TreeNormalizer()
        
        assert normalizer.normalize({}) == {}
        assert normalizer.normalize(None) == {}
    
    def test_normalize_preserves_structure(self):
        """Verify that normalization preserves the overall tree structure."""
        normalizer = TreeNormalizer()
        normalized = normalizer.normalize(DISCORD_CHAT_TREE)
        
        assert "root" in normalized
        root = normalized["root"]
        assert root["role"] == "window"
        assert root["name"] == "Discord"
        assert len(root["children"]) == 2
        
        # Check nested structure is preserved
        sidebar = root["children"][1]  # After sorting
        assert sidebar["name"] == "sidebar"
        assert "children" in sidebar


class TestSignatureGenerator:
    """Test suite for SignatureGenerator."""
    
    def test_generate_produces_sha256_hash(self):
        """Verify that generate() produces a valid SHA256 hash."""
        normalizer = TreeNormalizer()
        sig_gen = SignatureGenerator()
        
        normalized = normalizer.normalize(DISCORD_CHAT_TREE)
        signature = sig_gen.generate(normalized)
        
        # SHA256 produces 64 character hex string
        assert len(signature) == 64
        assert all(c in '0123456789abcdef' for c in signature)
    
    def test_generate_excludes_transient_properties(self):
        """Verify that transient properties don't affect signature."""
        sig_gen = SignatureGenerator()
        
        tree_base = {
            "root": {
                "role": "window",
                "name": "Test"
            }
        }
        
        tree_with_transients = {
            "root": {
                "role": "window",
                "name": "Test",
                "timestamp": "2024-01-01",
                "id": "xyz123",
                "focused": True
            }
        }
        
        sig1 = sig_gen.generate(tree_base)
        sig2 = sig_gen.generate(tree_with_transients)
        
        # Signatures should be identical
        assert sig1 == sig2
    
    def test_generate_is_deterministic(self):
        """Verify that generating signature multiple times produces same result."""
        normalizer = TreeNormalizer()
        sig_gen = SignatureGenerator()
        
        normalized = normalizer.normalize(DISCORD_CHAT_TREE)
        
        sig1 = sig_gen.generate(normalized)
        sig2 = sig_gen.generate(normalized)
        sig3 = sig_gen.generate(normalized)
        
        assert sig1 == sig2 == sig3
    
    def test_generate_detects_structure_changes(self):
        """Verify that structural changes produce different signatures."""
        normalizer = TreeNormalizer()
        sig_gen = SignatureGenerator()
        
        tree1 = copy.deepcopy(DISCORD_CHAT_TREE)
        tree2 = copy.deepcopy(DISCORD_CHAT_TREE)
        
        # Modify structure: remove a child node
        tree2["root"]["children"][1]["children"].pop()
        
        norm1 = normalizer.normalize(tree1)
        norm2 = normalizer.normalize(tree2)
        
        sig1 = sig_gen.generate(norm1)
        sig2 = sig_gen.generate(norm2)
        
        assert sig1 != sig2
    
    def test_generate_detects_content_changes(self):
        """Verify that content changes produce different signatures."""
        normalizer = TreeNormalizer()
        sig_gen = SignatureGenerator()
        
        tree1 = copy.deepcopy(DOORDASH_OFFER_TREE)
        tree2 = copy.deepcopy(DOORDASH_OFFER_TREE)
        
        # Change content value
        tree2["root"]["children"][0]["children"][1]["value"] = "$15.00"
        
        norm1 = normalizer.normalize(tree1)
        norm2 = normalizer.normalize(tree2)
        
        sig1 = sig_gen.generate(norm1)
        sig2 = sig_gen.generate(norm2)
        
        assert sig1 != sig2
    
    def test_generate_structural_ignores_content(self):
        """Verify that structural signatures ignore content changes."""
        sig_gen = SignatureGenerator()
        
        tree1 = {
            "root": {
                "role": "window",
                "name": "Test",
                "children": [
                    {"role": "text", "name": "label", "value": "Original"}
                ]
            }
        }
        
        tree2 = {
            "root": {
                "role": "window",
                "name": "Test",
                "children": [
                    {"role": "text", "name": "label", "value": "Modified"}
                ]
            }
        }
        
        sig1 = sig_gen.generate_structural(tree1)
        sig2 = sig_gen.generate_structural(tree2)
        
        # Structural signatures should be identical despite content change
        assert sig1 == sig2
    
    def test_generate_structural_uses_role_and_type(self):
        """Verify that structural signatures use role and type information."""
        sig_gen = SignatureGenerator()
        
        # Test with normalized structures that extract_structure can handle
        tree1 = {
            "role": "window",
            "type": "container",
            "children": [
                {"role": "button", "type": "action"},
                {"role": "text", "type": "display"}
            ]
        }
        
        tree2 = {
            "role": "window",
            "type": "container",
            "children": [
                {"role": "button", "type": "action"}
            ]
        }
        
        sig1 = sig_gen.generate_structural(tree1)
        sig2 = sig_gen.generate_structural(tree2)
        
        # Should detect structural difference (different children count)
        assert sig1 != sig2
    
    def test_generate_content_extracts_text(self):
        """Verify that content signatures extract and hash text content."""
        sig_gen = SignatureGenerator()
        
        tree = {
            "root": {
                "role": "window",
                "name": "Main",
                "children": [
                    {"role": "text", "name": "Welcome"},
                    {"role": "button", "name": "Submit"}
                ]
            }
        }
        
        sig = sig_gen.generate_content(tree)
        
        # Should produce a valid hash
        assert len(sig) == 64
        assert all(c in '0123456789abcdef' for c in sig)
    
    def test_generate_content_is_order_independent(self):
        """Verify that content signatures are order-independent."""
        sig_gen = SignatureGenerator()
        
        tree1 = {
            "root": {
                "children": [
                    {"name": "Alpha"},
                    {"name": "Beta"}
                ]
            }
        }
        
        tree2 = {
            "root": {
                "children": [
                    {"name": "Beta"},
                    {"name": "Alpha"}
                ]
            }
        }
        
        sig1 = sig_gen.generate_content(tree1)
        sig2 = sig_gen.generate_content(tree2)
        
        # Content signatures should be same (sorted internally)
        assert sig1 == sig2
    
    def test_generate_multi_returns_all_signature_types(self):
        """Verify that generate_multi() returns all signature types."""
        normalizer = TreeNormalizer()
        sig_gen = SignatureGenerator()
        
        normalized = normalizer.normalize(GMAIL_INBOX_TREE)
        sigs = sig_gen.generate_multi(normalized)
        
        assert "full" in sigs
        assert "structural" in sigs
        assert "content" in sigs
        
        # All should be valid SHA256 hashes
        for sig_type, sig_value in sigs.items():
            assert len(sig_value) == 64
            assert all(c in '0123456789abcdef' for c in sig_value)
    
    def test_compare_signatures_equality(self):
        """Verify signature comparison works correctly."""
        sig_gen = SignatureGenerator()
        
        sig1 = hashlib.sha256(b"test").hexdigest()
        sig2 = hashlib.sha256(b"test").hexdigest()
        sig3 = hashlib.sha256(b"different").hexdigest()
        
        assert sig_gen.compare_signatures(sig1, sig2) is True
        assert sig_gen.compare_signatures(sig1, sig3) is False
    
    def test_signature_consistency_across_mock_trees(self):
        """Verify each mock tree produces unique, consistent signatures."""
        normalizer = TreeNormalizer()
        sig_gen = SignatureGenerator()
        
        trees = [
            DISCORD_CHAT_TREE,
            DOORDASH_OFFER_TREE,
            GMAIL_INBOX_TREE,
            SETTINGS_PANEL_TREE,
            LOGIN_FORM_TREE
        ]
        
        signatures = []
        for tree in trees:
            normalized = normalizer.normalize(tree)
            sig = sig_gen.generate(normalized)
            signatures.append(sig)
        
        # All signatures should be unique
        assert len(signatures) == len(set(signatures))
        
        # Regenerate to verify consistency
        for i, tree in enumerate(trees):
            normalized = normalizer.normalize(tree)
            sig = sig_gen.generate(normalized)
            assert sig == signatures[i]
    
    def test_empty_tree_signature(self):
        """Verify empty tree produces consistent empty signature."""
        sig_gen = SignatureGenerator()
        
        empty_sig = sig_gen.generate({})
        
        # Should be SHA256 of empty string
        expected = hashlib.sha256(b"").hexdigest()
        assert empty_sig == expected
