"""Mock UI tree structures for testing."""
from typing import Dict, Any


DISCORD_CHAT_TREE: Dict[str, Any] = {
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
                            {"role": "button", "name": "send_button"},
                        ]
                    }
                ]
            }
        ]
    }
}


DOORDASH_OFFER_TREE: Dict[str, Any] = {
    "root": {
        "role": "window",
        "name": "DoorDash Driver",
        "children": [
            {
                "role": "panel",
                "name": "offer_card",
                "children": [
                    {"role": "text", "name": "restaurant_name", "value": "Pizza Palace"},
                    {"role": "text", "name": "payout", "value": "$12.50"},
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


GMAIL_INBOX_TREE: Dict[str, Any] = {
    "root": {
        "role": "window",
        "name": "Gmail",
        "children": [
            {
                "role": "panel",
                "name": "sidebar",
                "children": [
                    {"role": "button", "name": "compose"},
                    {"role": "button", "name": "inbox"},
                    {"role": "button", "name": "starred"},
                    {"role": "button", "name": "sent"},
                ]
            },
            {
                "role": "panel",
                "name": "email_list",
                "children": [
                    {
                        "role": "list",
                        "name": "message_list",
                        "children": [
                            {"role": "text", "name": "email_1", "value": "Meeting reminder"},
                            {"role": "text", "name": "email_2", "value": "Project update"},
                            {"role": "text", "name": "email_3", "value": "Weekly report"},
                        ]
                    }
                ]
            }
        ]
    }
}


SETTINGS_PANEL_TREE: Dict[str, Any] = {
    "root": {
        "role": "window",
        "name": "Settings",
        "children": [
            {
                "role": "panel",
                "name": "navigation",
                "children": [
                    {"role": "button", "name": "general"},
                    {"role": "button", "name": "privacy"},
                    {"role": "button", "name": "notifications"},
                    {"role": "button", "name": "account"},
                ]
            },
            {
                "role": "panel",
                "name": "content",
                "children": [
                    {"role": "checkbox", "name": "dark_mode", "checked": True},
                    {"role": "checkbox", "name": "notifications", "checked": False},
                    {"role": "textbox", "name": "username", "value": "user123"},
                    {"role": "button", "name": "save_button"},
                ]
            }
        ]
    }
}


LOGIN_FORM_TREE: Dict[str, Any] = {
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
                    {"role": "link", "name": "forgot_password"},
                    {"role": "link", "name": "create_account"},
                ]
            }
        ]
    }
}


def get_tree_by_name(name: str) -> Dict[str, Any]:
    """Get a mock tree by name.
    
    Args:
        name: Tree identifier (discord, doordash, gmail, settings, login)
        
    Returns:
        Mock tree structure
    """
    trees = {
        "discord": DISCORD_CHAT_TREE,
        "doordash": DOORDASH_OFFER_TREE,
        "gmail": GMAIL_INBOX_TREE,
        "settings": SETTINGS_PANEL_TREE,
        "login": LOGIN_FORM_TREE,
    }
    return trees.get(name.lower(), {})
