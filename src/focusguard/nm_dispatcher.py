"""NetworkManager dispatcher entry point."""

from __future__ import annotations

from .config import load_config
from .nft import install_nft_rules, write_dnsmasq_config
from .paths import CONFIG_PATH, DNSMASQ_CONF, NFT_TABLE_FILE
from .schedule import local_now, schedule_state


def main() -> int:
    """Reapply rules after network changes."""
    cfg = load_config(CONFIG_PATH)
    state = schedule_state(local_now(), cfg.allow_start, cfg.allow_end, cfg.active_days)
    if not state.allowed:
        install_nft_rules(NFT_TABLE_FILE)
        write_dnsmasq_config(DNSMASQ_CONF, cfg, True)
    return 0
