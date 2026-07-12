# Limitations and trade-offs

FocusGuard uses NetworkManager dnsmasq `nftset` population (for nftables sets) plus nftables egress rejects. This is browser-independent and does not require extensions, but HTTPS requests show the browser's native connection failure page instead of a custom informational page. Transparent HTTPS redirection would require local certificate interception, which is brittle and invasive.

YouTube and YouTube Music share domains, CDNs, cookies, and media infrastructure (notably `googlevideo.com` and `ytimg.com` for video/audio delivery). FocusGuard blocks the main `youtube.com` / `youtu.be` domains plus the common CDNs, but always excludes `music.youtube.com` from explicit DNS nftset rules (to preserve the YouTube Music web UI where possible). Video and audio streams for both regular YouTube and YouTube Music may still be affected by the shared CDN blocks.

The nft rules reject both TCP (80/443) and UDP 443 (QUIC/HTTP3) to classified IPs. Some embedded media, pre-resolved connections, browser DNS cache, or connection reuse may still succeed briefly.

DNS-over-HTTPS inside a browser can bypass local DNS-based classification entirely.

DNS-over-HTTPS inside a browser can bypass local DNS-based classification. FocusGuard still blocks IPs learned by local DNS, but users who force browser DoH may need to disable it or configure enterprise policies.
