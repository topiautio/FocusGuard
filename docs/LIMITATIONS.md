# Limitations and trade-offs

FocusGuard uses NetworkManager dnsmasq `nftset` population (for nftables sets) plus nftables egress rejects. This is browser-independent and does not require extensions, but HTTPS requests show the browser's native connection failure page instead of a custom informational page. Transparent HTTPS redirection would require local certificate interception, which is brittle and invasive.

YouTube and YouTube Music share domains, CDNs, cookies, and media infrastructure. FocusGuard always excludes `music.youtube.com` from DNS nftset rules, which preserves the most common YouTube Music flow. Some embedded media or already-resolved YouTube CDN connections may continue or fail depending on browser DNS cache and connection reuse.

DNS-over-HTTPS inside a browser can bypass local DNS-based classification. FocusGuard still blocks IPs learned by local DNS, but users who force browser DoH may need to disable it or configure enterprise policies.
