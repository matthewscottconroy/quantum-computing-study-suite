"""Headless drives of the confidence strip and the mistake-journal row through
MainWindow: schema of what lands on disk, cause/note capture, resolution,
sprint behaviour, the opt-out, and the accessibility guarantees.

Problems are fabricated and handed straight to MainWindow._on_problem_ready, so
these tests never start a ProblemWorker (test_flows.py covers the real threads).
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent

import persistence
from core.models import (
    AnswerFormat, Attempt, Problem, ProblemCategory, TrainerConfig,
)
from core.session import TrainerSession
from ui import theme

MISTAKE_FIELDS = {
    "id", "app", "category", "question", "your_answer", "correct_answer",
    "cause", "note", "timestamp", "resolved",
}


def _problem(text="Apply H to |0⟩. What is the output state?",
             cat=ProblemCategory.SINGLE_GATE_OUTPUT,
             fmt=AnswerFormat.MULTIPLE_CHOICE, correct="1") -> Problem:
    return Problem(
        category=cat, difficulty="beginner", question_text=text,
        answer_format=fmt, correct_answer=correct,
        choices=None if fmt is AnswerFormat.FREE_FORM else ["|0⟩", "|+⟩", "|1⟩", "|−⟩"],
        circuit_png=None, aux_circuit_png=None, matrix_str=None, state_str=None,
        solution_steps=["H|0⟩ = (|0⟩+|1⟩)/√2 = |+⟩"], key_concepts=["Hadamard"],
    )


class _StubEvalWorker(QObject):
    """Stands in for the Claude grading QThread.

    Submitting a free-form answer with no API key would start the real worker,
    whose error signal lands in whatever event loop runs next and pops a modal
    QMessageBox -- which aborts under offscreen Qt, in an unrelated test. The
    tests below feed MainWindow._on_eval_ready() the graded Attempt directly.
    """
    evaluation_ready = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, problem, answer, parent=None) -> None:
        super().__init__(parent)

    def start(self) -> None:
        pass


@pytest.fixture
def window(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    monkeypatch.setattr("ui.main_window.EvaluationWorker", _StubEvalWorker)
    win = MainWindow()
    # Never generate a real problem: these tests supply their own.
    monkeypatch.setattr(win, "_fetch_next", lambda: None)
    yield win
    win._sprint.stop_timers()
    win._problem._tick_timer.stop()
    win.close()


def _start(win, problem: Problem, count: int = 4, sprint: bool = False) -> None:
    win._session = TrainerSession(TrainerConfig(
        categories=[problem.category], difficulty="beginner",
        problem_count=count, sprint=sprint))
    win._on_problem_ready(problem)


def _key(widget, key) -> None:
    widget.keyPressEvent(QKeyEvent(QKeyEvent.Type.KeyPress, key, Qt.KeyboardModifier.NoModifier))


# ── The full loop: rate, miss, categorise, then get it right ──────────────────

def test_wrong_answer_journals_a_mistake_with_a_cause(window, isolated_data_dir):
    win, screen = window, window._problem
    p = _problem()
    _start(win, p)

    # (3) Confidence strip is offered before the answer and records a pairing.
    assert screen._conf_widget.isVisibleTo(screen)
    assert screen.selected_confidence() is None
    screen._conf_btns[4].click()
    assert screen.selected_confidence() == 4
    assert screen._conf_btns[4].objectName() == "confidence_on"
    assert screen._conf_btns[4].text().startswith("✓")     # not colour alone
    assert screen._conf_btns[1].objectName() == "confidence"

    # (1) Answer wrongly -> mistake row appears, entry already on disk.
    screen._choice_btns[3].click()
    assert win._session.stats.wrong == 1
    assert screen.mistake_prompt_visible()
    assert screen._verdict_lbl.text() == "✗ Incorrect — correct answer: |+⟩"

    # (2) Entry schema, field for field, in the temp data dir.
    path = isolated_data_dir / "mistakes.json"
    assert persistence.mistakes_file() == path
    entries = json.loads(path.read_text())
    assert len(entries) == 1
    e = entries[0]
    assert set(e) == MISTAKE_FIELDS
    assert e["id"] == persistence.flag_id_for(p)
    assert e["app"] == "circuit-trainer"
    assert e["category"] == "Single-gate output"
    assert e["question"] == "Apply H to |0⟩. What is the output state?"
    assert e["your_answer"] == "|−⟩" and e["correct_answer"] == "|+⟩"
    assert e["cause"] is None and e["note"] == ""          # skippable: logged anyway
    assert isinstance(e["timestamp"], float) and e["resolved"] is False

    # Confidence pairing: certain, and wrong -> the "confidently wrong" signal.
    rows = json.loads((isolated_data_dir / "confidence.json").read_text())
    assert rows == [{
        "id": e["id"], "app": "circuit-trainer", "category": "Single-gate output",
        "confidence": 4, "correct": False, "timestamp": rows[0]["timestamp"],
    }]
    assert persistence.calibration_by_level() == {4: (0, 1)}

    # Categorise it: same entry updated, never a second row.
    screen._note_edit.setText("read the ket as |1⟩")
    screen._cause_btns["misread"].click()
    assert screen.selected_cause() == "misread"
    assert screen._cause_btns["misread"].text().startswith("✓")
    stored = persistence.load_mistakes()
    assert len(stored) == 1
    assert stored[0]["cause"] == "misread"
    assert stored[0]["note"] == "read the ket as |1⟩"

    # (4) Same item answered correctly later -> resolved.
    win._problem._next_btn.click()
    _start(win, p)
    assert not screen.mistake_prompt_visible()
    assert screen.selected_confidence() is None            # reset for the new item
    screen._choice_btns[1].click()
    assert screen._verdict_lbl.text() == "✓ Correct"
    assert not screen.mistake_prompt_visible()
    resolved = persistence.load_mistakes()
    assert len(resolved) == 1 and resolved[0]["resolved"] is True
    assert resolved[0]["cause"] == "misread"               # analysis preserved
    # A skipped rating records no second confidence row.
    assert len(persistence.load_confidence()) == 1


def test_correct_answer_logs_nothing_and_shows_no_prompt(window, isolated_data_dir):
    win, screen = window, window._problem
    _start(win, _problem())
    screen._choice_btns[1].click()
    assert win._session.stats.correct == 1
    assert not screen.mistake_prompt_visible()
    assert persistence.load_mistakes() == []
    assert not (isolated_data_dir / "mistakes.json").exists()
    assert not (isolated_data_dir / "confidence.json").exists()


def test_note_typed_but_not_committed_is_saved_on_next(window, isolated_data_dir):
    win, screen = window, window._problem
    _start(win, _problem())
    screen._choice_btns[0].click()
    screen._note_edit.setText("global phase ≠ relative phase")
    assert persistence.load_mistakes()[0]["note"] == ""
    win._problem._next_btn.click()                          # flushes the note
    assert persistence.load_mistakes()[0]["note"] == "global phase ≠ relative phase"
    assert persistence.load_mistakes()[0]["cause"] is None


def test_confidence_cannot_be_set_after_the_answer(window, isolated_data_dir):
    win, screen = window, window._problem
    _start(win, _problem())
    screen._choice_btns[2].click()                          # answer with no rating
    screen.set_confidence(4)                                # hindsight attempt
    _key(screen, Qt.Key.Key_4)
    assert screen.selected_confidence() is None
    assert all(not b.isEnabled() for b in screen._conf_btns.values())
    assert persistence.load_confidence() == []

    # Free-form: locked from the moment Submit is pressed, i.e. while Claude is
    # still grading and the answer has not been revealed either.
    ff = _problem("Explain the circuit.", ProblemCategory.CIRCUIT_EXPLANATION,
                  AnswerFormat.FREE_FORM, correct="")
    _start(win, ff)
    screen._free_form_edit.setPlainText("an answer")
    screen._submit_btn.click()
    screen.set_confidence(4)
    _key(screen, Qt.Key.Key_1)
    assert screen.selected_confidence() is None
    win._on_eval_ready(Attempt(ff, "an answer", False, 1, "No."))
    assert persistence.load_confidence() == []


def test_opt_out_button_stays_live_after_answering(window, isolated_data_dir):
    win, screen = window, window._problem
    _start(win, _problem())
    screen._choice_btns[1].click()
    assert all(not b.isEnabled() for b in screen._conf_btns.values())
    assert screen._conf_off_btn.isEnabled()      # being asked is when you opt out
    screen._conf_off_btn.click()
    assert persistence.confidence_prompt_enabled() is False


def test_number_keys_rate_confidence_before_answering(window, isolated_data_dir):
    win, screen = window, window._problem
    _start(win, _problem())
    _key(screen, Qt.Key.Key_2)
    assert screen.selected_confidence() == 2
    _key(screen, Qt.Key.Key_3)
    assert screen.selected_confidence() == 3
    screen._choice_btns[1].click()
    assert persistence.load_confidence()[0] == {
        "id": persistence.load_confidence()[0]["id"], "app": "circuit-trainer",
        "category": "Single-gate output", "confidence": 3, "correct": True,
        "timestamp": persistence.load_confidence()[0]["timestamp"],
    }


def test_opt_out_hides_the_strip_and_is_remembered(window, isolated_data_dir):
    win, screen = window, window._problem
    _start(win, _problem())
    assert screen.confidence_enabled() is True
    screen._conf_off_btn.click()

    assert screen.confidence_enabled() is False
    assert persistence.confidence_prompt_enabled() is False
    assert win._setup.confidence_pref() is False
    _start(win, _problem("another question"))
    assert screen.confidence_enabled() is False             # never asked again
    screen._choice_btns[0].click()
    assert persistence.load_confidence() == []

    # Re-enabled from the setup screen.
    win._setup._conf_cb.setChecked(True)
    assert persistence.confidence_prompt_enabled() is True
    assert screen.confidence_enabled() is True


# ── Free-form (Claude-graded) ────────────────────────────────────────────────

def test_free_form_below_four_is_a_mistake_and_eight_resolves_it(window, isolated_data_dir):
    win, screen = window, window._problem
    p = _problem("Explain what this circuit does.", ProblemCategory.CIRCUIT_EXPLANATION,
                 AnswerFormat.FREE_FORM, correct="")
    _start(win, p)
    screen._free_form_edit.setPlainText("it makes the qubit random")
    screen._conf_btns[3].click()
    screen._submit_btn.click()                              # grading worker stubbed out
    win._on_eval_ready(Attempt(p, "it makes the qubit random", False, 2,
                               "Missed the entanglement.",
                               model_answer="It prepares a Bell state."))
    entry = persistence.load_mistakes()[0]
    assert entry["your_answer"] == "it makes the qubit random"
    assert entry["correct_answer"] == "It prepares a Bell state."
    assert entry["category"] == "Circuit explanation"
    assert screen.mistake_prompt_visible()
    assert persistence.load_confidence()[0]["confidence"] == 3
    assert persistence.load_confidence()[0]["correct"] is False

    screen._cause_btns["didnt_know"].click()
    win._problem._next_btn.click()

    _start(win, p)
    win._on_eval_ready(Attempt(p, "a Bell state", True, 8, "Good.",
                               model_answer="It prepares a Bell state."))
    assert not screen.mistake_prompt_visible()
    assert persistence.load_mistakes()[0]["resolved"] is True
    assert persistence.load_mistakes()[0]["cause"] == "didnt_know"


def test_free_form_partial_credit_neither_journals_nor_resolves(window, isolated_data_dir):
    win, screen = window, window._problem
    p = _problem("Explain the circuit.", ProblemCategory.CIRCUIT_EXPLANATION,
                 AnswerFormat.FREE_FORM, correct="")
    _start(win, p)
    win._on_eval_ready(Attempt(p, "partly right", False, 5, "Half there."))
    assert persistence.load_mistakes() == []                # score >= 4: not a mistake
    assert not screen.mistake_prompt_visible()


# ── Sprint mode ───────────────────────────────────────────────────────────────

def test_sprint_journals_mistakes_but_never_asks_for_confidence(window, isolated_data_dir):
    from ui.main_window import PAGE_SPRINT

    win = window
    p = _problem("Measure after H.", ProblemCategory.MEASUREMENT_PROBS)
    _start(win, p, count=2, sprint=True)
    assert win._stack.currentIndex() == PAGE_SPRINT

    win._sprint._choice_btns[0].click()                     # wrong
    entries = persistence.load_mistakes()
    assert len(entries) == 1
    assert entries[0]["cause"] is None                      # uncategorised in sprint
    assert entries[0]["your_answer"] == "|0⟩"
    assert entries[0]["category"] == "Measurement probabilities"
    assert persistence.load_confidence() == []              # no strip, no rows

    # A timeout is journalled pre-categorised as out_of_time.
    q = _problem("Another one.", ProblemCategory.MEASUREMENT_PROBS)
    _start(win, q, count=2, sprint=True)
    win._sprint.timed_out.emit(60)
    timeout_entry = persistence.load_mistakes()[-1]
    assert timeout_entry["cause"] == "out_of_time"
    assert timeout_entry["your_answer"] == "(no answer)"
    assert persistence.load_confidence() == []

    # Getting it right in a sprint still closes out an open mistake.
    _start(win, p, count=2, sprint=True)
    win._sprint._choice_btns[1].click()
    by_id = {e["id"]: e for e in persistence.load_mistakes()}
    assert by_id[persistence.flag_id_for(p)]["resolved"] is True
    assert by_id[persistence.flag_id_for(q)]["resolved"] is False


# ── Robustness & accessibility ────────────────────────────────────────────────

def test_a_broken_data_dir_never_breaks_the_flow(window, isolated_data_dir, monkeypatch):
    win, screen = window, window._problem

    def boom(*a, **k):
        raise OSError("disk on fire")

    # Every write this app makes -- journal, calibration, flags, history,
    # prefs -- funnels through common.schema.save_versioned, so one patch here
    # breaks all of them at once.
    from common import schema

    monkeypatch.setattr(schema, "atomic_write_json", boom)
    _start(win, _problem())
    screen._conf_btns[2].click()
    screen._choice_btns[0].click()                          # must not raise
    assert win._session.stats.wrong == 1
    assert screen._next_btn.isEnabled()
    assert not screen.mistake_prompt_visible()              # nothing logged, nothing to edit
    screen._note_edit.setText("x")
    screen.commit_note()                                    # no pending entry: no-op


def test_new_controls_are_keyboard_reachable_and_named(window):
    screen = window._problem
    controls = [
        *screen._conf_btns.values(),
        screen._conf_off_btn,
        *screen._cause_btns.values(),
        screen._note_edit,
        window._setup._conf_cb,
    ]
    for w in controls:
        assert w.focusPolicy().value & Qt.FocusPolicy.TabFocus.value, w
        assert w.accessibleName(), w
    # Meaning is never colour-only: each button carries its own words.
    assert [b.text() for b in screen._conf_btns.values()] == [
        "1 · Guessing", "2 · Unsure", "3 · Fairly sure", "4 · Certain"]
    assert "Misread it" in [b.text() for b in screen._cause_btns.values()]


def test_focus_ring_and_contrast_of_the_new_widgets():
    # A visible focus ring for every new control.
    for selector in ("QPushButton#confidence:focus", "QPushButton#cause:focus",
                     "QPushButton#choice:focus", "QLineEdit:focus"):
        assert selector in theme.QSS, selector

    def _lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    def _ratio(fg: str, bg: str) -> float:
        def lum(h):
            h = h.lstrip("#")
            r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
            return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)
        a, b = sorted((lum(fg), lum(bg)))
        return (b + 0.05) / (a + 0.05)

    pairs = [
        (theme.TEXT, theme.SURFACE2),        # confidence / cause button text
        (theme.ACCENT, theme.SURFACE2),      # selected state
        (theme.TEXT_MUTED, theme.SURFACE),   # strip + row headers, status line
        (theme.TEXT, theme.SURFACE),         # note field text
        (theme.SUCCESS, theme.SURFACE),      # "✓ Correct" verdict
        (theme.ERROR, theme.SURFACE),        # "✗ Incorrect" verdict
        (theme.TEAL, theme.SURFACE),         # focus ring against the panel
    ]
    for fg, bg in pairs:
        assert _ratio(fg, bg) >= 4.5, f"{fg} on {bg} = {_ratio(fg, bg):.2f}"


# ── History screen summary ────────────────────────────────────────────────────

def test_history_screen_summarises_the_journal(qapp, isolated_data_dir):
    from ui.screens.history_screen import HistoryScreen

    screen = HistoryScreen()
    screen.refresh()
    assert screen.journal_lines() == []          # empty state, no crash

    a, b, c = _problem("one"), _problem("two"), _problem("three")
    for p in (a, b, c):
        persistence.log_mistake_for_attempt(Attempt(p, "0", False, 0, "fb"))
    persistence.update_mistake(persistence.flag_id_for(a), cause="misread")
    persistence.update_mistake(persistence.flag_id_for(b), cause="misread")
    persistence.resolve_mistake(persistence.flag_id_for(a))
    for conf, ok in [(4, False), (4, False), (4, True), (2, True)]:
        persistence.log_confidence("i", "Single-gate output", conf, ok)

    screen.refresh()
    lines = screen.journal_lines()
    assert lines[0] == "3 logged · 2 still open · 1 answered correctly since"
    assert "Misread it: 2 logged (1 open)" in lines
    assert "Not yet categorised: 1 logged (1 open)" in lines
    assert any(l.startswith("Confidence calibration — ") and "4 Certain: 1/3 right" in l
               for l in lines)
    assert any(l.startswith("⚠ Confidently wrong: 2 of 3") for l in lines)
