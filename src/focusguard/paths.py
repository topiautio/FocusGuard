"""Filesystem paths used by FocusGuard."""

from pathlib import Path

CONFIG_PATH = Path("/etc/focusguard/config.toml")
STATE_DIR = Path("/var/lib/focusguard")
LOG_DIR = Path("/var/log/focusguard")
LOG_PATH = LOG_DIR / "focusguard.log"
STATE_PATH = STATE_DIR / "state.json"
DNSMASQ_CONF = Path("/etc/NetworkManager/dnsmasq.d/focusguard.conf")
NFT_TABLE_FILE = Path("/etc/nftables.d/focusguard.nft")
