#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then echo "Run as root: sudo ./install.sh" >&2; exit 1; fi
ROOT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
need=(python3 systemctl nft nmcli)
missing=()
for cmd in "${need[@]}"; do command -v "$cmd" >/dev/null 2>&1 || missing+=("$cmd"); done
if ((${#missing[@]})); then
  if command -v pacman >/dev/null 2>&1; then
    pacman -Sy --needed --noconfirm python nftables networkmanager python-pip
  else
    echo "Missing dependencies: ${missing[*]}. Install Python 3.13+, nftables, systemd, NetworkManager." >&2; exit 1
  fi
fi
python3 - <<'PY'
import sys
if sys.version_info < (3, 13):
    raise SystemExit('FocusGuard requires Python 3.13+')
PY
install -d /opt/focusguard /etc/focusguard /etc/systemd/system /etc/NetworkManager/dispatcher.d /etc/NetworkManager/dnsmasq.d /etc/nftables.d /var/lib/focusguard /var/log/focusguard /etc/logrotate.d
cp -a "$ROOT_DIR/src" "$ROOT_DIR/pyproject.toml" "$ROOT_DIR/README.md" "$ROOT_DIR/LICENSE" /opt/focusguard/
python3 -m pip install --break-system-packages --upgrade /opt/focusguard
if [[ ! -f /etc/focusguard/config.toml ]]; then install -m 0644 "$ROOT_DIR/config/config.toml" /etc/focusguard/config.toml; fi
install -m 0644 "$ROOT_DIR/systemd/focusguard.service" /etc/systemd/system/focusguard.service
install -m 0644 "$ROOT_DIR/systemd/focusguard-logrotate" /etc/logrotate.d/focusguard
install -m 0755 "$ROOT_DIR/scripts/focusguard-nm-dispatcher" /etc/NetworkManager/dispatcher.d/90-focusguard
if ! grep -q '^dns=dnsmasq' /etc/NetworkManager/NetworkManager.conf 2>/dev/null; then
  install -d /etc/NetworkManager/conf.d
  printf '[main]\ndns=dnsmasq\n' >/etc/NetworkManager/conf.d/90-focusguard-dnsmasq.conf
fi
systemctl daemon-reload
systemctl enable --now nftables NetworkManager focusguard
systemctl is-active --quiet focusguard || { journalctl -u focusguard -n 50 --no-pager; exit 1; }
echo "FocusGuard installed. Edit /etc/focusguard/config.toml and run: sudo systemctl restart focusguard"
