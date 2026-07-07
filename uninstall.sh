#!/usr/bin/env bash
set -euo pipefail
if [[ ${EUID} -ne 0 ]]; then echo "Run as root: sudo ./uninstall.sh" >&2; exit 1; fi
systemctl disable --now focusguard 2>/dev/null || true
nft delete table inet focusguard 2>/dev/null || true
rm -f /etc/systemd/system/focusguard.service /etc/logrotate.d/focusguard /etc/NetworkManager/dispatcher.d/90-focusguard /etc/NetworkManager/dnsmasq.d/focusguard.conf /etc/nftables.d/focusguard.nft
python3 -m pip uninstall -y focusguard >/dev/null 2>&1 || true
rm -rf /opt/focusguard /var/lib/focusguard
read -r -p "Remove /etc/focusguard configuration? [y/N] " cfg
[[ ${cfg,,} == y ]] && rm -rf /etc/focusguard
read -r -p "Remove /var/log/focusguard logs? [y/N] " logs
[[ ${logs,,} == y ]] && rm -rf /var/log/focusguard
systemctl daemon-reload
systemctl reload-or-restart NetworkManager 2>/dev/null || true
echo "FocusGuard uninstalled."
