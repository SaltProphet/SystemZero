"""CLI commands for System//Zero."""
from typing import Optional
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.normalization import TreeNormalizer, SignatureGenerator
from core.baseline import TemplateLoader, TemplateValidator
from core.drift import Matcher, DiffEngine, DriftEvent
from core.logging import ImmutableLog
from tests.helpers import run_pipeline
from tests.fixtures.mock_trees import DISCORD_CHAT_TREE, DOORDASH_OFFER_TREE, LOGIN_FORM_TREE
from interface.cli.display import (
    display, display_tree_structure, display_pipeline_results,
    display_drift_table, display_log_entry, display_status_dashboard
)


def cmd_simulate(tree_path: Optional[str] = None, template: Optional[str] = None) -> None:
    """Simulate pipeline execution with a mock UI tree.
    
    Args:
        tree_path: Path to JSON file containing UI tree (or use fixture name)
        template: Template ID to match against (default: auto-match)
    """
    display(f"[bold cyan]System//Zero Pipeline Simulation[/bold cyan]\n")
    
    # Load tree
    tree = None
    if tree_path:
        # Check if it's a fixture name
        fixtures = {
            'discord': DISCORD_CHAT_TREE,
            'doordash': DOORDASH_OFFER_TREE,
            'login': LOGIN_FORM_TREE
        }
        if tree_path.lower() in fixtures:
            tree = fixtures[tree_path.lower()]
            display(f"Using fixture: {tree_path}")
        elif Path(tree_path).exists():
            with open(tree_path, 'r') as f:
                tree = json.load(f)
            display(f"Loaded tree from: {tree_path}")
        else:
            display(f"[red]Error: Tree file not found: {tree_path}[/red]")
            return
    else:
        # Default to Discord fixture
        tree = DISCORD_CHAT_TREE
        display("Using default fixture: Discord Chat")
    
    # Display tree structure
    display_tree_structure(tree, title="Input Tree")
    
    # Run pipeline
    display("\n[yellow]Running pipeline...[/yellow]")
    results = run_pipeline(tree)
    
    # Display results
    display_pipeline_results(results)


def cmd_drift(log_path: Optional[str] = None, filter_type: Optional[str] = None, 
              severity: Optional[str] = None) -> None:
    """Display drift events from log.
    
    Args:
        log_path: Path to log file (default: logs/systemzero.log)
        filter_type: Filter by drift type (layout, content, sequence, manipulative)
        severity: Filter by severity (info, warning, critical)
    """
    if not log_path:
        log_path = "logs/systemzero.log"
    
    display(f"[bold cyan]Drift Events from {log_path}[/bold cyan]\n")
    
    # Check if log exists
    if not Path(log_path).exists():
        display(f"[yellow]No log file found at {log_path}[/yellow]")
        return
    
    # Load log
    log = ImmutableLog(log_path)
    entries = log.get_entries()
    
    if not entries:
        display("[yellow]Log is empty[/yellow]")
        return
    
    # Filter drift events
    drift_entries = []
    for entry in entries:
        data = entry.get('data', {})
        if 'drift_type' in data:
            # Apply filters
            if filter_type and data.get('drift_type') != filter_type:
                continue
            if severity and data.get('severity') != severity:
                continue
            drift_entries.append(data)
    
    if not drift_entries:
        display("[yellow]No drift events found matching criteria[/yellow]")
        return
    
    # Display drift table
    display_drift_table(drift_entries)
    
    # Summary statistics
    display(f"\n[bold]Total drift events: {len(drift_entries)}[/bold]")
    
    # Count by type
    type_counts = {}
    for entry in drift_entries:
        dtype = entry.get('drift_type', 'unknown')
        type_counts[dtype] = type_counts.get(dtype, 0) + 1
    
    display("\n[bold]By Type:[/bold]")
    for dtype, count in sorted(type_counts.items()):
        display(f"  • {dtype}: {count}")


def cmd_replay(log_path: Optional[str] = None, start: int = 0, end: Optional[int] = None,
               entry: Optional[int] = None) -> None:
    """Replay events from log with timeline navigation.
    
    Args:
        log_path: Path to log file
        start: Starting entry index
        end: Ending entry index (None = all)
        entry: View single entry by index
    """
    if not log_path:
        log_path = "logs/systemzero.log"
    
    display(f"[bold cyan]Log Replay: {log_path}[/bold cyan]\n")
    
    # Check if log exists
    if not Path(log_path).exists():
        display(f"[yellow]No log file found at {log_path}[/yellow]")
        return
    
    # Load log
    log = ImmutableLog(log_path)
    
    # Verify integrity
    display("[yellow]Verifying hash chain integrity...[/yellow]")
    if log.verify_integrity():
        display("[green]✓ Hash chain valid[/green]\n")
    else:
        display("[red]✗ Hash chain INVALID - log may be tampered![/red]\n")
    
    # Get entries
    if entry is not None:
        entries = [log.get_entries()[entry]] if entry < log.get_entry_count() else []
        start_idx = entry
    else:
        entries = log.get_entries(start, end)
        start_idx = start
    
    total = log.get_entry_count()
    
    if not entries:
        display("[yellow]No entries in range[/yellow]")
        return
    
    # Display entries
    for i, entry_data in enumerate(entries):
        display_log_entry(entry_data, start_idx + i, total)


def cmd_status() -> None:
    """Display current system status."""
    display("[bold green]═══ System//Zero Status ═══[/bold green]\n")
    
    # Gather status information
    status = {
        'log_path': 'logs/systemzero.log',
        'log_size': 0,
        'template_count': 0,
        'integrity': 'Unknown',
        'recent_events': [],
        'drift_counts': {}
    }
    
    # Check log
    log_path = Path('logs/systemzero.log')
    if log_path.exists():
        log = ImmutableLog(str(log_path))
        status['log_size'] = log.get_entry_count()
        status['integrity'] = 'Valid' if log.verify_integrity() else 'INVALID'
        
        # Get recent events
        recent = log.get_entries(max(0, status['log_size'] - 5))
        for entry in recent:
            data = entry.get('data', {})
            evt_type = data.get('event_type', data.get('drift_type', 'unknown'))
            status['recent_events'].append(f"{evt_type} at {entry.get('timestamp', '?')}")
        
        # Count drift types
        for entry in log.get_entries():
            data = entry.get('data', {})
            if 'drift_type' in data:
                dtype = data['drift_type']
                status['drift_counts'][dtype] = status['drift_counts'].get(dtype, 0) + 1
    
    # Check templates
    template_dir = Path('core/baseline/templates')
    if template_dir.exists():
        status['template_count'] = len(list(template_dir.glob('*.yaml')))
    
    # Display dashboard
    display_status_dashboard(status)


def cmd_capture() -> None:
    """Start capture mode to record new screens."""
    display("[SZ] capture: not yet implemented (Phase 4)")
    # TODO Phase 4: Implement capture mode


def cmd_dashboard(log_path: Optional[str] = None) -> None:
    """Launch live monitoring dashboard.
    
    Args:
        log_path: Path to drift log file (default: logs/drift.log)
    """
    from interface.ui.dashboard import render_dashboard
    
    display("[bold cyan]Launching Live Dashboard...[/bold cyan]")
    
    log_file = Path(log_path or "logs/systemzero.log")
    render_dashboard(log_file)


def cmd_forensic(log_path: Optional[str] = None) -> None:
    """Launch forensic drift viewer for historical analysis.
    
    Args:
        log_path: Path to drift log file (default: logs/drift.log)
    """
    from interface.ui.drift_viewer import render_forensic_viewer
    
    display("[bold cyan]Launching Forensic Viewer...[/bold cyan]")
    
    log_file = Path(log_path or "logs/systemzero.log")
    render_forensic_viewer(log_file)


def cmd_consistency(log_path: Optional[str] = None) -> None:
    """Launch cross-app consistency monitor.
    
    Args:
        log_path: Path to drift log file (default: logs/drift.log)
    """
    from interface.ui.log_viewer import render_consistency_monitor
    
    display("[bold cyan]Launching Consistency Monitor...[/bold cyan]")
    
    log_file = Path(log_path or "logs/systemzero.log")
    render_consistency_monitor(log_file)


def cmd_baseline(action: str, template_id: Optional[str] = None) -> None:
    """Manage baseline templates.
    
    Args:
        action: Action to perform (list, show, validate, export)
        template_id: Template identifier for show/validate actions
    """
    print(f"[SZ] baseline: action={action}, template={template_id}")
    # TODO Phase 5: Implement baseline management


def cmd_export(log_path: str, output_format: str = "json") -> None:
    """Export log data to various formats.
    
    Args:
        log_path: Path to log file
        output_format: Output format (json, csv, html)
    """
    print(f"[SZ] export: log={log_path}, format={output_format}")
    # TODO Phase 5: Implement export functionality
