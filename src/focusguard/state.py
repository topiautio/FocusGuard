"""Persistent runtime state."""

from __future__ import annotations

import json
from pathlib import Path


def load_state(path: Path) -> dict:
    """Load state JSON, tolerating missing or corrupt files."""
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return state if isinstance(state, dict) else {}


def save_state(path: Path, state: dict) -> None:
    """Save state JSON atomically enough for small local state."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)
