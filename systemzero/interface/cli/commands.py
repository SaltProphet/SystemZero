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


def cmd_capture(output_path: Optional[str] = None, tree_path: Optional[str] = None) -> None:
    """Capture a UI tree and persist it to disk.
    
    Args:
        output_path: Optional capture file path (defaults to captures/capture_<timestamp>.json)
        tree_path: Optional JSON file to use instead of live capture (for testing/offline)
    """
    from extensions.capture_mode.recorder import Recorder
    from extensions.capture_mode.ui_tree_export import export_tree
    from extensions.capture_mode.signature_export import export_signatures

    display("[bold cyan]Capturing UI tree...[/bold cyan]")

    # If a tree file is provided, load it; otherwise capture live
    tree = None
    if tree_path:
        candidate = Path(tree_path)
        if candidate.exists():
            with open(candidate, "r", encoding="utf-8") as f:
                try:
                    tree = json.load(f)
                    display(f"Using provided tree file: {tree_path}")
                except json.JSONDecodeError:
                    display(f"[red]Invalid JSON in {tree_path}[/red]")
                    return
        else:
            display(f"[red]Tree file not found: {tree_path}[/red]")
            return

    recorder = Recorder()
    result = recorder.record(Path(output_path) if output_path else None, tree)

    # Also emit standalone normalized tree and signatures alongside payload for convenience
    path = Path(result["path"])
    export_tree(result.get("normalized", {}), path.with_suffix(".normalized.json"))
    export_signatures(result.get("signatures", {}), path.with_suffix(".signatures.json"))

    display(
        f"[green]✓ Capture saved[/green] → {path}\n"
        f"full={result['signatures']['full']}\n"
        f"struct={result['signatures']['structural']}\n"
        f"content={result['signatures']['content']}"
    )


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


def cmd_baseline(action: str, build_source: Optional[str] = None, build_out: Optional[str] = None,
                template_id: Optional[str] = None, app: Optional[str] = None) -> None:
    """Manage baseline templates (Phase 4).
    
    Args:
        action: Action (list, build, validate, show)
        build_source: Source capture file for build action
        build_out: Output YAML path for build action
        template_id: Template identifier for show/validate actions
        app: App name for template metadata
    """
    from extensions.template_builder.builder import TemplateBuilder
    from core.baseline import TemplateLoader

    if action == "list":
        display("[bold cyan]Available Templates[/bold cyan]")
        loader = TemplateLoader()
        templates = loader.load_all()
        if not templates:
            display("[yellow]No templates found[/yellow]")
        else:
            for screen_id in sorted(templates.keys()):
                display(f"  • {screen_id}")

    elif action == "build":
        if not build_source:
            display("[red]Error: --source required for build action[/red]")
            return
        if not build_out:
            build_out = f"core/baseline/templates/{Path(build_source).stem}.yaml"

        display(f"[bold cyan]Building template from {build_source}[/bold cyan]")
        builder = TemplateBuilder()
        
        screen_id = Path(build_source).stem
        try:
            template = builder.build_from_capture(Path(build_source), screen_id, app)
            builder.save_yaml(template, Path(build_out))
            display(f"[green]✓ Template saved[/green] → {build_out}")
            display(f"  screen_id: {screen_id}")
            display(f"  required_nodes: {len(template['required_nodes'])}")
            display(f"  structure_signature: {template['structure_signature'][:16]}...")
        except Exception as e:
            display(f"[red]Error: {e}[/red]")

    elif action == "validate":
        if not template_id:
            display("[red]Error: --template required for validate action[/red]")
            return
        loader = TemplateLoader()
        template = loader.get(template_id)
        if not template:
            display(f"[red]Template not found: {template_id}[/red]")
            return
        
        from core.baseline import TemplateValidator
        validator = TemplateValidator()
        is_valid, errors = validator.validate_with_errors(template)
        
        if is_valid:
            display(f"[green]✓ Template valid: {template_id}[/green]")
        else:
            display(f"[red]✗ Template invalid: {template_id}[/red]")
            for error in errors:
                display(f"  - {error}")

    elif action == "show":
        if not template_id:
            display("[red]Error: --template required for show action[/red]")
            return
        loader = TemplateLoader()
        template = loader.get(template_id)
        if not template:
            display(f"[red]Template not found: {template_id}[/red]")
            return
        
        import json
        display(json.dumps(template, indent=2))

    else:
        display(f"[red]Unknown action: {action}[/red]")


def cmd_export(log_path: Optional[str] = None, output_format: str = "json", output_path: Optional[str] = None) -> None:
    """Export log data or templates to various formats.
    
    Args:
        log_path: Path to log file to export
        output_format: Output format (json, csv, html)
        output_path: Output file path (defaults to logs/export_<timestamp>.<ext>)
    """
    from extensions.template_builder.exporters import LogExporter
    from core.logging import ImmutableLog
    from datetime import datetime

    if not log_path:
        log_path = "logs/systemzero.log"

    if not Path(log_path).exists():
        display(f"[red]Log file not found: {log_path}[/red]")
        return

    display(f"[bold cyan]Exporting {log_path} to {output_format}...[/bold cyan]")

    # Load log
    log = ImmutableLog(log_path)
    entries = log.get_entries()

    if not entries:
        display("[yellow]Log is empty[/yellow]")
        return

    # Determine output path
    if not output_path:
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S")
        ext = output_format if output_format in ["csv", "html"] else "json"
        output_path = f"logs/export_{timestamp}.{ext}"

    # Export
    exporter = LogExporter()
    try:
        if output_format == "json":
            exporter.to_json(entries, Path(output_path))
        elif output_format == "csv":
            exporter.to_csv(entries, Path(output_path))
        elif output_format == "html":
            exporter.to_html(entries, Path(output_path), title=f"Log Export from {log_path}")
        else:
            display(f"[red]Unsupported format: {output_format}[/red]")
            return

        display(f"[green]✓ Exported[/green] → {output_path}")
        display(f"  entries: {len(entries)}")
    except Exception as e:
        display(f"[red]Error: {e}[/red]")
