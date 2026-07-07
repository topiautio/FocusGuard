from focusguard.matcher import domain_matches, is_blocked


def test_root_pattern_matches_subdomain():
    assert domain_matches("www.reddit.com", "reddit.com")


def test_whitelist_overrides_block():
    assert not is_blocked("music.youtube.com", ("youtube.com",), ("music.youtube.com",))
