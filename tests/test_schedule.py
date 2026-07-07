from datetime import datetime, time

from focusguard.schedule import is_allowed, schedule_state


def test_default_schedule_allows_afternoon():
    assert is_allowed(datetime(2026, 1, 1, 16), time(15), time(22))


def test_default_schedule_blocks_late_night_and_morning():
    assert not is_allowed(datetime(2026, 1, 1, 23), time(15), time(22))
    assert not is_allowed(datetime(2026, 1, 1, 9), time(15), time(22))


def test_next_transition():
    state = schedule_state(datetime(2026, 1, 1, 14, 30), time(15), time(22))
    assert not state.allowed
    assert state.next_transition == datetime(2026, 1, 1, 15)
