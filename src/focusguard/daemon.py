"""FocusGuard daemon."""

from __future__ import annotations

import logging
import signal
import subprocess
import sys
import threading
from pathlib import Path

from .config import ConfigError, load_config
from .nft import disable_nft_rules, install_nft_rules, write_dnsmasq_config
from .paths import (
    CONFIG_PATH,
    DNSMASQ_CONF,
    LOG_PATH,
    NFT_TABLE_FILE,
    STATE_PATH,
)
from .schedule import local_now, schedule_state
from .state import load_state, save_state

_STOP = False
_RELOAD = True
_WAKE = threading.Event()


def _signal(signum: int, _frame: object) -> None:
    global _STOP, _RELOAD
    if signum in {signal.SIGTERM, signal.SIGINT}:
        _STOP = True
    if signum == signal.SIGHUP:
        _RELOAD = True
    _WAKE.set()


def _wait_for_wakeup(seconds: float) -> None:
    """Wait for a schedule deadline or a signal-driven reload."""
    _WAKE.wait(seconds)
    _WAKE.clear()


def setup_logging(log_path: str | None = None, enabled: bool = True) -> None:
    """Configure persistent file logging when enabled.

    When persistent logging is disabled, messages go to stderr so systemd can
    retain them in the journal without creating a FocusGuard log file.
    """
    log_format = "%(asctime)s %(levelname)s %(message)s"
    if not enabled:
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler(sys.stderr)],
            force=True,
        )
        return

    target = log_path or str(LOG_PATH)
    try:
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=target,
            level=logging.INFO,
            format=log_format,
            force=True,
        )
    except (PermissionError, OSError):
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[logging.StreamHandler(sys.stderr)],
            force=True,
        )


def restart_networkmanager() -> None:
    """Restart NetworkManager to reload dnsmasq rules."""
    subprocess.run(["systemctl", "reload-or-restart", "NetworkManager"], check=False)


def main() -> int:
    """Run the daemon loop."""
    global _RELOAD
    signal.signal(signal.SIGTERM, _signal)
    signal.signal(signal.SIGINT, _signal)
    signal.signal(signal.SIGHUP, _signal)
    cfg = None
    blocked = None
    while not _STOP:
        try:
            if _RELOAD or cfg is None:
                cfg = load_config(CONFIG_PATH)
                setup_logging(enabled=cfg.logging)
                _RELOAD = False
                blocked = None
                logging.info("configuration loaded")
            state = schedule_state(
                local_now(), cfg.allow_start, cfg.allow_end, cfg.active_days
            )
            should_block = not state.allowed
            if should_block != blocked:
                if should_block:
                    install_nft_rules(NFT_TABLE_FILE)
                else:
                    disable_nft_rules()
                write_dnsmasq_config(DNSMASQ_CONF, cfg, should_block)
                restart_networkmanager()
                blocked = should_block
                logging.info("mode changed to %s", "focus" if should_block else "free")
            existing = load_state(STATE_PATH)
            existing.update(
                {
                    "mode": "focus" if should_block else "free",
                    "next_transition": state.next_transition.isoformat(),
                }
            )
            save_state(STATE_PATH, existing)
            sleep_for = max(
                1, min(3600, int((state.next_transition - local_now()).total_seconds()))
            )
            _wait_for_wakeup(sleep_for)
        except ConfigError as exc:
            logging.error("configuration error: %s", exc)
            _wait_for_wakeup(30)
        except PermissionError as exc:
            logging.error("daemon error: %s", exc)
            _wait_for_wakeup(10)
        except Exception as exc:  # noqa: BLE001
            logging.exception("daemon error: %s", exc)
            _wait_for_wakeup(10)
    disable_nft_rules()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
