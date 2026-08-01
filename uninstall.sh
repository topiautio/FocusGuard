#!/usr/bin/env bash
set -euo pipefail
if [[ ${EUID} -ne 0 ]]; then echo "Run as root: sudo ./uninstall.sh" >&2; exit 1; fi
APP_DIR=/opt/focusguard
VENV_DIR=$APP_DIR/.venv
BIN_DIR=/usr/local/bin
systemctl disable --now focusguard 2>/dev/null || true
nft delete table inet focusguard 2>/dev/null || true
rm -f /etc/systemd/system/focusguard.service /etc/logrotate.d/focusguard /etc/NetworkManager/dispatcher.d/90-focusguard /etc/NetworkManager/dnsmasq.d/focusguard.conf /etc/NetworkManager/conf.d/90-focusguard-dnsmasq.conf /etc/nftables.d/focusguard.nft
for exe in focusguard focusguard-daemon focusguard-nm-dispatcher; do
  link="$BIN_DIR/$exe"
  legacy_link="/usr/bin/$exe"
  if [[ -L "$legacy_link" ]] && [[ $(readlink "$legacy_link") == "$BIN_DIR/$exe" ]]; then
    rm -f "$legacy_link"
  fi
  if [[ -L "$link" ]] && [[ $(readlink "$link") == "$VENV_DIR/bin/$exe" ]]; then
    rm -f "$link"
  fi
  legacy="/usr/bin/$exe"
  if [[ -f "$legacy" && ! -L "$legacy" ]] \
    && { ! command -v pacman >/dev/null 2>&1 || ! pacman -Qo "$legacy" >/dev/null 2>&1; } \
    && grep -Fq "from focusguard." "$legacy" \
    && grep -Fq "sys.argv[0]" "$legacy"; then
    rm -f "$legacy"
  fi
done
rm -rf "$APP_DIR" /var/lib/focusguard
read -r -p "Remove /etc/focusguard configuration? [y/N] " cfg
[[ ${cfg,,} == y ]] && rm -rf /etc/focusguard
read -r -p "Remove /var/log/focusguard logs? [y/N] " logs
[[ ${logs,,} == y ]] && rm -rf /var/log/focusguard
systemctl daemon-reload
systemctl reload-or-restart NetworkManager 2>/dev/null || true
echo "FocusGuard uninstalled."
