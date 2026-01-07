"""FastAPI server for System//Zero REST API."""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from core.accessibility import TreeCapture
from core.normalization import TreeNormalizer, SignatureGenerator
from core.baseline import TemplateLoader, TemplateValidator
from core.drift import Matcher, DriftEvent
from core.logging import ImmutableLog
from extensions.capture_mode.recorder import Recorder
from extensions.template_builder.builder import TemplateBuilder
from extensions.template_builder.exporters import LogExporter


# Pydantic models for request/response validation
class CaptureRequest(BaseModel):
    """Request body for capture endpoint."""
    tree: Optional[Dict[str, Any]] = None
    app: Optional[str] = None


class CaptureResponse(BaseModel):
    """Response body for capture."""
    path: str
    normalized: Dict[str, Any]
    signatures: Dict[str, str]
    captured_at: str


class TemplateResponse(BaseModel):
    """Response body for template."""
    screen_id: str
    required_nodes: List[str]
    structure_signature: str
    metadata: Dict[str, Any]


class LogEntry(BaseModel):
    """Log entry response."""
    timestamp: str
    data: Dict[str, Any]
    entry_hash: str


class StatusResponse(BaseModel):
    """System status response."""
    version: str
    log_path: str
    log_size: int
    template_count: int
    log_integrity: str
    recent_events: List[str]


class DashboardData(BaseModel):
    """Dashboard data response."""
    timestamp: str
    recent_drifts: List[Dict[str, Any]]
    compliance: float
    total_events: int


# Create FastAPI app
app = FastAPI(
    title="System//Zero API",
    description="REST API for environment parser drift detection",
    version="0.5.0"
)


@app.get("/")
def root():
    """API root endpoint."""
    return {
        "service": "System//Zero",
        "version": "0.5.0",
        "docs": "/docs",
        "endpoints": {
            "captures": "POST /captures",
            "templates": "GET /templates, POST /templates",
            "logs": "GET /logs",
            "status": "GET /status",
            "dashboard": "GET /dashboard"
        }
    }


@app.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    """Get system status."""
    log_path = Path("logs/systemzero.log")
    log_size = 0
    log_integrity = "Unknown"
    recent_events = []

    if log_path.exists():
        try:
            log = ImmutableLog(str(log_path))
            log_size = log.get_entry_count()
            log_integrity = "Valid" if log.verify_integrity() else "INVALID"

            recent = log.get_entries(max(0, log_size - 5))
            for entry in recent:
                data = entry.get("data", {})
                evt_type = data.get("event_type", data.get("drift_type", "unknown"))
                recent_events.append(f"{evt_type} at {entry.get('timestamp', '?')}")
        except Exception as e:
            log_integrity = f"Error: {e}"

    # Count templates
    template_loader = TemplateLoader()
    templates = template_loader.load_all()
    template_count = len(templates)

    return StatusResponse(
        version="0.5.0",
        log_path=str(log_path),
        log_size=log_size,
        template_count=template_count,
        log_integrity=log_integrity,
        recent_events=recent_events
    )


@app.post("/captures", response_model=CaptureResponse)
def create_capture(request: CaptureRequest) -> CaptureResponse:
    """Capture a UI tree."""
    try:
        recorder = Recorder()
        result = recorder.record(tree=request.tree)

        return CaptureResponse(
            path=result["path"],
            normalized=result.get("normalized", {}),
            signatures=result.get("signatures", {}),
            captured_at=result.get("captured_at", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates", response_model=List[TemplateResponse])
def list_templates():
    """List all available templates."""
    try:
        loader = TemplateLoader()
        templates = loader.load_all()

        results = []
        for template in templates.values():
            results.append(TemplateResponse(
                screen_id=template.get("screen_id", "unknown"),
                required_nodes=template.get("required_nodes", []),
                structure_signature=template.get("structure_signature", ""),
                metadata=template.get("metadata", {})
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/templates/{screen_id}", response_model=TemplateResponse)
def get_template(screen_id: str) -> TemplateResponse:
    """Get a specific template by ID."""
    try:
        loader = TemplateLoader()
        template = loader.get(screen_id)

        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {screen_id}")

        return TemplateResponse(
            screen_id=template.get("screen_id", screen_id),
            required_nodes=template.get("required_nodes", []),
            structure_signature=template.get("structure_signature", ""),
            metadata=template.get("metadata", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/templates")
def build_template(capture_path: str = Query(...), screen_id: str = Query(...), app: str = Query("unknown")):
    """Build a template from a capture file."""
    try:
        builder = TemplateBuilder()
        template = builder.build_from_capture(Path(capture_path), screen_id, app)

        return template
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs", response_model=List[LogEntry])
def get_logs(limit: int = Query(100), offset: int = Query(0)):
    """Get log entries."""
    try:
        log_path = Path("logs/systemzero.log")
        if not log_path.exists():
            return []

        log = ImmutableLog(str(log_path))
        entries = log.get_entries(offset, offset + limit)

        results = []
        for entry in entries:
            results.append(LogEntry(
                timestamp=entry.get("timestamp", ""),
                data=entry.get("data", {}),
                entry_hash=entry.get("entry_hash", "")
            ))
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs/export")
def export_logs(format: str = Query("json", pattern="^(json|csv|html)$")):
    """Export logs in specified format."""
    try:
        log_path = Path("logs/systemzero.log")
        if not log_path.exists():
            raise HTTPException(status_code=404, detail="No logs found")

        log = ImmutableLog(str(log_path))
        entries = log.get_entries()

        exporter = LogExporter()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        
        if format == "json":
            export_path = Path(f"/tmp/export_{timestamp}.json")
            exporter.to_json(entries, export_path)
            return FileResponse(export_path, media_type="application/json", filename=f"logs_{timestamp}.json")
        elif format == "csv":
            export_path = Path(f"/tmp/export_{timestamp}.csv")
            exporter.to_csv(entries, export_path)
            return FileResponse(export_path, media_type="text/csv", filename=f"logs_{timestamp}.csv")
        elif format == "html":
            export_path = Path(f"/tmp/export_{timestamp}.html")
            exporter.to_html(entries, export_path, title="System//Zero Log Export")
            return FileResponse(export_path, media_type="text/html", filename=f"logs_{timestamp}.html")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dashboard", response_model=DashboardData)
def get_dashboard_data() -> DashboardData:
    """Get dashboard data (recent drifts, compliance metrics)."""
    try:
        log_path = Path("logs/systemzero.log")
        recent_drifts = []
        compliance = 1.0
        total_events = 0

        if log_path.exists():
            log = ImmutableLog(str(log_path))
            entries = log.get_entries()
            total_events = len(entries)

            # Get last 10 events
            recent = entries[-10:] if len(entries) > 10 else entries

            critical_count = 0
            for entry in recent:
                data = entry.get("data", {})
                if data.get("severity") == "critical":
                    critical_count += 1
                recent_drifts.append({
                    "timestamp": entry.get("timestamp", ""),
                    "drift_type": data.get("drift_type", "unknown"),
                    "severity": data.get("severity", "info")
                })

            # Calculate compliance (1.0 - critical ratio)
            if total_events > 0:
                compliance = 1.0 - (critical_count / len(recent))
        else:
            compliance = 1.0

        return DashboardData(
            timestamp=datetime.now(timezone.utc).isoformat(),
            recent_drifts=recent_drifts,
            compliance=max(0.0, min(1.0, compliance)),
            total_events=total_events
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def get_app() -> FastAPI:
    """Return the FastAPI app instance."""
    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
