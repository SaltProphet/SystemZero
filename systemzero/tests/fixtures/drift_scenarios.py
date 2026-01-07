"""Pre-built drift scenarios for testing."""
from typing import Dict, Any, Tuple
import copy
from .mock_trees import DISCORD_CHAT_TREE, DOORDASH_OFFER_TREE, LOGIN_FORM_TREE


# Scenario 1: Missing critical button (layout drift)
MISSING_BUTTON_DRIFT: Tuple[Dict[str, Any], Dict[str, Any]] = (
    DISCORD_CHAT_TREE,  # Original
    {  # Modified - missing send_button
        "root": {
            "role": "window",
            "name": "Discord",
            "children": [
                {
                    "role": "panel",
                    "name": "sidebar",
                    "children": [
                        {"role": "button", "name": "home"},
                        {"role": "list", "name": "server_list", "children": [
                            {"role": "button", "name": "server_1"},
                            {"role": "button", "name": "server_2"},
                        ]},
                    ]
                },
                {
                    "role": "panel",
                    "name": "main_content",
                    "children": [
                        {
                            "role": "list",
                            "name": "message_list",
                            "children": [
                                {"role": "text", "name": "message_1", "value": "Hello"},
                                {"role": "text", "name": "message_2", "value": "World"},
                            ]
                        },
                        {
                            "role": "panel",
                            "name": "input_area",
                            "children": [
                                {"role": "textbox", "name": "input_box", "value": ""},
                                # send_button REMOVED
                            ]
                        }
                    ]
                }
            ]
        }
    }
)


# Scenario 2: Text content changed (content drift)
TEXT_CHANGE_DRIFT: Tuple[Dict[str, Any], Dict[str, Any]] = (
    DOORDASH_OFFER_TREE,  # Original - $12.50 payout
    {  # Modified - payout reduced to $8.00
        "root": {
            "role": "window",
            "name": "DoorDash Driver",
            "children": [
                {
                    "role": "panel",
                    "name": "offer_card",
                    "children": [
                        {"role": "text", "name": "restaurant_name", "value": "Pizza Palace"},
                        {"role": "text", "name": "payout", "value": "$8.00"},  # CHANGED
                        {"role": "text", "name": "distance", "value": "3.2 mi"},
                        {"role": "text", "name": "time_estimate", "value": "25-30 min"},
                        {
                            "role": "panel",
                            "name": "actions",
                            "children": [
                                {"role": "button", "name": "accept_button"},
                                {"role": "button", "name": "decline_button"},
                            ]
                        }
                    ]
                }
            ]
        }
    }
)


# Scenario 3: Layout structure shifted (layout drift)
LAYOUT_SHIFT_DRIFT: Tuple[Dict[str, Any], Dict[str, Any]] = (
    DISCORD_CHAT_TREE,  # Original
    {  # Modified - sidebar moved after main_content
        "root": {
            "role": "window",
            "name": "Discord",
            "children": [
                {
                    "role": "panel",
                    "name": "main_content",
                    "children": [
                        {
                            "role": "list",
                            "name": "message_list",
                            "children": [
                                {"role": "text", "name": "message_1", "value": "Hello"},
                                {"role": "text", "name": "message_2", "value": "World"},
                            ]
                        },
                        {
                            "role": "panel",
                            "name": "input_area",
                            "children": [
                                {"role": "textbox", "name": "input_box", "value": ""},
                                {"role": "button", "name": "send_button"},
                            ]
                        }
                    ]
                },
                {
                    "role": "panel",
                    "name": "sidebar",
                    "children": [
                        {"role": "button", "name": "home"},
                        {"role": "list", "name": "server_list", "children": [
                            {"role": "button", "name": "server_1"},
                            {"role": "button", "name": "server_2"},
                        ]},
                    ]
                },
            ]
        }
    }
)


# Scenario 4: Manipulative dark pattern (manipulative drift)
MANIPULATIVE_PATTERN_DRIFT: Tuple[Dict[str, Any], Dict[str, Any]] = (
    LOGIN_FORM_TREE,  # Original - balanced options
    {  # Modified - decline hidden, accept emphasized
        "root": {
            "role": "window",
            "name": "Login",
            "children": [
                {
                    "role": "panel",
                    "name": "login_form",
                    "children": [
                        {"role": "text", "name": "title", "value": "Sign In"},
                        {"role": "textbox", "name": "email_input", "value": ""},
                        {"role": "textbox", "name": "password_input", "value": "", "secure": True},
                        {"role": "button", "name": "login_button"},
                        # Dark pattern: premium upsell added with deceptive design
                        {
                            "role": "panel",
                            "name": "upsell_modal",
                            "children": [
                                {"role": "text", "name": "upsell_text", "value": "Unlock Premium Features!"},
                                {"role": "button", "name": "accept_premium", "size": "large", "color": "green"},
                                {"role": "text", "name": "decline_premium", "size": "tiny", "color": "gray"},  # Disguised as text
                            ]
                        },
                        {"role": "link", "name": "forgot_password"},
                        {"role": "link", "name": "create_account"},
                    ]
                }
            ]
        }
    }
)


# Scenario 5: Invalid state transition (sequence drift)
SEQUENCE_VIOLATION_DRIFT: Dict[str, Any] = {
    "description": "User went from Gmail inbox directly to DoorDash offer without logout",
    "from_screen": "gmail_inbox",
    "to_screen": "doordash_offer",
    "expected_transitions": ["gmail_settings", "gmail_logout"],
    "actual_transition": "doordash_offer",
    "drift_type": "sequence",
    "severity": "warning"
}


# Alias for backwards compatibility
CONTENT_CHANGE_DRIFT = TEXT_CHANGE_DRIFT


def get_drift_scenario(name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Get a drift scenario by name.
    
    Args:
        name: Scenario identifier (missing_button, text_change, layout_shift, manipulative)
        
    Returns:
        Tuple of (original_tree, drifted_tree)
    """
    scenarios = {
        "missing_button": MISSING_BUTTON_DRIFT,
        "text_change": TEXT_CHANGE_DRIFT,
        "layout_shift": LAYOUT_SHIFT_DRIFT,
        "manipulative": MANIPULATIVE_PATTERN_DRIFT,
    }
    return scenarios.get(name.lower(), ({}, {}))
