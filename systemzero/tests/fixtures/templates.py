"""Programmatic template generation for testing."""
from typing import Dict, Any, List
from core.normalization import TreeNormalizer, SignatureGenerator


def build_template(
    screen_id: str,
    tree: Dict[str, Any],
    required_nodes: List[str],
    valid_transitions: List[str] = None
) -> Dict[str, Any]:
    """Build a template from a tree structure.
    
    Args:
        screen_id: Unique screen identifier
        tree: UI tree structure
        required_nodes: List of required node names
        valid_transitions: List of valid next screen IDs
        
    Returns:
        Template dictionary ready for YAML export
    """
    normalizer = TreeNormalizer()
    sig_gen = SignatureGenerator()
    
    normalized = normalizer.normalize(tree)
    signature = sig_gen.generate(normalized)
    structural_sig = sig_gen.generate_structural(normalized)
    
    return {
        "screen_id": screen_id,
        "required_nodes": required_nodes,
        "structure_signature": structural_sig,
        "full_signature": signature,
        "valid_transitions": valid_transitions or []
    }


def template_from_tree(tree: Dict[str, Any], screen_id: str = "auto_generated") -> Dict[str, Any]:
    """Generate a basic template from a tree by extracting node names.
    
    Args:
        tree: UI tree structure
        screen_id: Screen identifier
        
    Returns:
        Template dictionary
    """
    required_nodes = _extract_node_names(tree)
    return build_template(screen_id, tree, required_nodes, [])


# Alias for backwards compatibility
generate_template = template_from_tree


def _extract_node_names(node: Any, names: List[str] = None) -> List[str]:
    """Recursively extract all node names from a tree."""
    if names is None:
        names = []
    
    if isinstance(node, dict):
        if "name" in node and node["name"] not in names:
            names.append(node["name"])
        
        for key, value in node.items():
            if key == "children" and isinstance(value, list):
                for child in value:
                    _extract_node_names(child, names)
            elif isinstance(value, dict):
                _extract_node_names(value, names)
    
    return names


# Pre-built template builders for common screens
def discord_chat_template() -> Dict[str, Any]:
    """Build Discord chat template."""
    from .mock_trees import DISCORD_CHAT_TREE
    return build_template(
        screen_id="discord_chat",
        tree=DISCORD_CHAT_TREE,
        required_nodes=["message_list", "input_box", "send_button"],
        valid_transitions=["discord_settings", "discord_voice"]
    )


def doordash_offer_template() -> Dict[str, Any]:
    """Build DoorDash offer template."""
    from .mock_trees import DOORDASH_OFFER_TREE
    return build_template(
        screen_id="doordash_offer",
        tree=DOORDASH_OFFER_TREE,
        required_nodes=["restaurant_name", "payout", "accept_button", "decline_button"],
        valid_transitions=["doordash_active_delivery", "doordash_home"]
    )


def gmail_inbox_template() -> Dict[str, Any]:
    """Build Gmail inbox template."""
    from .mock_trees import GMAIL_INBOX_TREE
    return build_template(
        screen_id="gmail_inbox",
        tree=GMAIL_INBOX_TREE,
        required_nodes=["compose", "inbox", "message_list"],
        valid_transitions=["gmail_compose", "gmail_settings"]
    )


def settings_panel_template() -> Dict[str, Any]:
    """Build settings panel template."""
    from .mock_trees import SETTINGS_PANEL_TREE
    return build_template(
        screen_id="settings_panel",
        tree=SETTINGS_PANEL_TREE,
        required_nodes=["general", "privacy", "notifications", "save_button"],
        valid_transitions=["main_screen"]
    )


def login_form_template() -> Dict[str, Any]:
    """Build login form template."""
    from .mock_trees import LOGIN_FORM_TREE
    return build_template(
        screen_id="login_form",
        tree=LOGIN_FORM_TREE,
        required_nodes=["email_input", "password_input", "login_button"],
        valid_transitions=["main_screen", "signup_form"]
    )
