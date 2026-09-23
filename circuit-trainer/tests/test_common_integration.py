"""circuit-trainer really uses the shared ``common`` package, not a copy of it.

The point of the extraction is that a cross-cutting fix lands once.  These
tests fail if a future edit quietly re-forks a piece of it back into the app.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent


# ── The import shim ───────────────────────────────────────────────────────────

def test_the_shim_is_the_unedited_copy_of_common_app_shim():
    """Copied verbatim, so a fix to the shim reaches every app that has one."""
    ours = (APP_ROOT / "common_path.py").read_text(encoding="utf-8")
    canonical = (REPO_ROOT / "common" / "app_shim.py").read_text(encoding="utf-8")
    assert ours == canonical


def test_the_shim_appends_so_a_root_module_can_never_shadow_an_app_module():
    import common_path

    assert common_path.ROOT == REPO_ROOT
    assert str(REPO_ROOT) in sys.path
    assert sys.path.index(str(REPO_ROOT)) > 0, (
        "the repo root must come after the app directory: it holds tests/, "
        "tools/, coach.py, and prepending it would shadow this app's modules")


def test_every_module_that_imports_common_imports_the_shim_first():
    """A module that relies on someone else having run the shim works right up
    until the day something imports it first (pytest does, by path)."""
    # tests/ is exempt: conftest.py runs the shim before any test module is
    # imported, and it is the only importer of the suite that pytest guarantees
    # to load first.
    offenders = []
    for path in sorted(APP_ROOT.rglob("*.py")):
        if ("__pycache__" in path.parts or "tests" in path.parts
                or path.name == "common_path.py"):
            continue
        text = path.read_text(encoding="utf-8")
        uses_common = ("from common " in text or "from common." in text
                       or "import common\n" in text)
        if uses_common and "import common_path" not in text:
            offenders.append(str(path.relative_to(APP_ROOT)))
    assert offenders == [], f"missing `import common_path` in: {offenders}"


def test_persistence_imports_standalone_by_path_as_the_root_suite_does():
    """tests/test_journal_concurrency.py loads this module with no conftest."""
    code = (
        "import importlib.util, sys;"
        f"sys.path.insert(0, {str(APP_ROOT)!r});"
        "spec = importlib.util.spec_from_file_location('store',"
        f" {str(APP_ROOT / 'persistence.py')!r});"
        "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m);"
        "print(m.APP, m.mistakes_file().name)"
    )
    out = subprocess.run([sys.executable, "-c", code], cwd="/", capture_output=True,
                         text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    assert out.stdout.split() == ["circuit-trainer", "mistakes.json"]


# ── No re-forking ─────────────────────────────────────────────────────────────

def test_the_app_no_longer_carries_its_own_copies():
    gone = [
        "ui/widgets/loading_overlay.py",
        "ui/widgets/collapsible_panel.py",
    ]
    for rel in gone:
        assert not (APP_ROOT / rel).exists(), f"{rel} came back"


def test_the_shared_widgets_are_the_shared_ones():
    from common.ui import widgets
    from ui.screens.problem_screen import CollapsiblePanel
    from ui.main_window import LoadingOverlay

    assert CollapsiblePanel is widgets.CollapsiblePanel
    assert LoadingOverlay is widgets.LoadingOverlay


def test_the_reference_screen_is_the_shared_one_with_this_apps_two_arguments():
    from common.ui.reference import ReferenceScreen as Shared
    from ui.screens.reference_screen import CATEGORY_DOCS, ReferenceScreen

    from common.ui.reference import docs_root

    assert issubclass(ReferenceScreen, Shared)
    # The only per-app differences are the two constructor arguments, and every
    # doc the category map points at has to exist or the picker drops it.
    missing = [rel for rel in CATEGORY_DOCS.values()
               if not (docs_root() / rel).is_file()]
    assert missing == [], f"category map points at missing docs: {missing}"


def test_the_palette_comes_from_common_and_the_vocabulary_stays_local():
    from common.ui import theme as shared
    from core.models import ProblemCategory
    from ui import theme

    for name in ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2",
                 "TEXT", "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR",
                 "PARTIAL", "PURPLE", "TEAL"):
        assert getattr(theme, name) == getattr(shared, name), name
    # The base stylesheet is inherited whole, this app's rules are appended.
    assert theme.QSS.startswith(shared.QSS)
    assert "QPushButton#choice" in theme.QSS
    # ...and the one thing that is genuinely this app's vocabulary is complete.
    assert set(theme.CATEGORY_COLORS) == {c.value for c in ProblemCategory}


def test_the_store_delegates_to_the_shared_journal_and_flag_stores(isolated_data_dir):
    from common import datadir, flags, journal
    import persistence

    assert persistence.mistakes_file() == journal.mistakes_path()
    assert persistence.confidence_file() == journal.confidence_path()
    assert persistence.flagged_file() == flags.flagged_path("circuit-trainer")
    assert persistence.history_file() == datadir.app_file("circuit-trainer", "history")
    assert persistence.prefs_file() == datadir.app_file("circuit-trainer", "settings")
    assert persistence.MISTAKE_CAUSES is journal.MISTAKE_CAUSES
    assert persistence.CONFIDENCE_LEVELS is journal.CONFIDENCE_LEVELS


def test_the_data_dir_file_names_still_match_what_coach_reads():
    """coach.py maps trainer_history.json / trainer_flagged.json to this app."""
    from common import datadir

    assert datadir.APP_FILES["circuit-trainer"] == {
        "history": "trainer_history.json",
        "flagged": "trainer_flagged.json",
        "settings": "trainer_prefs.json",
    }
