import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest

from denckring.core.errors import UnknownLanguage
from denckring.lang import get_pack, installed_languages


def test_english_is_available_without_entry_point_metadata() -> None:
    assert get_pack("en").lang == "en"


def test_installed_languages_reports_what_is_loadable() -> None:
    assert "en" in installed_languages()


def test_unknown_language_still_raises() -> None:
    with pytest.raises(UnknownLanguage):
        get_pack("xx")


def test_two_packs_claiming_one_language_raise_rather_than_one_winning() -> None:
    """Silently taking whichever loaded first is the failure ADR 0004 forbids."""
    from denckring.core.protocol import LanguagePack
    from denckring.lang import DuplicatePack, _install
    from denckring.lang.en import EnglishPack

    installed: dict[str, LanguagePack] = {}
    _install(installed, "en", EnglishPack(), source="first")
    with pytest.raises(DuplicatePack, match="first"):
        _install(installed, "en", EnglishPack(), source="second")


def test_german_is_a_default_so_a_data_pack_can_override_it() -> None:
    """A data distribution claiming `de` must win, not collide.

    German shipped as an entry point (ADR 0010). Two entry points claiming one
    language raise DuplicatePack, so `pip install denckring[de]` would have
    broken on first use.
    """
    from denckring.lang import _DEFAULTS

    assert "de" in _DEFAULTS, "German must be a default for a data pack to override it"


def test_core_declares_no_language_entry_points() -> None:
    import tomllib
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "pyproject.toml"
    manifest = tomllib.loads(root.read_text(encoding="utf-8"))
    groups = manifest["project"].get("entry-points", {})
    assert "denckring.lang" not in groups, (
        "core must not claim a language by entry point; a data pack could not override it"
    )


def test_the_german_data_pack_overrides_the_core_pack_when_installed() -> None:
    """The whole point of Task 1: an entry point beats a default, no collision."""
    pytest.importorskip("denckring_de_data")
    from denckring.lang.base import NOUNS

    pack = get_pack("de")
    assert NOUNS in pack.capabilities, "the data pack did not win over the core pack"


class _FakeEntryPoint:
    def __init__(self, name: str, value: str, factory: object) -> None:
        self.name = name
        self.value = value
        self._factory = factory

    def load(self) -> object:
        return self._factory


def test_a_late_caller_blocks_until_pack_discovery_finishes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P1-01: a second thread must block on the lock, not see a partial `_PACKS`."""
    from denckring import lang as lang_module
    from denckring.lang.en import EnglishPack

    saved_packs = dict(lang_module._PACKS)
    saved_sources = dict(lang_module._SOURCES)
    saved_discovered = lang_module._DISCOVERED
    monkeypatch.setattr(lang_module, "_PACKS", {})
    monkeypatch.setattr(lang_module, "_SOURCES", {})
    monkeypatch.setattr(lang_module, "_DISCOVERED", False)

    release = threading.Event()

    def slow_factory() -> EnglishPack:
        assert release.wait(timeout=5), "test setup did not release the held thread"
        return EnglishPack()

    fake_entry = _FakeEntryPoint("en", "fake.module:factory", slow_factory)
    monkeypatch.setattr(lang_module, "entry_points", lambda group=None: [fake_entry])

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(lang_module.installed_languages)
        time.sleep(0.1)
        second = pool.submit(lang_module.installed_languages)
        time.sleep(0.1)
        assert not second.done(), "a concurrent caller must block, not see a partial _PACKS"
        release.set()
        result_first = first.result(timeout=5)
        result_second = second.result(timeout=5)

    assert result_first == result_second

    monkeypatch.setattr(lang_module, "_PACKS", saved_packs)
    monkeypatch.setattr(lang_module, "_SOURCES", saved_sources)
    monkeypatch.setattr(lang_module, "_DISCOVERED", saved_discovered)


def test_a_failed_entry_point_can_be_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    """P1-01: a broken third-party pack must not permanently poison discovery,
    and must not partially publish into `_PACKS` before the failure."""
    from denckring import lang as lang_module
    from denckring.lang.en import EnglishPack

    saved_packs = dict(lang_module._PACKS)
    saved_sources = dict(lang_module._SOURCES)
    saved_discovered = lang_module._DISCOVERED
    monkeypatch.setattr(lang_module, "_PACKS", {})
    monkeypatch.setattr(lang_module, "_SOURCES", {})
    monkeypatch.setattr(lang_module, "_DISCOVERED", False)

    attempt = {"count": 0}

    def broken_factory() -> EnglishPack:
        if attempt["count"] == 0:
            attempt["count"] += 1
            raise RuntimeError("simulated broken third-party pack")
        return EnglishPack()

    fake_entry = _FakeEntryPoint("en", "broken.module:factory", broken_factory)
    monkeypatch.setattr(lang_module, "entry_points", lambda group=None: [fake_entry])

    with pytest.raises(RuntimeError):
        lang_module._discover()
    assert lang_module._DISCOVERED is False
    assert lang_module._PACKS == {}, "a failed attempt must not partially publish"

    lang_module._discover()
    assert lang_module._is_discovered() is True
    assert "en" in lang_module._PACKS

    monkeypatch.setattr(lang_module, "_PACKS", saved_packs)
    monkeypatch.setattr(lang_module, "_SOURCES", saved_sources)
    monkeypatch.setattr(lang_module, "_DISCOVERED", saved_discovered)
