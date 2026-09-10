"""TrainerSession bookkeeping and adaptive difficulty (pure logic, no Qt)."""
from __future__ import annotations

import random

from core.models import (
    AnswerFormat, Attempt, Problem, ProblemCategory, SessionStats, TrainerConfig,
)
from core.session import TrainerSession

DIFFS = {"beginner", "intermediate", "advanced"}


def _problem(cat: ProblemCategory) -> Problem:
    return Problem(
        category=cat, difficulty="beginner", question_text="q",
        answer_format=AnswerFormat.MULTIPLE_CHOICE, correct_answer="0",
        choices=["a", "b"], circuit_png=None, aux_circuit_png=None,
        matrix_str=None, state_str=None, solution_steps=["s"], key_concepts=["k"],
    )


def _attempt(cat: ProblemCategory, score: int) -> Attempt:
    return Attempt(_problem(cat), "0", score >= 7, score, "fb")


def test_fixed_difficulty_and_category_queue_respect_config():
    cats = [ProblemCategory.SINGLE_GATE_OUTPUT, ProblemCategory.GATE_SEQUENCE]
    cfg = TrainerConfig(categories=cats, difficulty="advanced", problem_count=6)
    random.seed(1)
    s = TrainerSession(cfg)
    assert s.problem_number() == 1 and not s.is_complete()
    for _ in range(10):                     # beyond the queue it still stays in-config
        assert s.next_category() in cats
        assert s.next_difficulty() == "advanced"
        s.record_skip()
    assert s.is_complete()


def test_record_tallies_correct_partial_wrong_and_accuracy():
    cfg = TrainerConfig(categories=[ProblemCategory.NOISE_CHANNEL], difficulty=None, problem_count=4)
    s = TrainerSession(cfg)
    s.record(_attempt(ProblemCategory.NOISE_CHANNEL, 10))
    s.record(_attempt(ProblemCategory.NOISE_CHANNEL, 5))
    s.record(_attempt(ProblemCategory.NOISE_CHANNEL, 0))
    assert (s.stats.correct, s.stats.partial, s.stats.wrong, s.stats.total) == (1, 1, 1, 3)
    assert s.problem_number() == 4 and not s.is_complete()
    s.record_skip()
    assert s.stats.total == 4 and s.is_complete()
    assert s.stats.accuracy == 0.25


def test_adaptive_difficulty_tracks_accuracy():
    cfg = TrainerConfig(categories=[ProblemCategory.GATE_SEQUENCE], difficulty=None, problem_count=20)
    random.seed(3)
    s = TrainerSession(cfg)
    assert s.next_difficulty() == "beginner"          # < 2 attempts -> warm-up
    s.record(_attempt(ProblemCategory.GATE_SEQUENCE, 10))
    assert s.next_difficulty() == "beginner"
    for _ in range(4):
        s.record(_attempt(ProblemCategory.GATE_SEQUENCE, 10))
    picks = {s.next_difficulty() for _ in range(30)}
    assert picks <= {"advanced", "intermediate"} and "advanced" in picks

    low = TrainerSession(cfg)
    for _ in range(5):
        low.record(_attempt(ProblemCategory.GATE_SEQUENCE, 0))
    picks = {low.next_difficulty() for _ in range(30)}
    assert picks <= {"beginner", "intermediate"} and "beginner" in picks
    assert picks <= DIFFS


def test_session_stats_groups_scores_by_category():
    stats = SessionStats()
    for cat, score in [
        (ProblemCategory.SINGLE_GATE_OUTPUT, 10),
        (ProblemCategory.SINGLE_GATE_OUTPUT, 0),
        (ProblemCategory.ENTANGLEMENT, 5),
    ]:
        stats.attempts.append(_attempt(cat, score))
    grouped = stats.scores_by_category()
    assert grouped[ProblemCategory.SINGLE_GATE_OUTPUT.value] == [10, 0]
    assert grouped[ProblemCategory.ENTANGLEMENT.value] == [5]
    assert stats.accuracy == 0.0            # total never incremented -> guarded
