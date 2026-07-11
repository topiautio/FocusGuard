"""FocusGuard daemon."""

from __future__ import annotations

import logging
import signal
import subprocess
import time

from .config import ConfigError, load_config
from .nft import disable_nft_rules, install_nft_rules, write_dnsmasq_config
from .paths import (
    CONFIG_PATH,
    DNSMASQ_CONF,
    LOG_DIR,
    LOG_PATH,
    NFT_TABLE_FILE,
    RUN_DIR,
    STATE_PATH,
)
from .schedule import local_now, schedule_state
from .state import load_state, save_state

_STOP = False
_RELOAD = True


def _signal(signum: int, _frame: object) -> None:
    global _STOP, _RELOAD
    if signum in {signal.SIGTERM, signal.SIGINT}:
        _STOP = True
    if signum == signal.SIGHUP:
        _RELOAD = True


def setup_logging() -> None:
    """Configure file logging."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        RUN_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        # non-root direct run or test; service runs as root after install creates it
        pass
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
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
    setup_logging()
    cfg = None
    blocked = None
    while not _STOP:
        try:
            if _RELOAD or cfg is None:
                cfg = load_config(CONFIG_PATH)
                _RELOAD = False
                blocked = None
                logging.info("configuration loaded")
            state = schedule_state(local_now(), cfg.allow_start, cfg.allow_end)
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
            time.sleep(sleep_for)
        except ConfigError as exc:
            logging.error("configuration error: %s", exc)
            time.sleep(30)
        except Exception as exc:  # noqa: BLE001
            logging.exception("daemon error: %s", exc)
            time.sleep(10)
    disable_nft_rules()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
