"""Pure scoring functions: points-weighted problem score, derivation score."""
import pytest

from core.models import (AttemptRecord, GradeResult, Part, PartState, SessionStats,
                         Step, StepState, derivation_score, problem_score)


def _part(pid: str, points: int) -> Part:
    return Part(part_id=pid, prompt="p", points=points, rubric=["r"], model_solution="m")


def _state(points: int, score: int | None) -> PartState:
    result = GradeResult(score=score, feedback="") if score is not None else None
    return PartState(part=_part("x", points), result=result)


def _step_state(accepted: bool, revealed: bool = False) -> StepState:
    step = Step(step_id="s", prompt="p", expected="e", hint="h", model_step="m")
    return StepState(step=step, accepted=accepted, model_revealed=revealed)


def test_problem_score_is_points_weighted():
    states = [_state(3, 10), _state(3, 0), _state(4, 5)]
    # earned = 3*1.0 + 3*0.0 + 4*0.5 = 5 of 10 points -> 5.0 / 10
    assert problem_score(states) == pytest.approx(5.0)


def test_problem_score_extremes_and_rounding():
    assert problem_score([_state(3, 10), _state(7, 10)]) == 10.0
    assert problem_score([_state(3, 0), _state(7, 0)]) == 0.0
    assert problem_score([_state(1, 10), _state(2, 0)]) == pytest.approx(3.33)


def test_problem_score_ungraded_parts_count_zero():
    assert problem_score([_state(5, 10), _state(5, None)]) == pytest.approx(5.0)
    assert _state(5, None).score == 0


def test_problem_score_empty_or_zero_points():
    assert problem_score([]) == 0.0
    assert problem_score([_state(0, 10)]) == 0.0


def test_derivation_score_counts_only_clean_accepts():
    states = [
        _step_state(True), _step_state(True), _step_state(True),
        _step_state(True, revealed=True),   # accepted only after the reveal
        _step_state(False),
    ]
    assert derivation_score(states) == pytest.approx(6.0)


def test_derivation_score_extremes_and_rounding():
    assert derivation_score([]) == 0.0
    assert derivation_score([_step_state(True)] * 4) == 10.0
    assert derivation_score([_step_state(False, revealed=True)] * 3) == 0.0
    assert derivation_score([_step_state(True), _step_state(False), _step_state(False)]) == pytest.approx(3.33)


def test_session_stats_average():
    assert SessionStats().avg_score == 0.0
    stats = SessionStats(attempts=[
        AttemptRecord("p1", "problem", 8.0),
        AttemptRecord("d1", "derivation", 4.0),
    ])
    assert stats.total == 2
    assert stats.avg_score == pytest.approx(6.0)
