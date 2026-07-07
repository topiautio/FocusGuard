from focusguard.cli import main


def test_version(capsys):
    assert main(["version"]) == 0
    assert "FocusGuard" in capsys.readouterr().out
