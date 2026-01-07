"""CLI commands for System//Zero."""
from typing import Optional
import json
from pathlib import Path


def cmd_status() -> None:
    """Display current system status."""
    print("[SZ] status: not yet implemented")


def cmd_drift(log_path: Optional[str] = None, filter_type: Optional[str] = None) -> None:
    """Display drift events from log.
    
    Args:
        log_path: Path to log file (default: logs/systemzero.log)
        filter_type: Filter by drift type (layout, content, sequence, manipulative)
    """
    print("[SZ] drift: not yet implemented")
    # TODO Phase 2: Implement drift viewer


def cmd_replay(log_path: Optional[str] = None, start: int = 0, end: Optional[int] = None) -> None:
    """Replay events from log with timeline navigation.
    
    Args:
        log_path: Path to log file
        start: Starting entry index
        end: Ending entry index (None = all)
    """
    print("[SZ] replay: not yet implemented")
    # TODO Phase 2: Implement replay viewer


def cmd_simulate(tree_path: str, template: Optional[str] = None) -> None:
    """Simulate pipeline execution with a mock UI tree.
    
    Args:
        tree_path: Path to JSON file containing UI tree
        template: Template ID to match against (default: auto-match)
    """
    print(f"[SZ] simulate: tree={tree_path}, template={template}")
    # TODO Phase 2: Implement simulation mode
    

def cmd_capture() -> None:
    """Start capture mode to record new screens."""
    print("[SZ] capture: not yet implemented")
    # TODO Phase 4: Implement capture mode


def cmd_baseline(action: str, template_id: Optional[str] = None) -> None:
    """Manage baseline templates.
    
    Args:
        action: Action to perform (list, show, validate, export)
        template_id: Template identifier for show/validate actions
    """
    print(f"[SZ] baseline: action={action}, template={template_id}")
    # TODO Phase 5: Implement baseline management


<<<<<<< Updated upstream
def cmd_export(log_path: str, output_format: str = "json") -> None:
=======
def cmd_export(log_path: Optional[str] = None, output_format: str = "json", output_path: Optional[str] = None) -> None:
>>>>>>> Stashed changes
    """Export log data to various formats.
    
    Args:
        log_path: Path to log file
        output_format: Output format (json, csv, html)
    """
<<<<<<< Updated upstream
    print(f"[SZ] export: log={log_path}, format={output_format}")
    # TODO Phase 5: Implement export functionality
=======
    from datetime import datetime
    from extensions.template_builder.exporters import LogExporter
    from core.logging import ImmutableLog

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
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
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


def cmd_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False) -> None:
    """Start FastAPI REST server.
    
    Args:
        host: Server host (default: 0.0.0.0)
        port: Server port (default: 8000)
        reload: Auto-reload on code changes (development only)
    """
    import uvicorn
    from interface.api.server import app

    display(f"[bold cyan]Starting System//Zero API server[/bold cyan]")
    display(f"  Host: {host}")
    display(f"  Port: {port}")
    display(f"  Docs: http://{host}:{port}/docs")
    
    uvicorn.run(app, host=host, port=port, reload=reload, log_level="info")
>>>>>>> Stashed changes
