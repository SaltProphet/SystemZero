"""Phase 5 API server tests."""
import json
from fastapi.testclient import TestClient

from interface.api.server import app


client = TestClient(app)


def test_root_endpoint():
    """Test API root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "System//Zero"
    assert "docs" in data
    assert "endpoints" in data


def test_status_endpoint():
    """Test status endpoint."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "log_path" in data
    assert "template_count" in data


def test_capture_endpoint():
    """Test capture endpoint."""
    tree = {
        "root": {
            "role": "window",
            "name": "TestWindow",
            "type": "container",
            "children": []
        }
    }
    
    response = client.post("/captures", json={"tree": tree, "app": "test_app"})
    assert response.status_code == 200
    data = response.json()
    assert "path" in data
    assert "signatures" in data


def test_templates_list_endpoint():
    """Test list templates endpoint."""
    response = client.get("/templates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_templates_get_endpoint():
    """Test get specific template."""
    response = client.get("/templates/discord_chat")
    assert response.status_code == 200
    data = response.json()
    assert data["screen_id"] == "discord_chat"


def test_templates_get_notfound():
    """Test get non-existent template returns 404."""
    response = client.get("/templates/nonexistent_template_12345")
    assert response.status_code == 404


def test_logs_endpoint():
    """Test logs endpoint."""
    response = client.get("/logs")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_dashboard_endpoint():
    """Test dashboard endpoint."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "timestamp" in data
    assert "recent_drifts" in data
    assert "compliance" in data
