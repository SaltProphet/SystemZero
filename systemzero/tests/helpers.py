"""Integration test helpers for System//Zero pipeline testing."""
from typing import Dict, Any, Optional, List, Tuple
import tempfile
import os
from pathlib import Path

from core.normalization import TreeNormalizer, SignatureGenerator
from core.baseline import TemplateLoader, TemplateValidator
from core.drift import Matcher, DiffEngine, DriftEvent
from core.logging import ImmutableLog, HashChain


def run_pipeline(tree: Dict[str, Any], templates: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Execute the full System//Zero pipeline on a tree.
    
    Args:
        tree: Raw UI tree structure
        templates: Optional list of templates to match against
        
    Returns:
        Dictionary containing pipeline results:
            - normalized_tree: Normalized tree
            - signature: Tree signature
            - best_match: Best matching template (or None)
            - match_score: Match score (0.0-1.0)
            - drift_events: List of detected drift events
    """
    # Step 1: Normalize tree
    normalizer = TreeNormalizer()
    normalized = normalizer.normalize(tree)
    
    # Step 2: Generate signature
    sig_gen = SignatureGenerator()
    signature = sig_gen.generate(normalized)
    structural_sig = sig_gen.generate_structural(normalized)
    
    # Step 3: Match against templates
    matcher = Matcher()
    best_match = None
    match_score = 0.0
    
    if templates:
        result = matcher.find_best_match(normalized, templates)
        if result:
            best_match, match_score = result
    
    # Step 4: Detect drift
    drift_events = []
    if best_match and match_score < 0.8:
        drift_events.append(
            DriftEvent("layout", "warning", {
                "expected_template": best_match.get("screen_id"),
                "match_score": match_score,
                "signature": signature
            })
        )
    elif not best_match:
        drift_events.append(
            DriftEvent("layout", "critical", {
                "reason": "no_template_match",
                "signature": signature
            })
        )
    
    return {
        "normalized_tree": normalized,
        "signature": signature,
        "structural_signature": structural_sig,
        "best_match": best_match,
        "match_score": match_score,
        "drift_events": drift_events
    }


def verify_log_integrity(log_path: str) -> Tuple[bool, Optional[str]]:
    """Verify the hash chain integrity of a log file.
    
    Args:
        log_path: Path to the log file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        log = ImmutableLog(log_path, verify_on_load=True)
        is_valid = log.verify_integrity()
        
        if is_valid:
            return (True, None)
        else:
            return (False, "Hash chain verification failed")
    except Exception as e:
        return (False, f"Error verifying log: {str(e)}")


def create_temp_log() -> Tuple[str, ImmutableLog]:
    """Create a temporary log file for testing.
    
    Returns:
        Tuple of (log_path, log_instance)
    """
    temp_dir = tempfile.mkdtemp()
    log_path = os.path.join(temp_dir, "test_log.jsonl")
    log = ImmutableLog(log_path, verify_on_load=False)
    return (log_path, log)


def assert_drift_detected(
    tree: Dict[str, Any],
    template: Dict[str, Any],
    expected_type: str,
    expected_severity: str = None
) -> bool:
    """Assert that drift is detected when comparing tree to template.
    
    Args:
        tree: UI tree structure
        template: Expected template
        expected_type: Expected drift type (layout, content, sequence, manipulative)
        expected_severity: Expected severity (info, warning, critical)
        
    Returns:
        True if drift detected matches expectations
        
    Raises:
        AssertionError: If expectations not met
    """
    result = run_pipeline(tree, [template])
    drift_events = result["drift_events"]
    
    assert len(drift_events) > 0, "No drift detected"
    
    drift = drift_events[0]
    assert drift.drift_type == expected_type, \
        f"Expected drift type '{expected_type}', got '{drift.drift_type}'"
    
    if expected_severity:
        assert drift.severity == expected_severity, \
            f"Expected severity '{expected_severity}', got '{drift.severity}'"
    
    return True


def compare_trees(tree_a: Dict[str, Any], tree_b: Dict[str, Any]) -> Dict[str, Any]:
    """Compare two trees and return diff summary.
    
    Args:
        tree_a: First tree
        tree_b: Second tree
        
    Returns:
        Dictionary with diff results:
            - added_nodes: List of added node summaries
            - removed_nodes: List of removed node summaries
            - modified_nodes: List of modified node summaries
            - has_significant_changes: Boolean
    """
    normalizer = TreeNormalizer()
    diff_engine = DiffEngine()
    
    norm_a = normalizer.normalize(tree_a)
    norm_b = normalizer.normalize(tree_b)
    
    diff = diff_engine.diff(norm_a, norm_b)
    
    return {
        "added_nodes": diff.get("added", []),
        "removed_nodes": diff.get("removed", []),
        "modified_nodes": diff.get("modified", []),
        "has_significant_changes": diff_engine.has_significant_changes(diff)
    }


def load_all_test_templates() -> List[Dict[str, Any]]:
    """Load all templates from the templates directory.
    
    Returns:
        List of template dictionaries
    """
    loader = TemplateLoader()
    templates_dict = loader.load_all()
    return list(templates_dict.values())


def validate_template(template: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate a template structure.
    
    Args:
        template: Template dictionary to validate
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    validator = TemplateValidator()
    errors = []
    
    # Check required fields
    required_fields = ["screen_id", "required_nodes"]
    for field in required_fields:
        if field not in template:
            errors.append(f"Missing required field: {field}")
    
    # Validate using TemplateValidator
    try:
        is_valid = validator.validate(template)
        if not is_valid:
            errors.append("Template validation failed")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
        is_valid = False
    
    return (is_valid and len(errors) == 0, errors)


def simulate_drift_detection_pipeline(
    original_tree: Dict[str, Any],
    drifted_tree: Dict[str, Any],
    template: Dict[str, Any],
    log_path: Optional[str] = None
) -> Dict[str, Any]:
    """Simulate complete drift detection and logging.
    
    Args:
        original_tree: Baseline tree
        drifted_tree: Tree with drift
        template: Expected template
        log_path: Optional log file path (temp file if None)
        
    Returns:
        Dictionary with:
            - original_result: Pipeline result for original tree
            - drifted_result: Pipeline result for drifted tree
            - diff: Diff between trees
            - log_entries: Logged events
    """
    # Create log if needed
    if log_path is None:
        log_path, log = create_temp_log()
    else:
        log = ImmutableLog(log_path)
    
    # Run pipeline on both trees
    original_result = run_pipeline(original_tree, [template])
    drifted_result = run_pipeline(drifted_tree, [template])
    
    # Compute diff
    diff = compare_trees(original_tree, drifted_tree)
    
    # Log drift events
    for drift in drifted_result["drift_events"]:
        log.append(drift)
    
    return {
        "original_result": original_result,
        "drifted_result": drifted_result,
        "diff": diff,
        "log_path": log_path,
        "log_entries": log.get_entries()
    }
