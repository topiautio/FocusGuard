import subprocess
from unittest import mock

import focusguard.notify as notify_module


def _fake_run_user(monkeypatch, tmp_path, uids=("1000",)):
    for uid in uids:
        (tmp_path / uid).mkdir()
        (tmp_path / uid / "bus").touch()
    monkeypatch.setattr(notify_module, "_RUN_USER", tmp_path)
    monkeypatch.setattr(notify_module, "_LAST", 0.0)
    monkeypatch.setattr(
        notify_module.pwd, "getpwuid", lambda uid: mock.Mock(pw_name=f"user{uid}")
    )


def test_notify_runs_notify_send_on_user_session_bus(monkeypatch, tmp_path):
    _fake_run_user(monkeypatch, tmp_path)
    run = mock.Mock()
    monkeypatch.setattr(notify_module.subprocess, "run", run)

    notify_module.notify("Focus mode enabled")

    cmd = run.call_args.args[0]
    assert cmd[:4] == ["runuser", "-u", "user1000", "--"]
    assert f"DBUS_SESSION_BUS_ADDRESS=unix:path={tmp_path}/1000/bus" in cmd
    assert cmd[-3:] == ["notify-send", "FocusGuard", "Focus mode enabled"]


def test_notify_skips_system_users(monkeypatch, tmp_path):
    _fake_run_user(monkeypatch, tmp_path, uids=("0", "999"))
    run = mock.Mock()
    monkeypatch.setattr(notify_module.subprocess, "run", run)

    notify_module.notify("Focus mode enabled")

    run.assert_not_called()


def test_notify_is_throttled(monkeypatch, tmp_path):
    _fake_run_user(monkeypatch, tmp_path)
    run = mock.Mock()
    monkeypatch.setattr(notify_module.subprocess, "run", run)

    notify_module.notify("one")
    notify_module.notify("two")

    run.assert_called_once()


def test_notify_ignores_missing_desktop_notification_tools(monkeypatch, tmp_path):
    _fake_run_user(monkeypatch, tmp_path)
    run = mock.Mock(side_effect=FileNotFoundError)
    monkeypatch.setattr(notify_module.subprocess, "run", run)

    notify_module.notify("Focus mode enabled")

    run.assert_called_once()


def test_notify_ignores_subprocess_failures(monkeypatch, tmp_path):
    _fake_run_user(monkeypatch, tmp_path)
    run = mock.Mock(side_effect=subprocess.TimeoutExpired("notify-send", 1))
    monkeypatch.setattr(notify_module.subprocess, "run", run)

    notify_module.notify("Focus mode enabled")

    run.assert_called_once()
