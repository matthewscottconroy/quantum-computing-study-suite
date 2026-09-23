"""Headless drive of the two new learning-signal surfaces.

* the confidence strip on the question screen (shown *before* Submit, so the
  rating cannot be hindsight), its opt-out, and the row it pairs with the grade
* the "What went wrong?" row on the feedback screen: a wrong answer is logged
  before a cause is picked, picking one updates that entry, answering the same
  item correctly later resolves it
* accessibility of every new control (focusable, named, glyph-not-colour) and
  the contrast of the colours they use against the dark palette

Everything runs offscreen with a stubbed generator/grader and a temp data dir.
"""
from __future__ import annotations

import json
import time

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QPushButton

import persistence
from core.models import Evaluation, Question, Verdict

TITLE = "Surface Code Paper"
QUESTIONS = [
    Question(1, "QUESTION-1: what is the code distance of the patch?", "factual"),
    Question(2, "QUESTION-2: why does the threshold theorem matter here?", "conceptual"),
]
MISTAKE_KEYS = {"id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}


# ---------------------------------------------------------------------------
# Helpers and fixtures (mirrors tests/test_screens.py so the two files stay
# independent of each other)
# ---------------------------------------------------------------------------

def _button(widget, text: str) -> QPushButton:
    for btn in widget.findChildren(QPushButton):
        if btn.text() == text:
            return btn
    have = [b.text() for b in widget.findChildren(QPushButton)]
    raise AssertionError(f"no button {text!r}; have {have}")


def _pump(qapp, predicate, timeout: float = 5.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        qapp.processEvents()
        if predicate():
            return True
        time.sleep(0.005)
    qapp.processEvents()
    return bool(predicate())


def _pages():
    from ui import main_window as mw
    return mw


@pytest.fixture
def fake_ai(monkeypatch):
    import ai.generator
    import ai.grader

    state = {"questions": list(QUESTIONS), "scores": [], "fail_next_grade": False}

    def generate(paper_text, count):
        return list(state["questions"])

    def grade(paper_text, question, answer):
        if state["fail_next_grade"]:
            state["fail_next_grade"] = False
            raise RuntimeError("simulated grading outage")
        score = state["scores"].pop(0) if state["scores"] else 8
        verdict = (Verdict.CORRECT if score >= 7 else
                   Verdict.PARTIAL if score >= 4 else Verdict.INCORRECT)
        return Evaluation(score=score, verdict=verdict,
                          feedback=f"graded:{question}",
                          model_answer="distance 5")

    monkeypatch.setattr(ai.generator, "generate_questions", generate)
    monkeypatch.setattr(ai.grader, "grade_answer", grade)
    return state


@pytest.fixture
def window(qapp, data_dir, no_api_key):
    from ui.main_window import MainWindow

    win = MainWindow()
    win.show()
    qapp.processEvents()
    yield win
    for name in ("_gen_worker", "_grade_worker"):
        worker = getattr(win, name, None)
        if worker is not None:
            worker.wait(3000)
    win.close()
    win.deleteLater()
    qapp.processEvents()


def _start_session(qapp, win, title: str = TITLE):
    mw = _pages()
    inp = win._input
    inp._title_edit.setText(title)
    inp._text_edit.setPlainText("We present a distance-5 surface code patch.")
    inp._count_spin.setValue(len(QUESTIONS))
    inp._save_chk.setChecked(False)
    qapp.processEvents()
    _button(inp, "Generate Questions").click()
    assert _pump(qapp, lambda: win._stack.currentIndex() == mw.PAGE_QUESTION), \
        "generation never reached the question screen"
    return win._question


def _submit(qapp, win, text: str) -> None:
    mw = _pages()
    q = win._question
    q._answer_edit.setPlainText(text)
    qapp.processEvents()
    _button(q, "Submit Answer").click()
    assert _pump(qapp, lambda: win._stack.currentIndex() == mw.PAGE_FEEDBACK), \
        "feedback screen never shown"


def _item_id(question_text: str = QUESTIONS[0].text, title: str = TITLE) -> str:
    return persistence.make_flag_id(title, question_text)


def _mistakes(data_dir) -> list[dict]:
    path = data_dir / "mistakes.json"
    return json.loads(path.read_text()) if path.exists() else []


def _confidence(data_dir) -> list[dict]:
    path = data_dir / "confidence.json"
    return json.loads(path.read_text()) if path.exists() else []


# ---------------------------------------------------------------------------
# Mistake journal — feedback screen
# ---------------------------------------------------------------------------

class TestMistakeJournal:
    def test_wrong_answer_logs_entry_then_a_cause_updates_it(self, qapp, window,
                                                             fake_ai, data_dir):
        fake_ai["scores"] = [2]
        before = time.time()
        _start_session(qapp, window)
        _submit(qapp, window, "three, I think")
        fb = window._feedback

        # 1. Logged the moment it was graded — before any cause is picked.
        assert fb.mistake_prompt_visible()
        assert fb.selected_cause() is None
        entries = _mistakes(data_dir)
        assert len(entries) == 1
        entry = entries[0]
        assert set(entry) == MISTAKE_KEYS
        assert entry["id"] == _item_id()
        assert entry["app"] == "paper-drill"
        assert entry["category"] == TITLE                 # category = paper title
        assert entry["question"] == QUESTIONS[0].text
        assert entry["your_answer"] == "three, I think"
        assert entry["correct_answer"] == "distance 5"
        assert entry["cause"] is None
        assert entry["note"] == ""
        assert entry["resolved"] is False
        assert isinstance(entry["timestamp"], float)
        assert before <= entry["timestamp"] <= time.time() + 1

        # 2. Picking a cause updates that same entry, adding the typed note.
        fb._note_edit.setText("read the qubit order backwards")
        fb._cause_buttons["knew_but_slipped"].click()
        qapp.processEvents()
        entries = _mistakes(data_dir)
        assert len(entries) == 1
        assert entries[0]["cause"] == "knew_but_slipped"
        assert entries[0]["note"] == "read the qubit order backwards"
        assert fb.selected_cause() == "knew_but_slipped"
        assert fb._cause_buttons["knew_but_slipped"].text() == "✓ Knew but slipped"

        # 3. Re-picking a different cause still edits one row.
        fb._cause_buttons["misread"].click()
        qapp.processEvents()
        entries = _mistakes(data_dir)
        assert len(entries) == 1 and entries[0]["cause"] == "misread"
        assert fb._cause_buttons["knew_but_slipped"].text() == "Knew but slipped"

        # 4. Clicking the chosen cause again clears it back to "not categorised".
        fb._cause_buttons["misread"].click()
        qapp.processEvents()
        assert fb.selected_cause() is None
        assert _mistakes(data_dir)[0]["cause"] is None
        assert persistence.cause_counts() == {"uncategorised": 1}

    def test_skipping_the_row_still_records_the_mistake(self, qapp, window,
                                                        fake_ai, data_dir):
        mw = _pages()
        fake_ai["scores"] = [1, 9]
        _start_session(qapp, window)
        _submit(qapp, window, "no idea")
        fb = window._feedback
        assert fb.mistake_prompt_visible()

        # Nothing blocks the flow: Next Question is live with the row open.
        _button(fb, "Next Question").click()
        qapp.processEvents()
        assert window._stack.currentIndex() == mw.PAGE_QUESTION
        entries = _mistakes(data_dir)
        assert len(entries) == 1 and entries[0]["cause"] is None

        # A right answer hides the row and logs nothing new.
        _submit(qapp, window, "because errors are suppressed exponentially")
        assert not fb.mistake_prompt_visible()
        assert len(_mistakes(data_dir)) == 1

    def test_note_without_a_cause_is_saved_on_commit(self, qapp, window,
                                                     fake_ai, data_dir):
        fake_ai["scores"] = [0]
        _start_session(qapp, window)
        _submit(qapp, window, "blank")
        fb = window._feedback
        fb._note_edit.setText("ran out of patience, not time")
        fb._note_edit.returnPressed.emit()
        qapp.processEvents()
        entry = _mistakes(data_dir)[0]
        assert entry["cause"] is None
        assert entry["note"] == "ran out of patience, not time"

    def test_answering_the_same_item_correctly_resolves_it(self, qapp, window,
                                                           fake_ai, data_dir):
        mw = _pages()
        fake_ai["scores"] = [2]
        _start_session(qapp, window)
        _submit(qapp, window, "three")
        window._feedback._cause_buttons["didnt_know"].click()
        qapp.processEvents()
        assert _mistakes(data_dir)[0]["resolved"] is False

        # Back out and drill the same paper again — same title, same question,
        # therefore the same item id.
        _button(window._feedback, "Next Question").click()
        qapp.processEvents()
        _button(window._question, "Cancel").click()
        qapp.processEvents()
        assert window._stack.currentIndex() == mw.PAGE_INPUT

        fake_ai["scores"] = [9]
        _start_session(qapp, window)
        _submit(qapp, window, "distance 5")
        assert not window._feedback.mistake_prompt_visible()
        entries = _mistakes(data_dir)
        assert len(entries) == 1                      # resolved, not duplicated
        assert entries[0]["id"] == _item_id()
        assert entries[0]["resolved"] is True
        assert entries[0]["cause"] == "didnt_know"    # the analysis is kept

    def test_partial_credit_is_not_a_mistake(self, qapp, window, fake_ai, data_dir):
        fake_ai["scores"] = [4]                       # threshold is score < 4
        _start_session(qapp, window)
        _submit(qapp, window, "half right")
        assert not window._feedback.mistake_prompt_visible()
        assert _mistakes(data_dir) == []

    def test_grading_failure_records_nothing(self, qapp, window, fake_ai,
                                             data_dir, monkeypatch):
        monkeypatch.setattr(QMessageBox, "question",
                            staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes))
        _start_session(qapp, window)
        window._question._conf_buttons[4].click()
        fake_ai["fail_next_grade"] = True
        _submit(qapp, window, "d = 5")
        fb = window._feedback
        assert fb._score_lbl.text() == "0/10"         # stand-in for "never graded"
        assert not fb.mistake_prompt_visible()
        assert _mistakes(data_dir) == []
        assert _confidence(data_dir) == []

    def test_unwritable_store_never_derails_the_drill(self, qapp, window, fake_ai,
                                                      data_dir, monkeypatch):
        data_dir.mkdir(parents=True, exist_ok=True)
        blocker = data_dir / "blocker"
        blocker.write_text("not a directory")
        monkeypatch.setattr(persistence, "MISTAKES_FILE", blocker / "mistakes.json")
        monkeypatch.setattr(persistence, "CONFIDENCE_FILE", blocker / "confidence.json")

        fake_ai["scores"] = [1]
        q = _start_session(qapp, window)
        q._conf_buttons[2].click()
        _submit(qapp, window, "guess")                # must not raise
        fb = window._feedback
        assert fb._score_lbl.text() == "1/10"
        assert fb.mistake_prompt_visible()
        fb._cause_buttons["other"].click()            # still must not raise
        qapp.processEvents()
        assert fb.selected_cause() == "other"


# ---------------------------------------------------------------------------
# Confidence calibration — question screen
# ---------------------------------------------------------------------------

class TestConfidenceStrip:
    def test_rating_is_taken_before_submit_and_paired_with_the_grade(
            self, qapp, window, fake_ai, data_dir):
        fake_ai["scores"] = [2, 9]
        q = _start_session(qapp, window)
        assert q.confidence_enabled()
        assert q.confidence() is None

        q._conf_buttons[4].click()                    # "Certain" — before Submit
        qapp.processEvents()
        assert q.confidence() == 4
        assert q._conf_buttons[4].text() == "✓ Certain"
        assert _confidence(data_dir) == []             # nothing logged yet

        _submit(qapp, window, "three")
        rows = _confidence(data_dir)
        assert len(rows) == 1
        row = rows[0]
        assert set(row) == CONFIDENCE_KEYS
        assert row["id"] == _item_id()
        assert row["app"] == "paper-drill"
        assert row["category"] == TITLE
        assert row["confidence"] == 4
        assert row["correct"] is False                 # confidently wrong
        assert isinstance(row["timestamp"], float)
        assert [e["id"] for e in persistence.confidently_wrong()] == [_item_id()]

        # Next question starts unrated; a right answer pairs as correct.
        _button(window._feedback, "Next Question").click()
        qapp.processEvents()
        assert q.confidence() is None
        assert q._conf_buttons[4].text() == "Certain"
        q._conf_buttons[1].click()
        _submit(qapp, window, "threshold")
        rows = _confidence(data_dir)
        assert [(r["confidence"], r["correct"]) for r in rows] == [(4, False), (1, True)]
        assert rows[1]["id"] == _item_id(QUESTIONS[1].text)

    def test_rating_is_skippable_and_retractable(self, qapp, window, fake_ai, data_dir):
        q = _start_session(qapp, window)
        q._conf_buttons[3].click()
        qapp.processEvents()
        assert q.confidence() == 3
        q._conf_buttons[3].click()                    # click again = unrate
        qapp.processEvents()
        assert q.confidence() is None
        assert q._conf_buttons[3].text() == "Fairly sure"

        _submit(qapp, window, "no rating given")
        assert _confidence(data_dir) == []             # skipped, nothing recorded

    def test_opt_out_hides_the_strip_and_is_remembered(self, qapp, window,
                                                       fake_ai, data_dir):
        q = _start_session(qapp, window)
        q._conf_buttons[2].click()
        _button(q, "Don't ask again").click()
        qapp.processEvents()
        assert not q.confidence_enabled()
        assert q.confidence() is None
        assert persistence.confidence_prompt_enabled() is False
        assert json.loads((data_dir / "paper_settings.json").read_text()) == {
            "confidence_prompt": False}

        _submit(qapp, window, "still answerable")
        assert _confidence(data_dir) == []

        # A freshly built screen honours the saved opt-out…
        from ui.screens.question_screen import QuestionScreen
        fresh = QuestionScreen()
        assert not fresh.confidence_enabled()
        # …and turning it back on shows it again.
        persistence.set_confidence_prompt_enabled(True)
        fresh._refresh_confidence_visibility()
        assert fresh.confidence_enabled()
        fresh.deleteLater()

    def test_corrupt_settings_leave_the_strip_on(self, qapp, data_dir):
        from ui.screens.question_screen import QuestionScreen

        data_dir.mkdir(parents=True, exist_ok=True)
        persistence.SETTINGS_FILE.write_text("{not json")
        screen = QuestionScreen()
        assert screen.confidence_enabled()
        screen.deleteLater()


# ---------------------------------------------------------------------------
# Accessibility of the new controls
# ---------------------------------------------------------------------------

def _contrast(fg: str, bg: str) -> float:
    def lum(hexc: str) -> float:
        channels = [int(hexc[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        channels = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                    for c in channels]
        return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

    light, dark = sorted((lum(fg), lum(bg)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


class TestAccessibility:
    def test_every_new_control_is_focusable_and_named(self, qapp):
        from ui.screens.feedback_screen import FeedbackScreen
        from ui.screens.question_screen import QuestionScreen

        q = QuestionScreen()
        fb = FeedbackScreen()
        controls = (list(q._conf_buttons.values()) + [q._conf_optout_btn]
                    + list(fb._cause_buttons.values()) + [fb._note_edit])
        for widget in controls:
            assert widget.focusPolicy() in (Qt.FocusPolicy.StrongFocus,
                                            Qt.FocusPolicy.WheelFocus), widget
            assert widget.accessibleName().strip(), widget
        assert q._conf_buttons[1].accessibleName() == "Confidence 1 of 4: Guessing"
        assert fb._cause_buttons["out_of_time"].accessibleName() == "Cause: Out of time"
        q.deleteLater()
        fb.deleteLater()

    def test_focus_ring_and_selection_glyph_are_styled_not_colour_only(self, qapp):
        from ui.screens.feedback_screen import FeedbackScreen
        from ui.screens.question_screen import QuestionScreen
        from ui import theme

        q = QuestionScreen()
        fb = FeedbackScreen()
        for sheet in (q._conf_strip.styleSheet(), fb._mistake_row.styleSheet()):
            assert ":focus" in sheet
            assert f"dashed {theme.ACCENT}" in sheet     # visible focus ring
            assert '[chosen="yes"]' in sheet

        # Selected state carries a glyph and bold weight, not just a colour.
        q._conf_buttons[2].click()
        assert q._conf_buttons[2].text().startswith("✓ ")
        assert q._conf_buttons[2].property("chosen") == "yes"
        assert q._conf_buttons[2].accessibleDescription() == "Selected"
        fb.show_mistake_prompt(True)
        fb._cause_buttons["confused"].click()
        assert fb._cause_buttons["confused"].text().startswith("✓ ")
        assert fb._cause_buttons["confused"].property("chosen") == "yes"
        q.deleteLater()
        fb.deleteLater()

    def test_text_colours_clear_4_5_to_1_on_the_dark_palette(self):
        from ui import theme

        pairs = [
            (theme.TEXT, theme.BG), (theme.TEXT, theme.SURFACE),
            (theme.TEXT, theme.SURFACE2),
            (theme.TEXT_MUTED, theme.BG), (theme.TEXT_MUTED, theme.SURFACE),
            (theme.ACCENT, theme.BG), (theme.ACCENT, theme.SURFACE),
        ]
        for fg, bg in pairs:
            assert _contrast(fg, bg) >= 4.5, f"{fg} on {bg}"


# ---------------------------------------------------------------------------
# Mistake patterns on the history screen
# ---------------------------------------------------------------------------

class TestHistoryPatterns:
    @staticmethod
    def _rows(hs):
        return [hs._insight_list.itemAt(i).widget()
                for i in range(hs._insight_list.count())]

    def test_hidden_until_something_is_logged(self, qapp, data_dir):
        from ui.screens.history_screen import HistoryScreen

        hs = HistoryScreen()
        hs.refresh()
        qapp.processEvents()
        assert hs.insight_count() == 0
        assert hs._insight_section.isHidden()
        hs.deleteLater()

    def test_tallies_causes_and_confidently_wrong(self, qapp, data_dir):
        from ui.screens.history_screen import HistoryScreen

        persistence.log_mistake("paper-a", "P", "Q1", "w", "r")
        persistence.set_mistake_cause("paper-a", "misread")
        persistence.log_mistake("paper-b", "P", "Q2", "w", "r")
        persistence.set_mistake_cause("paper-b", "misread")
        persistence.resolve_mistake("paper-b")
        persistence.log_mistake("paper-c", "P", "Q3", "w", "r")    # uncategorised
        persistence.log_confidence("paper-a", "P", 4, False)       # confidently wrong
        persistence.log_confidence("paper-c", "P", 1, False)       # knew it was a guess
        # another app's rows must not leak into this app's tally
        foreign = persistence.load_mistakes() + [{
            "id": "quiz-x", "app": "quantum-quiz", "category": "Gates",
            "question": "q", "your_answer": "a", "correct_answer": "b",
            "cause": "confused", "note": "", "timestamp": 1.0, "resolved": False}]
        persistence._save_mistakes(foreign)

        hs = HistoryScreen()
        hs.refresh()
        qapp.processEvents()
        assert not hs._insight_section.isHidden()
        rows = self._rows(hs)
        assert [(r.label, r.value) for r in rows] == [
            ("Misread", "2"),
            ("Not categorised yet", "1"),
            ("Confidently wrong", "1 of 2"),
        ]
        assert rows[0].detail == "1 still open"          # one of the two resolved
        assert "fairly sure" in rows[2].detail
        hs.deleteLater()

    def test_end_to_end_from_a_drilled_mistake(self, qapp, window, fake_ai, data_dir):
        mw = _pages()
        fake_ai["scores"] = [1]
        q = _start_session(qapp, window)
        q._conf_buttons[3].click()
        _submit(qapp, window, "no idea")
        window._feedback._cause_buttons["out_of_time"].click()
        qapp.processEvents()

        _button(window._feedback, "Next Question").click()
        qapp.processEvents()
        _button(window._question, "Cancel").click()
        qapp.processEvents()
        _button(window._input, "View History").click()
        qapp.processEvents()
        assert window._stack.currentIndex() == mw.PAGE_HISTORY

        rows = self._rows(window._history)
        assert [(r.label, r.value, r.detail) for r in rows] == [
            ("Out of time", "1", "1 still open"),
            ("Confidently wrong", "1 of 1",
             "answers you rated ‘fairly sure’ or ‘certain’ and still got wrong"),
        ]
