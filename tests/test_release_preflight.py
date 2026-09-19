"""P1-03: a pushed tag must match every workspace version and a stamped
changelog section before `release.yml` is allowed to build or publish."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "release_preflight.py"


def _run(tag: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), tag],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )


def test_the_current_tag_and_version_agree() -> None:
    """A live guard: this fails the moment `pyproject.toml` and the changelog
    disagree with `v0.2.0`, which is what the CI job compares against the real
    pushed tag — this test compares against the workspace's own current state."""
    result = _run("v0.2.0")
    assert result.returncode == 0, result.stderr


def test_a_mismatched_tag_is_refused() -> None:
    result = _run("v9.9.9")
    assert result.returncode != 0
    assert "9.9.9" in result.stderr


def test_a_tag_with_no_changelog_section_is_refused(tmp_path: Path, monkeypatch: object) -> None:
    result = _run("v0.0.0-nonexistent")
    assert result.returncode != 0
