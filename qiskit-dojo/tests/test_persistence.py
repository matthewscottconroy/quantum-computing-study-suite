"""Persistence writes the documented dojo_history.json schema (temp dir only)."""
import json
import time

import pytest

import persistence
from core.models import Kata, KataAttempt, SessionStats


def _kata(kid: str, section: str) -> Kata:
    return Kata(id=kid, section=section, title="t", difficulty="beginner",
                prompt="p", starter_code="", test_code="", solution_code="")


def _session(*attempts: tuple[str, str, bool, int]) -> SessionStats:
    return SessionStats(attempts=[
        KataAttempt(_kata(kid, sec), passed=passed, tries=tries)
        for kid, sec, passed, tries in attempts
    ])


def test_save_session_writes_documented_schema(data_dir):
    before = time.time()
    persistence.save_session(_session(("a1", "Sampler", True, 1),
                                      ("b2", "Estimator", False, 3)))

    path = data_dir / "dojo_history.json"
    assert persistence.HISTORY_FILE == path
    raw = json.loads(path.read_text())
    assert len(raw) == 1
    entry = raw[0]
    assert set(entry) >= {"timestamp", "total", "passed", "attempts"}
    assert isinstance(entry["timestamp"], float)
    assert entry["timestamp"] >= before - 1
    assert entry["total"] == 2
    assert entry["passed"] == 1
    expected = [
        {"kata_id": "a1", "section": "Sampler", "passed": True, "tries": 1},
        {"kata_id": "b2", "section": "Estimator", "passed": False, "tries": 3},
    ]
    assert len(entry["attempts"]) == len(expected)
    for got, want in zip(entry["attempts"], expected):
        assert {k: got[k] for k in want} == want   # documented keys; extras tolerated


def test_save_session_appends(data_dir):
    persistence.save_session(_session(("a1", "Sampler", True, 1)))
    persistence.save_session(_session(("a2", "Sampler", False, 2)))
    raw = persistence._load_raw()
    assert [s["attempts"][0]["kata_id"] for s in raw] == ["a1", "a2"]


def test_corrupt_history_is_treated_as_empty(data_dir):
    data_dir.mkdir(parents=True)
    persistence.HISTORY_FILE.write_text("not json at all")
    assert persistence._load_raw() == []
    assert persistence.pass_rates_by_section() == {}
    assert persistence.kata_weights() == {}


def test_pass_rates_by_section(data_dir):
    persistence.save_session(_session(("s1", "Sampler", True, 1),
                                      ("s2", "Sampler", False, 2),
                                      ("e1", "Estimator", True, 1)))
    persistence.save_session(_session(("s1", "Sampler", True, 1)))
    rates = persistence.pass_rates_by_section()
    assert rates["Sampler"] == pytest.approx(2 / 3)
    assert rates["Estimator"] == pytest.approx(1.0)
    assert set(rates) == {"Sampler", "Estimator"}


def test_kata_weights_never_passed_vs_solid(data_dir):
    persistence.save_session(_session(("never", "Sampler", False, 3),
                                      ("solid", "Sampler", True, 1)))
    weights = persistence.kata_weights()
    assert weights["never"] == pytest.approx(2.0)
    assert weights["solid"] == pytest.approx(0.5)
    assert all(0.5 <= w <= 2.0 for w in weights.values())


def test_kata_weights_use_last_three_results(data_dir):
    for passed in (False, False, False, True, True, True):
        persistence.save_session(_session(("k", "Sampler", passed, 1)))
    assert persistence.kata_weights()["k"] == pytest.approx(0.5)
    persistence.save_session(_session(("k", "Sampler", False, 1)))
    # window is now [True, True, False] -> rate 2/3 -> 2.0 - 1.0 = 1.0
    assert persistence.kata_weights()["k"] == pytest.approx(1.0)
