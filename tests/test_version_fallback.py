from importlib.metadata import PackageNotFoundError

import pytest


def test_version_falls_back_when_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    """P3-02: an ad-hoc source-tree import should not raise just to read a
    version string that isn't needed to run anything."""
    from importlib.metadata import version as real_version

    def raise_not_found(name: str) -> str:
        raise PackageNotFoundError(name)

    monkeypatch.setattr("importlib.metadata.version", raise_not_found)
    import importlib

    import denckring

    reloaded = importlib.reload(denckring)
    assert reloaded.__version__ == "0+unknown"
    monkeypatch.setattr("importlib.metadata.version", real_version)
    importlib.reload(denckring)  # restore the real installed version for later tests
