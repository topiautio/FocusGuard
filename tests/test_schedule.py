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


def test_schedule_only_applies_on_selected_days():
    weekdays = ("monday", "tuesday", "wednesday", "thursday", "friday")

    assert not is_allowed(datetime(2026, 1, 2, 9), time(15), time(22), weekdays)
    assert is_allowed(datetime(2026, 1, 3, 9), time(15), time(22), weekdays)


def test_selected_day_transition_at_midnight():
    weekdays = ("monday", "tuesday", "wednesday", "thursday", "friday")
    state = schedule_state(datetime(2026, 1, 2, 23), time(15), time(22), weekdays)

    assert state.allowed is False
    assert state.next_transition == datetime(2026, 1, 3)


def test_empty_active_days_never_blocks():
    now = datetime(2026, 1, 3, 9)
    assert is_allowed(now, time(15), time(22), ())
    state = schedule_state(now, time(15), time(22), ())

    assert state.allowed
    assert state.next_transition == datetime(2026, 1, 4)
