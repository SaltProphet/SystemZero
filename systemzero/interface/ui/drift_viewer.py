"""Forensic viewer for historical drift analysis."""
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Static, DataTable, Label, Input, Button
from textual.reactive import reactive
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel
import json

from core.logging import ImmutableLog
from core.drift import DriftEvent
from core.drift import DiffEngine


class FilterPanel(Static):
    """Panel for filtering events."""
    
    def compose(self) -> ComposeResult:
        """Create filter controls."""
        yield Label("Filters", classes="panel-title")
        yield Horizontal(
            Label("Type:"),
            Input(placeholder="layout, content, sequence...", id="filter-type"),
            Label("Severity:"),
            Input(placeholder="info, warning, critical", id="filter-severity"),
            Button("Apply", id="apply-filter", variant="primary"),
            Button("Export", id="export-events"),
            id="filter-controls"
        )


class EventList(Static):
    """Scrollable list of drift events."""
    
    current_page: reactive[int] = reactive(0)
    page_size: int = 50
    
    def __init__(self, log_path: Optional[Path] = None):
        super().__init__()
        self.log_path = log_path or Path("logs/drift.log")
        self.all_events: List[dict] = []
        self.filtered_events: List[dict] = []
        self.filters: Dict[str, str] = {}
    
    def compose(self) -> ComposeResult:
        """Create event list table."""
        yield Label("Event Timeline", classes="panel-title")
        yield DataTable(id="event-list-table")
        yield Horizontal(
            Button("◀ Previous", id="prev-page"),
            Label("Page 1", id="page-indicator"),
            Button("Next ▶", id="next-page"),
            id="pagination"
        )
    
    def on_mount(self) -> None:
        """Initialize table."""
        table = self.query_one("#event-list-table", DataTable)
        table.add_columns("ID", "Timestamp", "Type", "Severity", "Summary")
        table.cursor_type = "row"
        self.load_events()
    
    def load_events(self) -> None:
        """Load all events from log."""
        try:
            if not self.log_path.exists():
                return
            
            log = ImmutableLog(str(self.log_path))
            self.all_events = log.read_all()
            self.apply_filters()
        except Exception as e:
            pass
    
    def apply_filters(self, filters: Optional[Dict[str, str]] = None) -> None:
        """Filter events based on criteria."""
        if filters:
            self.filters = filters
        
        self.filtered_events = self.all_events
        
        if "type" in self.filters and self.filters["type"]:
            filter_type = self.filters["type"].lower()
            self.filtered_events = [
                e for e in self.filtered_events
                if filter_type in e.get("data", {}).get("drift_type", "").lower()
            ]
        
        if "severity" in self.filters and self.filters["severity"]:
            filter_severity = self.filters["severity"].lower()
            self.filtered_events = [
                e for e in self.filtered_events
                if filter_severity in e.get("data", {}).get("severity", "").lower()
            ]
        
        self.current_page = 0
        self.render_page()
    
    def render_page(self) -> None:
        """Render current page of events."""
        table = self.query_one("#event-list-table", DataTable)
        table.clear()
        
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_events = self.filtered_events[start_idx:end_idx]
        
        for idx, entry in enumerate(page_events):
            data = entry.get("data", {})
            timestamp = entry.get("timestamp", "")
            drift_type = data.get("drift_type", "unknown")
            severity = data.get("severity", "info")
            metadata = data.get("metadata", {})
            
            # Create summary
            summary = self._create_summary(metadata)
            
            # Color code by severity
            severity_style = {
                "critical": "red",
                "warning": "yellow",
                "info": "blue"
            }.get(severity, "white")
            
            table.add_row(
                str(start_idx + idx),
                timestamp.split("T")[0] if "T" in timestamp else timestamp[:10],
                Text(drift_type, style=severity_style),
                Text(severity, style=severity_style),
                summary
            )
        
        # Update page indicator
        total_pages = (len(self.filtered_events) + self.page_size - 1) // self.page_size
        page_label = self.query_one("#page-indicator", Label)
        page_label.update(f"Page {self.current_page + 1} of {max(1, total_pages)}")
    
    def _create_summary(self, metadata: Dict[str, Any]) -> str:
        """Create one-line summary of event."""
        if "missing_nodes" in metadata:
            nodes = metadata["missing_nodes"][:2]
            return f"Missing: {', '.join(nodes)}"
        elif "score" in metadata:
            return f"Match: {metadata['score']:.2f}"
        else:
            return "State change detected"
    
    def next_page(self) -> None:
        """Go to next page."""
        total_pages = (len(self.filtered_events) + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.render_page()
    
    def prev_page(self) -> None:
        """Go to previous page."""
        if self.current_page > 0:
            self.current_page -= 1
            self.render_page()
    
    def get_selected_event(self) -> Optional[dict]:
        """Get currently selected event."""
        table = self.query_one("#event-list-table", DataTable)
        if table.cursor_row is not None and table.cursor_row < len(self.filtered_events):
            start_idx = self.current_page * self.page_size
            return self.filtered_events[start_idx + table.cursor_row]
        return None


class DetailPanel(Static):
    """Panel showing detailed view of selected event."""
    
    def compose(self) -> ComposeResult:
        """Create detail display."""
        yield Label("Event Details", classes="panel-title")
        yield ScrollableContainer(
            Static("Select an event to view details", id="detail-content"),
            id="detail-scroll"
        )
        yield Horizontal(
            Button("View Diff", id="view-diff"),
            id="detail-actions"
        )
    
    def show_event(self, event: Optional[dict]) -> None:
        """Display event details."""
        content = self.query_one("#detail-content", Static)
        
        if not event:
            content.update("No event selected")
            return
        
        # Format event as JSON with syntax highlighting
        json_str = json.dumps(event, indent=2)
        syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
        content.update(syntax)


class DriftViewerApp(App):
    """Forensic viewer for drift analysis.
    
    Keyboard shortcuts:
    - q: Quit
    - r: Refresh
    - /: Focus filter
    - Enter: Show event details
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
    
    #event-list-table {
        height: 20;
        border: solid blue;
    }
    
    #detail-scroll {
        height: 1fr;
        border: solid green;
    }
    
    #filter-controls {
        padding: 1;
    }
    
    #pagination {
        padding: 1;
        align: center middle;
    }
    """
    
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("/", "focus_filter", "Filter"),
        ("e", "export", "Export"),
        ("d", "show_diff", "Diff"),
    ]
    
    def __init__(self, log_path: Optional[Path] = None):
        super().__init__()
        self.log_path = log_path
        self._diff_engine = DiffEngine()
        self._last_export_path: Optional[Path] = None
    
    def compose(self) -> ComposeResult:
        """Create application widgets."""
        yield Header(show_clock=True)
        yield Container(
            FilterPanel(),
            EventList(self.log_path),
            DetailPanel(),
            id="main-container"
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks."""
        if event.button.id == "apply-filter":
            self.apply_filters()
        elif event.button.id == "export-events":
            self.action_export()
        elif event.button.id == "next-page":
            event_list = self.query_one(EventList)
            event_list.next_page()
        elif event.button.id == "prev-page":
            event_list = self.query_one(EventList)
            event_list.prev_page()
        elif event.button.id == "view-diff":
            self.action_show_diff()
    
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Handle row selection in event list."""
        event_list = self.query_one(EventList)
        detail_panel = self.query_one(DetailPanel)
        
        selected_event = event_list.get_selected_event()
        detail_panel.show_event(selected_event)
    
    def apply_filters(self) -> None:
        """Apply filter inputs."""
        filter_type = self.query_one("#filter-type", Input).value
        filter_severity = self.query_one("#filter-severity", Input).value
        
        filters = {
            "type": filter_type,
            "severity": filter_severity
        }
        
        event_list = self.query_one(EventList)
        event_list.apply_filters(filters)
    
    def action_refresh(self) -> None:
        """Refresh event list."""
        event_list = self.query_one(EventList)
        event_list.load_events()
    
    def action_focus_filter(self) -> None:
        """Focus filter input."""
        filter_input = self.query_one("#filter-type", Input)
        filter_input.focus()

    def action_export(self) -> None:
        """Export filtered events to a JSON file."""
        event_list = self.query_one(EventList)
        events = event_list.filtered_events or []
        # Normalize entries to a consistent shape
        export_data = []
        for e in events:
            if isinstance(e, dict) and 'data' in e:
                export_data.append(e)
            else:
                export_data.append({"data": e})
        export_dir = Path("logs")
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = export_dir / "forensic_export.json"
        with open(export_path, "w", encoding="utf-8") as f:
            import json as _json
            _json.dump(export_data, f, indent=2)
        self._last_export_path = export_path
        # Update footer hint
        self.screen.sub_title = f"Exported {len(export_data)} events → {export_path}"

    def action_show_diff(self) -> None:
        """Render a diff view for the selected event if trees are available."""
        event_list = self.query_one(EventList)
        detail_panel = self.query_one(DetailPanel)
        selected = event_list.get_selected_event()
        if not selected:
            return
        # Try to locate before/after trees from common locations
        data = selected.get("data", selected)
        details = data.get("details", data.get("metadata", {})) if isinstance(data, dict) else {}
        before = details.get("before_tree") or details.get("before")
        after = details.get("after_tree") or details.get("after")
        if before and after:
            try:
                changes = self._diff_engine.diff(before, after)
                summary = self._diff_engine.diff_summary(changes)
                from rich.panel import Panel as _Panel
                detail_panel.query_one("#detail-content", Static).update(_Panel(summary, title="Diff Summary"))
                return
            except Exception:
                pass
        # Fallback: show event JSON
        detail_panel.show_event(selected)


def render_forensic_viewer(log_path: Optional[Path] = None) -> None:
    """Launch the forensic drift viewer.
    
    Args:
        log_path: Path to drift log file (default: logs/drift.log)
    """
    app = DriftViewerApp(log_path)
    app.run()


if __name__ == "__main__":
    render_forensic_viewer()
