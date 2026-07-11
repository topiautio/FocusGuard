# Security model

FocusGuard has no telemetry, analytics, or cloud dependency. It modifies local NetworkManager dnsmasq and nftables configuration and therefore the systemd daemon currently runs as root. The service uses systemd hardening options and write access is constrained to the FocusGuard configuration/state paths required for operation.

Future versions may split privilege boundaries into an unprivileged scheduler plus a small privileged rule-application helper.
