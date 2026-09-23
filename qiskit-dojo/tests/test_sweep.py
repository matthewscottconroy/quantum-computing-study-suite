"""Full bank sweep through the real execution harness (core/runner.py).

For every kata (72+ at last count):

* the reference ``solution_code`` must pass its ``test_code``;
* the ``starter_code`` must NOT already pass - for Debugging and
  Modernization katas that is the whole point (the starter contains a real
  bug / retired API), for the rest the starter is a stub.

Two subprocess runs per kata, roughly 1 s each, so the sweep takes a minute
or two and is opt-in::

    python -m pytest -m slow tests/test_sweep.py
    python -m pytest -m slow tests/test_sweep.py -k "dbg or mod"   # fix-it katas only
    python -m pytest -m slow tests/test_sweep.py --durations=10    # slowest katas

Each kata is its own parametrised case, so a failure names the kata in the
test id instead of burying it in an aggregated message.
"""
from __future__ import annotations

import pytest

from core.runner import run_kata
from katas import all_katas

pytestmark = pytest.mark.slow

# Loaded at collection time so the kata id can be the test id. Module import
# is cheap (kata files only import core.models); nothing runs here.
_KATAS = all_katas()
_IDS = [k.id for k in _KATAS]

# Starters in these sections are deliberately broken and must fail for a
# reason the learner can act on: a failing assertion or an exception from
# their code - never a timeout or a harness crash.
FIX_IT_SECTIONS = {"Debugging", "Modernization"}
ACTIONABLE_FAILURE_PHASES = {"test_failed", "user_error"}


def _tail(text: str, n: int = 800) -> str:
    return text if len(text) <= n else "..." + text[-n:]


@pytest.mark.parametrize("kata", _KATAS, ids=_IDS)
def test_solution_passes(kata):
    result = run_kata(kata.solution_code, kata.test_code)
    assert result.passed, (
        f"{kata.id} ({kata.section}) reference solution failed "
        f"[{result.phase}, {result.duration_secs:.1f}s]:\n{_tail(result.output)}")


@pytest.mark.parametrize("kata", _KATAS, ids=_IDS)
def test_starter_does_not_pass(kata):
    result = run_kata(kata.starter_code, kata.test_code)
    assert not result.passed, (
        f"{kata.id} ({kata.section}) starter code already satisfies its tests")
    if kata.section in FIX_IT_SECTIONS:
        assert result.phase in ACTIONABLE_FAILURE_PHASES, (
            f"{kata.id} ({kata.section}) starter must fail with a test failure or "
            f"a user-code error, got phase={result.phase!r}:\n{_tail(result.output)}")


def test_sweep_covers_every_kata(katas):
    """The parametrised lists above are built at import; make sure they match
    the bank the app actually loads (guards against a stale collection)."""
    assert _IDS == [k.id for k in katas]
    assert {k.section for k in _KATAS} >= FIX_IT_SECTIONS
