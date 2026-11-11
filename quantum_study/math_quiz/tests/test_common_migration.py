"""What math-quiz takes from ``quantum_study.common`` and what stays its own.

The shared journal, flag store, data directory, theme and Reference screen
must be the shared implementations, not private copies that drifted; the
app's own vocabulary (categories, colours, file names) must survive.
"""
from __future__ import annotations

import ast
import pathlib

import pytest

from quantum_study.common import datadir, flags, journal, schema
from quantum_study.common.ui import theme as common_theme
from quantum_study.common.ui import widgets as common_widgets

from quantum_study.math_quiz import persistence
from quantum_study.math_quiz.core.models import Question

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent.parent


def _app_modules() -> list[pathlib.Path]:
    return sorted(p for p in APP_ROOT.rglob("*.py")
                  if "__pycache__" not in p.parts)



# ── The forks are gone ────────────────────────────────────────────────────────

@pytest.mark.parametrize("gone", [
    "ui/widgets/loading_overlay.py",
    "ui/widgets/score_bar.py",
    "ui/widgets/collapsible_panel.py",
])
def test_the_duplicated_widgets_were_deleted(gone):
    assert not (APP_ROOT / gone).exists()


def test_the_reference_screen_is_the_shared_one_plus_two_constants():
    from quantum_study.common.ui.reference import ReferenceScreen as Shared
    from quantum_study.math_quiz.ui.screens.reference_screen import ReferenceScreen

    assert issubclass(ReferenceScreen, Shared)
    source = (APP_ROOT / "ui" / "screens" / "reference_screen.py")
    assert len(source.read_text(encoding="utf-8").splitlines()) < 100


def test_the_widgets_and_the_palette_come_from_common():
    from quantum_study.math_quiz.ui import theme
    from quantum_study.math_quiz.ui.widgets.pill_badge import PillBadge

    assert PillBadge is common_widgets.PillBadge
    for name in ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2",
                 "TEXT", "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL"):
        assert getattr(theme, name) == getattr(common_theme, name), name
    # The app keeps only its own vocabulary and its own extra rules.
    assert theme.subject_color("Linear Algebra") == "#6e40c9"
    assert theme.QSS.startswith(common_theme.QSS)
    assert "QStatusBar" in theme.QSS and "QStatusBar" not in common_theme.QSS


# ── The stores really are the shared ones ─────────────────────────────────────

def test_the_paths_are_the_ones_common_records_for_this_app():
    assert persistence.mistakes_file() == datadir.mistakes_file()
    assert persistence.confidence_file() == datadir.confidence_file()
    assert persistence.flagged_file() == flags.flagged_path("math-quiz")
    names = datadir.APP_FILES["math-quiz"]
    assert persistence.history_file().name == names["history"] == "math_history.json"
    assert persistence.flagged_file().name == names["flagged"] == "math_flagged.json"
    assert persistence.draft_file().name == names["draft"] == "math_draft.json"
    assert persistence.settings_file().name == names["settings"] == "math_settings.json"


def test_the_data_dir_is_resolved_at_call_time(tmp_path, monkeypatch):
    """No frozen module constants: one setenv moves every file this app writes."""
    first = tmp_path / "one"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(first))
    assert persistence.history_file().parent == first
    second = tmp_path / "two"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(second))
    assert persistence.history_file().parent == second
    assert persistence.mistakes_file().parent == second
    # A blank override is no override, and ~ is expanded.
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", "   ")
    assert persistence.data_dir() == datadir.default_data_dir()


def test_our_growth_cap_never_trims_another_apps_rows():
    """The data-loss bug the shared journal fixed, pinned from this app."""
    foreign = [{"id": f"tutor-{i}", "app": "quantum-tutor"} for i in range(4)]
    persistence.save_mistakes(foreign)
    ours = [{"id": str(i), "app": "math-quiz"} for i in range(6)]
    journal_max = journal.MISTAKES_MAX
    try:
        journal.MISTAKES_MAX = 6
        persistence.save_mistakes(foreign + ours)
    finally:
        journal.MISTAKES_MAX = journal_max
    rows = persistence.load_mistakes()
    assert [r["id"] for r in rows if r["app"] == "quantum-tutor"] == [
        "tutor-0", "tutor-1", "tutor-2", "tutor-3"]
    assert [r["id"] for r in rows if r["app"] == "math-quiz"] == ["4", "5"]


def test_every_file_this_app_writes_has_a_registered_schema_kind():
    for kind in ("mistakes", "confidence", "flagged", "history", "settings",
                 persistence.DRAFT_KIND):
        assert schema.get(kind).version == 1
    assert persistence.DRAFT_KIND in schema.kinds()


def test_the_note_is_no_longer_silently_wiped_by_choosing_a_cause():
    """paper-drill's ``note=""`` default wiped a note whenever a cause was
    picked after it had been typed; ``note=None`` (the common default) keeps
    it, which is what the feedback screen relies on."""
    q = Question(subject="Linear Algebra", topic="t", difficulty="beginner",
                 question_type="conceptual", text="Q?")
    entry_id = persistence.log_mistake(q, "wrong", "right")["id"]
    persistence.update_mistake(entry_id, note="little-endian again")
    persistence.update_mistake(entry_id, cause="misread")
    row = persistence.load_mistakes()[0]
    assert row["cause"] == "misread" and row["note"] == "little-endian again"
