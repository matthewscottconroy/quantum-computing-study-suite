"""The two places dependencies are declared must agree.

``requirements.txt`` / ``requirements-dev.txt`` are what ``setup.sh`` and CI
install; ``[project.dependencies]`` and the ``[dev]`` extra in
``pyproject.toml`` are what ``pip install -e .[dev]`` resolves.  They are
maintained by hand in both places, and they had already drifted once
(``genanki`` was in requirements-dev.txt only), so compare them.
"""
from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parent.parent


def _normalise(spec: str) -> tuple[str, str]:
    req = Requirement(spec)
    return (req.name.lower().replace("_", "-"),
            ",".join(sorted(str(s) for s in req.specifier)))


def _requirements_file(name: str) -> dict[str, str]:
    """name -> specifier for every requirement line (comments and -r skipped)."""
    out: dict[str, str] = {}
    for raw in (ROOT / name).read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or line.startswith("-"):
            continue
        key, spec = _normalise(line)
        assert key not in out, f"{name} lists {key} twice"
        out[key] = spec
    return out


@pytest.fixture(scope="module")
def project() -> dict:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)["project"]


def test_runtime_dependencies_match_requirements_txt(project):
    declared = dict(_normalise(d) for d in project["dependencies"])
    assert declared == _requirements_file("requirements.txt")


def test_dev_extra_matches_requirements_dev_txt(project):
    declared = dict(_normalise(d) for d in project["optional-dependencies"]["dev"])
    assert declared == _requirements_file("requirements-dev.txt")


def test_requirements_dev_pulls_in_the_runtime_set():
    text = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "-r requirements.txt" in text.splitlines()
