"""Display utilities using Rich library."""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax
from rich import box
from typing import Dict, Any, List
import json

console = Console()


def display(msg: str) -> None:
    """Display a simple message."""
    console.print(msg)


def display_tree_structure(tree: Dict[str, Any], title: str = "UI Tree") -> None:
    """Display tree structure with Rich."""
    rich_tree = Tree(f"[bold cyan]{title}[/bold cyan]")
    _build_rich_tree(tree.get('root', tree), rich_tree)
    console.print(rich_tree)


def _build_rich_tree(node: Dict[str, Any], parent: Tree) -> None:
    """Recursively build Rich tree."""
    if not isinstance(node, dict):
        return
    
    role = node.get('role', 'unknown')
    name = node.get('name', '')
    label = f"[yellow]{role}[/yellow]: {name}" if name else f"[yellow]{role}[/yellow]"
    
    branch = parent.add(label)
    
    children = node.get('children', [])
    for child in children:
        _build_rich_tree(child, branch)


def display_pipeline_results(results: Dict[str, Any]) -> None:
    """Display pipeline execution results."""
    console.print("\n[bold green]Pipeline Execution Results[/bold green]\n")
    
    # Signature
    sig = results.get('signature', 'N/A')
    console.print(Panel(f"[cyan]{sig[:32]}...[/cyan]", title="Signature (truncated)", border_style="cyan"))
    
    # Best match
    match = results.get('best_match')
    score = results.get('match_score', 0.0)
    if match:
        match_text = f"Template: [yellow]{match.get('screen_id', 'unknown')}[/yellow]\nScore: [green]{score:.2%}[/green]"
        console.print(Panel(match_text, title="Best Match", border_style="green"))
    else:
        console.print(Panel("[red]No match found[/red]", title="Best Match", border_style="red"))
    
    # Drift events
    drifts = results.get('drift_events', [])
    if drifts:
        console.print(f"\n[bold red]⚠ Drift Detected: {len(drifts)} events[/bold red]\n")
        for drift in drifts:
            console.print(f"  • [{drift.severity}] {drift.drift_type}: {drift.details}")
    else:
        console.print("\n[bold green]✓ No Drift Detected[/bold green]\n")


def display_drift_table(entries: List[Dict[str, Any]]) -> None:
    """Display drift events in a table."""
    table = Table(title="Drift Events", box=box.ROUNDED)
    table.add_column("#", style="cyan", width=6)
    table.add_column("Timestamp", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Severity", style="red")
    table.add_column("Details", style="white")
    
    for entry in entries:
        if 'drift_type' in entry:
            idx = str(entry.get('entry_id', '?'))
            ts = str(entry.get('timestamp', '?'))[:10]
            dtype = entry.get('drift_type', 'unknown')
            severity = entry.get('severity', 'info')
            details = str(entry.get('details', ''))[:50]
            table.add_row(idx, ts, dtype, severity, details)
    
    console.print(table)


def display_log_entry(entry: Dict[str, Any], index: int, total: int) -> None:
    """Display a single log entry."""
    console.print(f"\n[bold cyan]Entry {index + 1} / {total}[/bold cyan]")
    console.print(Panel(
        json.dumps(entry, indent=2),
        title=f"Entry ID: {entry.get('entry_id', '?')}",
        border_style="blue"
    ))


def display_status_dashboard(status: Dict[str, Any]) -> None:
    """Display system status dashboard."""
    console.print("\n[bold green]═══ System//Zero Status ═══[/bold green]\n")
    
    # Configuration
    config_text = f"""Log Path: {status.get('log_path', 'N/A')}
Log Size: {status.get('log_size', 0)} entries
Templates: {status.get('template_count', 0)} loaded
Integrity: {status.get('integrity', 'Unknown')}"""
    console.print(Panel(config_text, title="Configuration", border_style="cyan"))
    
    # Recent activity
    if status.get('recent_events'):
        console.print("\n[bold]Recent Events:[/bold]")
        for event in status['recent_events'][:5]:
            console.print(f"  • {event}")
    
    # Drift summary
    drift_counts = status.get('drift_counts', {})
    if drift_counts:
        console.print("\n[bold]Drift Summary:[/bold]")
        for dtype, count in drift_counts.items():
            console.print(f"  • {dtype}: {count}")
