"""Schedule calculations for allow and focus periods."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta


@dataclass(frozen=True)
class ScheduleState:
    """Current schedule state."""

    allowed: bool
    next_transition: datetime


def _combine(day: datetime, clock: time) -> datetime:
    return day.replace(hour=clock.hour, minute=clock.minute, second=0, microsecond=0)


def is_allowed(now: datetime, start: time, end: time) -> bool:
    """Return true when now is within the allowed window."""
    current = now.timetz().replace(tzinfo=None)
    if start < end:
        return start <= current < end
    return current >= start or current < end


def schedule_state(now: datetime, start: time, end: time) -> ScheduleState:
    """Return current mode and next transition."""
    candidates = [
        _combine(now, start),
        _combine(now, end),
        _combine(now + timedelta(days=1), start),
        _combine(now + timedelta(days=1), end),
    ]
    future = min(dt for dt in candidates if dt > now)
    return ScheduleState(is_allowed(now, start, end), future)


def local_now() -> datetime:
    """Return the current local time."""
    return datetime.now().astimezone()
