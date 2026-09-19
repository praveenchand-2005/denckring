"""Refuse to build/publish a release whose tag disagrees with the workspace.

Run before `build`, `docs`, `rehearse` and `publish` in release.yml — PyPI will
not take a version back, so this has to fail *before* any of those jobs, not
after (review finding P1-03). `notes` already checks the changelog, but only
after `publish`, which is worse than late: it is irreversible-late.

DISTRIBUTIONS below is deliberately the same six (import_name, pyproject_path)
pairs as tests/test_packaging.py's DISTRIBUTIONS — that list exists because a
sixth distribution went uncounted twice before (see packaging.md). Keep them
in sync; a new distribution needs both.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DISTRIBUTIONS = (
    ("denckring", "pyproject.toml"),
    ("denckring_en_data", "packages/denckring-en-data/pyproject.toml"),
    ("denckring_de_data", "packages/denckring-de-data/pyproject.toml"),
    ("denckring_de_wiktionary", "packages/denckring-de-wiktionary/pyproject.toml"),
    ("denckring_de_frequency", "packages/denckring-de-frequency/pyproject.toml"),
    ("denckring_fr_data", "packages/denckring-fr-data/pyproject.toml"),
)


def _version(pyproject_path: str) -> str:
    manifest = tomllib.loads((ROOT / pyproject_path).read_text(encoding="utf-8"))
    return str(manifest["project"]["version"])


def _changelog_has_section(version: str) -> bool:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    return re.search(rf"^## \[{re.escape(version)}\]", changelog, re.MULTILINE) is not None


def main(tag: str) -> int:
    if not tag.startswith("v"):
        print(f"tag {tag!r} does not start with 'v'", file=sys.stderr)
        return 1
    tag_version = tag[1:]

    versions = {name: _version(path) for name, path in DISTRIBUTIONS}
    unique_versions = set(versions.values())
    if len(unique_versions) != 1:
        print(f"workspace versions disagree: {versions}", file=sys.stderr)
        return 1
    (workspace_version,) = unique_versions

    if tag_version != workspace_version:
        print(
            f"tag {tag!r} does not match workspace version {workspace_version!r}",
            file=sys.stderr,
        )
        return 1

    if not _changelog_has_section(workspace_version):
        print(
            f"CHANGELOG.md has no '## [{workspace_version}]' section — stamp it before tagging",
            file=sys.stderr,
        )
        return 1

    print(f"preflight ok: tag {tag} == workspace version {workspace_version}, changelog stamped")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: release_preflight.py vX.Y.Z", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
