"""Tests for API authentication and authorization."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from interface.api.server import app
from interface.api.auth import APIKeyManager, Role


@pytest.fixture(scope="session")
def temp_keys_file():
    """Create a temporary API keys file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def key_manager(temp_keys_file):
    """Create an API key manager with temporary file."""
    manager = APIKeyManager(keys_file=temp_keys_file)
    # Start fresh for each test
    manager._keys_cache = None
    manager._cache_time = None
    # Clear the file with valid YAML
    with open(temp_keys_file, 'w') as f:
        f.write('keys: {}')
    return manager


@pytest.fixture
def admin_key(key_manager):
    """Generate an admin API key for testing."""
    return key_manager.create_key("test-admin", Role.ADMIN, "Test admin key")


@pytest.fixture
def operator_key(key_manager):
    """Generate an operator API key for testing."""
    return key_manager.create_key("test-operator", Role.OPERATOR, "Test operator key")


@pytest.fixture
def readonly_key(key_manager):
    """Generate a readonly API key for testing."""
    return key_manager.create_key("test-readonly", Role.READONLY, "Test readonly key")


@pytest.fixture
def client(key_manager):
    """Create test client with mocked key manager."""
    # Mock the global key manager to use our test instance
    # Patch in both places where it's imported and used
    with patch('interface.api.auth.get_key_manager', return_value=key_manager):
        with patch('interface.api.server.get_key_manager', return_value=key_manager):
            yield TestClient(app)


class TestAPIKeyManager:
    """Test API key management."""
    
    def test_generate_key(self):
        """Test key generation."""
        key = APIKeyManager.generate_key()
        assert isinstance(key, str)
        assert len(key) > 20
    
    def test_hash_key_deterministic(self):
        """Test key hashing is deterministic."""
        key = "test-key-12345"
        hash1 = APIKeyManager.hash_key(key)
        hash2 = APIKeyManager.hash_key(key)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex
    
    def test_create_key(self, key_manager):
        """Test creating a new API key."""
        key = key_manager.create_key("test-user", Role.OPERATOR, "Test key")
        
        assert isinstance(key, str)
        assert len(key) > 20
        
        # Verify key was stored
        metadata = key_manager.validate_key(key)
        assert metadata is not None
        assert metadata["name"] == "test-user"
        assert metadata["role"] == Role.OPERATOR
        assert metadata["description"] == "Test key"
    
    def test_create_key_invalid_role(self, key_manager):
        """Test creating key with invalid role raises error."""
        with pytest.raises(ValueError):
            key_manager.create_key("test", "invalid-role")
    
    def test_validate_key_success(self, key_manager):
        """Test validating a valid key."""
        key = key_manager.create_key("test", Role.READONLY)
        metadata = key_manager.validate_key(key)
        
        assert metadata is not None
        assert metadata["name"] == "test"
        assert metadata["role"] == Role.READONLY
    
    def test_validate_key_invalid(self, key_manager):
        """Test validating an invalid key."""
        metadata = key_manager.validate_key("invalid-key-123")
        assert metadata is None
    
    def test_validate_key_updates_usage(self, key_manager):
        """Test that validation updates last_used and use_count."""
        key = key_manager.create_key("test", Role.READONLY)
        
        # First validation
        metadata1 = key_manager.validate_key(key)
        assert metadata1["use_count"] == 1
        assert metadata1["last_used"] is not None
        
        # Second validation
        metadata2 = key_manager.validate_key(key)
        assert metadata2["use_count"] == 2
    
    def test_revoke_key(self, key_manager):
        """Test revoking a key."""
        key = key_manager.create_key("test", Role.READONLY)
        
        # Verify key works
        assert key_manager.validate_key(key) is not None
        
        # Revoke key
        result = key_manager.revoke_key(key)
        assert result is True
        
        # Verify key no longer works
        assert key_manager.validate_key(key) is None
    
    def test_revoke_nonexistent_key(self, key_manager):
        """Test revoking a key that doesn't exist."""
        result = key_manager.revoke_key("nonexistent-key")
        assert result is False
    
    def test_list_keys(self, key_manager):
        """Test listing all keys."""
        key_manager.create_key("user1", Role.ADMIN)
        key_manager.create_key("user2", Role.OPERATOR)
        key_manager.create_key("user3", Role.READONLY)
        
        keys = key_manager.list_keys()
        assert len(keys) == 3
        
        names = [k["name"] for k in keys]
        assert "user1" in names
        assert "user2" in names
        assert "user3" in names


class TestAuthenticationEndpoints:
    """Test authentication endpoints."""
    
    def test_create_token_admin_success(self, client, admin_key):
        """Test admin can create new tokens."""
        response = client.post(
            "/auth/token",
            headers={"X-API-Key": admin_key},
            json={"name": "new-key", "role": "operator", "description": "Test"}
        )
        
        print(f"Response: {response.status_code} {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["name"] == "new-key"
        assert data["role"] == "operator"
        assert "save this token securely" in data["message"].lower()
    
    def test_create_token_non_admin_forbidden(self, client, operator_key):
        """Test non-admin cannot create tokens."""
        response = client.post(
            "/auth/token",
            headers={"X-API-Key": operator_key},
            json={"name": "new-key", "role": "readonly"}
        )
        
        assert response.status_code == 403
        assert "administrators" in response.json()["detail"].lower()
    
    def test_create_token_no_auth(self, client):
        """Test creating token without auth fails."""
        response = client.post(
            "/auth/token",
            json={"name": "new-key", "role": "readonly"}
        )
        
        assert response.status_code == 401
    
    def test_validate_token_success(self, client, operator_key):
        """Test validating a valid token."""
        response = client.post(
            "/auth/validate",
            headers={"X-API-Key": operator_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["name"] == "test-operator"
        assert data["role"] == "operator"
        assert "use_count" in data
    
    def test_validate_token_invalid(self, client):
        """Test validating invalid token."""
        response = client.post(
            "/auth/validate",
            headers={"X-API-Key": "invalid-key-123"}
        )
        
        assert response.status_code == 403
    
    def test_list_keys_admin_success(self, client, admin_key, operator_key):
        """Test admin can list all keys."""
        response = client.get(
            "/auth/keys",
            headers={"X-API-Key": admin_key}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "keys" in data
        assert "total" in data
        assert data["total"] >= 2  # admin + operator keys
    
    def test_list_keys_non_admin_forbidden(self, client, operator_key):
        """Test non-admin cannot list keys."""
        response = client.get(
            "/auth/keys",
            headers={"X-API-Key": operator_key}
        )
        
        assert response.status_code == 403


class TestProtectedEndpoints:
    """Test authentication requirements on protected endpoints."""
    
    def test_post_captures_with_operator_auth(self, client, operator_key):
        """Test operator can create captures."""
        response = client.post(
            "/captures",
            headers={"X-API-Key": operator_key},
            json={"tree": {"role": "window", "name": "Test"}, "app": "test"}
        )
        
        # Should succeed (status 200) or fail for other reasons, but not auth (401/403)
        assert response.status_code not in [401, 403]
    
    def test_post_captures_with_admin_auth(self, client, admin_key):
        """Test admin can create captures."""
        response = client.post(
            "/captures",
            headers={"X-API-Key": admin_key},
            json={"tree": {"role": "window", "name": "Test"}, "app": "test"}
        )
        
        assert response.status_code not in [401, 403]
    
    def test_post_captures_with_readonly_forbidden(self, client, readonly_key):
        """Test readonly cannot create captures."""
        response = client.post(
            "/captures",
            headers={"X-API-Key": readonly_key},
            json={"tree": {"role": "window", "name": "Test"}, "app": "test"}
        )
        
        assert response.status_code == 403
        assert "insufficient permissions" in response.json()["detail"].lower()
    
    def test_post_captures_no_auth(self, client):
        """Test creating capture without auth fails."""
        response = client.post(
            "/captures",
            json={"tree": {"role": "window", "name": "Test"}, "app": "test"}
        )
        
        assert response.status_code == 401
    
    def test_post_templates_with_operator_auth(self, client, operator_key):
        """Test operator can create templates."""
        response = client.post(
            "/templates?capture_path=test.json&screen_id=test&app=test",
            headers={"X-API-Key": operator_key}
        )
        
        # Should fail for missing file, not auth
        assert response.status_code != 401
        assert response.status_code != 403
    
    def test_post_templates_with_readonly_forbidden(self, client, readonly_key):
        """Test readonly cannot create templates."""
        response = client.post(
            "/templates?capture_path=test.json&screen_id=test&app=test",
            headers={"X-API-Key": readonly_key}
        )
        
        assert response.status_code == 403
    
    def test_get_endpoints_no_auth_allowed(self, client):
        """Test GET endpoints work without auth (public read)."""
        # Status endpoint
        response = client.get("/status")
        assert response.status_code == 200
        
        # Templates list
        response = client.get("/templates")
        assert response.status_code == 200
        
        # Dashboard
        response = client.get("/dashboard")
        assert response.status_code == 200
        
        # Logs
        response = client.get("/logs")
        assert response.status_code == 200


class TestRolePermissions:
    """Test role-based access control."""
    
    def test_admin_role_permissions(self):
        """Test admin has all permissions."""
        from interface.api.auth import check_permission
        
        assert check_permission(Role.ADMIN, "read:status")
        assert check_permission(Role.ADMIN, "write:captures")
        assert check_permission(Role.ADMIN, "admin:keys")
    
    def test_operator_role_permissions(self):
        """Test operator has read + write permissions."""
        from interface.api.auth import check_permission
        
        assert check_permission(Role.OPERATOR, "read:status")
        assert check_permission(Role.OPERATOR, "write:captures")
        assert not check_permission(Role.OPERATOR, "admin:keys")
    
    def test_readonly_role_permissions(self):
        """Test readonly has only read permissions."""
        from interface.api.auth import check_permission
        
        assert check_permission(Role.READONLY, "read:status")
        assert not check_permission(Role.READONLY, "write:captures")
        assert not check_permission(Role.READONLY, "admin:keys")
