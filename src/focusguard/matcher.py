"""Domain matching helpers."""


def domain_matches(domain: str, pattern: str) -> bool:
    """Return true when domain matches an exact or wildcard/root pattern."""
    domain = domain.lower().strip(".")
    pattern = pattern.lower().strip(".")
    if pattern.startswith("*."):
        suffix = pattern[2:]
        return domain == suffix or domain.endswith(f".{suffix}")
    return domain == pattern or domain.endswith(f".{pattern}")


def is_blocked(
    domain: str, blocklist: tuple[str, ...], whitelist: tuple[str, ...]
) -> bool:
    """Return true if the domain should be blocked after whitelist overrides."""
    if any(domain_matches(domain, item) for item in whitelist):
        return False
    return any(domain_matches(domain, item) for item in blocklist)
