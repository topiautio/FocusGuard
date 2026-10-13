"""Tests for schedule reconciliation after NetworkManager events."""

from datetime import datetime

import focusguard.nm_dispatcher as dispatcher
from focusguard.config import Config
from focusguard.schedule import ScheduleState


def _set_schedule(monkeypatch, *, allowed: bool) -> Config:
    cfg = Config()
    monkeypatch.setattr(dispatcher, "load_config", lambda _path: cfg)
    monkeypatch.setattr(dispatcher, "local_now", lambda: datetime(2026, 9, 3, 16))
    monkeypatch.setattr(
        dispatcher,
        "schedule_state",
        lambda *_args: ScheduleState(
            allowed=allowed,
            next_transition=datetime(2026, 9, 3, 22),
        ),
    )
    return cfg


def test_dispatcher_reapplies_focus_mode(monkeypatch):
    cfg = _set_schedule(monkeypatch, allowed=False)
    calls = []
    monkeypatch.setattr(
        dispatcher, "install_nft_rules", lambda path: calls.append(("install", path))
    )
    monkeypatch.setattr(
        dispatcher, "disable_nft_rules", lambda: calls.append(("disable",))
    )
    monkeypatch.setattr(
        dispatcher,
        "write_dnsmasq_config",
        lambda path, config, enabled: calls.append(("dnsmasq", path, config, enabled)),
    )

    assert dispatcher.main() == 0

    assert calls == [
        ("install", dispatcher.NFT_TABLE_FILE),
        ("dnsmasq", dispatcher.DNSMASQ_CONF, cfg, True),
    ]


def test_dispatcher_clears_stale_focus_mode_during_free_time(monkeypatch):
    cfg = _set_schedule(monkeypatch, allowed=True)
    calls = []
    monkeypatch.setattr(
        dispatcher, "install_nft_rules", lambda path: calls.append(("install", path))
    )
    monkeypatch.setattr(
        dispatcher, "disable_nft_rules", lambda: calls.append(("disable",))
    )
    monkeypatch.setattr(
        dispatcher,
        "write_dnsmasq_config",
        lambda path, config, enabled: calls.append(("dnsmasq", path, config, enabled)),
    )

    assert dispatcher.main() == 0

    assert calls == [
        ("disable",),
        ("dnsmasq", dispatcher.DNSMASQ_CONF, cfg, False),
    ]
