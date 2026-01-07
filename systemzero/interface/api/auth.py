"""Authentication and authorization for System//Zero API."""
import hashlib
import secrets
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from functools import wraps

from fastapi import Request, HTTPException, status
from fastapi.security import APIKeyHeader


# API key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class Role:
    """User roles for access control."""
    ADMIN = "admin"
    OPERATOR = "operator"
    READONLY = "readonly"
    
    ALL_ROLES = [ADMIN, OPERATOR, READONLY]
    
    @classmethod
    def validate(cls, role: str) -> bool:
        """Check if role is valid."""
        return role in cls.ALL_ROLES


class APIKeyManager:
    """Manages API keys and authentication."""
    
    def __init__(self, keys_file: Path = None):
        self.keys_file = keys_file or Path("config/api_keys.yaml")
        self._keys_cache: Optional[Dict[str, Any]] = None
        self._cache_time: Optional[datetime] = None
        self._cache_ttl = 60  # Cache for 60 seconds
    
    def _load_keys(self) -> Dict[str, Any]:
        """Load API keys from YAML file."""
        if not self.keys_file.exists():
            return {"keys": {}}
        
        # Check cache
        now = datetime.now(timezone.utc)
        if self._keys_cache and self._cache_time:
            elapsed = (now - self._cache_time).total_seconds()
            if elapsed < self._cache_ttl:
                return self._keys_cache
        
        with open(self.keys_file, 'r') as f:
            data = yaml.safe_load(f)
        
        # Ensure data is a dict with "keys" field
        if not isinstance(data, dict):
            data = {"keys": {}}
        elif "keys" not in data:
            data["keys"] = {}
        
        # Never cache None or incomplete data
        if not isinstance(data, dict) or "keys" not in data:
            raise ValueError("Failed to load keys file properly")
        
        self._keys_cache = data
        self._cache_time = now
        return data
    
    def _save_keys(self, data: Dict[str, Any]) -> None:
        """Save API keys to YAML file."""
        self.keys_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.keys_file, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        # Invalidate cache
        self._keys_cache = None
        self._cache_time = None
    
    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key using SHA256."""
        return hashlib.sha256(key.encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new random API key."""
        return secrets.token_urlsafe(32)
    
    def create_key(self, name: str, role: str = Role.READONLY, description: str = "") -> str:
        """Create a new API key.
        
        Args:
            name: Key identifier (e.g., "service-bot", "operator-alice")
            role: User role (admin, operator, readonly)
            description: Optional description
            
        Returns:
            The plaintext API key (only shown once)
        """
        if not Role.validate(role):
            raise ValueError(f"Invalid role: {role}. Must be one of {Role.ALL_ROLES}")
        
        # Generate key
        key = self.generate_key()
        key_hash = self.hash_key(key)
        
        # Load existing keys
        data = self._load_keys()
        if "keys" not in data:
            data["keys"] = {}
        
        # Store hashed key with metadata
        data["keys"][key_hash] = {
            "name": name,
            "role": role,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_used": None,
            "use_count": 0
        }
        
        self._save_keys(data)
        return key
    
    def validate_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Validate an API key and return its metadata.
        
        Args:
            key: The plaintext API key
            
        Returns:
            Key metadata dict with 'name', 'role', etc., or None if invalid
        """
        if not key:
            return None
        
        key_hash = self.hash_key(key)
        data = self._load_keys()
        
        # data should always have "keys" key due to _load_keys normalization
        if "keys" not in data or not isinstance(data["keys"], dict):
            return None
        
        if key_hash not in data["keys"]:
            return None
        
        # Update last used timestamp and count
        metadata = data["keys"][key_hash]
        metadata["last_used"] = datetime.now(timezone.utc).isoformat()
        metadata["use_count"] = metadata.get("use_count", 0) + 1
        
        # Save updated metadata
        self._save_keys(data)
        
        return metadata
    
    def revoke_key(self, key: str) -> bool:
        """Revoke an API key.
        
        Args:
            key: The plaintext API key to revoke
            
        Returns:
            True if key was revoked, False if not found
        """
        key_hash = self.hash_key(key)
        data = self._load_keys()
        
        keys = data.get("keys", {})
        if key_hash in keys:
            del keys[key_hash]
            self._save_keys(data)
            return True
        
        return False
    
    def list_keys(self) -> List[Dict[str, Any]]:
        """List all API keys (without plaintext keys).
        
        Returns:
            List of key metadata dicts
        """
        data = self._load_keys()
        keys = data.get("keys", {})
        
        return [
            {
                "key_hash": key_hash[:16] + "...",  # Truncated hash
                **metadata
            }
            for key_hash, metadata in keys.items()
        ]


# Global key manager instance
_key_manager: Optional[APIKeyManager] = None


def get_key_manager() -> APIKeyManager:
    """Get or create the global API key manager."""
    global _key_manager
    if _key_manager is None:
        _key_manager = APIKeyManager()
    return _key_manager


async def verify_api_key(request: Request, api_key: Optional[str] = None) -> Dict[str, Any]:
    """FastAPI dependency to verify API key.
    
    Args:
        request: FastAPI request object
        api_key: API key from header (injected by APIKeyHeader)
        
    Returns:
        Key metadata dict
        
    Raises:
        HTTPException: If key is missing or invalid
    """
    # Try header first
    if not api_key:
        api_key = request.headers.get("X-API-Key")
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"}
        )
    
    manager = get_key_manager()
    metadata = manager.validate_key(api_key)
    
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
    
    # Attach metadata to request state for access in endpoints
    request.state.api_key_metadata = metadata
    return metadata


def require_role(*allowed_roles: str):
    """Decorator to require specific roles for an endpoint.
    
    Usage:
        @app.post("/admin-only")
        @require_role(Role.ADMIN)
        async def admin_endpoint(metadata: dict = Depends(verify_api_key)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract metadata from kwargs (injected by verify_api_key dependency)
            metadata = kwargs.get('metadata') or kwargs.get('api_key_metadata')
            
            if not metadata:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            user_role = metadata.get("role")
            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {allowed_roles}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


# Permission matrix (for documentation)
PERMISSIONS = {
    Role.ADMIN: [
        "read:status", "read:logs", "read:templates", "read:captures", "read:dashboard",
        "write:captures", "write:templates", "write:config",
        "admin:keys", "admin:users"
    ],
    Role.OPERATOR: [
        "read:status", "read:logs", "read:templates", "read:captures", "read:dashboard",
        "write:captures", "write:templates"
    ],
    Role.READONLY: [
        "read:status", "read:logs", "read:templates", "read:captures", "read:dashboard"
    ]
}


def check_permission(role: str, permission: str) -> bool:
    """Check if a role has a specific permission.
    
    Args:
        role: User role
        permission: Permission string (e.g., "write:captures")
        
    Returns:
        True if role has permission
    """
    return permission in PERMISSIONS.get(role, [])
