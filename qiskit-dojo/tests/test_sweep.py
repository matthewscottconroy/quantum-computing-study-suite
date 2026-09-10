"""Full bank sweep: every solution passes, no starter already passes.

~30 s wall clock (36 katas x 2 subprocess runs), so it is opt-in:
    python -m pytest -m slow tests/test_sweep.py
"""
import pytest

from core.runner import run_kata

pytestmark = pytest.mark.slow


def test_every_solution_passes(katas):
    failures = []
    for kata in katas:
        result = run_kata(kata.solution_code, kata.test_code)
        if not result.passed:
            failures.append(f"{kata.id} [{result.phase}]: {result.output[-200:]}")
    assert not failures, "solutions that do not pass their own tests:\n" + "\n".join(failures)


def test_no_starter_already_passes(katas):
    already_passing = [
        kata.id for kata in katas
        if run_kata(kata.starter_code, kata.test_code).passed
    ]
    assert not already_passing, f"starter code already satisfies tests: {already_passing}"
