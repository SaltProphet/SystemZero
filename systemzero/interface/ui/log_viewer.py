"""Consistency monitor for cross-app template compliance."""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Static, DataTable, Label, Button
from textual.reactive import reactive
from rich.text import Text
from rich.panel import Panel
from rich.table import Table

from core.logging import ImmutableLog
from core.baseline import TemplateLoader
from core.drift import DriftEvent


class AppMetricsTable(Static):
    """Table showing compliance metrics for each app."""
    
    def __init__(self, log_path: Optional[Path] = None):
        super().__init__()
        self.log_path = log_path or Path("logs/drift.log")
        self.metrics: Dict[str, dict] = {}
    
    def compose(self) -> ComposeResult:
        """Create metrics table."""
        yield Label("Multi-App Compliance Dashboard", classes="panel-title")
        yield DataTable(id="metrics-table")
    
    def on_mount(self) -> None:
        """Initialize table."""
        table = self.query_one("#metrics-table", DataTable)
        table.add_columns("App", "Templates", "Compliance", "Issues", "Trend")
        self.refresh_metrics()
    
    def refresh_metrics(self) -> None:
        """Recalculate compliance metrics."""
        try:
            if not self.log_path.exists():
                return
            
            log = ImmutableLog(str(self.log_path))
            entries = log.read_all()
            
            # Group events by app (from metadata)
            app_events: Dict[str, List[dict]] = defaultdict(list)
            for entry in entries:
                data = entry.get("data", {})
                app = data.get("metadata", {}).get("app", "Unknown")
                app_events[app].append(data)
            
            # Load templates for reference
            template_loader = TemplateLoader()
            templates = template_loader.load_all()
            
            # Calculate metrics
            table = self.query_one("#metrics-table", DataTable)
            table.clear()
            
            for app, events in app_events.items():
                if not events:
                    continue
                
                # Count events
                total_events = len(events)
                issues = sum(1 for e in events if e.get("severity") in ["warning", "critical"])
                
                # Calculate compliance (events within threshold)
                compliant = sum(1 for e in events if e.get("severity") == "info")
                compliance = (compliant / total_events * 100) if total_events > 0 else 0
                
                # Determine trend (simplified)
                recent = events[-10:] if len(events) > 10 else events
                recent_issues = sum(1 for e in recent if e.get("severity") in ["warning", "critical"])
                trend = "↑" if recent_issues > 2 else "↓" if recent_issues < 1 else "→"
                
                # Color code compliance
                compliance_color = (
                    "green" if compliance > 80 else
                    "yellow" if compliance > 60 else
                    "red"
                )
                
                table.add_row(
                    app,
                    str(len([t for t in templates.values() if t.get("metadata", {}).get("app") == app])),
                    Text(f"{compliance:.0f}%", style=compliance_color),
                    Text(str(issues), style="red" if issues > 0 else "green"),
                    Text(trend, style="yellow" if trend == "↑" else "green")
                )
        except Exception as e:
            pass


class AlertPanel(Static):
    """Panel showing active alerts and thresholds."""
    
    def compose(self) -> ComposeResult:
        """Create alert controls."""
        yield Label("Active Alerts", classes="panel-title")
        yield DataTable(id="alerts-table")
        yield Horizontal(
            Label("Compliance Threshold:"),
            Button("80%", id="threshold-80"),
            Button("70%", id="threshold-70"),
            Button("60%", id="threshold-60"),
            id="threshold-buttons"
        )
    
    def on_mount(self) -> None:
        """Initialize alerts table."""
        table = self.query_one("#alerts-table", DataTable)
        table.add_columns("App", "Alert", "Severity", "Time")
        self.refresh_alerts()
    
    def refresh_alerts(self) -> None:
        """Load and display alerts."""
        try:
            log_path = Path("logs/drift.log")
            if not log_path.exists():
                return
            
            log = ImmutableLog(str(log_path))
            entries = log.read_all()
            
            # Filter critical/warning events from last 24 hours
            cutoff = datetime.now() - timedelta(hours=24)
            critical_events = []
            
            for entry in entries:
                data = entry.get("data", {})
                if data.get("severity") in ["critical", "warning"]:
                    try:
                        ts = datetime.fromisoformat(entry.get("timestamp", ""))
                        if ts > cutoff:
                            critical_events.append(data)
                    except:
                        pass
            
            table = self.query_one("#alerts-table", DataTable)
            table.clear()
            
            for event in critical_events[-10:]:  # Show last 10 alerts
                app = event.get("metadata", {}).get("app", "Unknown")
                severity = event.get("severity", "info")
                drift_type = event.get("drift_type", "")
                timestamp = event.get("timestamp", "")
                
                severity_style = "red" if severity == "critical" else "yellow"
                time_str = timestamp.split("T")[1][:8] if "T" in timestamp else ""
                
                table.add_row(
                    app,
                    f"{drift_type} drift detected",
                    Text(severity, style=severity_style),
                    time_str
                )
        except Exception as e:
            pass


class TrendPanel(Static):
    """Panel showing compliance trends over time."""
    
    def compose(self) -> ComposeResult:
        """Create trend visualization."""
        yield Label("Compliance Trends (24h)", classes="panel-title")
        yield ScrollableContainer(
            Static("No trend data available", id="trend-content"),
            id="trend-scroll"
        )
    
    def on_mount(self) -> None:
        """Load trend data."""
        self.refresh_trends()
    
    def refresh_trends(self) -> None:
        """Calculate and display trend data."""
        try:
            log_path = Path("logs/drift.log")
            if not log_path.exists():
                return
            
            log = ImmutableLog(str(log_path))
            entries = log.read_all()
            
            # Group by hour
            hourly_stats = defaultdict(lambda: {"total": 0, "issues": 0})
            
            for entry in entries:
                try:
                    timestamp = entry.get("timestamp", "")
                    hour = timestamp[:13]  # YYYY-MM-DD HH
                    data = entry.get("data", {})
                    
                    hourly_stats[hour]["total"] += 1
                    if data.get("severity") in ["warning", "critical"]:
                        hourly_stats[hour]["issues"] += 1
                except:
                    pass
            
            # Create summary
            if hourly_stats:
                total_issues = sum(s["issues"] for s in hourly_stats.values())
                total_events = sum(s["total"] for s in hourly_stats.values())
                avg_compliance = ((total_events - total_issues) / total_events * 100) if total_events > 0 else 0
                
                summary = f"24h Summary: {total_events} events, {total_issues} issues, {avg_compliance:.0f}% compliance"
            else:
                summary = "No trend data available"
            
            content = self.query_one("#trend-content", Static)
            content.update(summary)
        except Exception as e:
            pass


class ConsistencyMonitorApp(App):
    """Cross-app template compliance monitor.
    
    Keyboard shortcuts:
    - q: Quit
    - r: Refresh
    - t: Configure thresholds
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
    
    #metrics-table {
        height: 1fr;
        border: solid blue;
    }
    
    #alerts-table {
        height: 10;
        border: solid red;
    }
    
    #threshold-buttons {
        padding: 1;
    }
    
    #trend-scroll {
        height: 8;
        border: solid green;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]
    
    def __init__(self, log_path: Optional[Path] = None):
        super().__init__()
        self.log_path = log_path
    
    def compose(self) -> ComposeResult:
        """Create application layout."""
        yield Header(show_clock=True)
        yield Container(
            AppMetricsTable(self.log_path),
            AlertPanel(),
            TrendPanel(),
            id="main-container"
        )
        yield Footer()
    
    def action_refresh(self) -> None:
        """Refresh all panels."""
        self.query_one(AppMetricsTable).refresh_metrics()
        self.query_one(AlertPanel).refresh_alerts()
        self.query_one(TrendPanel).refresh_trends()
    
    def on_button_pressed(self, event) -> None:
        """Handle button presses."""
        if event.button.id in ["threshold-80", "threshold-70", "threshold-60"]:
            # Would update threshold in real implementation
            pass


def render_consistency_monitor(log_path: Optional[Path] = None) -> None:
    """Launch the consistency monitor.
    
    Args:
        log_path: Path to drift log file (default: logs/drift.log)
    """
    app = ConsistencyMonitorApp(log_path)
    app.run()


if __name__ == "__main__":
    render_consistency_monitor()
