"""What paper-drill takes from ``quantum_study.common`` and what stays its own.

The shared journal, flag store, data directory, theme and Reference screen
must be the shared implementations, not private copies that drifted; the
app's own vocabulary (categories, colours, file names) must survive.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent.parent

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
    from quantum_study.paper_drill import persistence
    from quantum_study.common import flags, journal

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
    from quantum_study.common.ui import theme as shared
    from quantum_study.paper_drill.ui import theme

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
    from quantum_study.paper_drill.ui.main_window import MainWindow
    from quantum_study.paper_drill.ui.screens.question_screen import QuestionScreen

    import quantum_study.common.ui.reference  # noqa: F401
    from quantum_study import common
    import quantum_study.common.ui.widgets  # noqa: F401
    from quantum_study import common

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
    from quantum_study.paper_drill import persistence
    from quantum_study.common import flags

    ours = persistence.make_flag_id("P", "line one\nline two")
    theirs = flags.make_id("P", "line one\nline two", prefix="paper")
    assert ours != theirs
    # …but for single-line text, which is the common case, they agree, which is
    # why the difference is easy to miss.
    assert persistence.make_flag_id("P", "one line") == \
        flags.make_id("P", "one line", prefix="paper")
