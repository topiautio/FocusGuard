"""Configuration loading and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import time
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

DEFAULT_BLOCKLIST = [
    "x.com",
    "twitter.com",
    "reddit.com",
    "old.reddit.com",
    "www.reddit.com",
    "youtube.com",
    "www.youtube.com",
    "youtu.be",
    "googlevideo.com",
    "ytimg.com",
    "instagram.com",
    "facebook.com",
    "threads.net",
    "tiktok.com",
]
DEFAULT_WHITELIST = ["music.youtube.com"]
_DOMAIN_RE = re.compile(
    r"^(\*\.)?[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+$",
    re.I,
)


@dataclass(frozen=True)
class Config:
    """Validated FocusGuard settings."""

    allow_start: time = time(15, 0)
    allow_end: time = time(22, 0)
    notifications: bool = True
    logging: bool = True
    blocklist: tuple[str, ...] = tuple(DEFAULT_BLOCKLIST)
    whitelist: tuple[str, ...] = tuple(DEFAULT_WHITELIST)


class ConfigError(ValueError):
    """Raised when configuration is invalid."""


def parse_time(value: str) -> time:
    """Parse a HH:MM time string."""
    try:
        hour_s, minute_s = value.split(":", 1)
        hour, minute = int(hour_s), int(minute_s)
        return time(hour, minute)
    except Exception as exc:  # noqa: BLE001
        raise ConfigError(f"invalid time {value!r}; expected HH:MM") from exc


def normalize_domain(domain: str) -> str:
    """Normalize and validate a domain pattern."""
    value = (
        domain.strip()
        .lower()
        .removeprefix("http://")
        .removeprefix("https://")
        .rstrip("/")
    )
    if not _DOMAIN_RE.fullmatch(value):
        raise ConfigError(f"invalid domain {domain!r}")
    return value


def load_config(path: Path) -> Config:
    """Load configuration from TOML, returning defaults for a missing file."""
    if not path.exists():
        return Config()
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"invalid TOML: {exc}") from exc
    allowed = {
        "allow_start",
        "allow_end",
        "notifications",
        "logging",
        "blocklist",
        "whitelist",
    }
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise ConfigError(f"unknown config keys: {', '.join(unknown)}")
    blocklist = tuple(
        normalize_domain(x) for x in data.get("blocklist", DEFAULT_BLOCKLIST)
    )
    whitelist = tuple(
        normalize_domain(x) for x in data.get("whitelist", DEFAULT_WHITELIST)
    )
    if not isinstance(data.get("notifications", True), bool) or not isinstance(
        data.get("logging", True), bool
    ):
        raise ConfigError("notifications and logging must be booleans")
    return Config(
        allow_start=parse_time(data.get("allow_start", "15:00")),
        allow_end=parse_time(data.get("allow_end", "22:00")),
        notifications=data.get("notifications", True),
        logging=data.get("logging", True),
        blocklist=blocklist,
        whitelist=whitelist,
    )
