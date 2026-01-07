"""Test fixtures for System//Zero testing."""
from .mock_trees import *
from .drift_scenarios import *
from .templates import *

__all__ = [
    # Mock trees
    "DISCORD_CHAT_TREE",
    "DOORDASH_OFFER_TREE",
    "GMAIL_INBOX_TREE",
    "SETTINGS_PANEL_TREE",
    "LOGIN_FORM_TREE",
    
    # Drift scenarios
    "MISSING_BUTTON_DRIFT",
    "TEXT_CHANGE_DRIFT",
    "LAYOUT_SHIFT_DRIFT",
    "MANIPULATIVE_PATTERN_DRIFT",
    "SEQUENCE_VIOLATION_DRIFT",
    
    # Template builders
    "build_template",
    "template_from_tree",
]
