"""What qiskit-dojo takes from ``quantum_study.common`` and what stays its own.

The shared journal, flag store, data directory, theme and Reference screen
must be the shared implementations, not private copies that drifted; the
app's own vocabulary (categories, colours, file names) must survive.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent.parent
PY = sys.executable

def _modules_importing_common(tests: bool = False) -> list[Path]:
    """App modules that import from ``common`` (``tests=True`` for the suite)."""
    out = []
    for path in sorted(APP_ROOT.rglob("*.py")):
        if "__pycache__" in path.parts or path.name == "common_path.py":
            continue
        if (path.parts[len(APP_ROOT.parts):][0] == "tests") is not tests:
            continue
        text = path.read_text(encoding="utf-8")
        if "from common" in text or "import common\n" in text:
            out.append(path)
    return out


def _run(code: str, cwd: Path, **env_overrides: str) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "QUANTUM_STUDY_DATA_DIR"}
    env["QT_QPA_PLATFORM"] = "offscreen"
    env.update(env_overrides)
    return subprocess.run([PY, "-c", code], cwd=str(cwd), env=env,
                          capture_output=True, text=True, timeout=180)



# ------------------------------------------------------------- the run modes


def test_the_env_override_alone_is_enough_no_constant_patching(tmp_path,
                                                               monkeypatch):
    """Paths resolve at call time now: a test needs only the environment
    variable, never a monkeypatch of a module constant."""
    from quantum_study.qiskit_dojo import persistence
    target = tmp_path / "elsewhere"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(target))
    assert persistence.history_path() == target / "dojo_history.json"
    assert persistence.flagged_path() == target / "dojo_flagged.json"
    assert persistence.settings_path() == target / "dojo_settings.json"
    assert persistence.mistakes_path() == target / "mistakes.json"
    assert persistence.confidence_path() == target / "confidence.json"

    persistence.save_settings({"confidence_prompt": False})
    assert (target / "dojo_settings.json").is_file()
    assert persistence.confidence_prompt_enabled() is False


# ---------------------------------------------------- nothing was re-forked

DELETED = [
    "ui/screens/reference_screen.py",     # -> common.ui.reference
    "ui/widgets/loading_overlay.py",      # -> common.ui.widgets.LoadingOverlay
]


@pytest.mark.parametrize("rel", DELETED)
def test_the_duplicated_copies_are_gone(rel):
    assert not (APP_ROOT / rel).exists(), (
        f"{rel} is back; it duplicates code that now lives in common/")


def test_the_stores_and_the_palette_come_from_common():
    from quantum_study.qiskit_dojo import persistence
    from quantum_study.common import datadir, flags, journal, schema
    from quantum_study.common.ui import theme as base_theme
    from quantum_study.qiskit_dojo.ui import theme

    # the taxonomy, caps and clip helper are the shared objects themselves
    assert persistence.MISTAKE_CAUSES is journal.MISTAKE_CAUSES
    assert persistence.CONFIDENCE_LABELS is journal.CONFIDENCE_LABELS
    assert persistence.clip is journal.clip_text
    assert persistence.MAX_MISTAKES == journal.MISTAKES_MAX
    assert persistence.MAX_CONFIDENCE == journal.CONFIDENCE_MAX
    assert persistence.FIELD_LIMIT == journal.TEXT_MAX

    # the palette is the shared one, byte for byte
    for name in ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2",
                 "TEXT", "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL"):
        assert getattr(theme, name) == getattr(base_theme, name), name

    # the app's file names are the ones common.datadir records for it
    assert datadir.APP_FILES["qiskit-dojo"] == {
        "history": "dojo_history.json",
        "flagged": "dojo_flagged.json",
        "settings": "dojo_settings.json",
    }
    assert "mistakes" in schema.kinds() and "flagged" in schema.kinds()
    assert flags.flagged_path("qiskit-dojo") == persistence.flagged_path()


def test_the_cause_labels_are_this_apps_words_on_the_shared_taxonomy():
    """Only the button wording is local — the keys written to disk are not."""
    from quantum_study.common import journal
    from quantum_study.qiskit_dojo import persistence
    assert tuple(persistence.CAUSE_LABELS) == journal.MISTAKE_CAUSES
    assert persistence.CAUSE_LABELS != journal.CAUSE_LABELS
    assert persistence.CAUSE_LABELS["confused"] == "Confused two APIs"
    for label in persistence.CAUSE_LABELS.values():
        assert label.isascii(), label       # no typographic apostrophes
