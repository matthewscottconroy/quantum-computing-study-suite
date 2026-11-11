"""The correct answer must not be findable by position.

166 of qec-trainer's 170 multiple-choice problems keyed the answer at index 0.  The problem screen used to show the choices in
bank order, so the right answer was almost always row A and the scores said
nothing.  The choices are now shuffled when a problem is shown; these tests
drive the real screen and the real grader, so they fail if either goes back
to speaking in row letters.
"""
from __future__ import annotations

from collections import Counter

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.choices import positional_reference
from core.models import GradeMode, Problem, Verdict
from grading.auto_grader import grade_mc
from problems import all_problems


def _is_mc(p: Problem) -> bool:
    return p.grade_mode == GradeMode.AUTO and bool(p.choices)


def _mc(pid: str = "t", correct: int = 2) -> Problem:
    return Problem(
        id=pid, category="Repetition Code", difficulty="beginner",
        question=f"Question {pid}?", choices=["w", "x", "y", "z"],
        correct_index=correct, explanation="because", grade_mode=GradeMode.AUTO)


@pytest.fixture(scope="module")
def mc_bank() -> list[Problem]:
    return [p for p in all_problems() if _is_mc(p)]


@pytest.fixture
def screen(qapp):
    from ui.screens.problem_screen import ProblemScreen

    s = ProblemScreen()
    s.submitted = []
    s.answer_submitted.connect(lambda p, answer, hints, secs: s.submitted.append(answer))
    yield s
    s._tick_timer.stop()
    s.close()
    s.deleteLater()
    qapp.processEvents()


def _shown(screen) -> list[str]:
    """The choice texts in display order, letter prefix stripped."""
    return [rb.text().split(".  ", 1)[1]
            for rb in screen._radio_btns if not rb.isHidden()]


def _submit_row(screen, row: int) -> str:
    """Pick a display row and submit; returns the letter the screen emitted."""
    screen._radio_btns[row].setChecked(True)
    screen._validate_mc()
    screen._on_submit()
    return screen.submitted[-1]


# ------------------------------------------------------------------- the bank
def test_no_choice_refers_to_another_by_position(mc_bank):
    offenders = {
        p.id: hit
        for p in mc_bank
        for hit in [next(filter(None, map(positional_reference, p.choices)), None)]
        if hit
    }
    assert not offenders, (
        "choices are shuffled when shown, so a choice must not point at "
        f"another by letter or position: {offenders}")


def test_the_correct_choice_is_not_findable_by_length(mc_bank):
    """Shuffling hides position, not length.

    The right choice used to be the longest of the four in 86% of these
    problems, because it was a full definition among one-line distractors.  The
    detail now lives in ``explanation``.  Three things are held here:

    * "pick the longest" (ties split evenly) must score under 40%; chance is 25%;
    * no length rank - shortest, second, third, longest - may hold the answer
      more than 40% of the time, so trimming cannot simply move the tell;
    * the right choice may not stand out by more than 15 characters.
    """
    ranks: Counter = Counter()
    pick_longest = 0.0
    widest = (0, "")
    for p in mc_bank:
        lengths = [len(c) for c in p.choices]
        mine = lengths[p.correct_index]
        ranks[sorted(range(len(lengths)), key=lengths.__getitem__).index(p.correct_index)] += 1
        if mine == max(lengths):
            pick_longest += 1 / lengths.count(mine)
        others = max(n for i, n in enumerate(lengths) if i != p.correct_index)
        widest = max(widest, (mine - others, p.id))
    n = len(mc_bank)
    shares = {rank: round(count / n, 3) for rank, count in sorted(ranks.items())}
    assert pick_longest / n <= 0.40, f"'pick the longest' scores {pick_longest / n:.0%}"
    assert max(shares.values()) <= 0.40, (
        f"share of answers by length rank (0 = shortest): {shares}")
    assert widest[0] <= 15, (
        f"{widest[1]}: the right choice is {widest[0]} characters longer than "
        "every distractor - move the justification into `explanation`")


# ----------------------------------------------------------------- the screen
def test_rows_are_lettered_by_position_and_show_every_choice_once(screen):
    p = _mc()
    screen.show_problem(p, 1, 1)
    assert [rb.text()[:4] for rb in screen._radio_btns] == [
        "A.  ", "B.  ", "C.  ", "D.  "]
    assert sorted(screen._order) == [0, 1, 2, 3]
    assert _shown(screen) == [p.choices[i] for i in screen._order]


def test_the_emitted_letter_is_the_bank_letter_of_the_row_clicked(screen):
    """Every row, graded by the real grader: right exactly where the answer is."""
    p = _mc(correct=2)
    for _ in range(12):                       # several different shuffles
        screen.show_problem(p, 1, 1)
        for row, bank_index in enumerate(screen._order):
            letter = _submit_row(screen, row)
            assert letter == "ABCD"[bank_index]
            attempt = grade_mc(p, letter)
            assert (attempt.verdict is Verdict.CORRECT) is (bank_index == 2)
            assert p.choices[bank_index] == _shown(screen)[row]


def test_reshowing_a_problem_does_not_keep_the_same_order(screen):
    p = _mc()
    orders = set()
    for _ in range(40):
        screen.show_problem(p, 1, 1)
        orders.add(tuple(screen._order))
    assert len(orders) > 1


def test_the_previous_selection_does_not_carry_over(screen):
    """An exclusive button group will not uncheck its checked button, so the
    row picked for one problem used to stay picked for the next."""
    screen.show_problem(_mc("first"), 1, 2)
    _submit_row(screen, 3)
    screen.show_problem(_mc("second"), 2, 2)
    assert not any(rb.isChecked() for rb in screen._radio_btns)
    assert screen._btn_group.checkedId() == -1
    assert not screen._submit_btn.isEnabled()


def test_submitting_with_no_row_picked_emits_nothing(screen):
    screen.show_problem(_mc(), 1, 1)
    screen._on_submit()
    assert screen.submitted == []


def test_the_correct_answer_is_spread_across_the_rows(screen, mc_bank):
    """Every multiple-choice problem through the real screen.

    Each row should hold the answer about 25% of the time.  With n = 150-170
    the standard deviation of a row's share is about 3.4 points, so 45% is
    about six sigma out - a bound that fails on a regression, not on bad luck.  Bank order
    would put 98% of the answers in row A.
    """
    rows: Counter = Counter()
    for p in mc_bank:
        screen.show_problem(p, 1, 1)
        rows[screen._order.index(p.correct_index)] += 1
    assert set(rows) == {0, 1, 2, 3}
    assert max(rows.values()) / len(mc_bank) < 0.45, dict(rows)


def test_always_picking_the_first_row_scores_near_chance(screen, mc_bank):
    """The regression test for the bug itself: chance is 25%, the bank-order
    score was 98%, and 50% is more than seven sigma above chance."""
    correct = 0
    for p in mc_bank:
        screen.show_problem(p, 1, 1)
        if grade_mc(p, _submit_row(screen, 0)).verdict is Verdict.CORRECT:
            correct += 1
    assert correct / len(mc_bank) < 0.50, f"{correct}/{len(mc_bank)}"


# ----------------------------------------------------------------- the grader
def test_wrong_answer_feedback_names_the_right_choice_by_text():
    p = _mc(correct=2)
    feedback = grade_mc(p, "A").feedback
    assert "The right answer was: y" in feedback
    assert "was C" not in feedback and "C:" not in feedback
