"""What exam-sim takes from ``quantum_study.common`` and what stays its own.

The shared journal, flag store, data directory, theme and Reference screen
must be the shared implementations, not private copies that drifted; the
app's own vocabulary (categories, colours, file names) must survive.
"""
from __future__ import annotations

import ast
import pathlib
import subprocess
import sys

import pytest

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent.parent
APP_MODULES = sorted(p for p in APP_ROOT.rglob("*.py")
                     if "__pycache__" not in p.parts
                     and p.name != "common_path.py"
                     and "bank" not in p.relative_to(APP_ROOT).parts)


def _imports(path: pathlib.Path) -> set[str]:
    """Top-level module names imported by *path* (``import x`` / ``from x``)."""
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


@pytest.mark.parametrize("path", APP_MODULES, ids=lambda p: str(p.name))
def test_nothing_imports_the_replaced_local_copies(path):
    assert "journal_sync" not in _imports(path), (
        f"{path.relative_to(REPO_ROOT)} still uses the per-app journal lock; "
        f"common.locking is the extraction")


def test_the_palette_is_the_shared_one_and_the_app_keeps_its_own_vocabulary():
    from quantum_study.common.ui import theme as shared
    from quantum_study.exam_sim.ui import theme as app

    for name in ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2",
                 "TEXT", "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR"):
        assert getattr(app, name) == getattr(shared, name), name
    assert app.FLAG == shared.PARTIAL == "#e3b341"
    assert not hasattr(shared, "SECTION_COLORS")     # this app's words
    assert set(app.SECTION_COLORS) == set(__import__("quantum_study.exam_sim.config", fromlist=["x"]).SECTIONS)
    assert shared.QSS in app.QSS and "QPushButton#nav" in app.QSS


def test_the_journal_is_the_shared_one():
    from quantum_study.common import journal

    from quantum_study.exam_sim import persistence

    assert persistence.MISTAKE_CAUSES is journal.MISTAKE_CAUSES
    assert persistence.CAUSE_LABELS is journal.CAUSE_LABELS
    assert persistence.CONFIDENCE_LABELS is journal.CONFIDENCE_LABELS
    assert persistence.MISTAKES_CAP == journal.MISTAKES_MAX == 2000
    assert persistence.CONFIDENCE_CAP == journal.CONFIDENCE_MAX == 5000


def test_the_journal_trims_only_this_apps_rows(data_dir, monkeypatch):
    """The bug the migration fixes: the old copy trimmed the *merged* list.

    Capping at 3 with two foreign rows present used to delete the other app's
    history during exam-sim's own write.
    """
    import json

    from quantum_study.common import journal

    monkeypatch.setattr(journal, "MISTAKES_MAX", 3)
    data_dir.mkdir(parents=True)
    foreign = [{"id": f"t{i}", "app": "quantum-tutor", "timestamp": float(i)}
               for i in range(2)]
    (data_dir / "mistakes.json").write_text(json.dumps(foreign))
    for i in range(4):
        persistence_log(i)
    rows = json.loads((data_dir / "mistakes.json").read_text())
    assert [r for r in rows if r["app"] == "quantum-tutor"] == foreign
    assert [r["id"] for r in rows if r["app"] == "exam-sim"] == ["q3"]


def persistence_log(i: int) -> None:
    from quantum_study.exam_sim import persistence
    from quantum_study.exam_sim.core.models import Question

    persistence.log_mistake(persistence.mistake_entry_for(
        Question(id=f"q{i}", section="Sampler", question="q?",
                 options=["a", "b", "c", "d"], correct_index=0,
                 explanation="", difficulty="easy"), 1))
