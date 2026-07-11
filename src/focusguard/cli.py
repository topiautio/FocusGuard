"""Command-line interface for FocusGuard."""

from __future__ import annotations

import argparse
import subprocess
import sys

from . import __version__
from .config import ConfigError, load_config
from .paths import CONFIG_PATH, LOG_PATH, STATE_PATH
from .schedule import local_now, schedule_state
from .state import summarize


def service_active() -> bool:
    """Return true when the daemon service is active."""
    return (
        subprocess.run(
            ["systemctl", "is-active", "--quiet", "focusguard"], check=False
        ).returncode
        == 0
    )


def cmd_status(_args: argparse.Namespace) -> int:
    """Print current status."""
    try:
        cfg = load_config(CONFIG_PATH)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    state = schedule_state(local_now(), cfg.allow_start, cfg.allow_end)
    print(f"Mode: {'free time' if state.allowed else 'focus hours'}")
    print(f"Schedule: allow {cfg.allow_start:%H:%M} → {cfg.allow_end:%H:%M}")
    print(f"Next transition: {state.next_transition:%Y-%m-%d %H:%M:%S %Z}")
    print(f"Daemon running: {'yes' if service_active() else 'no'}")
    return 0


def cmd_stats(_args: argparse.Namespace) -> int:
    """Print block statistics."""
    stats = summarize(STATE_PATH)
    print(f"Today's blocked attempts: {stats['today_count']}")
    print("Top blocked domains:")
    for domain, count in stats["top_domains"]:
        print(f"  {domain}: {count}")
    print(f"Weekly blocked attempts: {stats['weekly_count']}")
    return 0


def cmd_reload(_args: argparse.Namespace) -> int:
    """Reload the daemon."""
    result = subprocess.run(
        ["systemctl", "reload-or-restart", "focusguard"], check=False
    )
    return result.returncode


def cmd_logs(args: argparse.Namespace) -> int:
    """Show recent logs."""
    if not LOG_PATH.exists():
        print("No FocusGuard log file found.")
        return 0
    lines = LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()[
        -args.lines :
    ]
    print("\n".join(lines))
    return 0


def cmd_version(_args: argparse.Namespace) -> int:
    """Print version."""
    print(f"FocusGuard {__version__}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(prog="focusguard")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status").set_defaults(func=cmd_status)
    sub.add_parser("stats").set_defaults(func=cmd_stats)
    sub.add_parser("reload").set_defaults(func=cmd_reload)
    logs = sub.add_parser("logs")
    logs.add_argument("-n", "--lines", type=int, default=50)
    logs.set_defaults(func=cmd_logs)
    sub.add_parser("version").set_defaults(func=cmd_version)
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
