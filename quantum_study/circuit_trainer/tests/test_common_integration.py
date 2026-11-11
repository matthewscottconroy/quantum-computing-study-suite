"""What circuit-trainer takes from ``quantum_study.common`` and what stays its own.

The shared journal, flag store, data directory, theme and Reference screen
must be the shared implementations, not private copies that drifted; the
app's own vocabulary (categories, colours, file names) must survive.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent.parent



# ── No re-forking ─────────────────────────────────────────────────────────────

def test_the_app_no_longer_carries_its_own_copies():
    gone = [
        "ui/widgets/loading_overlay.py",
        "ui/widgets/collapsible_panel.py",
    ]
    for rel in gone:
        assert not (APP_ROOT / rel).exists(), f"{rel} came back"


def test_the_shared_widgets_are_the_shared_ones():
    from quantum_study.common.ui import widgets
    from quantum_study.circuit_trainer.ui.screens.problem_screen import CollapsiblePanel
    from quantum_study.circuit_trainer.ui.main_window import LoadingOverlay

    assert CollapsiblePanel is widgets.CollapsiblePanel
    assert LoadingOverlay is widgets.LoadingOverlay


def test_the_reference_screen_is_the_shared_one_with_this_apps_two_arguments():
    from quantum_study.common.ui.reference import ReferenceScreen as Shared
    from quantum_study.circuit_trainer.ui.screens.reference_screen import CATEGORY_DOCS, ReferenceScreen

    from quantum_study.common.ui.reference import docs_root

    assert issubclass(ReferenceScreen, Shared)
    # The only per-app differences are the two constructor arguments, and every
    # doc the category map points at has to exist or the picker drops it.
    missing = [rel for rel in CATEGORY_DOCS.values()
               if not (docs_root() / rel).is_file()]
    assert missing == [], f"category map points at missing docs: {missing}"


def test_the_palette_comes_from_common_and_the_vocabulary_stays_local():
    from quantum_study.common.ui import theme as shared
    from quantum_study.circuit_trainer.core.models import ProblemCategory
    from quantum_study.circuit_trainer.ui import theme

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
    from quantum_study.common import datadir, flags, journal
    from quantum_study.circuit_trainer import persistence

    assert persistence.mistakes_file() == journal.mistakes_path()
    assert persistence.confidence_file() == journal.confidence_path()
    assert persistence.flagged_file() == flags.flagged_path("circuit-trainer")
    assert persistence.history_file() == datadir.app_file("circuit-trainer", "history")
    assert persistence.prefs_file() == datadir.app_file("circuit-trainer", "settings")
    assert persistence.MISTAKE_CAUSES is journal.MISTAKE_CAUSES
    assert persistence.CONFIDENCE_LEVELS is journal.CONFIDENCE_LEVELS


def test_the_data_dir_file_names_still_match_what_coach_reads():
    """coach.py maps trainer_history.json / trainer_flagged.json to this app."""
    from quantum_study.common import datadir

    assert datadir.APP_FILES["circuit-trainer"] == {
        "history": "trainer_history.json",
        "flagged": "trainer_flagged.json",
        "settings": "trainer_prefs.json",
    }
