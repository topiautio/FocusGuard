import pytest

from focusguard.config import (
    ConfigError,
    load_config,
    normalize_domain,
    parse_time,
)


def test_parse_time():
    assert parse_time("15:30").hour == 15


def test_normalize_domain():
    assert normalize_domain("HTTPS://Reddit.com/") == "reddit.com"


def test_load_config(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text(
        'allow_start = "10:00"\n'
        'active_days = ["Friday", "monday"]\n'
        'blocklist = ["reddit.com"]\n'
    )
    cfg = load_config(path)
    assert cfg.allow_start.hour == 10
    assert cfg.active_days == ("monday", "friday")
    assert cfg.blocklist == ("reddit.com",)


def test_missing_config_defaults_to_all_days(tmp_path):
    cfg = load_config(tmp_path / "missing.toml")

    assert cfg.active_days == (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )


def test_unknown_key(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("bad = true\n")
    with pytest.raises(ConfigError):
        load_config(path)


def test_invalid_active_day(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text('active_days = ["monday", "someday"]\n')

    with pytest.raises(ConfigError, match="invalid active_days"):
        load_config(path)


@pytest.mark.parametrize(
    ("field", "value"),
    [("blocklist", "[1]"), ("whitelist", "false")],
)
def test_invalid_domain_list(tmp_path, field, value):
    path = tmp_path / "config.toml"
    path.write_text(f"{field} = {value}\n")

    with pytest.raises(ConfigError, match=f"{field} must be an array"):
        load_config(path)
