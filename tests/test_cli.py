import unittest.mock as mock

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

def test_reload_rejects_invalid_config(tmp_path, monkeypatch, capsys):
    config_path = tmp_path / "config.toml"
    config_path.write_text("unknown = true\\n")
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)
    run = mock.Mock()
    monkeypatch.setattr(cli.subprocess, "run", run)

    assert main(["reload"]) == 2
    assert "Configuration error" in capsys.readouterr().err
    run.assert_not_called()


def test_reload_validates_config_before_reloading(tmp_path, monkeypatch):
    config_path = tmp_path / "config.toml"
    config_path.write_text("logging = false\\n")
    monkeypatch.setattr(cli, "CONFIG_PATH", config_path)
    run = mock.Mock(return_value=mock.Mock(returncode=0))
    monkeypatch.setattr(cli.subprocess, "run", run)

    assert main(["reload"]) == 0
    run.assert_called_once_with(
        ["systemctl", "reload-or-restart", "focusguard"], check=False
    )
