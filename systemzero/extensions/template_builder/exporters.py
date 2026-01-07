"""Export logs and templates to various formats."""
import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Optional


class LogExporter:
    """Export log entries to multiple formats."""

    def to_json(self, entries: List[Dict[str, Any]], output_path: Path) -> Path:
        """Export entries to JSON lines format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            for entry in entries:
                json.dump(entry, f)
                f.write("\n")

        return output_path

    def to_csv(self, entries: List[Dict[str, Any]], output_path: Path) -> Path:
        """Export entries to CSV format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if not entries:
            output_path.write_text("")
            return output_path

        # Extract fieldnames from first entry
        fieldnames = list(entries[0].keys())
        
        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry)

        return output_path

    def to_html(self, entries: List[Dict[str, Any]], output_path: Path, title: str = "Log Export") -> Path:
        """Export entries to HTML table."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: monospace; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    <table>
"""

        if entries:
            # Add header row
            fieldnames = list(entries[0].keys())
            html += "        <tr>\n"
            for field in fieldnames:
                html += f"            <th>{field}</th>\n"
            html += "        </tr>\n"

            # Add data rows
            for entry in entries:
                html += "        <tr>\n"
                for field in fieldnames:
                    value = entry.get(field, "")
                    if isinstance(value, dict):
                        value = json.dumps(value, indent=2)
                    html += f"            <td>{value}</td>\n"
                html += "        </tr>\n"

        html += """    </table>
</body>
</html>
"""
        output_path.write_text(html, encoding="utf-8")
        return output_path


class TemplateExporter:
    """Export templates to various formats."""

    def to_json(self, templates: Dict[str, Dict[str, Any]], output_path: Path) -> Path:
        """Export templates to JSON."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(templates, f, indent=2)

        return output_path
