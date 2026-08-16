# Limitations and trade-offs

FocusGuard uses NetworkManager dnsmasq `nftset` population plus nftables egress rejection. This is browser-independent and does not require an extension, but HTTPS requests show the browser's native connection-failure page instead of a custom informational page. Transparent HTTPS redirection would require local certificate interception, which is brittle and invasive.

## DNS classification

Browser DNS-over-HTTPS can bypass local DNS-based classification. FocusGuard can reject only addresses learned through the local dnsmasq path, so users who force browser DoH may need to disable it or apply an appropriate browser policy.

A blocked hostname is converted to its current IPv4 and IPv6 answers. An address may host multiple unrelated services, so blocking one domain can also affect other services on the same address. A DNS authority for a configured blocked name also controls which addresses enter the FocusGuard sets. Because the blocklist is root-controlled, this is a constrained local availability risk, but administrators should treat blocklist entries as trusted policy inputs.

`focusguard status` checks only whether the expected nftables table and generated dnsmasq rules are observable. It cannot prove that every current DNS answer is in the sets or detect browser DNS-over-HTTPS bypasses, and an unprivileged status invocation may report `unknown`.

The dynamically populated nftables sets currently have no explicit element timeout or size bound. FocusGuard recreates its dedicated table across mode transitions, which clears the sets, but unusually large or rapidly changing DNS answer sets have not been measured in a disposable privileged environment.

## Shared service infrastructure

YouTube and YouTube Music share domains, cookies, and media infrastructure, including `googlevideo.com` and `ytimg.com`. A whitelist such as `music.youtube.com` causes FocusGuard to omit an overlapping parent block rule such as `youtube.com`; explicit sibling rules such as `www.youtube.com` can remain. Shared CDN rules may still affect video or audio delivery for both services.

## Connection lifecycle

The nftables rules reject TCP ports 80 and 443 plus UDP 443 for QUIC/HTTP/3. Existing connections, browser DNS caches, pre-resolved addresses, embedded media, or connection reuse may continue briefly around a mode transition.

## Desktop notifications

Desktop notifications are best-effort. The system service may not have access to a graphical user's D-Bus session, and headless systems may not provide `notify-send`; either condition only suppresses the notification and does not change enforcement.
