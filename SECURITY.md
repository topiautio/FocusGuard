# Security policy

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature for this repository when it is available. Include the affected version or commit, impact, reproduction steps, and any suggested remediation.

If private vulnerability reporting is not enabled, open a public issue asking the maintainers to establish a private contact channel. Do not include exploit details, secrets, or sensitive system information in that issue.

Please allow a reasonable period for investigation and remediation before public disclosure.

## Supported versions

FocusGuard is currently an early-stage project. Security fixes are applied to the latest revision on the default branch; older revisions are not maintained separately.

## Security model

The core application has no telemetry, analytics, cloud dependency, or network-facing service. It modifies local NetworkManager dnsmasq and nftables configuration, so the systemd daemon runs as root. The service uses systemd hardening options and limits writable paths to the state, log, NetworkManager, and nftables locations required for operation.

Blocklist and whitelist configuration are trusted administrator inputs. DNS answers are external inputs and can influence which IP addresses are rejected for configured blocked domains; see [the documented limitations](docs/LIMITATIONS.md).

The optional browser extension runs content scripts only on its declared supported sites and stores boolean preferences with `chrome.storage.sync`. It does not send page content or browsing history to FocusGuard.
