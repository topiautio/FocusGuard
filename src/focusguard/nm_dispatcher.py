"""NetworkManager dispatcher entry point."""

from __future__ import annotations

from .config import load_config
from .nft import disable_nft_rules, install_nft_rules, write_dnsmasq_config
from .paths import CONFIG_PATH, DNSMASQ_CONF, NFT_TABLE_FILE
from .schedule import local_now, schedule_state


def main() -> int:
    """Reconcile enforcement with the schedule after network changes."""
    cfg = load_config(CONFIG_PATH)
    state = schedule_state(local_now(), cfg.allow_start, cfg.allow_end, cfg.active_days)
    should_block = not state.allowed
    if should_block:
        install_nft_rules(NFT_TABLE_FILE)
    else:
        disable_nft_rules()
    write_dnsmasq_config(DNSMASQ_CONF, cfg, should_block)
    return 0
