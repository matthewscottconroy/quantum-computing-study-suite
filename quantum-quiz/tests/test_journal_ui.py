"""Headless drive of the mistake journal and the confidence strip.

Covers the whole loop through the real controller: rate confidence → submit →
grade wrong → journal entry with a cause → answer the same item well → resolved.
Also asserts the accessibility pass on every control these features added.
"""
from __future__ import annotations

import json

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QPushButton

import persistence
from core.models import Evaluation, QuizConfig, Question
from core.session import QuizSession
from qiskit_contexts import EMPTY_CONTEXT
from ui import theme

MISTAKE_KEYS = {
    "id", "app", "category", "question", "your_answer", "correct_answer",
    "cause", "note", "timestamp", "resolved",
}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}

QUESTION_TEXT = "Which qubit is the most significant bit in Qiskit's ordering?"


def _question(text: str = QUESTION_TEXT, subject: str = "Qiskit") -> Question:
    return Question(subject=subject, topic="little-endian ordering",
                    difficulty="beginner", question_type="conceptual explanation",
                    text=text)


def _evaluation(score: int) -> Evaluation:
    verdict = ("Correct" if score >= 7 else
               "Partially correct" if score >= 4 else "Incorrect")
    return Evaluation(score=score, verdict=verdict, feedback="See the model answer.",
                      model_answer="Qiskit is little-endian: qubit 0 is the rightmost bit.")


@pytest.fixture
def win(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    w = MainWindow()
    w._session = QuizSession(QuizConfig(
        subjects=["Qiskit"], difficulty="beginner",
        question_types=["conceptual explanation"], question_count=5,
    ))
    w.show()
    qapp.processEvents()
    yield w
    w.close()
    w.deleteLater()


def _ask(win, question: Question) -> None:
    """Put a question on screen exactly as the controller does after generation."""
    win._current_question = question
    win._question_screen.set_confidence_enabled(win._confidence_prompt_enabled())
    win._question_screen.load_question(question, EMPTY_CONTEXT, number=1, total=5)


def _grade(win, score: int, answer: str = "qubit 0 is the leftmost bit") -> Evaluation:
    ev = _evaluation(score)
    win._on_evaluation_ready(answer, ev)
    return ev


def _mistakes() -> list:
    return json.loads(persistence.mistakes_file().read_text())


def _confidence() -> list:
    return json.loads(persistence.confidence_file().read_text())


# ── The full loop ─────────────────────────────────────────────────────────────

def test_wrong_answer_journals_a_cause_and_a_right_answer_resolves_it(win, qapp, data_dir):
    from ui.main_window import PAGE_FEEDBACK

    qs, fb = win._question_screen, win._feedback_screen
    q = _question()

    # (1) rate confidence BEFORE submitting, then answer wrongly
    _ask(win, q)
    assert qs.confidence_enabled() and qs.selected_confidence() is None
    qs._confidence_btns[4].click()
    qapp.processEvents()
    assert qs.selected_confidence() == 4
    assert qs._confidence_btns[4].isChecked()
    assert qs._confidence_btns[4].text().startswith("✓")     # glyph, not colour alone

    _grade(win, 1, answer="qubit 0 is the leftmost bit")
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_FEEDBACK
    assert fb.mistake_journal_visible()

    # (2) the journal entry, field for field, in the temp data dir
    entries = _mistakes()
    assert len(entries) == 1
    e = entries[0]
    assert set(e) == MISTAKE_KEYS
    assert e["id"] == persistence.mistake_item_id("Qiskit", QUESTION_TEXT)
    assert e["app"] == "quantum-quiz"
    assert e["category"] == "Qiskit"
    assert e["question"] == QUESTION_TEXT
    assert e["your_answer"] == "qubit 0 is the leftmost bit"
    assert e["correct_answer"].startswith("Qiskit is little-endian")
    assert e["cause"] is None            # logged before the user says anything
    assert e["note"] == ""
    assert isinstance(e["timestamp"], float) and e["resolved"] is False
    assert fb.selected_cause() is None

    # (3) the confidence pairing row
    rows = _confidence()
    assert len(rows) == 1
    c = rows[0]
    assert set(c) == CONFIDENCE_KEYS
    assert c["id"] == e["id"] and c["app"] == "quantum-quiz"
    assert c["category"] == "Qiskit" and c["confidence"] == 4
    assert c["correct"] is False         # certain and wrong: the payload
    assert persistence.confidently_wrong() == {"Qiskit": 1}

    # choosing a cause updates the same entry (no second row)
    fb._cause_btns["knew_but_slipped"].click()
    qapp.processEvents()
    assert fb.selected_cause() == "knew_but_slipped"
    assert fb._cause_btns["knew_but_slipped"].text().startswith("✓")
    assert len(_mistakes()) == 1 and _mistakes()[0]["cause"] == "knew_but_slipped"
    assert "Knew but slipped" in fb._mistake_status.text()

    # the optional note rides along on the same entry
    fb._mistake_note.setText("read the register right-to-left again")
    fb._mistake_note.returnPressed.emit()
    qapp.processEvents()
    assert _mistakes()[0]["note"] == "read the register right-to-left again"
    assert _mistakes()[0]["cause"] == "knew_but_slipped"
    assert persistence.mistake_cause_counts() == {"knew_but_slipped": 1}

    # (4) answer the same item well later → resolved, journal row gone
    _ask(win, q)
    assert qs.selected_confidence() is None          # rating never carries over
    _grade(win, 8, answer="qubit 0 is the least significant bit")
    qapp.processEvents()
    stored = _mistakes()
    assert len(stored) == 1 and stored[0]["resolved"] is True
    assert stored[0]["cause"] == "knew_but_slipped"  # the analysis is kept
    assert not fb.mistake_journal_visible()
    assert persistence.mistake_cause_counts() == {}  # nothing open any more
    assert len(_confidence()) == 1                   # no rating → no new pairing


def test_skipping_the_row_still_logs_and_never_blocks(win, qapp, data_dir, monkeypatch):
    """Skipping "what went wrong?" must lose nothing and must not raise a modal."""
    dialogs: list[str] = []
    for name in ("warning", "question", "information", "critical"):
        monkeypatch.setattr(QMessageBox, name,
                            staticmethod(lambda *a, **k: dialogs.append(a[1] if len(a) > 1 else "")
                                         or QMessageBox.StandardButton.Ok))

    _ask(win, _question())
    _grade(win, 2)
    qapp.processEvents()
    assert dialogs == []
    assert _mistakes()[0]["cause"] is None
    assert win._feedback_screen.mistake_journal_visible()
    assert persistence.mistake_cause_counts() == {"uncategorised": 1}
    assert not persistence.confidence_file().exists()     # confidence is optional too

    # clicking the chosen cause again clears it, back to uncategorised
    fb = win._feedback_screen
    fb._cause_btns["misread"].click()
    assert _mistakes()[0]["cause"] == "misread"
    fb._cause_btns["misread"].click()
    assert _mistakes()[0]["cause"] is None
    assert fb.selected_cause() is None
    assert dialogs == []


def test_partially_correct_answer_opens_no_journal_entry(win, qapp, data_dir):
    _ask(win, _question())
    _grade(win, 4)                                    # SCORE_PARTIAL_THRESHOLD
    qapp.processEvents()
    assert not win._feedback_screen.mistake_journal_visible()
    assert not persistence.mistakes_file().exists()


def test_confidence_pairing_uses_the_correct_verdict_threshold(win, qapp, data_dir):
    qs = win._question_screen
    _ask(win, _question())
    qs._confidence_btns[2].click()
    _grade(win, 7)
    assert _confidence()[0] == {**_confidence()[0], "confidence": 2, "correct": True}

    _ask(win, _question("A second question about endianness."))
    qs._confidence_btns[3].click()
    _grade(win, 6)
    assert [r["correct"] for r in _confidence()] == [True, False]
    assert persistence.confidence_calibration()[3] == {"n": 1, "correct": 0, "accuracy": 0.0}


def test_confidence_rating_can_be_cleared_before_submitting(win, qapp, data_dir):
    qs = win._question_screen
    _ask(win, _question())
    qs._confidence_btns[3].click()
    qs._confidence_btns[3].click()                    # same chip again = cleared
    assert qs.selected_confidence() is None
    assert not qs._confidence_btns[3].isChecked()
    assert qs._confidence_btns[3].text() == "3 · Fairly sure"
    _grade(win, 9)
    assert not persistence.confidence_file().exists()


def test_opt_out_is_remembered_and_never_asks_again(win, qapp, data_dir):
    qs = win._question_screen
    _ask(win, _question())
    assert qs.confidence_enabled()

    qs._confidence_optout_btn.click()
    qapp.processEvents()
    assert qs.confidence_enabled() is False
    assert persistence.confidence_prompt_enabled() is False
    assert json.loads(persistence.settings_file().read_text()) == {
        "confidence_prompt_enabled": False
    }

    _ask(win, _question("Another question entirely."))
    assert qs.confidence_enabled() is False
    assert qs.selected_confidence() is None
    _grade(win, 1)
    assert not persistence.confidence_file().exists()
    assert len(_mistakes()) == 1                      # the journal still works

    persistence.set_confidence_prompt_enabled(True)
    _ask(win, _question())
    assert qs.confidence_enabled() is True


def test_viva_followups_participate_normally(win, qapp, data_dir):
    """A follow-up is just a question: its own id, its own journal entry."""
    base, followup = _question(), _question("And why does that matter for SamplerV2 bitstrings?")
    _ask(win, base)
    _grade(win, 1)
    win._current_question = followup
    win._current_is_followup = True
    win._question_screen.load_question(followup, EMPTY_CONTEXT, 1, 5, is_followup=True)
    win._question_screen._confidence_btns[1].click()
    _grade(win, 0, answer="no idea")
    ids = [e["id"] for e in _mistakes()]
    assert ids == [persistence.mistake_item_id("Qiskit", base.text),
                   persistence.mistake_item_id("Qiskit", followup.text)]
    assert _confidence()[0]["id"] == ids[1]


def test_write_failure_is_reported_inline_not_as_a_dialog(win, qapp, monkeypatch):
    warnings: list = []
    monkeypatch.setattr(QMessageBox, "warning",
                        staticmethod(lambda *a, **k: warnings.append(a)
                                     or QMessageBox.StandardButton.Ok))

    def boom(*_a, **_k):
        raise PermissionError("read-only data directory")

    monkeypatch.setattr(persistence, "log_mistake", boom)
    _ask(win, _question())
    _grade(win, 1)
    qapp.processEvents()
    fb = win._feedback_screen
    assert warnings == []                              # never a modal in this flow
    assert fb.mistake_journal_visible()
    assert "✗" in fb._mistake_status.text()
    assert "read-only data directory" in fb._mistake_status.text()

    fb._cause_btns["other"].click()                    # no entry to update: stays quiet
    assert win._journal_id is None
    assert warnings == []


def test_history_screen_summarises_causes_and_calibration(qapp, data_dir):
    from ui.screens.history_screen import HistoryScreen

    screen = HistoryScreen()
    screen.refresh()
    assert screen.insight_lines() and "No mistakes logged yet" in screen.insight_lines()[0]
    assert screen._insight_count_lbl.text() == ""

    for i, cause in enumerate(["didnt_know", "didnt_know", "misread"]):
        persistence.log_mistake(f"id{i}", "Qiskit", "q", "a", "b")
        persistence.set_mistake_cause(f"id{i}", cause)
    persistence.log_mistake("id3", "QASM", "q", "a", "b")     # uncategorised
    persistence.resolve_mistake("id2")
    persistence.log_confidence("id0", "Qiskit", 4, False)
    persistence.log_confidence("id1", "Qiskit", 4, True)
    persistence.log_confidence("id3", "QASM", 1, False)

    screen.refresh()
    lines = screen.insight_lines()
    assert "Didn't know — 2" in lines
    assert "Not categorised yet — 1" in lines
    assert "misread" not in " ".join(lines).lower()            # resolved, so not open
    assert "Certain (4/4) — 1 of 2 correct (50%)" in lines
    assert "Guessing (1/4) — 0 of 1 correct (0%)" in lines
    assert any(l.startswith("⚠ Confidently wrong — Qiskit ×1") for l in lines)
    assert screen._insight_count_lbl.text() == "3 open / 4 logged  ·  3 rated"
    screen.close()


# ── Accessibility pass on the new controls ────────────────────────────────────

def _relative_luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    channels = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast(fg: str, bg: str) -> float:
    a, b = _relative_luminance(fg), _relative_luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def test_new_controls_are_keyboard_reachable_and_named(win, qapp):
    qs, fb = win._question_screen, win._feedback_screen
    _ask(win, _question())
    _grade(win, 1)
    qapp.processEvents()

    new_controls = (
        list(qs._confidence_btns.values())
        + [qs._confidence_optout_btn]
        + list(fb._cause_btns.values())
        + [fb._mistake_note]
    )
    for widget in new_controls:
        assert widget.focusPolicy() == Qt.FocusPolicy.StrongFocus, widget
        assert widget.accessibleName(), widget
        widget.setFocus()
        qapp.processEvents()
        assert widget.hasFocus(), widget

    # Tab must be able to leave the answer box, or nothing below it is reachable
    assert qs._answer_edit.tabChangesFocus() is True
    assert qs._answer_edit.accessibleName() == "Your answer"
    assert qs._confidence_row.accessibleName() == "Confidence rating"


def test_new_controls_have_a_visible_focus_ring_in_the_dark_palette():
    qss = theme.QSS
    assert "QPushButton#chip:focus" in qss and "QLineEdit:focus" in qss
    assert "QPushButton:focus" in qss and "QPushButton#accent:focus" in qss
    # focus ring colours must themselves be visible against what they sit on
    assert _contrast(theme.TEXT, theme.SURFACE2) >= 4.5
    assert _contrast(theme.ACCENT, theme.SURFACE) >= 4.5


@pytest.mark.parametrize("fg,bg,what", [
    (theme.TEXT, theme.SURFACE2, "chip label"),
    (theme.BG, theme.ACCENT, "selected chip label"),
    (theme.TEXT_MUTED, theme.SURFACE, "journal hint / status"),
    (theme.TEXT, theme.SURFACE, "note field text"),
    (theme.WARNING, theme.SURFACE, "confidently-wrong line"),
    (theme.ACCENT, theme.SURFACE, "don't-ask-again button"),
])
def test_new_text_meets_wcag_aa_contrast(fg, bg, what):
    assert _contrast(fg, bg) >= 4.5, f"{what}: {_contrast(fg, bg):.2f}:1"


def test_meaning_is_never_carried_by_colour_alone(win, qapp, data_dir):
    qs, fb = win._question_screen, win._feedback_screen
    _ask(win, _question())
    qs._confidence_btns[2].click()
    # selected state carries a glyph as well as the accent fill
    assert qs._confidence_btns[2].text().startswith("✓")
    assert not qs._confidence_btns[1].text().startswith("✓")

    _grade(win, 1)
    qapp.processEvents()
    assert fb._mistake_status.text().startswith("✓")          # "logged" says so in words
    fb._cause_btns["confused"].click()
    assert fb._cause_btns["confused"].text().startswith("✓")
    assert "Confused" in fb._mistake_status.text()
