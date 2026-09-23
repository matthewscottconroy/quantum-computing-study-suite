"""Offscreen drive of the confidence strip and the mistake-journal row.

Covers the whole loop the feature exists for: rate before the first Run, fail,
reveal the solution, categorise the cause, then pass and see the row resolved —
plus the opt-out, the skip paths, and the accessibility contract (focusable,
named, never colour-only).  All persistence goes to ``data_dir``.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtWidgets import QPushButton

import persistence
from core.models import Kata, RunResult

MISTAKE_KEYS = {"id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}


def _kata(kid: str = "ra_little_endian", title: str = "Per-qubit probabilities",
          section: str = "Results analysis") -> Kata:
    return Kata(id=kid, section=section, title=title, difficulty="beginner",
                prompt="p", starter_code="x = 0\n", test_code="assert x == 1\n",
                solution_code="# comment\n\nx = 1\n", hints=["h1", "h2"])


def _pump(qapp, n: int = 3) -> None:
    for _ in range(n):
        qapp.processEvents()


class _FakeWorker(QObject):
    """Same signals as RunWorker, no thread, completes on demand."""
    finished_run = pyqtSignal(object)
    failed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, user_code: str, test_code: str, parent=None) -> None:
        super().__init__(parent)

    def start(self) -> None:
        pass

    def complete(self, result: RunResult) -> None:
        self.finished_run.emit(result)
        self.finished.emit()


@pytest.fixture
def screen(qapp, data_dir, monkeypatch):
    """KataScreen with a fake harness and an auto-accepted Reveal dialog."""
    import ui.screens.kata_screen as mod
    monkeypatch.setattr(mod, "RunWorker", _FakeWorker)
    monkeypatch.setattr(
        mod.QMessageBox, "question",
        staticmethod(lambda *a, **k: mod.QMessageBox.StandardButton.Yes),
    )
    s = mod.KataScreen()
    yield s
    s.close(); s.deleteLater(); _pump(qapp)


def _run(screen, qapp, passed: bool, output: str = "") -> None:
    screen._run_btn.click(); _pump(qapp)
    screen._run_worker.complete(RunResult(
        passed=passed, output=output,
        phase="pass" if passed else "test_failed", duration_secs=0.1))
    _pump(qapp)


def _mistakes(data_dir: Path) -> list[dict]:
    return json.loads((data_dir / "mistakes.json").read_text())


def _cause_btn(screen, cause: str) -> QPushButton:
    return screen._mistake_row._buttons[cause]


# ------------------------------------------------- the full end-to-end loop

def test_fail_reveal_categorise_then_pass_resolves(screen, qapp, data_dir):
    k = _kata()
    before = time.time()
    screen.show_kata(k, 1, 1)

    # 1. rate confidence BEFORE the first run
    assert screen._conf_strip.isVisibleTo(screen)
    screen._conf_strip._buttons[4].click(); _pump(qapp)
    assert screen.confidence_value() == 4

    # 2. run and fail -> journalled straight away, cause not yet known
    _run(screen, qapp, False,
         "=== Test failed ===\nFAILED: qubit 0 probability was 0.0, expected 0.5\n")
    assert screen._status_lbl.text().startswith("✗ TESTS FAILED")
    assert screen._mistake_row.isHidden()              # not while you iterate
    rows = _mistakes(data_dir)
    assert len(rows) == 1 and rows[0]["cause"] is None

    # 3. confidence pairing recorded once the answer is graded
    conf = json.loads((data_dir / "confidence.json").read_text())
    assert len(conf) == 1
    c = conf[0]
    assert set(c) == CONFIDENCE_KEYS
    assert c["id"] == k.id and c["app"] == "qiskit-dojo"
    assert c["category"] == k.section
    assert c["confidence"] == 4 and c["correct"] is False    # confidently wrong
    assert isinstance(c["timestamp"], float) and c["timestamp"] >= before - 1
    assert persistence.confidently_wrong()[0]["id"] == k.id

    # 4. reveal the solution -> the "what went wrong?" row appears
    screen._reveal_btn.click(); _pump(qapp)
    assert not screen._mistake_row.isHidden()

    # 5. choose a cause + note
    screen._mistake_row._note.setText("little-endian again")
    _cause_btn(screen, "knew_but_slipped").click(); _pump(qapp)

    rows = _mistakes(data_dir)
    assert len(rows) == 1
    e = rows[0]
    assert set(e) == MISTAKE_KEYS
    assert e["id"] == "ra_little_endian"
    assert e["app"] == "qiskit-dojo"
    assert e["category"] == "Results analysis"
    assert e["question"] == "Per-qubit probabilities"
    assert e["your_answer"] == "FAILED: qubit 0 probability was 0.0, expected 0.5"
    assert e["correct_answer"] == "x = 1"              # comments/blanks stripped
    assert e["cause"] == "knew_but_slipped"
    assert e["note"] == "little-endian again"
    assert isinstance(e["timestamp"], float) and e["timestamp"] >= before - 1
    assert e["resolved"] is False
    assert all(len(e[f]) <= 200 for f in
               ("question", "your_answer", "correct_answer", "note"))

    # 6. re-answer correctly -> resolved, diagnosis kept, no second row
    _run(screen, qapp, True, "ok")
    assert screen._status_lbl.text().startswith("✓ PASSED")
    rows = _mistakes(data_dir)
    assert len(rows) == 1
    assert rows[0]["resolved"] is True
    assert rows[0]["cause"] == "knew_but_slipped"
    assert screen._mistake_row.isHidden()
    assert persistence.mistake_cause_counts() == {}
    # the rating paired with the FIRST run only — no hindsight second row
    assert len(json.loads((data_dir / "confidence.json").read_text())) == 1


def test_passing_resolves_a_row_left_open_by_an_earlier_session(screen, qapp, data_dir):
    k = _kata()
    persistence.log_mistake(persistence.make_mistake_entry(
        kata_id=k.id, category=k.section, question=k.title,
        your_answer="yesterday", correct_answer="x = 1", cause="didnt_know"))
    screen.show_kata(k, 1, 1)
    _run(screen, qapp, True, "ok")
    assert _mistakes(data_dir)[0]["resolved"] is True


def test_repeat_failures_refresh_one_row_not_five(screen, qapp, data_dir):
    screen.show_kata(_kata(), 1, 1)
    for i in range(5):
        _run(screen, qapp, False, f"FAILED: attempt {i}")
    rows = _mistakes(data_dir)
    assert len(rows) == 1
    assert rows[0]["your_answer"] == "FAILED: attempt 4"


def test_reveal_without_running_still_journals(screen, qapp, data_dir):
    screen.show_kata(_kata("cc_bell_state", section="Create circuits"), 1, 1)
    screen._reveal_btn.click(); _pump(qapp)
    rows = _mistakes(data_dir)
    assert len(rows) == 1
    assert rows[0]["your_answer"] == "(gave up without a passing run)"
    assert rows[0]["cause"] is None
    assert not screen._mistake_row.isHidden()


def test_revealing_after_a_pass_journals_nothing(screen, qapp, data_dir):
    screen.show_kata(_kata(), 1, 1)
    _run(screen, qapp, True, "ok")
    screen._reveal_btn.click(); _pump(qapp)
    assert not persistence.MISTAKES_FILE.exists()
    assert screen._mistake_row.isHidden()


def test_skipping_the_diagnosis_keeps_the_mistake(screen, qapp, data_dir):
    screen.show_kata(_kata(), 1, 1)
    _run(screen, qapp, False, "FAILED: nope")
    screen._reveal_btn.click(); _pump(qapp)
    screen._mistake_row._skip_btn.click(); _pump(qapp)
    assert screen._mistake_row.isHidden()
    rows = _mistakes(data_dir)
    assert len(rows) == 1 and rows[0]["cause"] is None
    assert persistence.mistake_cause_counts() == {"": 1}


def test_a_note_alone_is_saved_without_a_cause(screen, qapp, data_dir):
    screen.show_kata(_kata(), 1, 1)
    _run(screen, qapp, False, "FAILED: nope")
    screen._reveal_btn.click(); _pump(qapp)
    screen._mistake_row._note.setText("check qubit order first")
    screen._mistake_row._note.returnPressed.emit(); _pump(qapp)
    row = _mistakes(data_dir)[0]
    assert row["cause"] is None and row["note"] == "check qubit order first"


def test_state_is_per_kata_and_leaks_nothing_forward(screen, qapp, data_dir):
    screen.show_kata(_kata("a"), 1, 2)
    screen._conf_strip._buttons[2].click(); _pump(qapp)
    _run(screen, qapp, False, "FAILED: a")
    screen._reveal_btn.click(); _pump(qapp)
    screen._mistake_row._note.setText("note for a")
    _cause_btn(screen, "misread").click(); _pump(qapp)

    screen.show_kata(_kata("b"), 2, 2)                 # next kata
    assert screen.confidence_value() is None
    assert screen._mistake_row.isHidden()
    assert screen._mistake_row.selected_cause() is None
    assert screen._mistake_row.note_text() == ""
    assert screen._conf_strip.value() is None
    assert all(not b.isChecked() for b in screen._conf_strip._buttons.values())

    _run(screen, qapp, False, "FAILED: b")             # no rating this time
    rows = _mistakes(data_dir)
    assert [r["id"] for r in rows] == ["a", "b"]
    assert rows[0]["cause"] == "misread" and rows[0]["note"] == "note for a"
    assert rows[1]["cause"] is None and rows[1]["note"] == ""
    conf = json.loads((data_dir / "confidence.json").read_text())
    assert [(r["id"], r["confidence"]) for r in conf] == [("a", 2)]


# ------------------------------------------------------- confidence details

def test_unrated_katas_record_no_pairing(screen, qapp, data_dir):
    screen.show_kata(_kata(), 1, 1)
    _run(screen, qapp, True, "ok")
    assert not persistence.CONFIDENCE_FILE.exists()


def test_rating_is_frozen_once_you_have_run(screen, qapp):
    s = screen
    s.show_kata(_kata(), 1, 1)
    s._conf_strip._buttons[1].click(); _pump(qapp)
    _run(s, qapp, False, "FAILED: nope")
    assert all(not b.isEnabled() for b in s._conf_strip._buttons.values())
    assert s._conf_strip._prompt.text() == "Confidence: 1/4 Guessing"
    s._conf_strip._buttons[4].click(); _pump(qapp)     # inert: no hindsight
    assert s.confidence_value() == 1


def test_unrated_strip_says_so_after_a_run(screen, qapp):
    screen.show_kata(_kata(), 1, 1)
    _run(screen, qapp, False, "FAILED: nope")
    assert screen._conf_strip._prompt.text() == "Confidence: not rated"


def test_opt_out_persists_and_survives_a_rebuild(screen, qapp, data_dir, monkeypatch):
    s = screen
    s.show_kata(_kata(), 1, 1)
    assert s._conf_strip.isVisibleTo(s)
    s._conf_strip._dismiss.click(); _pump(qapp)
    assert s._conf_strip.isHidden()
    assert persistence.confidence_prompt_enabled() is False

    s.show_kata(_kata("b"), 1, 1)
    assert s._conf_strip.isHidden()                    # stays gone
    _run(s, qapp, False, "FAILED: nope")
    assert not persistence.CONFIDENCE_FILE.exists()

    import ui.screens.kata_screen as mod               # and across a restart
    fresh = mod.KataScreen()
    try:
        fresh.show_kata(_kata(), 1, 1)
        assert fresh._conf_strip.isHidden()
    finally:
        fresh.close(); fresh.deleteLater(); _pump(qapp)


def test_unreadable_data_dir_never_breaks_the_run_loop(screen, qapp, monkeypatch):
    """Persistence blowing up must not take the kata loop with it."""
    def boom(*a, **k):
        raise OSError("read-only file system")
    for name in ("log_mistake", "log_confidence", "resolve_mistakes",
                 "set_mistake_cause", "confidence_prompt_enabled",
                 "set_confidence_prompt_enabled"):
        monkeypatch.setattr("ui.screens.kata_screen." + name, boom)
    s = screen
    s.show_kata(_kata(), 1, 1)
    s._conf_strip._buttons[3].click(); _pump(qapp)
    _run(s, qapp, False, "FAILED: nope")
    s._reveal_btn.click(); _pump(qapp)
    _cause_btn(s, "other").click(); _pump(qapp)
    _run(s, qapp, True, "ok")
    assert s._status_lbl.text().startswith("✓ PASSED")


# -------------------------------------------------------------- history view

def test_history_surfaces_causes_and_calibration(qapp, data_dir):
    from ui.screens.history_screen import HistoryScreen
    h = HistoryScreen()
    try:
        h.refresh(); _pump(qapp)
        causes, calib = h.journal_text()
        assert "No open mistakes" in causes
        assert "No confidence ratings yet" in calib

        persistence.log_mistake(persistence.make_mistake_entry(
            "a", "Sampler", "q", "a", "b", cause="didnt_know"))
        persistence.log_mistake(persistence.make_mistake_entry(
            "b", "Sampler", "q", "a", "b", cause="didnt_know"))
        persistence.log_mistake(persistence.make_mistake_entry(
            "c", "Sampler", "q", "a", "b"))
        persistence.log_confidence("a", "Sampler", 4, False)
        persistence.log_confidence("b", "Sampler", 1, True)
        h.refresh(); _pump(qapp)

        causes, calib = h.journal_text()
        assert h._journal_lbl.text() == "Mistake journal (3 open)"
        assert causes.startswith("Didn't know it 2")
        assert "Not categorised 1" in causes
        assert "Certain 0/1" in calib and "Guessing 1/1" in calib
        assert "confidently wrong: 1" in calib
    finally:
        h.close(); h.deleteLater(); _pump(qapp)


# ------------------------------------------------------------ accessibility

def test_every_new_control_is_focusable_and_named(screen):
    s = screen
    controls = (list(s._conf_strip._buttons.values())
                + [s._conf_strip._dismiss]
                + list(s._mistake_row._buttons.values())
                + [s._mistake_row._skip_btn, s._mistake_row._note])
    for w in controls:
        assert w.focusPolicy() == Qt.FocusPolicy.StrongFocus, w
        assert w.accessibleName(), w
        assert w.accessibleDescription(), w
    for w in (s._conf_strip, s._mistake_row):
        assert w.accessibleName() and w.accessibleDescription()
    # the focus ring is an explicit accent border, not the platform default
    from PyQt6.QtGui import QColor, QPalette
    from ui import theme
    for btn in list(s._conf_strip._buttons.values()) + list(s._mistake_row._buttons.values()):
        assert f"QPushButton:focus {{ border: 1px solid {theme.ACCENT}" in btn.styleSheet()
    # Qt's 50%-alpha placeholder is 4.36:1 on SURFACE2; TEXT_MUTED is 4.95:1
    placeholder = s._mistake_row._note.palette().color(QPalette.ColorRole.PlaceholderText)
    assert placeholder == QColor(theme.TEXT_MUTED)


def test_selection_is_never_colour_alone(screen, qapp):
    s = screen
    s.show_kata(_kata(), 1, 1)
    assert s._conf_strip._buttons[3].text() == "○ 3  Fairly sure"
    s._conf_strip._buttons[3].click(); _pump(qapp)
    assert s._conf_strip._buttons[3].text() == "● 3  Fairly sure"
    assert s._conf_strip._buttons[2].text() == "○ 2  Unsure"

    _run(s, qapp, False, "FAILED: nope")
    s._reveal_btn.click(); _pump(qapp)
    assert _cause_btn(s, "misread").text() == "Misread the task"
    _cause_btn(s, "misread").click(); _pump(qapp)
    assert _cause_btn(s, "misread").text() == "✓ Misread the task"
    assert _cause_btn(s, "other").text() == "Other"
    _cause_btn(s, "other").click(); _pump(qapp)        # exclusive: tick moves
    assert _cause_btn(s, "misread").text() == "Misread the task"
    assert _cause_btn(s, "other").text() == "✓ Other"


def test_chips_reserve_room_for_the_selection_glyph(screen):
    """Regression: the tick made the label wider than the already-laid-out
    button and clipped it ("✓ Knew it, slippe…")."""
    s = screen
    from persistence import CAUSE_LABELS, CONFIDENCE_LABELS
    for cause, btn in s._mistake_row._buttons.items():
        need = btn.fontMetrics().horizontalAdvance(f"✓ {CAUSE_LABELS[cause]}")
        assert btn.minimumWidth() >= need, cause
    for level, btn in s._conf_strip._buttons.items():
        need = btn.fontMetrics().horizontalAdvance(
            f"● {level}  {CONFIDENCE_LABELS[level]}")
        assert btn.minimumWidth() >= need, level


def test_feedback_rows_do_not_shrink_the_editor_or_output_panes(screen):
    """Both rows live in the screen's root column, not inside the output
    card, so revealing a solution never squeezes the output pane."""
    s = screen
    root = s.layout()
    owned = {root.itemAt(i).widget() for i in range(root.count())}
    assert s._conf_strip in owned
    assert s._mistake_row in owned
    assert s._output_view.parent() is not s._mistake_row.parent()


def test_theme_has_a_visible_focus_ring_for_every_button_variant():
    """The focus rules now come from the shared base stylesheet, and this app's
    own rules are appended to it rather than replacing it."""
    from common.ui import theme as base
    from ui import theme
    assert f"QPushButton:focus {{ border: 2px solid {theme.ACCENT}" in theme.QSS
    assert "QPushButton#accent:focus" in theme.QSS
    assert "QPushButton#flat:focus" in theme.QSS
    assert "QPushButton#pill:focus" in theme.QSS
    # the shared base is present verbatim, plus this app's extra rules
    assert theme.QSS.startswith(base.QSS)
    assert "QPlainTextEdit#code, QPlainTextEdit#output" in theme.QSS
    assert "QSplitter::handle" in theme.QSS
    # the palette is the shared one, and the section colours are not
    assert theme.ACCENT == base.ACCENT and theme.BG == base.BG
    assert not hasattr(base, "SECTION_COLORS")
    assert set(theme.SECTION_COLORS) and "Sampler" in theme.SECTION_COLORS
