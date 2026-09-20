import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

import pytest
from pydantic import BaseModel

from denckring.core import catalogue, registry
from denckring.core.base import BaseProcedure
from denckring.core.errors import UnknownProcedure
from denckring.core.protocol import LanguagePack, Report


def test_get_raises_on_unknown_id() -> None:
    with pytest.raises(UnknownProcedure):
        registry.get("wobble")


def test_registered_ids_are_a_subset_of_the_catalogue() -> None:
    assert set(registry.all_procedures()) <= set(catalogue.ids())


def test_every_registered_procedure_is_a_base_procedure() -> None:
    for proc in registry.all_procedures().values():
        assert isinstance(proc, BaseProcedure)


def test_module_name_must_equal_procedure_id() -> None:
    for proc_id, proc in registry.all_procedures().items():
        assert type(proc).__module__.rsplit(".", 1)[-1] == proc_id


def test_registering_a_procedure_whose_module_disagrees_with_its_id_fails() -> None:
    class Params(BaseModel):
        pass

    class Mismatched(BaseProcedure[Params]):
        id = "definitely_not_this_module"

        @classmethod
        def params_model(cls) -> type[Params]:
            return Params

        def _check(self, text: str, pack: LanguagePack, params: Params) -> Report:
            raise NotImplementedError

    with pytest.raises(ValueError, match="module"):
        registry.register(Mismatched)


def test_a_late_caller_blocks_until_discovery_finishes_rather_than_seeing_partial_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """P1-01: a second thread racing `_discover()` must block on the lock, not
    return a registry that is still being populated by the first thread."""
    saved_registry = dict(registry._REGISTRY)
    saved_discovered = registry._DISCOVERED
    monkeypatch.setattr(registry, "_REGISTRY", {})
    monkeypatch.setattr(registry, "_DISCOVERED", False)

    release = threading.Event()
    original_import_module = registry.importlib.import_module

    def slow_import(name: str, *a: Any, **kw: Any) -> Any:
        result = original_import_module(name, *a, **kw)
        if name == "denckring.procedures.anagram":
            assert release.wait(timeout=5), "test setup did not release the held thread"
        return result

    monkeypatch.setattr(registry.importlib, "import_module", slow_import)

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(registry.all_procedures)
        time.sleep(0.1)  # let the first thread acquire the lock and reach "anagram"
        second = pool.submit(registry.all_procedures)
        time.sleep(0.1)
        assert not second.done(), "a concurrent caller must block, not see a partial registry"
        release.set()
        result_first = first.result(timeout=5)
        result_second = second.result(timeout=5)

    assert result_first == result_second
    assert len(result_first) == len(saved_registry)

    monkeypatch.setattr(registry, "_REGISTRY", saved_registry)
    monkeypatch.setattr(registry, "_DISCOVERED", saved_discovered)


def test_a_failed_first_discovery_can_be_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    """P1-01: a transient import failure must not permanently poison discovery,
    and must not leave the partially-registered ids of the failed attempt behind
    to collide as DuplicateProcedure on retry."""
    saved_registry = dict(registry._REGISTRY)
    saved_discovered = registry._DISCOVERED
    monkeypatch.setattr(registry, "_REGISTRY", {})
    monkeypatch.setattr(registry, "_DISCOVERED", False)

    original_import_module = registry.importlib.import_module
    attempt = {"count": 0}

    def flaky_import(name: str, *a: Any, **kw: Any) -> Any:
        if name == "denckring.procedures.anagram" and attempt["count"] == 0:
            attempt["count"] += 1
            raise ImportError("simulated plugin failure")
        return original_import_module(name, *a, **kw)

    monkeypatch.setattr(registry.importlib, "import_module", flaky_import)

    with pytest.raises(ImportError):
        registry.all_procedures()
    assert registry._DISCOVERED is False, "a failed first load must not poison discovery"
    assert registry._REGISTRY == {}, "a failed attempt must roll back what it registered"

    result = registry.all_procedures()
    assert "anagram" in result
    assert len(result) == len(saved_registry)

    monkeypatch.setattr(registry, "_REGISTRY", saved_registry)
    monkeypatch.setattr(registry, "_DISCOVERED", saved_discovered)
