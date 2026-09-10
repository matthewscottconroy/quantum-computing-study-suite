"""problems_history.json schema round-trip in a temp dir."""
import json
import time

import persistence
from core.models import AttemptRecord, SessionStats


def _stats(*scores: tuple[str, str, float]) -> SessionStats:
    return SessionStats(attempts=[AttemptRecord(pid, kind, score, title="t")
                                  for pid, kind, score in scores])


def test_save_session_writes_documented_schema(data_dir):
    before = time.time()
    persistence.save_session(_stats(("la_schmidt", "problem", 8.456),
                                    ("deriv_qpe", "derivation", 6.0)))

    path = data_dir / "problems_history.json"
    assert persistence.HISTORY_FILE == path
    raw = json.loads(path.read_text())
    assert len(raw) == 1
    entry = raw[0]
    assert set(entry) >= {"timestamp", "total", "avg_score", "attempts"}
    assert isinstance(entry["timestamp"], float) and entry["timestamp"] >= before - 1
    assert entry["total"] == 2
    assert entry["avg_score"] == round((8.456 + 6.0) / 2, 2)
    expected = [
        {"problem_id": "la_schmidt", "kind": "problem", "score": 8.46},
        {"problem_id": "deriv_qpe", "kind": "derivation", "score": 6.0},
    ]
    assert len(entry["attempts"]) == len(expected)
    for got, want in zip(entry["attempts"], expected):
        assert {k: got[k] for k in want} == want   # documented keys; extras tolerated


def test_empty_session_is_not_saved(data_dir):
    persistence.save_session(SessionStats())
    assert not (data_dir / "problems_history.json").exists()
    assert persistence.load_history() == []


def test_sessions_append_and_load_history_round_trips(data_dir):
    persistence.save_session(_stats(("a", "problem", 1.0)))
    persistence.save_session(_stats(("b", "derivation", 2.0)))
    history = persistence.load_history()
    assert [s["attempts"][0]["problem_id"] for s in history] == ["a", "b"]


def test_corrupt_or_non_list_history_is_empty(data_dir):
    data_dir.mkdir(parents=True)
    persistence.HISTORY_FILE.write_text("{oops")
    assert persistence.load_history() == []
    persistence.HISTORY_FILE.write_text(json.dumps({"not": "a list"}))
    assert persistence.load_history() == []
    persistence.save_session(_stats(("a", "problem", 1.0)))
    assert len(persistence.load_history()) == 1
