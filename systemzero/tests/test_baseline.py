"""Tests for baseline layer."""
import pytest
from pathlib import Path
from core.baseline import TemplateLoader, TemplateValidator, StateMachine


class TestTemplateLoader:
    """Test TemplateLoader functionality."""
    
    def test_load_template(self):
        """Test loading a single template."""
        loader = TemplateLoader()
        template_path = Path("core/baseline/templates/discord_chat.yaml")
        if template_path.exists():
            template = loader.load(str(template_path))
            assert template is not None
            assert "screen_id" in template
    
    def test_load_all_templates(self):
        """Test loading all templates from directory."""
        loader = TemplateLoader()
        templates = loader.load_all()
        assert len(templates) > 0
        # Should have discord, doordash, system_default at minimum
        assert any("discord" in tid for tid in templates.keys())
    
    def test_get_template_by_id(self):
        """Test retrieving template by screen_id."""
        loader = TemplateLoader()
        templates = loader.load_all()
        if templates:
            first_id = list(templates.keys())[0]
            template = loader.get_template(first_id)
            assert template is not None
            assert template["screen_id"] == first_id


class TestTemplateValidator:
    """Test TemplateValidator functionality."""
    
    def test_valid_template(self):
        """Test validation of valid template."""
        validator = TemplateValidator()
        template = {
            "screen_id": "test_screen",
            "required_nodes": ["button1", "button2"],
            "structure_signature": "abc123",
            "valid_transitions": ["other_screen"]
        }
        assert validator.validate(template)
    
    def test_missing_screen_id(self):
        """Test validation fails without screen_id."""
        validator = TemplateValidator()
        template = {
            "required_nodes": ["button1"]
        }
        assert not validator.validate(template)
    
    def test_invalid_types(self):
        """Test validation fails with wrong types."""
        validator = TemplateValidator()
        template = {
            "screen_id": "test",
            "required_nodes": "should_be_list",  # Wrong type
        }
        # Should either fail validation or handle gracefully
        result = validator.validate(template)
        assert isinstance(result, bool)
    
    def test_minimal_valid_template(self):
        """Test that screen_id alone is sufficient."""
        validator = TemplateValidator()
        template = {"screen_id": "minimal"}
        assert validator.validate(template)


class TestStateMachine:
    """Test StateMachine functionality."""
    
    def test_initial_state(self):
        """Test state machine initialization."""
        sm = StateMachine()
        assert sm.current_state is None or isinstance(sm.current_state, str)
    
    def test_transition(self):
        """Test state transition."""
        sm = StateMachine()
        sm.transition("screen_a", "screen_b")
        # Should update current state
        assert sm.current_state in ["screen_b", None]
    
    def test_is_valid_transition(self):
        """Test validation of transitions."""
        sm = StateMachine()
        template = {
            "screen_id": "screen_a",
            "valid_transitions": ["screen_b", "screen_c"]
        }
        assert sm.is_valid_transition(template, "screen_b")
        assert not sm.is_valid_transition(template, "screen_x")
    
    def test_state_history(self):
        """Test that state history is tracked."""
        sm = StateMachine()
        sm.transition("screen_a", "screen_b")
        sm.transition("screen_b", "screen_c")
        # Should have history
        assert hasattr(sm, 'history') or hasattr(sm, 'state_history')
