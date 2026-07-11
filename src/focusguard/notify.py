"""Desktop notification helper."""

from __future__ import annotations

import os
import subprocess
import time

_LAST = 0.0


def notify(message: str, throttle_seconds: int = 30) -> None:
    """Best-effort desktop notification with spam throttling."""
    global _LAST
    now = time.monotonic()
    if now - _LAST < throttle_seconds:
        return
    _LAST = now
    user = os.environ.get("SUDO_USER") or os.environ.get("USER")
    if not user:
        return
    subprocess.run(
        ["sudo", "-u", user, "notify-send", "FocusGuard", message], check=False
    )
