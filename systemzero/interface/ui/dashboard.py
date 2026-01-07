"""Live dashboard for real-time drift monitoring."""
import asyncio
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, DataTable, Label
from textual.reactive import reactive
from rich.table import Table
from rich.text import Text

from core.logging import ImmutableLog
from core.drift import DriftEvent


class EventPanel(Static):
    """Panel displaying recent drift events."""
    
    events: reactive[List[dict]] = reactive([])
    
    def __init__(self, log_path: Optional[Path] = None):
        super().__init__()
        self.log_path = log_path or Path("logs/drift.log")
        self.max_events = 20
    
    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Label("Recent Drift Events", classes="panel-title")
        yield DataTable(id="events-table")
    
    def on_mount(self) -> None:
        """Initialize table when mounted."""
        table = self.query_one("#events-table", DataTable)
        table.add_columns("Time", "Type", "Severity", "Details")
        self.refresh_events()
    
    def refresh_events(self) -> None:
        """Reload events from log."""
        try:
            if not self.log_path.exists():
                return
            
            log = ImmutableLog(str(self.log_path))
            entries = log.read_all()
            
            # Take last N events
            recent = entries[-self.max_events:] if len(entries) > self.max_events else entries
            
            table = self.query_one("#events-table", DataTable)
            table.clear()
            
            for entry in reversed(recent):  # Show newest first
                data = entry.get("data", {})
                timestamp = entry.get("timestamp", "")
                
                # Parse DriftEvent data
                drift_type = data.get("drift_type", "unknown")
                severity = data.get("severity", "info")
                metadata = data.get("metadata", {})
                
                # Format details
                details = self._format_details(metadata)
                
                # Add row with color based on severity
                severity_color = {
                    "critical": "red",
                    "warning": "yellow",
                    "info": "blue"
                }.get(severity, "white")
                
                table.add_row(
                    timestamp.split("T")[1][:8] if "T" in timestamp else timestamp[:8],
                    Text(drift_type, style=severity_color),
                    Text(severity, style=severity_color),
                    details[:50]
                )
        except Exception as e:
            # Fail silently in UI
            pass
    
    def _format_details(self, metadata: dict) -> str:
        """Format metadata as readable string."""
        if not metadata:
            return "No details"
        
        # Extract key information
        if "missing_nodes" in metadata:
            return f"Missing: {', '.join(metadata['missing_nodes'][:3])}"
        elif "expected_sig" in metadata:
            return f"Signature mismatch"
        elif "score" in metadata:
            return f"Match score: {metadata['score']:.2f}"
        else:
            # Generic format
            items = [f"{k}={v}" for k, v in list(metadata.items())[:2]]
            return ", ".join(items)


class StatusPanel(Static):
    """Panel showing system status."""
    
    def compose(self) -> ComposeResult:
        """Create status indicators."""
        yield Label("System Status", classes="panel-title")
        yield Label("● Monitoring Active", id="status-indicator", classes="status-active")
        yield Label(f"Last Update: {datetime.now().strftime('%H:%M:%S')}", id="last-update")
    
    def update_status(self) -> None:
        """Refresh status timestamp."""
        label = self.query_one("#last-update", Label)
        label.update(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")


class DashboardApp(App):
    """Live monitoring dashboard for System//Zero.
    
    Keyboard shortcuts:
    - q: Quit
    - r: Refresh
    - f: Focus events table
    """
    
    CSS = """
    Screen {
        background: $surface;
    }
    
    .panel-title {
        background: $primary;
        color: $text;
        padding: 1;
        text-style: bold;
    }
    
    .status-active {
        color: green;
        padding: 1;
    }
    
    #events-table {
        height: 1fr;
        border: solid green;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("f", "focus_events", "Focus Events"),
    ]
    
    def __init__(self, log_path: Optional[Path] = None):
        super().__init__()
        self.log_path = log_path
        self.auto_refresh = True
        self.refresh_interval = 5.0  # seconds
    
    def compose(self) -> ComposeResult:
        """Create application widgets."""
        yield Header(show_clock=True)
        yield Container(
            StatusPanel(),
            EventPanel(self.log_path),
            id="main-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        """Start auto-refresh when app starts."""
        if self.auto_refresh:
            self.set_interval(self.refresh_interval, self.action_refresh)
    
    def action_refresh(self) -> None:
        """Refresh all data."""
        event_panel = self.query_one(EventPanel)
        event_panel.refresh_events()
        
        status_panel = self.query_one(StatusPanel)
        status_panel.update_status()
    
    def action_focus_events(self) -> None:
        """Focus the events table."""
        table = self.query_one("#events-table", DataTable)
        table.focus()


def render_dashboard(log_path: Optional[Path] = None) -> None:
    """Launch the live dashboard.
    
    Args:
        log_path: Path to drift log file (default: logs/drift.log)
    """
    app = DashboardApp(log_path)
    app.run()


if __name__ == "__main__":
    render_dashboard()
