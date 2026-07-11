# Development guide

See also: [AGENTS.md](../AGENTS.md) — important rules for AI agents and automated work.

## Setup

Install development dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

Or with Make:

```bash
make install-dev
```

## Verification

Run checks with:

```bash
make verify
```

Or manually:

```bash
pytest
ruff check .
black --check .
```

**Verification must stay minimal.** See AGENTS.md for strict rules against building elaborate harnesses, reports, gates, or verification loops.

The package is intentionally small and modular:

- `config.py` validates TOML.
- `schedule.py` contains time-window logic.
- `matcher.py` contains wildcard/root domain matching.
- `nft.py` writes nftables and NetworkManager dnsmasq integration.
- `daemon.py` applies schedule transitions.
- `cli.py` provides user commands.

## Manual Testing

For end-to-end testing of install + daemon, use a VM or disposable container:

```bash
sudo ./install.sh
focusguard status
# ... exercise the CLI and schedule
```

Do not automate this into complex scripts or harnesses.

