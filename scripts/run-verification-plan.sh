#!/usr/bin/env bash
set -euo pipefail

SCRATCH=${SCRATCH:-/tmp/grok-goal-328be8cb4070/implementer}
REPO=/home/topi/git/FocusGuard
VENV=/tmp/fg-plan-venv

mkdir -p "$SCRATCH"

if [ ! -x "$VENV/bin/python" ]; then
  echo "Creating pinned non-editable venv at $VENV ..."
  rm -rf "$VENV"
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install "$REPO"
fi

PYTHON="$VENV/bin/python"
FG="$VENV/bin/focusguard"

echo "=== Using installed package from venv ==="
"$PYTHON" -c 'import focusguard; print("focusguard.__file__:", focusguard.__file__)'

# Step 1: focusguard status x2 (real installed CLI)
echo "=== Step 1: focusguard status x2 ==="
"$FG" status > "$SCRATCH/status-1.out" 2>&1
cat "$SCRATCH/status-1.out"
"$FG" status > "$SCRATCH/status-2.out" 2>&1
cat "$SCRATCH/status-2.out"

# Step 2: schedule with schedule_state
echo "=== Step 2: schedule-test ==="
"$PYTHON" -c '
import focusguard
print("focusguard.__file__:", focusguard.__file__)
from focusguard.schedule import is_allowed, schedule_state
from datetime import datetime, time
start = time(15, 0)
end = time(22, 0)
dt16 = datetime(2026, 7, 11, 16, 0)
print("16:00 is_allowed:", is_allowed(dt16, start, end))
st16 = schedule_state(dt16, start, end)
print("16:00 schedule_state allowed:", st16.allowed, "next_transition:", st16.next_transition)
dt23 = datetime(2026, 7, 11, 23, 0)
print("23:00 is_allowed:", is_allowed(dt23, start, end))
st23 = schedule_state(dt23, start, end)
print("23:00 schedule_state allowed:", st23.allowed, "next_transition:", st23.next_transition)
dt9 = datetime(2026, 7, 11, 9, 0)
print("09:00 is_allowed:", is_allowed(dt9, start, end))
st9 = schedule_state(dt9, start, end)
print("09:00 schedule_state allowed:", st9.allowed, "next_transition:", st9.next_transition)
assert is_allowed(dt16, start, end) == True
assert is_allowed(dt23, start, end) == False
assert is_allowed(dt9, start, end) == False
assert st16.allowed == True
assert st23.allowed == False
assert st9.allowed == False
print("SCHEDULE-TEST PASS")
' > "$SCRATCH/schedule-test.out" 2>&1
cat "$SCRATCH/schedule-test.out"

# Step 3: rules with both enabled
echo "=== Step 3: rules-test ==="
"$PYTHON" -c '
import focusguard
print("focusguard.__file__:", focusguard.__file__)
from focusguard.config import Config
from focusguard.nft import write_dnsmasq_config, NFT_RULES
from pathlib import Path
import tempfile, shutil, os
cfg = Config()
print("x.com present in default blocklist:", "x.com" in cfg.blocklist)
with tempfile.TemporaryDirectory() as td:
    p_en = Path(td) / "enabled.conf"
    p_dis = Path(td) / "disabled.conf"
    write_dnsmasq_config(p_en, cfg, True)
    write_dnsmasq_config(p_dis, cfg, False)
    shutil.copy(str(p_en), os.environ.get("SCRATCH", "/tmp") + "/dnsmasq.conf")
    c_en = p_en.read_text()
    c_dis = p_dis.read_text()
print("=== enabled dnsmasq ===")
print(c_en)
print("=== disabled dnsmasq ===")
print(c_dis)
print("=== NFT_RULES ===")
print(NFT_RULES)
print("ipset=/x.com/ appears in focus-enabled output:", "ipset=/x.com/" in c_en)
print("ipset=/x.com/ appears in disabled output:", "ipset=/x.com/" in c_dis)
print("music.youtube.com is omitted from enabled:", "music.youtube.com" not in c_en)
print("NFT_RULES has blocked_v4 reject on 80/443:", "blocked_v4" in NFT_RULES and "tcp dport { 80, 443 } reject" in NFT_RULES)
print("NFT_RULES has v6 equivalent:", "blocked_v6" in NFT_RULES)
assert "ipset=/x.com/" in c_en
assert "ipset=/x.com/" not in c_dis
assert "music.youtube.com" not in c_en
assert "blocked_v4" in NFT_RULES and "tcp dport { 80, 443 } reject" in NFT_RULES
print("RULES-TEST PASS")
' > "$SCRATCH/rules-test.out" 2>&1
cat "$SCRATCH/rules-test.out"

# Step 4: matcher separate
echo "=== Step 4: matcher-test ==="
"$PYTHON" -c '
import focusguard
print("focusguard.__file__:", focusguard.__file__)
from focusguard.matcher import is_blocked
from focusguard.config import DEFAULT_BLOCKLIST, DEFAULT_WHITELIST
bl = tuple(DEFAULT_BLOCKLIST)
wl = tuple(DEFAULT_WHITELIST)
print("is_blocked(x.com):", is_blocked("x.com", bl, wl))
print("is_blocked(www.reddit.com):", is_blocked("www.reddit.com", bl, wl))
print("is_blocked(music.youtube.com):", is_blocked("music.youtube.com", bl, wl))
assert is_blocked("x.com", bl, wl) == True
assert is_blocked("www.reddit.com", bl, wl) == True
assert is_blocked("music.youtube.com", bl, wl) == False
print("MATCHER-TEST PASS")
' > "$SCRATCH/matcher-test.out" 2>&1
cat "$SCRATCH/matcher-test.out"

# Step 5
echo "=== Step 5: install-syntax and versions ==="
( echo "=== bash -n $REPO/install.sh ===" ; bash -n "$REPO/install.sh" ; echo "BASH_N_EXIT=0" ) > "$SCRATCH/install-syntax.log" 2>&1
"$FG" version > "$SCRATCH/version-1.out" 2>&1
cat "$SCRATCH/version-1.out"
"$FG" version > "$SCRATCH/version-2.out" 2>&1
cat "$SCRATCH/version-2.out"

# Step 6
echo "=== Step 6: daemon-launch ==="
timeout 3s /usr/bin/focusguard-daemon 2>&1 | tee "$SCRATCH/daemon-launch.log" || true

# Step 7
echo "=== Step 7: system-state ==="
{
  echo "=== /etc/focusguard/config.toml ==="
  cat /etc/focusguard/config.toml 2>/dev/null || echo "(missing)"
  echo "=== focusguard logs -n 20 ==="
  focusguard logs -n 20 2>&1 || true
  echo "=== journalctl -u focusguard -n 20 --no-pager ==="
  journalctl -u focusguard -n 20 --no-pager 2>&1 || true
} > "$SCRATCH/system-state.log"

echo "=== verification plan run complete ==="
