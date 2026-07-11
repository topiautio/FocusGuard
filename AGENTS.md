# Agent Guidelines for FocusGuard

This project is intentionally small, focused, and boring in the best way. It is a local Linux website blocker using nftables + dnsmasq. The browser extension is a separate, optional companion.

**The primary goal is always to improve the actual product for users**, not to generate proof artifacts.

## Strict Rules for AI Agents and Automated Work

- **No verification theater.** Do not create elaborate harnesses, verification plans, capture scripts, pre-push gates, manifest files, "VERIFIED-*.txt" reports, github-sync verifiers, or any meta-layer whose main purpose is to prove that previous work was correct.

- **Verification is minimal and uses existing tools only.** When asked to "make sure it works", "verify", "test", or similar:
  - Run the documented checks (see below).
  - Optionally perform simple manual smoke tests (e.g. `focusguard status`, `focusguard --help`).
  - Stop after one clean pass. Do **not** enter loops of re-running, capturing output, "fresh evidence", "addressing gaps", or re-pushing reports.
  - One round of `pytest` + linters is sufficient unless actual bugs are found.

- **Vague goals are dangerous.** If given a vague instruction like "make the project do what it's supposed to do and fix it until it works" or "run in a loop until verified":
  - Break it down into specific, bounded tasks.
  - Ask for clarification if needed.
  - Never build scaffolding just to satisfy a verification loop.

- **Keep scripts/ minimal.** `scripts/` currently only contains runtime support files needed by the installer/daemon (e.g. the NetworkManager dispatcher). Do not add new scripts for verification, building, publishing manifests, or gates.

- **Changes must be useful.** Every change should make the blocker more reliable, the CLI better, installation smoother, docs clearer, or the extension nicer. Avoid changes whose only purpose is to make some internal check "pass".

- **Commit messages.** Use clear, conventional messages. Avoid messages that read like status reports to a skeptic ("re-verif", "honest evidence", "skeptic gaps", "app works as intended").

- **Loops and agents.** Unbounded or long-running verification/fix loops are prohibited unless the user explicitly and repeatedly asks for them with narrow scope. Prefer small, reviewable steps.

## Allowed Development Commands

See `docs/DEVELOPMENT.md` and the Development section in `README.md`.

Preferred single command for verification:

```bash
make verify
```

Or manually:

```bash
pytest
ruff check .
black --check .
```

For manual end-to-end testing, use a VM or container and `./install.sh` + the CLI. Do not automate this into complex harnesses.

## What "Done" Looks Like

- The feature or fix works for real users.
- Existing tests pass.
- Linters are happy.
- Code and docs are clear and minimal.
- No new meta-infrastructure was added.

If in doubt, make the smallest possible useful change and stop.

## Browser Extension

The `extension/` directory is a separate TypeScript project. Follow its own `package.json` scripts. The same "keep it simple" rules apply.
