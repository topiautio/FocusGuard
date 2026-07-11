# Development guide

Install development dependencies:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
```

Run checks:

```bash
pytest
ruff check .
black --check .
```

The package is intentionally small and modular:

- `config.py` validates TOML.
- `schedule.py` contains time-window logic.
- `matcher.py` contains wildcard/root domain matching.
- `nft.py` writes nftables and NetworkManager dnsmasq integration.
- `daemon.py` applies schedule transitions.
- `cli.py` provides user commands.
