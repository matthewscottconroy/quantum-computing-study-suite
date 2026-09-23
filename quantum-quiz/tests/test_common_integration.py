"""The migration itself: this app really does use ``common/``, and only it.

These tests are about *wiring*, not behaviour — the behaviour is covered by
the suites beside them.  They fail if someone re-forks a shared concern back
into the app, or breaks the import shim that makes ``common`` reachable from
inside an app directory that is not a package.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import common_path
from common import datadir, errata, flags, journal, schema
from common.ui import reference as shared_reference
from common.ui import theme as shared_theme
from common.ui import widgets as shared_widgets

import persistence
from ui import theme

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = APP_ROOT.parent
PY = sys.executable


# ── the import shim ───────────────────────────────────────────────────────────

def test_the_shim_is_the_canonical_copy_byte_for_byte():
    """``common/app_shim.py`` is the contract; a local edit is a fork."""
    ours = (APP_ROOT / "common_path.py").read_bytes()
    canonical = (REPO_ROOT / "common" / "app_shim.py").read_bytes()
    assert ours == canonical


def test_the_shim_appends_so_a_root_module_can_never_shadow_an_app_module():
    root = str(common_path.ROOT)
    assert common_path.ROOT == REPO_ROOT
    assert root in sys.path
    # the app directory must still come first, or `import ui`/`import tests`
    # would resolve to the repository's copies
    assert sys.path.index(str(APP_ROOT)) < sys.path.index(root)


def test_the_app_still_runs_as_a_plain_script_from_its_own_directory(tmp_path):
    """`cd quantum-quiz && python main.py` — the way the launcher starts it."""
    probe = (
        "import main, persistence, common_path;"
        "from ui.main_window import MainWindow;"
        "assert common_path.ROOT is not None;"
        "assert persistence.APP_ID == 'quantum-quiz';"
        "print('ok')"
    )
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(tmp_path),
        "QT_QPA_PLATFORM": "offscreen",
        "QUANTUM_STUDY_DATA_DIR": str(tmp_path / "data"),
    }
    out = subprocess.run([PY, "-c", probe], cwd=str(APP_ROOT), env=env,
                         capture_output=True, text=True, timeout=180)
    assert out.returncode == 0, out.stderr
    assert "ok" in out.stdout
    assert not (tmp_path / "data").exists()      # importing writes nothing


# ── the shared stores are the shared stores ───────────────────────────────────

def test_the_journal_helpers_are_common_journal_not_a_local_copy():
    assert persistence.MISTAKE_CAUSES is journal.MISTAKE_CAUSES
    assert persistence.CAUSE_LABELS is journal.CAUSE_LABELS
    assert persistence.CONFIDENCE_LABELS is journal.CONFIDENCE_LABELS
    assert persistence.clip_text is journal.clip_text
    assert persistence.normalise_cause is journal.normalise_cause
    assert persistence.mistakes_file() == journal.mistakes_path()
    assert persistence.confidence_file() == journal.confidence_path()
    assert persistence.FLAG_LABEL_MAX == flags.LABEL_MAX
    assert persistence.APP_ID in datadir.APPS


def test_every_file_name_matches_the_suite_wide_registry():
    expected = datadir.APP_FILES["quantum-quiz"]
    assert persistence.history_file().name == expected["history"]
    assert persistence.flagged_file().name == expected["flagged"]
    assert persistence.draft_file().name == expected["draft"]
    assert persistence.settings_file().name == expected["settings"]
    assert persistence.mistakes_file().name == "mistakes.json"
    assert persistence.confidence_file().name == "confidence.json"


def test_every_kind_this_app_writes_is_registered():
    for kind in ("history", "settings", "mistakes", "confidence", "flagged",
                 persistence.DRAFT_KIND):
        assert kind in schema.kinds()
        assert schema.get(kind).version >= 1


def test_paths_follow_the_env_var_without_reimporting(monkeypatch, tmp_path):
    """Call-time resolution: setting the variable is all a caller has to do."""
    first = tmp_path / "one"
    monkeypatch.setenv(datadir.ENV_VAR, str(first))
    assert persistence.history_file().parent == first
    second = tmp_path / "two"
    monkeypatch.setenv(datadir.ENV_VAR, str(second))
    assert persistence.history_file().parent == second
    assert persistence.mistakes_file().parent == second
    monkeypatch.setenv(datadir.ENV_VAR, "   ")            # blank = no override
    assert persistence.data_dir() == datadir.default_data_dir()


# ── the shared UI ─────────────────────────────────────────────────────────────

def test_the_theme_is_the_shared_palette_plus_this_apps_own_rules():
    for name in ("BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2",
                 "TEXT", "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL"):
        assert getattr(theme, name) == getattr(shared_theme, name), name
    assert shared_theme.QSS in theme.QSS                  # base, verbatim
    assert "QPushButton#chip" in theme.QSS                # this app's own
    assert "QLabel#muted" in theme.QSS
    assert "QPushButton#chip" not in shared_theme.QSS     # …and only this app's
    # the app's vocabulary stayed in the app
    assert set(theme.DIFFICULTY_COLORS) == {"beginner", "intermediate",
                                            "advanced", "expert"}
    assert not hasattr(shared_theme, "DIFFICULTY_COLORS")


def test_the_widgets_and_the_reference_screen_come_from_common(qapp):
    from ui.screens.feedback_screen import FeedbackScreen
    from ui.screens.reference_screen import ReferenceScreen
    from ui.widgets.pill_badge import PillBadge

    assert PillBadge is shared_widgets.PillBadge
    assert issubclass(ReferenceScreen, shared_reference.ReferenceScreen)
    assert not (APP_ROOT / "ui" / "widgets" / "score_bar.py").exists()
    assert not (APP_ROOT / "ui" / "widgets" / "collapsible_panel.py").exists()
    assert not (APP_ROOT / "ui" / "widgets" / "loading_overlay.py").exists()

    screen = FeedbackScreen()
    try:
        assert isinstance(screen._score_bar, shared_widgets.ScoreBar)
        assert isinstance(screen._model_panel, shared_widgets.CollapsiblePanel)
    finally:
        screen.deleteLater()


def test_the_app_still_honours_its_own_animation_settings(qapp):
    from config import COLLAPSIBLE_ANIMATION_MS, SCORE_BAR_ANIMATION_MS
    from ui.screens.feedback_screen import FeedbackScreen

    screen = FeedbackScreen()
    try:
        assert screen._score_bar._duration == SCORE_BAR_ANIMATION_MS
        assert screen._model_panel._duration == COLLAPSIBLE_ANIMATION_MS
    finally:
        screen.deleteLater()


# ── one end-to-end drive of everything this app writes ────────────────────────

def test_one_session_writes_every_file_through_common(data_dir, qapp, monkeypatch):
    """Mistake, confidence rating, flag, settings, history — one pass."""
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from core.models import Evaluation, QuizConfig, Question
    from core.session import QuizSession
    from qiskit_contexts import EMPTY_CONTEXT
    from ui.main_window import MainWindow

    win = MainWindow()
    try:
        win._session = QuizSession(QuizConfig(
            subjects=["Qiskit"], difficulty="beginner",
            question_types=["conceptual explanation"], question_count=1))
        q = Question(subject="Qiskit", topic="little-endian ordering",
                     difficulty="beginner", question_type="conceptual explanation",
                     text="Which qubit is the most significant bit?")
        win._current_question = q
        win._question_screen.set_confidence_enabled(True)
        win._question_screen.load_question(q, EMPTY_CONTEXT, number=1, total=1)
        win._question_screen._confidence_btns[4].click()
        win._on_evaluation_ready("the leftmost one", Evaluation(
            score=1, verdict="Incorrect", feedback="no",
            model_answer="qubit 0 is the least significant bit"))
        win._feedback_screen._cause_btns["knew_but_slipped"].click()
        win._on_flag_toggled()
        qapp.processEvents()
    finally:
        win.close()
        win.deleteLater()

    item_id = persistence.mistake_item_id(q.subject, q.text)
    mistakes = json.loads(persistence.mistakes_file().read_text())
    assert [(r["id"], r["app"], r["cause"]) for r in mistakes] == [
        (item_id, "quantum-quiz", "knew_but_slipped")]
    confidence = json.loads(persistence.confidence_file().read_text())
    assert [(r["id"], r["confidence"], r["correct"]) for r in confidence] == [
        (item_id, 4, False)]
    flagged = json.loads(persistence.flagged_file().read_text())
    assert [(r["id"], r["app"]) for r in flagged] == [
        (persistence.question_flag_id(q.subject, q.topic, q.text), "quantum-quiz")]

    # every one of them carries a version stamp, and the data files themselves
    # are still the plain lists coach.py and dashboard.py parse
    for path in (persistence.mistakes_file(), persistence.confidence_file(),
                 persistence.flagged_file()):
        assert json.loads(schema.sidecar_path(path).read_text())["schema"] == 1
        assert isinstance(json.loads(path.read_text()), list)


def test_the_real_coach_and_dashboard_still_read_what_this_app_writes(data_dir,
                                                                      monkeypatch):
    """The sidecars must be invisible to the loaders that matter."""
    persistence.log_mistake("m1", "Qiskit", "q", "a", "b")
    persistence.set_mistake_cause("m1", "misread")
    persistence.log_confidence("m1", "Qiskit", 4, False)
    persistence.toggle_flag("Qiskit::t::abc", "A flagged question", "Qiskit")
    monkeypatch.setenv(datadir.ENV_VAR, str(data_dir))

    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.append(root)
    import coach          # noqa: PLC0415 (root modules, imported lazily)
    import dashboard      # noqa: PLC0415

    # both freeze DATA_DIR at import time, so point them at ours explicitly
    monkeypatch.setattr(dashboard, "DATA_DIR", data_dir)
    monkeypatch.setattr(coach, "DATA_DIR", data_dir)

    rows = dashboard.load_mistakes(data_dir / "mistakes.json")
    assert [r["id"] for r in rows] == ["m1"]
    assert rows[0]["cause"] == "misread"
    assert [r["id"] for r in
            dashboard.load_confidence(data_dir / "confidence.json")] == ["m1"]
    assert [r["app"] for r in rows] == ["quantum-quiz"]
    assert any(item.get("id") == "Qiskit::t::abc"
               for item in coach.load_flagged_items())
    # the .schema.json / .lock sidecars must not be mistaken for flag files
    assert [p.name for _, p in coach.discover_flagged_files()] == \
        ["quiz_flagged.json"]


def test_reported_errata_points_at_this_app():
    assert errata.APP_ITEM_PATHS[persistence.APP_ID].startswith("quantum-quiz")
    url = errata.issue_url(persistence.APP_ID, "abc", "the question", "wrong")
    assert "quantum-quiz" in url and url.startswith("https://github.com/")
