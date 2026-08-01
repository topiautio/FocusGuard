"""Schedule calculations for allow and focus periods."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from datetime import datetime, time, timedelta

DAY_NAMES = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)


@dataclass(frozen=True)
class ScheduleState:
    """Current schedule state."""

    allowed: bool
    next_transition: datetime


def _combine(day: datetime, clock: time) -> datetime:
    return day.replace(hour=clock.hour, minute=clock.minute, second=0, microsecond=0)


def is_allowed(
    now: datetime,
    start: time,
    end: time,
    active_days: Collection[str] | None = None,
) -> bool:
    """Return true when now is within the allowed window and schedule days."""
    if active_days is not None and DAY_NAMES[now.weekday()] not in active_days:
        return True
    current = now.timetz().replace(tzinfo=None)
    if start < end:
        return start <= current < end
    return current >= start or current < end


def schedule_state(
    now: datetime,
    start: time,
    end: time,
    active_days: Collection[str] | None = None,
) -> ScheduleState:
    """Return current mode and next transition."""
    allowed = is_allowed(now, start, end, active_days)
    if active_days is not None and not active_days:
        return ScheduleState(allowed, _combine(now + timedelta(days=1), time.min))
    candidates = [
        _combine(now, start),
        _combine(now, end),
        _combine(now + timedelta(days=1), start),
        _combine(now + timedelta(days=1), end),
    ]
    if active_days is not None and set(active_days) != set(DAY_NAMES):
        candidates.extend(
            _combine(now + timedelta(days=offset), time.min) for offset in range(8)
        )
    future_candidates = sorted(dt for dt in candidates if dt > now)
    for candidate in future_candidates:
        if is_allowed(candidate, start, end, active_days) != allowed:
            return ScheduleState(allowed, candidate)
    return ScheduleState(allowed, future_candidates[0])


def local_now() -> datetime:
    """Return the current local time."""
    return datetime.now().astimezone()
