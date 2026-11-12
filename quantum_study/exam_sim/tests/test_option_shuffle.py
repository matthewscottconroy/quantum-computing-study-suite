"""The correct answer must not be findable by position.

The bank stores the right option first in 261 of 300 questions.  Before the
options were shuffled at display time, "always pick A" scored about 59/68 on a
full mock and cleared the 47 pass mark on every draw, which made every number
downstream of exam-sim meaningless.  These tests drive the real screens, so
they fail if a screen ever goes back to showing options in bank order.
"""
from __future__ import annotations

import random
from collections import Counter

import pytest

from quantum_study.exam_sim import config
from quantum_study.exam_sim.bank import build_exam_set
from quantum_study.exam_sim.core.models import ExamAttempt, Question


def _q(qid: str = "q", correct: int = 0) -> Question:
    return Question(id=qid, section="Sampler", question=f"Question {qid}?",
                    options=["opt-a", "opt-b", "opt-c", "opt-d"],
                    correct_index=correct, explanation="because",
                    difficulty="easy")


def _close(widget, qapp):
    widget.close()
    widget.deleteLater()
    qapp.processEvents()


def _shown(screen) -> list[str]:
    """The option texts in display order, letter prefix stripped."""
    return [rb.text().split(".  ", 1)[1]
            for rb in screen._radio_btns if not rb.isHidden()]


@pytest.fixture
def exam(qapp, data_dir):
    from quantum_study.exam_sim.ui.screens.exam_screen import ExamScreen

    screen = ExamScreen()
    yield screen
    screen.abort()
    _close(screen, qapp)


# ------------------------------------------------------------------ the model
def test_attempt_without_an_order_falls_back_to_bank_order():
    attempt = ExamAttempt(_q())
    assert attempt.display_order() == [0, 1, 2, 3]
    # a stale or malformed order must not index out of range either
    assert ExamAttempt(_q(), option_order=[0, 1]).display_order() == [0, 1, 2, 3]
    assert ExamAttempt(_q(), option_order=[3, 3, 1, 0]).display_order() == [0, 1, 2, 3]
    assert ExamAttempt(_q(), option_order=[2, 0, 3, 1]).display_order() == [2, 0, 3, 1]


# ---------------------------------------------------------------- exam screen
def test_rows_are_lettered_by_position_and_show_every_option_once(exam):
    exam.start_session([_q()], 10, "sprint")
    assert [rb.text()[:4] for rb in exam._radio_btns] == [
        "A.  ", "B.  ", "C.  ", "D.  "]
    assert sorted(_shown(exam)) == ["opt-a", "opt-b", "opt-c", "opt-d"]
    order = exam._attempts[0].option_order
    assert sorted(order) == [0, 1, 2, 3]
    assert _shown(exam) == [_q().options[i] for i in order]


def test_a_click_records_the_bank_index_of_the_option_in_that_row(exam):
    q = _q(correct=2)
    exam.start_session([q], 10, "sprint")
    attempt = exam._attempts[0]
    for row, bank_index in enumerate(attempt.option_order):
        exam._radio_btns[row].click()
        assert attempt.chosen_index == bank_index
        assert attempt.correct is (bank_index == q.correct_index)
        assert q.options[attempt.chosen_index] == _shown(exam)[row]


def test_the_order_and_the_selection_survive_leaving_and_returning(exam):
    exam.start_session([_q("a"), _q("b")], 10, "sprint")
    first = _shown(exam)
    exam._radio_btns[3].click()
    chosen = exam._attempts[0].chosen_index
    exam._goto(1)
    exam._goto(0)
    assert _shown(exam) == first
    assert [rb.isChecked() for rb in exam._radio_btns] == [False, False, False, True]
    assert exam._attempts[0].chosen_index == chosen


def test_clearing_an_answer_unchecks_every_row(exam):
    exam.start_session([_q()], 10, "sprint")
    exam._radio_btns[1].click()
    exam._on_clear()
    assert exam._attempts[0].chosen_index is None
    assert not any(rb.isChecked() for rb in exam._radio_btns)


def test_the_correct_answer_is_spread_across_the_rows(exam, questions):
    """All 300 bank questions through the real screen: no row is the answer row.

    Each row should hold the answer about 25% of the time.  With n = 300 the
    standard deviation of a row's share is 2.5 points, so 40% is six sigma out
    - a bound that fails on a regression, not on bad luck.
    """
    exam.start_session(list(questions), 90, "full")
    rows = Counter(a.option_order.index(a.question.correct_index)
                   for a in exam._attempts)
    assert set(rows) == {0, 1, 2, 3}
    assert max(rows.values()) / len(questions) < 0.40, dict(rows)


def test_always_picking_the_first_row_fails_a_full_mock(exam):
    """The regression test for the bug itself, end to end.

    Chance on 68 four-option questions is 17 +- 3.6; the pass mark is 47,
    more than eight sigma away.
    """
    random.seed(20261111)
    exam.start_session(build_exam_set(config.EXAM_QUESTION_COUNT),
                       config.EXAM_MINUTES, "full")
    finished = []
    exam.session_finished.connect(finished.append)
    for i in range(len(exam._attempts)):
        exam._goto(i)
        exam._radio_btns[0].click()
    exam._timer.stop()
    exam._finish()

    result = finished[0]
    assert result.total == config.EXAM_QUESTION_COUNT
    assert result.correct < config.PASS_MARK, (
        f"'always A' scored {result.correct}/{result.total}")


# -------------------------------------------------------------- review screen
def test_review_screen_shuffles_and_grades_by_bank_index(qapp, data_dir, monkeypatch):
    from quantum_study.exam_sim import persistence
    from quantum_study.exam_sim.ui.screens import review_screen
    from quantum_study.exam_sim.ui.screens.review_screen import ReviewScreen

    q = _q("only", correct=1)
    monkeypatch.setattr(review_screen, "all_questions", lambda: [q])
    persistence.record_miss(q, 0)

    screen = ReviewScreen()
    try:
        assert screen.start() is True
        seen = set()
        for _ in range(40):                     # re-shown, it does not stay put
            screen._show_current()
            assert sorted(_shown(screen)) == sorted(q.options)
            assert _shown(screen) == [q.options[i] for i in screen._order]
            seen.add(tuple(screen._order))
        assert len(seen) > 1

        # the row holding the right option is graded correct, wherever it is
        screen._show_current()
        screen._radio_btns[screen._order.index(q.correct_index)].click()
        screen._submit_btn.click()
        assert "Correct" in screen._feedback_lbl.text()
        assert persistence.load_missed() == []
    finally:
        _close(screen, qapp)


def test_review_screen_records_the_text_the_learner_actually_chose(
        qapp, data_dir, monkeypatch):
    from quantum_study.exam_sim import persistence
    from quantum_study.exam_sim.ui.screens import review_screen
    from quantum_study.exam_sim.ui.screens.review_screen import ReviewScreen

    q = _q("only", correct=1)
    monkeypatch.setattr(review_screen, "all_questions", lambda: [q])
    persistence.record_miss(q, 0)

    screen = ReviewScreen()
    try:
        assert screen.start() is True
        wrong_bank_index = 3
        row = screen._order.index(wrong_bank_index)
        clicked_text = _shown(screen)[row]
        screen._radio_btns[row].click()
        screen._submit_btn.click()
        assert "Incorrect" in screen._feedback_lbl.text()
        assert clicked_text == "opt-d"
        assert persistence.load_mistakes()[0]["your_answer"] == "opt-d"
        assert persistence.load_mistakes()[0]["correct_answer"] == "opt-b"
    finally:
        _close(screen, qapp)
