# FocusGuard

FocusGuard is a local Linux website blocker for focus hours. It blocks distracting sites across Brave, Chrome, Chromium, and Firefox without browser extensions, cloud services, Docker, or a VM.

Default free time is **15:00 → 22:00** local time. Focus hours are **22:00 → 15:00**.

## Architecture

- Python daemon and CLI.
- systemd service with `Restart=always` for boot persistence and crash recovery.
- NetworkManager dnsmasq `ipset` rules classify configured domains.
- nftables rejects outbound HTTP/HTTPS traffic to classified IP addresses.
- Local logs live in `/var/log/focusguard/` and are rotated for 30 days.

See [limitations](docs/LIMITATIONS.md) for redirect-page and YouTube Music trade-offs.

## Installation

```bash
sudo ./install.sh
```

The installer verifies dependencies, installs the Python package, config, systemd unit, NetworkManager dispatcher hook, logrotate config, enables services, starts FocusGuard, and verifies the daemon is active.

## Configuration

Edit `/etc/focusguard/config.toml`:

```toml
allow_start = "15:00"
allow_end = "22:00"
notifications = true
logging = true
blocklist = ["reddit.com", "x.com"]
whitelist = ["music.youtube.com"]
```

Apply changes:

```bash
sudo systemctl restart focusguard
```

## CLI

```bash
focusguard status
focusguard stats
focusguard reload
focusguard logs
focusguard version
```

## Troubleshooting

- Check service state: `systemctl status focusguard`
- Check logs: `focusguard logs` or `journalctl -u focusguard`
- Ensure NetworkManager uses dnsmasq. The installer writes `/etc/NetworkManager/conf.d/90-focusguard-dnsmasq.conf` when needed.
- Browser DNS-over-HTTPS can bypass local DNS classification; disable forced DoH for best results.

## FAQ

### Why not `/etc/hosts`?
Hosts files are fragile for large services, cannot handle wildcard domains reliably, and do not integrate with per-schedule IP sets.

### Why no custom HTTPS block page?
Reliable HTTPS redirection requires TLS interception or per-browser certificates. FocusGuard chooses transparent, maintainable blocking instead.

### Is there telemetry?
No. FocusGuard stores only local logs and local aggregate state.

## Development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]' || pip install -e . pytest ruff black
pytest
ruff check .
black --check .
```

## License

MIT

## Browser extension: Distraction-Free Mode

FocusGuard also includes an optional Manifest V3 browser extension in `extension/` that turns distracting websites into intentional tools instead of blocking them entirely. It hides algorithmic feeds, recommendations, and infinite-scroll entry points on YouTube, Reddit, X/Twitter, and LinkedIn while preserving direct links, search, subscriptions/following, saved pages, profiles, jobs, messaging, playlists, and embedded videos.

Build and load the extension:

```bash
cd extension
npm install
npm run build
```

Then load `extension/dist/` as an unpacked extension in a Chromium-compatible browser. Per-site controls are available from the extension options page.
