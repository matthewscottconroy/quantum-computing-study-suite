"""The app is wired to ``common/`` correctly, and nothing was forked.

Three things this file exists to catch:

1. **The shim.**  ``common_path.py`` must stay the verbatim copy of
   ``common/app_shim.py``, every module that imports ``common`` must import it
   first, and it must *append* to ``sys.path`` — prepending would let a
   repository-root module (``tests``, ``tools``, ``coach``) shadow one of this
   app's own.
2. **All three run modes.**  ``python main.py`` from the app directory,
   ``python -m pytest`` from the app directory, and ``persistence.py`` loaded
   **by path** — which is how ``tests/test_journal_concurrency.py`` drives this
   app from the root suite, with no ``main`` and no ``conftest`` in the way.
3. **No duplicates came back.**  The journal, the flag store, the data-dir
   resolver, the palette, the Reference screen and the loading overlay are
   imported, not copied.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent
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


# ------------------------------------------------------------------ the shim

def test_the_shim_is_the_verbatim_copy_of_the_canonical_one():
    ours = APP_ROOT / "common_path.py"
    canonical = REPO_ROOT / "common" / "app_shim.py"
    assert ours.is_file()
    assert ours.read_bytes() == canonical.read_bytes(), (
        "qiskit-dojo/common_path.py has drifted from common/app_shim.py; "
        "it is meant to be an unedited copy")


def test_every_app_module_that_uses_common_imports_the_shim_first():
    """Every module, not just main.py: persistence.py is imported by path from
    the root suite, and the screens are imported directly by the UI tests."""
    modules = _modules_importing_common()
    assert modules, "no module imports common — the migration did not happen"
    offenders = []
    for path in modules:
        text = path.read_text(encoding="utf-8")
        if "import common_path" not in text:
            offenders.append(str(path.relative_to(APP_ROOT)))
        elif text.index("import common_path") > text.index("from common"):
            offenders.append(f"{path.relative_to(APP_ROOT)} (shim imported late)")
    assert not offenders, f"modules missing the import shim: {offenders}"
    # the four that must be on the list, because something imports each of
    # them before anything else in the app does
    names = {str(p.relative_to(APP_ROOT)) for p in modules}
    assert {"config.py", "persistence.py", "ui/theme.py",
            "ui/main_window.py", "ui/screens/kata_screen.py"} <= names


def test_the_test_suite_gets_the_shim_from_conftest():
    """Test modules use ``common`` too; conftest is imported before all of
    them, so it is where the shim goes for the suite."""
    conftest = (APP_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert "import common_path" in conftest
    assert _modules_importing_common(tests=True)


def test_the_shim_appends_so_the_apps_own_modules_always_win():
    import common_path
    assert common_path.ROOT == REPO_ROOT
    assert str(REPO_ROOT) in sys.path
    # the app directory (or the tests rootdir) comes first
    assert sys.path.index(str(REPO_ROOT)) > 0
    # the repository root holds a top-level "tests" package too; ours wins
    import tests
    assert Path(tests.__file__).resolve().parent == APP_ROOT / "tests"


# ------------------------------------------------------------- the run modes

def test_the_app_imports_from_its_own_directory_with_no_api_key(tmp_path):
    proc = _run(
        "import main; from ui.main_window import MainWindow;"
        "from PyQt6.QtWidgets import QApplication;"
        "app = QApplication([]); main.theme.apply(app);"
        "w = MainWindow(); print('OK', w.windowTitle())",
        cwd=APP_ROOT,
        QUANTUM_STUDY_DATA_DIR=str(tmp_path / "data"),
        ANTHROPIC_API_KEY="",
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.startswith("OK Qiskit Dojo")
    assert not (tmp_path / "data").exists(), "building the window wrote to disk"


def test_persistence_loads_by_path_like_the_root_concurrency_suite(tmp_path):
    """``tests/test_journal_concurrency.py`` imports this module by path, with
    the app directory on sys.path and nothing else set up."""
    data = tmp_path / "quantum-study"
    code = f'''
import importlib.util, json, sys
sys.path.insert(0, {str(APP_ROOT)!r})
spec = importlib.util.spec_from_file_location(
    "store_qiskit_dojo", {str(APP_ROOT / "persistence.py")!r})
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
entry = {{"id": "k1", "app": "qiskit-dojo", "category": "Gates",
          "question": "q", "your_answer": "a", "correct_answer": "b",
          "cause": None, "note": "", "timestamp": 1000.0, "resolved": False}}
mod.log_mistake(entry)
mod.log_confidence("k1", "Gates", 3, False)
print(json.dumps([r["id"] for r in mod.load_mistakes()]))
'''
    proc = _run(code, cwd=Path("/"), QUANTUM_STUDY_DATA_DIR=str(data))
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout.strip()) == ["k1"]
    assert json.loads((data / "mistakes.json").read_text())[0]["app"] == "qiskit-dojo"
    assert (data / "mistakes.json.schema.json").is_file()


def test_the_env_override_alone_is_enough_no_constant_patching(tmp_path,
                                                               monkeypatch):
    """Paths resolve at call time now: a test needs only the environment
    variable, never a monkeypatch of a module constant."""
    import persistence
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
    import persistence
    from common import datadir, flags, journal, schema
    from common.ui import theme as base_theme
    from ui import theme

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
    from common import journal
    import persistence
    assert tuple(persistence.CAUSE_LABELS) == journal.MISTAKE_CAUSES
    assert persistence.CAUSE_LABELS != journal.CAUSE_LABELS
    assert persistence.CAUSE_LABELS["confused"] == "Confused two APIs"
    for label in persistence.CAUSE_LABELS.values():
        assert label.isascii(), label       # no typographic apostrophes
