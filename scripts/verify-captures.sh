#!/usr/bin/env bash
set -euo pipefail

SCRATCH=${SCRATCH:-/tmp/grok-goal-328be8cb4070/implementer}

# Check files exist
for f in status-1.out status-2.out schedule-test.out rules-test.out matcher-test.out install-syntax.log version-1.out version-2.out daemon-launch.log system-state.log dnsmasq.conf; do
  if [ ! -f "$SCRATCH/$f" ]; then
    echo "MISSING $f"
    exit 1
  fi
done

# __file__ from site-packages (not src)
for f in schedule-test.out rules-test.out matcher-test.out; do
  if ! grep -q "focusguard.__file__:" "$SCRATCH/$f"; then
    echo "MISSING __file__ in $f"
    exit 1
  fi
  if ! grep "focusguard.__file__:" "$SCRATCH/$f" | grep -q "site-packages"; then
    echo "$f not from site-packages: $(grep focusguard.__file__ "$SCRATCH/$f")"
    exit 1
  fi
done

# Step 1
grep -q "Mode: " "$SCRATCH/status-1.out"
grep -q "Schedule: allow 15:00 → 22:00" "$SCRATCH/status-1.out"
grep -q "Next transition: " "$SCRATCH/status-1.out"
grep -q "Daemon running: " "$SCRATCH/status-1.out"

# Step 2: has schedule_state and PASS
grep -q "schedule_state" "$SCRATCH/schedule-test.out"
grep -q "SCHEDULE-TEST PASS" "$SCRATCH/schedule-test.out"

# Step 3: both enabled/disabled, only in enabled, NFT
grep -q "ipset=/x.com/ appears in focus-enabled output: True" "$SCRATCH/rules-test.out"
grep -q "ipset=/x.com/ appears in disabled output: False" "$SCRATCH/rules-test.out"
grep -q "music.youtube.com is omitted from enabled: True" "$SCRATCH/rules-test.out"
grep -q "RULES-TEST PASS" "$SCRATCH/rules-test.out"
grep -q "blocked_v4" "$SCRATCH/rules-test.out"
grep -q "tcp dport { 80, 443 } reject" "$SCRATCH/rules-test.out"

# Step 4: matcher-test.out
grep -q "MATCHER-TEST PASS" "$SCRATCH/matcher-test.out"
grep -q "is_blocked(x.com): True" "$SCRATCH/matcher-test.out"
grep -q "is_blocked(music.youtube.com): False" "$SCRATCH/matcher-test.out"

# Step 5
grep -q "BASH_N_EXIT=0" "$SCRATCH/install-syntax.log"
grep -q "FocusGuard 0.1.0" "$SCRATCH/version-1.out"
grep -q "FocusGuard 0.1.0" "$SCRATCH/version-2.out"

echo "All captures verified OK"
