# FocusGuard

FocusGuard is a schedule-driven website blocker for Linux. It helps make a focus routine harder to bypass by enforcing blocks at the operating-system network layer instead of relying on a browser tab, cloud service, or account.

Technically, a small Python daemon switches between focus and free-use modes. During focus mode, NetworkManager's embedded dnsmasq classifies configured domains and adds their resolved addresses to nftables sets; nftables then rejects outbound web traffic to those addresses. systemd keeps the daemon running across boots and restarts. The core blocker therefore relies on Python, systemd, NetworkManager, dnsmasq, and nftables.

The repository also contains an optional Chromium-compatible browser extension that hides recommendation feeds and other high-distraction interface elements without blocking the entire site.

## How it works

```text
config.toml
    │
    ▼
Python daemon and CLI ── managed by systemd
    │
    ├── writes dnsmasq nftset rules through NetworkManager
    │       └── resolved blocklist addresses populate nftables sets
    │
    └── creates or removes the dedicated `inet focusguard` nftables table
            └── rejects TCP 80/443 and UDP 443 during focus mode
```

- `focusguard-daemon` reads the allow window, active days, and domain rules from `/etc/focusguard/config.toml`.
- In focus mode, it installs a dedicated nftables table and writes NetworkManager dnsmasq integration under `/etc/NetworkManager/dnsmasq.d/`.
- dnsmasq adds IPv4 and IPv6 answers for matching domains to the FocusGuard nftables sets.
- In free-use mode, the daemon removes the dedicated table and stops emitting block rules.
- The `focusguard` CLI reports status, reloads configuration, and exposes local logs.

FocusGuard does not replace the host's main firewall configuration and does not require Docker, a virtual machine, or a browser extension for core blocking.

## Requirements

- Linux with systemd
- Python 3.13 or newer with pip and venv support
- NetworkManager using its embedded dnsmasq integration
- nftables

The installer can install missing packages automatically on pacman-based systems. On other distributions, install the requirements with the system package manager first.

## Installation

Run the installer from a trusted checkout:

```bash
sudo ./install.sh
```

The installer installs the Python package into an isolated `/opt/focusguard/.venv`, creates CLI links in `/usr/local/bin`, and installs the example configuration, systemd unit, NetworkManager dispatcher hook, nftables support files, and logrotate configuration. It does not modify the system Python environment. It enables and starts the required services, which may briefly reload or restart NetworkManager.

To remove FocusGuard:

```bash
sudo ./uninstall.sh
```

The uninstaller asks before removing user configuration or logs.

## Configuration

Edit `/etc/focusguard/config.toml`. This example allows unrestricted use from 15:00 until 22:00 local time and enables focus mode outside that window:

```toml
allow_start = "15:00"
allow_end = "22:00"

# Apply the schedule on these calendar days. Omit this key to use every day.
active_days = [
  "monday",
  "tuesday",
  "wednesday",
  "thursday",
  "friday",
  "saturday",
  "sunday"
]

notifications = true
logging = false

blocklist = [
  "reddit.com",
  "x.com",
  "youtube.com",
  "www.youtube.com"
]

whitelist = ["music.youtube.com"]
```

Persistent file logging is disabled by default. Set `logging = true` if you want FocusGuard to write its rotated log file; with logging disabled, service messages remain available through `journalctl -u focusguard`.

The allow window is configurable and may cross midnight. `active_days` is optional, accepts lowercase or uppercase day names, and defaults to all seven days. On days not listed, FocusGuard stays in free-use mode for the entire calendar day; an empty list disables scheduled blocking. For example, use `active_days = ["monday", "tuesday", "wednesday", "thursday", "friday"]` for weekdays only. A whitelist entry takes precedence over an overlapping blocklist entry. If a whitelisted child domain overlaps a blocked parent, FocusGuard omits the parent rule; list any sibling domains that should remain blocked explicitly. Shared CDN domains may still affect both sites.

Apply changes with:

```bash
sudo systemctl restart focusguard
```

Domain entries may be exact domains, parent domains that include their subdomains, or patterns such as `*.example.com`. Invalid domains and unknown configuration keys are rejected.

## CLI

```bash
focusguard status
focusguard reload
focusguard logs
focusguard version
```

Reloading the system service requires appropriate systemd permissions, typically by running `sudo focusguard reload`.

## Limitations

- HTTPS blocks use the browser's normal connection-failure page. A custom HTTPS block page would require TLS interception or per-browser certificates.
- DNS-over-HTTPS can bypass local DNS classification.
- DNS-based IP blocking can affect unrelated services that share a returned address with a blocked domain. DNS answers for a blocked name also become part of the local firewall decision, so block only domains you trust as policy inputs.
- DNS caches, existing connections, and embedded media can briefly outlive a mode transition.
- Services such as YouTube and YouTube Music share domains and CDN infrastructure, so a precise split is not always possible.

See [limitations and trade-offs](docs/LIMITATIONS.md) for details.

## Privacy and telemetry

The core blocker has no telemetry, analytics, cloud service, or outbound reporting. Configuration and runtime state remain on the local machine. Persistent logs are disabled by default; when enabled, they are stored in `/var/log/focusguard/` and rotated for 30 days.

The optional browser extension stores only boolean site preferences with `chrome.storage.sync`. Depending on browser settings, the browser vendor may synchronize those preferences through the signed-in browser account. The extension does not transmit browsing history or page content to FocusGuard.

## Browser extension: Distraction-Free Mode

The optional Manifest V3 extension hides algorithmic feeds, recommendations, and infinite-scroll entry points on YouTube, Reddit, X/Twitter, and LinkedIn while preserving direct links, search, subscriptions or following views, saved pages, profiles, jobs, messaging, playlists, and embedded videos.

Build and load it with:

```bash
cd extension
npm ci
npm run build
```

Then load `extension/dist/` as an unpacked extension in a Chromium-compatible browser. Per-site controls are available from the extension options page.

## Troubleshooting

- Check service state: `systemctl status focusguard`
- Check logs: `focusguard logs` or `journalctl -u focusguard`
- Confirm that NetworkManager is active and uses dnsmasq. The installer writes `/etc/NetworkManager/conf.d/90-focusguard-dnsmasq.conf` when needed.
- Disable forced browser DNS-over-HTTPS if domains are not being classified.

## Development and contributing

See [the development guide](docs/DEVELOPMENT.md) for setup, tests, extension builds, and manual VM testing. The standard verification command is:

```bash
make verify
```

Bug reports and focused pull requests are welcome. Security issues should follow [the security policy](SECURITY.md). See also [AGENTS.md](AGENTS.md) for repository-specific rules for AI coding agents.

## FAQ

### Why not `/etc/hosts`?

Hosts files are fragile for large services, cannot express wildcard behavior cleanly, and do not integrate with scheduled dynamic IP sets.

### Why no custom HTTPS block page?

Reliable HTTPS redirection requires TLS interception or per-browser certificates. FocusGuard deliberately favors a smaller, transparent network policy.

### Is there telemetry?

No. The core application stores local operational data only. See [Privacy and telemetry](#privacy-and-telemetry) for the optional extension's preference-sync behavior.

## License

FocusGuard is available under the [MIT License](LICENSE).
