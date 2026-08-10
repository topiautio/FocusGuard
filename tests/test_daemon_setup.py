"""Test setup_logging fallback installs StreamHandler on PermissionError."""

import logging
import signal
import sys
import unittest.mock as mock

import focusguard.daemon as daemon
from focusguard.daemon import setup_logging

# ruff: noqa: ARG001 - monkeypatch is a pytest fixture (injected by name, unused in body)


def test_setup_logging_uses_streamhandler_on_permission_error(monkeypatch):
    """Force the except path in shipped setup_logging.

    Asserts StreamHandler fallback. Drives real code (no src on path).
    Uses default LOG_PATH to simulate daemon launch.
    """
    root = logging.getLogger()
    # Reset handlers so basicConfig in fallback actually attaches a fresh one
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(logging.NOTSET)

    def raise_perm(*_args, **_kwargs):
        raise PermissionError("simulated non-writable for test")

    with mock.patch("focusguard.daemon.Path") as mock_path_cls:
        # Force .parent.mkdir to raise for whatever target (default LOG_PATH or passed)
        mock_path_cls.return_value.parent.mkdir.side_effect = raise_perm

        # Call with no arg: uses real LOG_PATH=/var/log/... (protected for non-root)
        # This must take the except branch in the installed focusguard.daemon code.
        setup_logging()

    handlers = root.handlers
    has_stderr_stream = any(
        isinstance(h, logging.StreamHandler)
        and getattr(h, "stream", None) is sys.stderr
        for h in handlers
    )
    assert (
        has_stderr_stream
    ), f"Expected StreamHandler to sys.stderr after fallback; handlers={handlers}"

    # Prove we did not get file logging (except path taken)
    has_file = any(isinstance(h, logging.FileHandler) for h in handlers)
    assert (
        not has_file
    ), f"FileHandler present; fallback to StreamHandler did not occur: {handlers}"


def test_signal_wakes_daemon_wait(monkeypatch):
    wake = mock.Mock()
    monkeypatch.setattr(daemon, "_WAKE", wake)
    monkeypatch.setattr(daemon, "_STOP", False)

    daemon._signal(signal.SIGTERM, None)

    assert daemon._STOP
    wake.set.assert_called_once_with()


def test_wait_for_wakeup_uses_signal_event(monkeypatch):
    wake = mock.Mock()
    monkeypatch.setattr(daemon, "_WAKE", wake)

    daemon._wait_for_wakeup(30)

    wake.wait.assert_called_once_with(30)
    wake.clear.assert_called_once_with()


def test_setup_logging_disabled_uses_stderr_without_file(tmp_path):
    """Disable persistent logs while keeping messages in the system journal."""
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    root.setLevel(logging.NOTSET)

    log_path = tmp_path / "focusguard.log"
    setup_logging(str(log_path), enabled=False)

    assert any(
        isinstance(handler, logging.StreamHandler)
        and getattr(handler, "stream", None) is sys.stderr
        for handler in root.handlers
    )
    assert not any(isinstance(handler, logging.FileHandler) for handler in root.handlers)
    assert not log_path.exists()
