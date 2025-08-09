from pbcli import clipboard as cb


def test_file_cache_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    text = "hello world"
    cb.copy(text, backend="file")
    got = cb.paste(backend="file")
    assert got == text
