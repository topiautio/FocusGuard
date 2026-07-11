.PHONY: verify install-dev clean

install-dev:
	python -m venv .venv
	. .venv/bin/activate && pip install -e '.[dev]'

verify:
	python -m pytest
	python -m ruff check .
	python -m black --check .

# Manual full verification (run in a VM or disposable container as root):
#   sudo ./install.sh
#   focusguard status
#   focusguard --help
#   sudo systemctl status focusguard

clean:
	rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
