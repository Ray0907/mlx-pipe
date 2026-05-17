from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from mlx_pipe.registry import BUILTIN_DEFAULTS

CONFIG_HOME_ENV = "MLX_PIPE_CONFIG_HOME"


def config_dir() -> Path:
    if override := os.environ.get(CONFIG_HOME_ENV):
        return Path(override).expanduser()
    return Path.home() / ".config" / "mlx-pipe"


def config_path() -> Path:
    return config_dir() / "config.json"


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    target = Path(path) if path is not None else config_path()
    if not target.exists():
        return {}
    with target.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"Config file must contain a JSON object: {target}")
    return data


def save_config(config: dict[str, Any], path: str | Path | None = None) -> None:
    target = Path(path) if path is not None else config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as file:
        json.dump(config, file, indent=2, sort_keys=True)
        file.write("\n")


def get_default_model(
    domain: str,
    explicit: str | None = None,
    config_path: str | Path | None = None,
) -> str:
    if explicit:
        return explicit

    config = load_config(config_path)
    configured = config.get("defaults", {}).get(domain)
    if configured:
        return str(configured)

    try:
        return BUILTIN_DEFAULTS[domain]
    except KeyError as exc:
        raise ValueError(f"Unknown model domain: {domain}") from exc


def _normalize_key(key: str) -> tuple[str, str]:
    parts = key.split(".")
    if len(parts) != 2 or parts[1] != "default":
        raise ValueError("Only '<domain>.default' keys are supported")
    domain = parts[0]
    if domain not in BUILTIN_DEFAULTS:
        raise ValueError(f"Unknown model domain: {domain}")
    return domain, parts[1]


def get_config_value(key: str, path: str | Path | None = None) -> str | None:
    domain, _ = _normalize_key(key)
    return load_config(path).get("defaults", {}).get(domain)


def set_config_value(key: str, value: str, config_path: str | Path | None = None) -> None:
    domain, _ = _normalize_key(key)
    config = load_config(config_path)
    defaults = config.setdefault("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("'defaults' config value must be an object")
    defaults[domain] = value
    save_config(config, config_path)
