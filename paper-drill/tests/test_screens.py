"""Screen behaviour driven headlessly (offscreen Qt, real QThread workers,
stubbed generator/grader, temp data dir).

* grading-failure dialog: "No" keeps the same question in place (regression
  test for the index-drift bug), "Yes" skips it with score 0
* a full session lands on the summary and writes paper_history.json;
  an empty question list is reported as a generation failure
* the feedback screen's flag toggle round-trips to paper_flagged.json
* the history screen lists flags newest-first, unflags, and tolerates
  non-numeric timestamps written by other tools
* the reference screen: Reference button -> docs browser -> Back, overview
  first in ladder order, #fragment anchors
"""
from __future__ import annotations

import json
import time

import pytest
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QMessageBox, QPushButton

import persistence
from core.models import Evaluation, Question, Verdict

TITLE = "Surface Code Paper"
QUESTIONS = [
    Question(1, "QUESTION-1: what is the code distance of the patch?", "factual"),
    Question(2, "QUESTION-2: why does the threshold theorem matter here? " * 4, "conceptual"),
    Question(3, "QUESTION-3: derive the logical error rate scaling.", "derivation"),
]


# ---------------------------------------------------------------------------
# Helpers and fixtures
# ---------------------------------------------------------------------------

def _button(widget, text: str) -> QPushButton:
    for btn in widget.findChildren(QPushButton):
        if btn.text() == text:
            return btn
    have = [b.text() for b in widget.findChildren(QPushButton)]
    raise AssertionError(f"no button {text!r}; have {have}")


def _pump(qapp, predicate, timeout: float = 5.0) -> bool:
    """Spin the event loop until ``predicate()`` is true (worker signals are
    delivered as queued events, so a plain assert would race the thread)."""
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
    """Stub the generator/grader entry points the workers import at run time."""
    import ai.generator
    import ai.grader

    state = {
        "questions": list(QUESTIONS),   # what generate_questions returns
        "scores": [],                   # per-call grades (8 once exhausted)
        "fail_next_grade": False,       # raise once from grade_answer
        "graded": [],                   # (question, answer) the grader saw
    }

    def generate(paper_text, count):
        return list(state["questions"])

    def grade(paper_text, question, answer):
        state["graded"].append((question, answer))
        if state["fail_next_grade"]:
            state["fail_next_grade"] = False
            raise RuntimeError("simulated grading outage")
        score = state["scores"].pop(0) if state["scores"] else 8
        verdict = (Verdict.CORRECT if score >= 7 else
                   Verdict.PARTIAL if score >= 4 else Verdict.INCORRECT)
        return Evaluation(score=score, verdict=verdict,
                          feedback=f"graded:{question}", model_answer="model")

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


def _start_session(qapp, win, count: int = 3, title: str = TITLE):
    mw = _pages()
    inp = win._input
    inp._title_edit.setText(title)
    inp._text_edit.setPlainText("We present a distance-5 surface code patch.")
    inp._count_spin.setValue(count)
    inp._save_chk.setChecked(False)
    qapp.processEvents()
    _button(inp, "Generate Questions").click()
    assert _pump(qapp, lambda: win._stack.currentIndex() == mw.PAGE_QUESTION), \
        "generation never reached the question screen"
    return win._question


def _type_answer(qapp, win, text: str) -> QPushButton:
    q = win._question
    q._answer_edit.setPlainText(text)
    qapp.processEvents()
    btn = _button(q, "Submit Answer")
    assert btn.isEnabled()
    return btn


def _submit(qapp, win, text: str) -> None:
    mw = _pages()
    _type_answer(qapp, win, text).click()
    assert _pump(qapp, lambda: win._stack.currentIndex() == mw.PAGE_FEEDBACK), \
        "feedback screen never shown"


# ---------------------------------------------------------------------------
# Question screen index handling
# ---------------------------------------------------------------------------

def test_question_screen_submit_does_not_advance_and_never_overruns(qapp):
    from ui.screens.question_screen import QuestionScreen

    qs = QuestionScreen()
    emitted = []
    qs.answer_submitted.connect(emitted.append)
    qs.start(QUESTIONS[:2], "paper")
    assert qs.current_index() == 0 and qs.has_current()
    assert qs._progress_lbl.text() == "Question 1 of 2"

    qs._answer_edit.setPlainText("x")
    qapp.processEvents()
    qs._on_submit()
    assert emitted[-1].question.text == QUESTIONS[0].text
    assert qs.current_index() == 0                 # submitting does not advance

    qs.advance()
    qs.show_current()
    assert qs._progress_lbl.text() == "Question 2 of 2"
    assert qs._answer_edit.toPlainText() == ""

    qs.advance()
    assert not qs.has_current()
    qs.advance()                                   # clamps at len(questions)
    assert qs.current_index() == 2

    qs._answer_edit.setPlainText("late")
    qapp.processEvents()
    n = len(emitted)
    qs._on_submit()                                # no IndexError, nothing emitted
    assert len(emitted) == n
    assert not qs._submit_btn.isEnabled()
    qs.deleteLater()


# ---------------------------------------------------------------------------
# Grading-failure dialog
# ---------------------------------------------------------------------------

class TestGradingFailure:
    def test_no_keeps_same_question_and_resubmit_grades_it(self, qapp, window, fake_ai,
                                                            monkeypatch):
        mw = _pages()
        asked = []

        def answer_no(*args, **kwargs):
            asked.append(args)
            return QMessageBox.StandardButton.No

        monkeypatch.setattr(QMessageBox, "question", staticmethod(answer_no))

        q = _start_session(qapp, window)
        fb = window._feedback
        assert q.current_index() == 0

        fake_ai["fail_next_grade"] = True
        _type_answer(qapp, window, "d = 5").click()
        assert _pump(qapp, lambda: asked and not q._overlay.isVisible())

        # Still on question 1, answer intact, nothing recorded.
        assert window._stack.currentIndex() == mw.PAGE_QUESTION
        assert q.current_index() == 0
        assert q._question_lbl.text() == QUESTIONS[0].text
        assert q._answer_edit.toPlainText() == "d = 5"
        assert q._submit_btn.isEnabled()
        assert window._attempts == [] and window._stats.scores == []

        # Re-submit: grader, recap and attempt must all see QUESTION-1.
        _button(q, "Submit Answer").click()
        assert _pump(qapp, lambda: window._stack.currentIndex() == mw.PAGE_FEEDBACK)
        assert fake_ai["graded"][-1] == (QUESTIONS[0].text, "d = 5")
        assert window._current_attempt.question.text == QUESTIONS[0].text
        assert fb._q_lbl.text() == f"Q: {QUESTIONS[0].text}"
        assert fb._next_btn.text() == "Next Question"
        assert len(window._attempts) == 1

        # And the rest of the session lines up: Q2, Q3, View Summary.
        _button(fb, "Next Question").click()
        qapp.processEvents()
        assert q._progress_lbl.text() == "Question 2 of 3"
        assert q._question_lbl.text() == QUESTIONS[1].text
        _submit(qapp, window, "threshold")
        _button(fb, "Next Question").click()
        qapp.processEvents()
        assert q._progress_lbl.text() == "Question 3 of 3"
        _submit(qapp, window, "p_L")
        assert fb._next_btn.text() == "View Summary"
        assert [a.question.text for a in window._attempts] == [x.text for x in QUESTIONS]
        _button(fb, "View Summary").click()
        qapp.processEvents()
        assert window._stack.currentIndex() == mw.PAGE_SUMMARY
        assert window._summary._scores_lbl.text() == "Scores: 8  8  8"

    def test_yes_skips_with_zero_score(self, qapp, window, fake_ai, monkeypatch):
        monkeypatch.setattr(QMessageBox, "question",
                            staticmethod(lambda *a, **k: QMessageBox.StandardButton.Yes))
        q = _start_session(qapp, window)
        fb = window._feedback

        fake_ai["fail_next_grade"] = True
        _submit(qapp, window, "d = 5")
        assert (fb._score_lbl.text(), fb._verdict_lbl.text()) == ("0/10", "Incorrect")
        assert fb._feedback_browser.toPlainText().startswith("Grading failed")
        assert not q._overlay.isVisible()
        assert window._stats.scores == [0]
        assert fb._next_btn.text() == "Next Question"

        _button(fb, "Next Question").click()
        qapp.processEvents()
        assert q._progress_lbl.text() == "Question 2 of 3"
        assert q._question_lbl.text() == QUESTIONS[1].text


# ---------------------------------------------------------------------------
# Session flow
# ---------------------------------------------------------------------------

def test_full_session_reaches_summary_and_saves_history(qapp, window, fake_ai, data_dir):
    mw = _pages()
    fake_ai["scores"] = [9, 5, 2]
    q = _start_session(qapp, window)
    fb = window._feedback
    assert q._progress_lbl.text() == "Question 1 of 3"
    assert q._qtype_lbl.text() == "FACTUAL"
    assert not window._overlay.isVisible()

    _submit(qapp, window, "a1")
    assert (fb._score_lbl.text(), fb._verdict_lbl.text()) == ("9/10", "Correct")
    assert fb._feedback_browser.toPlainText() == f"graded:{QUESTIONS[0].text}"
    assert fb._model_browser.toPlainText() == "model"
    _button(fb, "Next Question").click()
    qapp.processEvents()
    assert q._answer_edit.toPlainText() == ""
    assert q._qtype_lbl.text() == "CONCEPTUAL"

    _submit(qapp, window, "a2")
    assert (fb._score_lbl.text(), fb._verdict_lbl.text()) == ("5/10", "Partially correct")
    _button(fb, "Next Question").click()
    qapp.processEvents()
    _submit(qapp, window, "a3")
    assert (fb._score_lbl.text(), fb._verdict_lbl.text()) == ("2/10", "Incorrect")
    assert fb._next_btn.text() == "View Summary"

    _button(fb, "View Summary").click()
    qapp.processEvents()
    assert window._stack.currentIndex() == mw.PAGE_SUMMARY
    sm = window._summary
    assert sm._avg_lbl.text() == "5.3/10"
    assert sm._paper_lbl.text() == TITLE
    assert sm._scores_lbl.text() == "Scores: 9  5  2"

    history = json.loads((data_dir / "paper_history.json").read_text())
    assert history == [{"title": TITLE, "total": 3,
                        "average": pytest.approx(16 / 3), "scores": [9, 5, 2]}]

    _button(sm, "← New Paper").click()
    qapp.processEvents()
    assert window._stack.currentIndex() == mw.PAGE_INPUT


def test_cancel_mid_session_saves_nothing(qapp, window, fake_ai, data_dir):
    mw = _pages()
    q = _start_session(qapp, window)
    _submit(qapp, window, "a1")
    _button(window._feedback, "Next Question").click()
    qapp.processEvents()
    _button(q, "Cancel").click()
    qapp.processEvents()
    assert window._stack.currentIndex() == mw.PAGE_INPUT
    assert not (data_dir / "paper_history.json").exists()


def test_empty_question_list_is_a_generation_failure(qapp, window, fake_ai, monkeypatch):
    mw = _pages()
    warned = []
    monkeypatch.setattr(
        QMessageBox, "warning",
        staticmethod(lambda parent, title, text, *a, **k: warned.append((title, text))),
    )
    fake_ai["questions"] = []
    inp = window._input
    inp._text_edit.setPlainText("some paper")
    inp._save_chk.setChecked(False)
    qapp.processEvents()
    _button(inp, "Generate Questions").click()
    assert _pump(qapp, lambda: bool(warned))
    qapp.processEvents()
    assert warned[0][0] == "Generation Failed"
    assert "no questions" in warned[0][1]
    assert window._stack.currentIndex() == mw.PAGE_INPUT
    assert not window._overlay.isVisible()


# ---------------------------------------------------------------------------
# Flag for review — feedback screen
# ---------------------------------------------------------------------------

def test_feedback_screen_set_flagged_updates_button(qapp):
    from ui.screens.feedback_screen import FeedbackScreen

    fb = FeedbackScreen()
    assert not fb.is_flagged_shown()
    fb.set_flagged(True)
    assert fb.is_flagged_shown()
    assert fb._flag_btn.text() == "⚑ Flagged — click to unflag"
    fb.set_flagged(False)
    assert not fb.is_flagged_shown()
    assert fb._flag_btn.text() == "⚑ Flag for Review"

    got = []
    fb.flag_requested.connect(lambda: got.append(True))
    fb._flag_btn.click()
    assert got == [True]
    fb.deleteLater()


def test_feedback_flag_toggle_round_trips_to_file(qapp, window, fake_ai, data_dir):
    _start_session(qapp, window)
    _submit(qapp, window, "d = 5")
    fb = window._feedback
    flagged_file = data_dir / "paper_flagged.json"
    assert persistence.FLAGGED_FILE == flagged_file
    assert not fb.is_flagged_shown()
    assert not flagged_file.exists()

    fb._flag_btn.click()
    qapp.processEvents()
    assert fb.is_flagged_shown()
    entries = json.loads(flagged_file.read_text())
    assert len(entries) == 1
    entry = entries[0]
    assert set(entry) == {"id", "label", "category", "app", "timestamp"}
    assert entry["id"] == persistence.make_flag_id(TITLE, QUESTIONS[0].text)
    assert entry["label"] == QUESTIONS[0].text
    assert entry["category"] == TITLE
    assert entry["app"] == "paper-drill"
    assert isinstance(entry["timestamp"], float)

    fb._flag_btn.click()
    qapp.processEvents()
    assert not fb.is_flagged_shown()
    assert json.loads(flagged_file.read_text()) == []

    fb._flag_btn.click()
    qapp.processEvents()
    assert fb.is_flagged_shown()

    # Per-question state: Q2 starts unflagged; its long text is truncated.
    _button(fb, "Next Question").click()
    qapp.processEvents()
    _submit(qapp, window, "threshold")
    assert not fb.is_flagged_shown()
    fb._flag_btn.click()
    qapp.processEvents()
    labels = {e["id"]: e["label"] for e in json.loads(flagged_file.read_text())}
    assert len(labels) == 2
    q2_label = labels[persistence.make_flag_id(TITLE, QUESTIONS[1].text)]
    assert len(q2_label) <= 80 and q2_label.endswith("…")


def test_feedback_shows_pre_existing_flag(qapp, window, fake_ai):
    persistence.toggle_flag(persistence.make_flag_id(TITLE, QUESTIONS[0].text), "x", TITLE)
    _start_session(qapp, window)
    _submit(qapp, window, "d = 5")
    assert window._feedback.is_flagged_shown()


# ---------------------------------------------------------------------------
# History screen — flagged list
# ---------------------------------------------------------------------------

class TestHistoryScreen:
    @staticmethod
    def _write(data_dir, entries):
        data_dir.mkdir(parents=True, exist_ok=True)
        (data_dir / "paper_flagged.json").write_text(json.dumps(entries))

    @staticmethod
    def _rows(hs):
        return [hs._flag_list.itemAt(i).widget() for i in range(hs._flag_list.count())]

    def test_hidden_when_nothing_flagged(self, qapp, data_dir):
        from ui.screens.history_screen import HistoryScreen

        hs = HistoryScreen()
        hs.refresh()
        qapp.processEvents()
        assert hs.flagged_count() == 0
        assert hs._flag_section.isHidden()
        assert not hs._empty_lbl.isHidden()
        hs.deleteLater()

    def test_lists_newest_first_and_unflag_removes(self, qapp, data_dir):
        from ui.screens.history_screen import HistoryScreen

        self._write(data_dir, [
            {"id": "old", "label": "Old Q", "category": "P", "app": "paper-drill",
             "timestamp": 100.0},
            {"id": "new", "label": "New Q", "category": "P", "app": "paper-drill",
             "timestamp": 200.0},
        ])
        hs = HistoryScreen()
        hs.refresh()
        qapp.processEvents()
        assert not hs._flag_section.isHidden()
        assert hs.flagged_count() == 2
        assert [r.flag_id for r in self._rows(hs)] == ["new", "old"]

        _button(self._rows(hs)[0], "Unflag").click()
        qapp.processEvents()
        assert hs.flagged_count() == 1
        remaining = json.loads((data_dir / "paper_flagged.json").read_text())
        assert [e["id"] for e in remaining] == ["old"]

        _button(self._rows(hs)[0], "Unflag").click()
        qapp.processEvents()
        assert hs.flagged_count() == 0
        assert hs._flag_section.isHidden()
        assert json.loads((data_dir / "paper_flagged.json").read_text()) == []
        hs.deleteLater()

    def test_mixed_timestamp_types_do_not_raise(self, qapp, data_dir):
        from ui.screens.history_screen import HistoryScreen

        self._write(data_dir, [
            {"id": "a", "label": "A", "timestamp": 1.0},
            {"id": "b", "label": "B", "timestamp": "2026-09-09T00:00:00+00:00"},
            {"id": "c", "label": "C", "timestamp": None},
            {"id": "d", "label": "D", "timestamp": "garbage"},
            {"id": "e", "label": "E"},                       # no category / app / timestamp
            {"id": "f", "label": "F", "timestamp": "1500.5"},
        ])
        hs = HistoryScreen()
        hs.refresh()                                         # must not raise
        qapp.processEvents()
        assert hs.flagged_count() == 6
        assert [r.flag_id for r in self._rows(hs)][:2] == ["b", "f"]
        hs.deleteLater()

    def test_flag_timestamp_coercion(self):
        from ui.screens.history_screen import _flag_timestamp

        assert _flag_timestamp({"timestamp": 12.5}) == 12.5
        assert _flag_timestamp({"timestamp": 7}) == 7.0
        assert _flag_timestamp({"timestamp": "3.5"}) == 3.5
        assert _flag_timestamp({"timestamp": "1970-01-01T00:00:10+00:00"}) == 10.0
        assert _flag_timestamp({"timestamp": "nope"}) == 0.0
        assert _flag_timestamp({"timestamp": None}) == 0.0
        assert _flag_timestamp({"timestamp": True}) == 0.0
        assert _flag_timestamp({}) == 0.0


# ---------------------------------------------------------------------------
# Reference screen
# ---------------------------------------------------------------------------

class TestReference:
    def test_button_opens_docs_browser_and_back_returns(self, qapp, window):
        from ui.screens.reference_screen import docs_root

        mw = _pages()
        _button(window._input, "Reference").click()
        qapp.processEvents()
        assert window._stack.currentIndex() == mw.PAGE_REFERENCE

        ref = window._reference
        root = docs_root()
        assert root.is_dir() and root.name == "docs"
        assert ref.doc_count() == len([p for p in root.rglob("*.md") if p.is_file()])
        assert ref.current_doc() == root / "README.md"
        assert ref._path_lbl.text() == "docs / README.md"
        assert ref._browser.toPlainText().strip()

        chapters = list(ref._chapter_items)
        assert chapters[0] == "Overview"
        assert chapters[1].startswith("01 ·")
        assert ref._tree.topLevelItem(0).text(0) == "Overview"
        assert ref._chapter_filter.itemText(0) == "All Chapters"
        assert ref._chapter_filter.itemText(1) == "Overview"
        assert ref._tree.currentItem() is ref._doc_items[root / "README.md"]

        _button(ref, "← Back").click()
        qapp.processEvents()
        assert window._stack.currentIndex() == mw.PAGE_INPUT

        # Second visit reuses the scan and still shows the corpus.
        _button(window._input, "Reference").click()
        qapp.processEvents()
        assert window._stack.currentIndex() == mw.PAGE_REFERENCE
        assert ref.doc_count() == len([p for p in root.rglob("*.md") if p.is_file()])

    def test_scan_docs_puts_root_files_first(self, tmp_path):
        from ui.screens.reference_screen import scan_docs

        (tmp_path / "01_alpha").mkdir()
        (tmp_path / "02_beta").mkdir()
        (tmp_path / "README.md").write_text("# Overview\n", encoding="utf-8")
        (tmp_path / "01_alpha" / "02_second.md").write_text("# Second\n", encoding="utf-8")
        (tmp_path / "01_alpha" / "01_first.md").write_text("# First\n", encoding="utf-8")
        (tmp_path / "02_beta" / "01_only_one.md").write_text("no heading\n", encoding="utf-8")

        entries = scan_docs(tmp_path)
        assert [(c, t) for c, t, _ in entries] == [
            ("Overview", "Overview"),
            ("01 · Alpha", "First"),
            ("01 · Alpha", "Second"),
            ("02 · Beta", "Only One"),
        ]
        assert scan_docs(tmp_path / "missing") == []

    def test_prettify_dir_title_casing(self):
        from ui.screens.reference_screen import _prettify_dir

        assert _prettify_dir("03_quantum_gates_and_circuits") == "03 · Quantum Gates and Circuits"
        assert _prettify_dir("05_quantum_error_correction") == "05 · Quantum Error Correction"
        assert _prettify_dir("09_qec_for_the_impatient") == "09 · QEC for the Impatient"
        assert _prettify_dir("notes") == "Notes"

    def test_anchor_fragments_scroll_and_open(self, qapp, monkeypatch):
        from ui.screens.reference_screen import ReferenceScreen, docs_root

        ref = ReferenceScreen()
        ref.load_all()
        qapp.processEvents()
        chapter = sorted(d for d in docs_root().iterdir() if d.is_dir())[0]
        docs = sorted(chapter.glob("*.md"))
        assert len(docs) >= 2

        scrolled = []
        monkeypatch.setattr(ref._browser, "scrollToAnchor", lambda name: scrolled.append(name))

        assert ref.open_doc(docs[0])
        ref._on_anchor_clicked(QUrl("#key-formulas"))               # same-document
        assert ref.current_doc() == docs[0]
        assert scrolled == ["key-formulas"]

        ref._on_anchor_clicked(QUrl(f"{docs[1].name}#summary"))     # sibling + fragment
        assert ref.current_doc() == docs[1]
        assert scrolled[-1] == "summary"

        ref._on_anchor_clicked(QUrl("../README.md"))                # parent dir, no fragment
        assert ref.current_doc() == docs_root() / "README.md"

        ref._on_anchor_clicked(QUrl("does_not_exist.md#x"))         # missing target ignored
        assert ref.current_doc() == docs_root() / "README.md"
        assert scrolled == ["key-formulas", "summary"]
        ref.deleteLater()
