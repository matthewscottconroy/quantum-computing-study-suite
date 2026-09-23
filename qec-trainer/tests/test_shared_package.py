"""This app uses ``common/`` rather than its own copy of it.

These are the assertions that would fail if someone re-forked one of the
extracted pieces back into the app tree — which is the whole failure mode the
shared package exists to prevent.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

import common_path
from common import datadir, flags, journal, locking, schema
from common.ui import reference as shared_reference
from common.ui import theme as shared_theme
from common.ui import widgets as shared_widgets

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent


# ── the import shim ───────────────────────────────────────────────────────────

def test_the_shim_finds_the_repo_and_appends_it():
    assert common_path.repo_root() == REPO_ROOT
    assert common_path.ROOT == REPO_ROOT
    assert str(REPO_ROOT) in sys.path


def test_the_shim_appends_so_the_apps_own_modules_always_win():
    """Prepending would let the repo's ``tests/`` shadow this app's ``tests/``."""
    paths = [p for p in sys.path if p]
    assert paths.index(str(REPO_ROOT)) > paths.index(str(APP_ROOT))
    import tests as app_tests                      # this suite, not the repo's
    assert pathlib.Path(app_tests.__file__).parent == APP_ROOT / "tests"


def test_the_shim_is_the_unedited_copy_of_the_canonical_one():
    assert (APP_ROOT / "common_path.py").read_text() == \
        (REPO_ROOT / "common" / "app_shim.py").read_text()


def test_the_app_still_runs_as_a_plain_script_from_its_own_directory():
    """`cd qec-trainer && python main.py` — the shim's first case, for real."""
    proc = subprocess.run(
        [sys.executable, "-c",
         "import main, persistence, config;"
         " from ui.screens.reference_screen import ReferenceScreen;"
         " print(persistence.APP_ID, config.DATA_DIR.name)"],
        cwd=APP_ROOT, capture_output=True, text=True, timeout=120,
        env={**_env(), "QT_QPA_PLATFORM": "offscreen"})
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.split() == ["qec-trainer", "quantum-study"]


def _env() -> dict:
    import os
    return {k: v for k, v in os.environ.items()}


# ── nothing is forked back in ─────────────────────────────────────────────────

def test_persistence_delegates_and_keeps_no_journal_of_its_own():
    source = (APP_ROOT / "persistence.py").read_text()
    for gone in ("import journal_sync", "def _atomic_write_json",
                 "def _read_json_list", "def merge_foreign", "fcntl"):
        assert gone not in source, gone
    assert "from common import" in source

    import persistence
    assert persistence.MISTAKE_CAUSES is journal.MISTAKE_CAUSES
    assert persistence.CAUSE_LABELS is journal.CAUSE_LABELS
    assert persistence.CONFIDENCE_LABELS is journal.CONFIDENCE_LABELS
    assert persistence.mistakes_path() == journal.mistakes_path()
    assert persistence.FLAGGED_FILE == flags.flagged_path("qec-trainer")


def test_the_theme_is_the_shared_palette_plus_this_apps_vocabulary():
    from ui import theme

    assert theme.QSS is shared_theme.QSS
    for name in ("BG", "SURFACE", "BORDER", "ACCENT", "TEXT", "SUCCESS",
                 "WARNING", "ERROR", "PARTIAL"):
        assert getattr(theme, name) == getattr(shared_theme, name), name
    # …and the one thing that is genuinely this app's: its topic colours.
    assert set(theme.CATEGORY_COLORS) == {
        "Repetition Code", "Stabilizer Formalism", "Steane Code",
        "Surface Code", "Fault Tolerance"}


def test_the_loading_overlay_is_the_shared_animated_one(qapp):
    from ui.screens.problem_screen import ProblemScreen

    screen = ProblemScreen()
    try:
        assert isinstance(screen._overlay, shared_widgets.LoadingOverlay)
        screen.show_grading()
        assert screen._overlay.isVisibleTo(screen)
        assert screen._overlay._timer.isActive()      # the dot animation runs
        screen.hide_grading()
        assert screen._overlay.isHidden()
        # the copy this replaced had no hide_overlay(): the timer ran forever
        assert not screen._overlay._timer.isActive()
    finally:
        screen.close()


def test_the_reference_screen_is_the_shared_one():
    from ui.screens import reference_screen

    assert issubclass(reference_screen.ReferenceScreen,
                      shared_reference.ReferenceScreen)
    source = (APP_ROOT / "ui" / "screens" / "reference_screen.py").read_text()
    assert "QTextBrowser" not in source          # the screen itself is not here
    assert len(source.splitlines()) < 120        # it was 992


#: The two modules the migration removed or orphaned.  ``journal_sync.py``
#: itself is still on disk: ``tests/test_journal_concurrency.py`` (the root
#: suite, which this agent does not own) asserts that all ten apps ship a
#: byte-identical copy, so it must be deleted in the same change that updates
#: that test.  Nothing in this app imports it any more.
_DEAD = ("ui.widgets.loading_overlay", "import journal_sync")


def test_no_app_module_imports_the_dead_local_copies():
    skip = {"journal_sync.py", pathlib.Path(__file__).name}
    for path in APP_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts or path.name in skip:
            continue
        source = path.read_text()
        for dead in _DEAD:
            assert dead not in source, f"{path} still references {dead}"


def test_the_duplicated_widget_file_is_gone():
    assert not (APP_ROOT / "ui" / "widgets" / "loading_overlay.py").exists()


# ── the file names and the locking contract are the suite's ───────────────────

def test_this_apps_file_names_are_the_ones_the_suite_records():
    import config

    names = datadir.APP_FILES["qec-trainer"]
    assert config.history_file().name == names["history"] == "qec_history.json"
    assert config.flagged_file().name == names["flagged"] == "qec_flagged.json"
    assert config.settings_file().name == names["settings"] == "qec_settings.json"


def test_the_lock_sidecar_matches_the_unmigrated_apps_convention(isolated_data_dir):
    """Nine apps still use their own ``journal_sync``; we must lock the same file.

    Both take an ``fcntl.flock`` on ``<file>.lock``.  If the two disagreed on
    the name, a migrated app and an unmigrated one would each think they held
    the journal and the race would be back.
    """
    import importlib.util

    import persistence

    target = persistence.mistakes_path()
    assert locking.lock_path_for(target) == \
        target.with_name(target.name + ".lock")

    spec = importlib.util.spec_from_file_location(
        "journal_sync_probe", REPO_ROOT / "flashcard-drill" / "journal_sync.py")
    other = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(other)
    assert other.lock_path_for(target) == locking.lock_path_for(target)
    assert other.LOCK_SUFFIX == locking.LOCK_SUFFIX

    with locking.lock(target, create=True) as held:
        assert held, "flock is unavailable here — the suite would be a no-op"
    assert locking.lock_path_for(target).exists()


@pytest.mark.parametrize("kind", ["mistakes", "confidence", "flagged",
                                  "history", "settings"])
def test_every_kind_this_app_writes_is_registered(kind):
    assert schema.get(kind).version >= 1
