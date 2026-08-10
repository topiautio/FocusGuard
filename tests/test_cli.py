import focusguard.cli as cli
from focusguard.cli import main


def test_version(capsys):
    assert main(["version"]) == 0
    assert "FocusGuard" in capsys.readouterr().out


def test_logs_reports_disabled_logging(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
    config_path.write_text("logging = false\n")
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)

    assert main(["logs"]) == 0
    assert "Persistent logging is disabled" in capsys.readouterr().out
