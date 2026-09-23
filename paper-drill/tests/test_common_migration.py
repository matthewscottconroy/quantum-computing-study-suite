"""paper-drill really uses ``common/``, and the duplicated copies are gone.

The point of the shared package is that a cross-cutting fix is one edit, not
ten.  That only holds if the app imports the shared code rather than keeping a
fork of it beside it, so these tests are about *where the code lives*:

* the import shim is the unedited copy of ``common/app_shim.py``, and it works
  the three ways this app is ever started (``python main.py`` from the app
  directory, ``python -m pytest`` from the app directory, and an installed
  wheel with no checkout at all);
* every module that imports ``common`` runs the shim itself, because
  ``persistence.py`` is loaded by path with no conftest in the way by
  ``tests/test_journal_concurrency.py``, and screens are imported directly by
  the UI tests;
* the forked copies — the journal store, the flag store, the theme palette, the
  loading overlay, the ~900-line Reference screen — are not on disk any more;
* what the app kept is genuinely this app's, not a fork of something shared.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent

#: Every module of this app that imports from ``common``.  Each one must run
#: the shim itself; see the module docstring.
MODULES_USING_COMMON = [
    "config.py",
    "persistence.py",
    "ui/theme.py",
    "ui/main_window.py",
    "ui/screens/feedback_screen.py",
    "ui/screens/question_screen.py",
]


# ---------------------------------------------------------------------------
# The shim
# ---------------------------------------------------------------------------

def test_the_shim_is_the_unedited_copy_of_the_canonical_one():
    """common/README.md: "Copy common/app_shim.py to <app>/common_path.py,
    unedited."  A local edit is how the ten copies drifted in the first place."""
    ours = (APP_ROOT / "common_path.py").read_bytes()
    canonical = (REPO_ROOT / "common" / "app_shim.py").read_bytes()
    assert ours == canonical, "common_path.py has drifted from common/app_shim.py"


def test_the_shim_appends_rather_than_prepends():
    """The repo root holds tests/, tools/, coach.py: prepending it would let a
    root module shadow an app module of the same name."""
    import common_path

    assert common_path.ROOT == REPO_ROOT
    assert str(REPO_ROOT) in sys.path
    # The app directory still wins: our own modules resolve to our own tree.
    import persistence
    assert Path(persistence.__file__).parent == APP_ROOT


@pytest.mark.parametrize("module", MODULES_USING_COMMON)
def test_every_module_that_imports_common_runs_the_shim(module):
    text = (APP_ROOT / module).read_text()
    assert "from common" in text or "import common\n" in text, \
        f"{module} is in the list but imports nothing from common"
    assert "import common_path" in text, (
        f"{module} imports common without running the shim; it works only for "
        f"as long as nothing imports it first")


def test_running_main_from_the_app_directory_resolves_common():
    """``cd paper-drill && python main.py`` — sys.path[0] is the app dir."""
    result = subprocess.run(
        [sys.executable, "-c",
         "import main, common, persistence, config;"
         " print(common.__file__); print(persistence.APP_ID)"],
        cwd=APP_ROOT, capture_output=True, text=True, timeout=120,
        env={**_offscreen_env()},
    )
    assert result.returncode == 0, result.stderr
    out = result.stdout.split()
    assert out[0] == str(REPO_ROOT / "common" / "__init__.py")
    assert out[1] == "paper-drill"


def test_persistence_loaded_by_path_with_no_conftest_still_works(tmp_path):
    """Exactly what tests/test_journal_concurrency.py does to this module."""
    script = (
        "import importlib.util, json, os, sys\n"
        f"sys.path.insert(0, {str(APP_ROOT)!r})\n"
        f"os.environ['QUANTUM_STUDY_DATA_DIR'] = {str(tmp_path)!r}\n"
        f"spec = importlib.util.spec_from_file_location('store_paper_drill', {str(APP_ROOT / 'persistence.py')!r})\n"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
        "m.log_mistake('paper-a', 'Gates', 'q', 'a', 'b')\n"
        "m.log_confidence('paper-a', 'Gates', 3, False)\n"
        "print(json.dumps([r['app'] for r in m.load_mistakes()]))\n"
    )
    result = subprocess.run([sys.executable, "-c", script], cwd=tmp_path,
                            capture_output=True, text=True, timeout=120,
                            env=_offscreen_env())
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().endswith('["paper-drill"]')
    assert (tmp_path / "mistakes.json").exists()


def test_the_shim_is_a_no_op_where_there_is_no_checkout(tmp_path):
    """An installed wheel: ``common`` is a real package and the shim finds no
    repository.  It must return None rather than fail."""
    lone = tmp_path / "app"
    lone.mkdir()
    (lone / "common_path.py").write_bytes((APP_ROOT / "common_path.py").read_bytes())
    result = subprocess.run(
        [sys.executable, "-c",
         "import common_path; print(common_path.repo_root()); print(common_path.install())"],
        cwd=lone, capture_output=True, text=True, timeout=120,
        env=_offscreen_env())
    assert result.returncode == 0, result.stderr
    assert result.stdout.split() == ["None", "None"]


def _offscreen_env() -> dict:
    import os

    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["MPLBACKEND"] = "Agg"
    env.pop("PYTHONPATH", None)          # only the shim may put the root on the path
    return env


# ---------------------------------------------------------------------------
# The forks are gone
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("gone", [
    "ui/widgets/loading_overlay.py",
    "ui/widgets",
    "ui/screens/reference_screen.py",
])
def test_the_duplicated_copies_are_deleted(gone):
    assert not (APP_ROOT / gone).exists(), (
        f"{gone} is back; it is common.ui.widgets / common.ui.reference now")


def test_the_stores_are_the_shared_ones_not_a_local_reimplementation():
    import persistence
    from common import flags, journal

    # The journal helpers are the shared functions, not copies of them.
    assert persistence.clip_text is journal.clip_text
    assert persistence.normalise_cause is journal.normalise_cause
    assert persistence.MISTAKE_CAUSES is journal.MISTAKE_CAUSES
    assert persistence.MISTAKE_CAUSE_LABELS is journal.CAUSE_LABELS
    assert persistence.CONFIDENCE_LEVELS is journal.CONFIDENCE_LABELS
    assert persistence.FLAG_LABEL_MAX == flags.LABEL_MAX

    text = (APP_ROOT / "persistence.py").read_text()
    for forked in ("def _atomic_write_json", "def _load_json_list",
                   "def merge_foreign", "def _trim_own", "fcntl"):
        assert forked not in text, f"persistence.py still carries {forked}"


def test_the_theme_is_the_shared_palette_plus_this_apps_vocabulary():
    from common.ui import theme as shared
    from ui import theme

    for name in ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2",
                 "TEXT", "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL"):
        assert getattr(theme, name) == getattr(shared, name), name
    # Kept locally, because it is paper-drill's own vocabulary.
    assert set(theme.QTYPE_COLORS) == {"factual", "conceptual", "derivation"}
    assert not hasattr(shared, "QTYPE_COLORS")
    # The installed sheet is the shared base plus this app's extra rules.
    assert theme.QSS_APP.startswith(shared.QSS)
    assert "QTreeWidget" in theme.QSS_APP and "QTreeWidget" not in shared.QSS


def test_the_widgets_and_the_reference_screen_come_from_common():
    from ui.main_window import MainWindow
    from ui.screens.question_screen import QuestionScreen

    import common.ui.reference
    import common.ui.widgets

    assert MainWindow.__init__.__globals__["LoadingOverlay"] is \
        common.ui.widgets.LoadingOverlay
    assert MainWindow.__init__.__globals__["ReferenceScreen"] is \
        common.ui.reference.ReferenceScreen
    assert QuestionScreen.__init__.__globals__["LoadingOverlay"] is \
        common.ui.widgets.LoadingOverlay


def test_make_flag_id_is_deliberately_not_common_flags_make_id():
    """The digest is written into paper_flagged.json and into every
    mistakes.json row this app has ever logged, so it is a compatibility
    contract, not an implementation detail.  common.flags.make_id normalises
    whitespace differently and would orphan every flag already on disk."""
    import persistence
    from common import flags

    ours = persistence.make_flag_id("P", "line one\nline two")
    theirs = flags.make_id("P", "line one\nline two", prefix="paper")
    assert ours != theirs
    # …but for single-line text, which is the common case, they agree, which is
    # why the difference is easy to miss.
    assert persistence.make_flag_id("P", "one line") == \
        flags.make_id("P", "one line", prefix="paper")
