"""Desktop notification helper."""

from __future__ import annotations

import pwd
import subprocess
import time
from pathlib import Path

_LAST = 0.0
_RUN_USER = Path("/run/user")
_MIN_UID = 1000


def _session_buses() -> list[tuple[str, str]]:
    """Return (username, D-Bus address) for each logged-in user session."""
    buses = []
    for bus in sorted(_RUN_USER.glob("*/bus")):
        if not bus.parent.name.isdigit() or int(bus.parent.name) < _MIN_UID:
            continue
        try:
            name = pwd.getpwuid(int(bus.parent.name)).pw_name
        except KeyError:
            continue
        buses.append((name, f"unix:path={bus}"))
    return buses


def notify(message: str, throttle_seconds: int = 30) -> None:
    """Best-effort desktop notification with spam throttling.

    The daemon runs as root, so each notification is delivered by running
    notify-send as the logged-in user on that user's session bus.
    """
    global _LAST
    now = time.monotonic()
    if now - _LAST < throttle_seconds:
        return
    _LAST = now
    for name, address in _session_buses():
        try:
            subprocess.run(
                [
                    "runuser",
                    "-u",
                    name,
                    "--",
                    "env",
                    f"DBUS_SESSION_BUS_ADDRESS={address}",
                    "notify-send",
                    "FocusGuard",
                    message,
                ],
                check=False,
                timeout=5,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (OSError, subprocess.SubprocessError):
            # A missing notification tool must not affect firewall enforcement.
            continue
