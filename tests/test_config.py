import pytest

from focusguard.config import ConfigError, load_config, normalize_domain, parse_time


def test_parse_time():
    assert parse_time("15:30").hour == 15


def test_normalize_domain():
    assert normalize_domain("HTTPS://Reddit.com/") == "reddit.com"


def test_load_config(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('allow_start = "10:00"\nblocklist = ["reddit.com"]\n')
    cfg = load_config(path)
    assert cfg.allow_start.hour == 10
    assert cfg.blocklist == ("reddit.com",)


def test_unknown_key(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("bad = true\n")
    with pytest.raises(ConfigError):
        load_config(path)
