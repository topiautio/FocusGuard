import subprocess
from unittest import mock

import focusguard.notify as notify_module


def test_notify_ignores_missing_desktop_notification_tools(monkeypatch):
    monkeypatch.setattr(notify_module, "_LAST", 0.0)
    run = mock.Mock(side_effect=FileNotFoundError)
    monkeypatch.setattr(notify_module.subprocess, "run", run)

    notify_module.notify("Focus mode enabled")

    run.assert_called_once()


def test_notify_ignores_subprocess_failures(monkeypatch):
    monkeypatch.setattr(notify_module, "_LAST", 0.0)
    run = mock.Mock(side_effect=subprocess.TimeoutExpired("notify-send", 1))
    monkeypatch.setattr(notify_module.subprocess, "run", run)

    notify_module.notify("Focus mode enabled")

    run.assert_called_once()
