"""Headless drive of the confidence strip and the mistake-cause row.

Covers the two new widgets on their own, their wiring into the exam / results /
review screens, the files they write, and the accessibility rules they have to
keep (keyboard reachable, accessible name, never colour alone, >= 4.5:1 text
contrast on the dark palette).
"""
import json

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QWidget

import persistence
from core.models import Question
from ui import theme
from ui.feedback import CauseRow, ConfidenceStrip

MISTAKE_KEYS = {"id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved"}


def _q(qid: str, section: str = "Sampler", correct: int = 0) -> Question:
    return Question(id=qid, section=section, question=f"Question {qid}?",
                    options=["opt-a", "opt-b", "opt-c", "opt-d"],
                    correct_index=correct, explanation="because",
                    difficulty="easy")


def _close(widget, qapp):
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


# --------------------------------------------------------- ConfidenceStrip
def test_confidence_strip_chips_are_keyboard_reachable_and_named(qapp):
    strip = ConfidenceStrip()
    try:
        assert sorted(strip._buttons) == [1, 2, 3, 4]
        for value, btn in strip._buttons.items():
            assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
            assert btn.accessibleName() == (
                f"Confidence {value} of 4: "
                f"{persistence.CONFIDENCE_LABELS[value].lower()}")
            assert btn.toolTip()
        assert strip._hide_btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
        assert strip._hide_btn.accessibleName()
    finally:
        _close(strip, qapp)


def test_confidence_strip_emits_and_marks_the_choice_with_a_glyph(qapp):
    strip = ConfidenceStrip()
    seen = []
    strip.rated.connect(seen.append)
    try:
        strip._buttons[3].click()
        assert seen == [3]
        assert strip.value() == 3
        # selected state is not colour alone: the chip text gains a check mark
        assert strip._buttons[3].text().startswith("✓")
        assert not strip._buttons[1].text().startswith("✓")
        strip.set_value(1)                   # programmatic: no extra signal
        assert seen == [3] and strip.value() == 1
        assert strip._buttons[1].text().startswith("✓")
    finally:
        _close(strip, qapp)


def test_confidence_strip_keys_1_to_4_rate_and_0_clears(qapp):
    host = QWidget()
    strip = ConfidenceStrip(host)
    strip.install_shortcuts(host)
    rated, cleared = [], []
    strip.rated.connect(rated.append)
    strip.cleared.connect(lambda: cleared.append(True))
    host.show()
    qapp.processEvents()
    try:
        QTest.keyClick(host, Qt.Key.Key_2)
        qapp.processEvents()
        assert rated == [2] and strip.value() == 2
        QTest.keyClick(host, Qt.Key.Key_0)
        qapp.processEvents()
        assert cleared == [True] and strip.value() is None
    finally:
        _close(host, qapp)


# ---------------------------------------------------------------- CauseRow
def test_cause_row_offers_every_cause_keyboard_reachable_and_named(qapp):
    row = CauseRow()
    try:
        assert list(row._buttons) == list(persistence.MISTAKE_CAUSES)
        for cause, btn in row._buttons.items():
            assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
            assert btn.accessibleName() == f"Cause: {persistence.CAUSE_LABELS[cause]}"
        assert row._note.accessibleName()
        assert row._note.maxLength() == 200
    finally:
        _close(row, qapp)


def test_cause_row_emits_cause_and_note_and_confirms_in_text(qapp):
    row = CauseRow()
    seen = []
    row.chosen.connect(lambda c, n: seen.append((c, n)))
    try:
        row._note.setText("  little-endian again  ")
        row._buttons["knew_but_slipped"].click()
        assert seen == [("knew_but_slipped", "little-endian again")]
        assert row.cause() == "knew_but_slipped"
        assert row._buttons["knew_but_slipped"].text().startswith("✓")
        assert row._status.isVisible() or row._status.isVisibleTo(row)
        assert "Knew it, slipped" in row._status.text()
        row.reset()
        assert row.cause() is None and row._note.text() == ""
        assert not row._buttons["knew_but_slipped"].text().startswith("✓")
    finally:
        _close(row, qapp)


def test_cause_row_note_alone_falls_back_to_other(qapp):
    row = CauseRow()
    seen = []
    row.chosen.connect(lambda c, n: seen.append((c, n)))
    try:
        row._note.setText("no idea why")
        row._note.returnPressed.emit()
        assert seen == [("other", "no idea why")]
    finally:
        _close(row, qapp)


# ------------------------------------------------------------- exam screen
def test_exam_screen_stores_the_rating_on_the_attempt(qapp, data_dir):
    from ui.screens.exam_screen import ExamScreen

    screen = ExamScreen()
    try:
        screen.start_session([_q("a"), _q("b")], 10, "sprint")
        assert screen._confidence.isVisibleTo(screen)      # default: prompt on
        screen._confidence._buttons[4].click()
        assert screen._attempts[0].confidence == 4
        screen._goto(1)
        assert screen._confidence.value() is None          # per question
        screen._goto(0)
        assert screen._confidence.value() == 4             # remembered
    finally:
        _close(screen, qapp)


def test_exam_screen_hides_the_strip_when_the_user_opted_out(qapp, data_dir):
    from ui.screens.exam_screen import ExamScreen

    persistence.set_confidence_enabled(False)
    screen = ExamScreen()
    try:
        screen.start_session([_q("a")], 10, "sprint")
        assert not screen._confidence.isVisibleTo(screen)
    finally:
        _close(screen, qapp)


def test_exam_screen_hide_button_remembers_the_opt_out(qapp, data_dir):
    from ui.screens.exam_screen import ExamScreen

    screen = ExamScreen()
    try:
        screen.start_session([_q("a")], 10, "sprint")
        screen._confidence._hide_btn.click()
        assert not screen._confidence.isVisibleTo(screen)
        assert persistence.confidence_enabled() is False
    finally:
        _close(screen, qapp)


def test_navigator_states_are_announced_and_flagging_is_not_colour_alone(
        qapp, data_dir):
    from ui.screens.exam_screen import ExamScreen

    screen = ExamScreen()
    try:
        screen.start_session([_q("a"), _q("b")], 10, "sprint")
        assert screen._nav_btns[0].accessibleName() == "Question 1: unanswered"
        screen._radio_btns[1].click()
        screen._confidence._buttons[2].click()
        screen._on_flag()
        name = screen._nav_btns[0].accessibleName()
        assert "answered" in name and "flagged" in name and "confidence 2 of 4" in name
        # flagged is also a dashed border, so it survives without colour vision
        assert "dashed" in screen._nav_btns[0].styleSheet()
        assert "dashed" not in screen._nav_btns[1].styleSheet()
    finally:
        _close(screen, qapp)


# ---------------------------------------------- full session through MainWindow
def _finished_session(win, attempts_spec):
    """Run a synthetic session: [(question, chosen_index, confidence), ...]."""
    questions = [spec[0] for spec in attempts_spec]
    win._exam.start_session(questions, 10, "sprint")
    for i, (_, chosen, conf) in enumerate(attempts_spec):
        win._exam._goto(i)
        if chosen is not None:
            win._exam._radio_btns[chosen].click()
        if conf is not None:
            win._exam._confidence._buttons[conf].click()
    win._exam._timer.stop()
    win._exam._finish()


@pytest.fixture
def window(qapp, data_dir):
    from ui.main_window import MainWindow

    win = MainWindow()
    yield win
    _close(win, qapp)


def test_submitting_a_session_journals_the_miss_and_the_pairings(window, data_dir):
    miss, hit = _q("s2", "Sampler", correct=0), _q("s1", "Sampler", correct=0)
    _finished_session(window, [(miss, 2, 4), (hit, 0, 2)])

    rows = json.loads((data_dir / "mistakes.json").read_text())
    assert len(rows) == 1
    entry = rows[0]
    assert set(entry) == MISTAKE_KEYS
    assert entry["id"] == "s2"
    assert entry["app"] == "exam-sim"
    assert entry["category"] == "Sampler"
    assert entry["question"] == "Question s2?"
    assert entry["your_answer"] == "opt-c"
    assert entry["correct_answer"] == "opt-a"
    assert entry["cause"] is None and entry["note"] == ""
    assert entry["resolved"] is False
    assert isinstance(entry["timestamp"], float)

    pairs = json.loads((data_dir / "confidence.json").read_text())
    assert [(p["id"], p["confidence"], p["correct"]) for p in pairs] == [
        ("s2", 4, False), ("s1", 2, True)]          # a confidently-wrong item
    assert all(p["app"] == "exam-sim" for p in pairs)

    # exam_missed.json keeps its own schema, untouched
    missed = json.loads((data_dir / "exam_missed.json").read_text())
    assert set(missed[0]) == {"question_id", "section", "question",
                              "correct_answer", "chosen", "timestamp"}


def test_results_screen_cause_row_categorises_the_logged_miss(window, data_dir):
    miss = _q("s2", "Sampler", correct=0)
    _finished_session(window, [(miss, 2, None)])

    rows = window._results._cause_rows
    assert len(rows) == 1
    rows[0]._note.setText("misread the index")
    rows[0]._buttons["misread"].click()

    entry = json.loads((data_dir / "mistakes.json").read_text())
    assert len(entry) == 1, "categorising must update the row, not add one"
    assert entry[0]["cause"] == "misread"
    assert entry[0]["note"] == "misread the index"


def test_results_screen_shows_no_cause_row_for_a_clean_run(window, data_dir):
    _finished_session(window, [(_q("s1", correct=0), 0, None)])
    assert window._results._cause_rows == []
    assert not (data_dir / "mistakes.json").exists() or \
        json.loads((data_dir / "mistakes.json").read_text()) == []


def test_answering_the_item_correctly_later_resolves_the_mistake(window, data_dir):
    item = _q("s2", "Sampler", correct=0)
    _finished_session(window, [(item, 2, None)])
    window._results._cause_rows[0]._buttons["didnt_know"].click()
    assert [r["resolved"] for r in persistence.load_mistakes()] == [False]

    _finished_session(window, [(item, 0, None)])        # same item, correct now
    rows = persistence.load_mistakes()
    assert [r["resolved"] for r in rows] == [True]
    assert rows[0]["cause"] == "didnt_know"             # analysis preserved


def test_home_screen_summarises_the_journal_and_toggles_the_prompt(window, data_dir):
    _finished_session(window, [(_q("s2", correct=0), 2, None)])
    window._results._cause_rows[0]._buttons["out_of_time"].click()
    window._go_home()

    text = window._home._journal_lbl.text()
    assert "1 open mistake" in text and "Out of time" in text

    btn = window._home._confidence_btn
    assert btn.text() == "Confidence prompt: on"
    assert "on" in btn.accessibleName()
    btn.click()
    assert persistence.confidence_enabled() is False
    assert btn.text() == "Confidence prompt: off"
    btn.click()
    assert persistence.confidence_enabled() is True


# ------------------------------------------------------------ review screen
def test_review_screen_journals_a_miss_then_resolves_it(qapp, data_dir, questions):
    from ui.screens.review_screen import ReviewScreen

    q = questions[0]
    wrong = (q.correct_index + 1) % len(q.options)
    persistence.record_miss(q, wrong)

    screen = ReviewScreen()
    try:
        assert screen.start() is True
        assert screen._queue[0].id == q.id
        assert screen._confidence.isVisibleTo(screen)
        assert not screen._cause_row.isVisibleTo(screen)

        # miss it again: journalled, cause row appears, pairing recorded
        screen._confidence._buttons[3].click()
        screen._radio_btns[wrong].click()
        screen._submit_btn.click()
        assert screen._cause_row.isVisibleTo(screen)
        assert "Incorrect" in screen._feedback_lbl.text()
        assert "✗" in screen._feedback_lbl.text()     # glyph, not colour alone
        rows = persistence.load_mistakes()
        assert [(r["id"], r["cause"], r["resolved"]) for r in rows] == [
            (q.id, None, False)]
        assert [(p["id"], p["confidence"], p["correct"])
                for p in persistence.load_confidence()] == [(q.id, 3, False)]

        screen._cause_row._buttons["confused"].click()
        assert persistence.load_mistakes()[0]["cause"] == "confused"

        # now get it right: every row for the item resolves
        screen._show_current()
        screen._radio_btns[q.correct_index].click()
        screen._submit_btn.click()
        assert "Correct" in screen._feedback_lbl.text()
        assert "✓" in screen._feedback_lbl.text()
        rows = persistence.load_mistakes()
        assert [(r["cause"], r["resolved"]) for r in rows] == [("confused", True)]
        assert persistence.load_missed() == []       # existing behaviour intact
    finally:
        _close(screen, qapp)


# ------------------------------------------------------------ accessibility
def _contrast(fg: str, bg: str) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    def luminance(colour: str) -> float:
        r, g, b = (int(colour.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
        return (0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b))

    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


@pytest.mark.parametrize("fg,bg,what", [
    (theme.TEXT, theme.SURFACE2, "chip label"),
    (theme.BG, theme.ACCENT, "selected chip label"),
    (theme.TEXT_MUTED, theme.BG, "'How sure?' / 'What went wrong?' prompt"),
    (theme.TEXT_MUTED, theme.SURFACE, "prompt inside a results card"),
    (theme.SUCCESS, theme.SURFACE, "'Logged as ...' confirmation"),
    (theme.TEXT, theme.SURFACE2, "note field text"),
])
def test_new_widget_text_meets_4_5_to_1_contrast(fg, bg, what):
    assert _contrast(fg, bg) >= 4.5, f"{what}: {_contrast(fg, bg):.2f}:1"


def test_theme_draws_a_focus_ring_for_every_new_control():
    for selector in ("QPushButton:focus", "QPushButton#chip:focus",
                     "QPushButton#flat:focus", "QLineEdit:focus"):
        assert selector in theme.QSS, selector
