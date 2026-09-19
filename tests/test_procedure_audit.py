"""P2-07: the audit went stale once (three procedures with no file, an
undercounted README) with nothing to catch it. This closes that gap."""

from pathlib import Path

from denckring.core.registry import all_procedures

ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = ROOT / "docs" / "audit"


def test_every_registered_procedure_has_an_audit_file() -> None:
    audited = {path.stem for path in AUDIT_DIR.glob("*.md") if path.stem != "README"}
    registered = set(all_procedures())
    missing = sorted(registered - audited)
    assert not missing, (
        f"{missing} are registered procedures with no docs/audit/<id>.md — "
        f"add one (see Task 12 of the 2026-09-19 hardening plan for the method) "
        f"or this file goes stale the same way it did before"
    )
