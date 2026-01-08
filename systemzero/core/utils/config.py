"""Environment and YAML-backed configuration loader for System//Zero.

Reads defaults from config/settings.yaml and config/paths.yaml, then applies
SZ_* environment variable overrides. Provides a validated, immutable config
snapshot via get_config().

Environment variables (prefix SZ_):
- SZ_LOG_LEVEL: DEBUG|INFO|WARNING|ERROR|CRITICAL (default: INFO)
- SZ_JSON_LOGS: true|false (default: false)
- SZ_LOG_PATH: path to log file (default from settings.yaml)
- SZ_ENABLE_HEALTH: true|false (default: true)
- SZ_ENABLE_METRICS: true|false (default: true)
- SZ_CORS_ORIGINS: comma-separated origins (default: security.DEFAULT_CORS_ORIGINS)
- SZ_RATE_LIMIT_RPM: integer requests/min (default: 100)
- SZ_RATE_LIMIT_BURST: integer burst in 5s (default: 20)
- SZ_MAX_REQUEST_SIZE_MB: integer MB (default: 10)
- SZ_ENABLE_RATE_LIMITING: true|false (default: true)
- SZ_TRUSTED_HOSTS: comma-separated host patterns (default: empty)
- SZ_API_KEYS_PATH: path to api_keys.yaml (default: systemzero/config/api_keys.yaml)
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Defaults
_DEFAULTS: Dict[str, Any] = {
    "log_level": "INFO",
    "json_logs": False,
    "log_path": "logs/systemzero.log",
    "enable_health": True,
    "enable_metrics": True,
    "cors_origins": [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    "rate_limit_rpm": 100,
    "rate_limit_burst": 20,
    "max_request_size_mb": 10,
    "enable_rate_limiting": True,
    "trusted_hosts": [],
    "api_keys_path": "systemzero/config/api_keys.yaml",
}

_CONFIG_CACHE: Optional[Dict[str, Any]] = None


def _to_bool(val: Any, default: bool) -> bool:
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    s = str(val).strip().lower()
    return s in {"1", "true", "yes", "on"}


def _to_int(val: Any, default: int) -> int:
    try:
        return int(val)
    except Exception:
        return default


def _split_csv(val: Optional[str]) -> List[str]:
    if not val:
        return []
    return [item.strip() for item in val.split(",") if item.strip()]


def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            return {}
        return data
    except Exception:
        return {}


def load_settings() -> Dict[str, Any]:
    """Load YAML defaults from settings.yaml and paths.yaml."""
    base = Path(__file__).resolve().parents[2]  # points to systemzero/
    settings_path = base / "config" / "settings.yaml"
    paths_path = base / "config" / "paths.yaml"

    settings = _load_yaml(settings_path)
    paths = _load_yaml(paths_path)

    # Start with defaults, apply YAML overrides
    cfg = dict(_DEFAULTS)
    if "log_path" in settings:
        cfg["log_path"] = settings.get("log_path")

    # Resolve paths with root from paths.yaml if provided
    root = paths.get("root")
    if root:
        root_path = Path(root)
        if not Path(cfg["log_path"]).is_absolute():
            cfg["log_path"] = str(root_path / cfg["log_path"])

    return cfg


def apply_env_overrides(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Apply SZ_* environment overrides to the config dict."""
    env = os.environ

    cfg["log_level"] = env.get("SZ_LOG_LEVEL", cfg["log_level"]).upper()
    cfg["json_logs"] = _to_bool(env.get("SZ_JSON_LOGS"), cfg["json_logs"])
    cfg["log_path"] = env.get("SZ_LOG_PATH", cfg["log_path"]) or cfg["log_path"]

    cfg["enable_health"] = _to_bool(env.get("SZ_ENABLE_HEALTH"), cfg["enable_health"])
    cfg["enable_metrics"] = _to_bool(env.get("SZ_ENABLE_METRICS"), cfg["enable_metrics"])

    cors_csv = env.get("SZ_CORS_ORIGINS")
    if cors_csv:
        cfg["cors_origins"] = _split_csv(cors_csv)

    cfg["rate_limit_rpm"] = _to_int(env.get("SZ_RATE_LIMIT_RPM"), cfg["rate_limit_rpm"])
    cfg["rate_limit_burst"] = _to_int(env.get("SZ_RATE_LIMIT_BURST"), cfg["rate_limit_burst"])
    cfg["max_request_size_mb"] = _to_int(env.get("SZ_MAX_REQUEST_SIZE_MB"), cfg["max_request_size_mb"])
    cfg["enable_rate_limiting"] = _to_bool(env.get("SZ_ENABLE_RATE_LIMITING"), cfg["enable_rate_limiting"])

    trusted_csv = env.get("SZ_TRUSTED_HOSTS")
    if trusted_csv:
        cfg["trusted_hosts"] = _split_csv(trusted_csv)

    cfg["api_keys_path"] = env.get("SZ_API_KEYS_PATH", cfg["api_keys_path"]) or cfg["api_keys_path"]

    return cfg


def validate_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Basic validation and normalization of configuration values."""
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if cfg["log_level"] not in valid_levels:
        cfg["log_level"] = "INFO"

    # Normalize paths to absolute
    cfg["log_path"] = str(Path(cfg["log_path"]).resolve())
    cfg["api_keys_path"] = str(Path(cfg["api_keys_path"]).resolve())

    # Ensure lists
    if not isinstance(cfg.get("cors_origins"), list):
        cfg["cors_origins"] = _DEFAULTS["cors_origins"]
    if not isinstance(cfg.get("trusted_hosts"), list):
        cfg["trusted_hosts"] = []

    return cfg


def get_config(refresh: bool = False) -> Dict[str, Any]:
    """Get the merged, validated configuration. Uses an internal cache."""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None and not refresh:
        return _CONFIG_CACHE

    cfg = load_settings()
    cfg = apply_env_overrides(cfg)
    cfg = validate_config(cfg)
    _CONFIG_CACHE = cfg
    return cfg


__all__ = ["get_config", "load_settings"]
