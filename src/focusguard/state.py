"""Persistent state and statistics."""

from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

EMPTY = {"blocked": []}


def load_state(path: Path) -> dict:
    """Load state JSON, tolerating missing or corrupt files."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return dict(EMPTY)


def save_state(path: Path, state: dict) -> None:
    """Save state JSON atomically enough for small local state."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(path)


def record_block(path: Path, domain: str, app: str | None = None) -> None:
    """Append a blocked attempt."""
    state = load_state(path)
    events = state.setdefault("blocked", [])
    events.append(
        {
            "ts": datetime.now().astimezone().isoformat(),
            "domain": domain,
            "app": app or "unknown",
        }
    )
    cutoff = datetime.now().astimezone() - timedelta(days=30)
    state["blocked"] = [e for e in events if datetime.fromisoformat(e["ts"]) >= cutoff]
    save_state(path, state)


def summarize(path: Path) -> dict:
    """Return today and weekly statistics."""
    events = load_state(path).get("blocked", [])
    today = date.today()
    week_ago = datetime.now().astimezone() - timedelta(days=7)
    today_events = [
        e for e in events if datetime.fromisoformat(e["ts"]).date() == today
    ]
    week_events = [e for e in events if datetime.fromisoformat(e["ts"]) >= week_ago]
    return {
        "today_count": len(today_events),
        "top_domains": Counter(e["domain"] for e in today_events).most_common(10),
        "weekly_count": len(week_events),
    }
