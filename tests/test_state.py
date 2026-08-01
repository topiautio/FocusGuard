from focusguard.state import load_state


def test_missing_or_invalid_state_returns_an_empty_mapping(tmp_path):
    path = tmp_path / "missing.json"
    assert load_state(path) == {}

    path.write_text("[]")
    assert load_state(path) == {}
