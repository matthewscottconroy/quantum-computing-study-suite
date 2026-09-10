"""History / flag persistence round-trips against a temp data dir."""
from __future__ import annotations

import json
import time

import pytest

import persistence.storage as storage
from core.models import CardResult, Rating, SessionStats


def _stats(*ratings: Rating, category: str = "Algorithms") -> SessionStats:
    stats = SessionStats(total=len(ratings))
    for i, r in enumerate(ratings):
        stats.results.append(CardResult(card_id=f"card_{i}", category=category, rating=r))
        if r is Rating.GOT_IT:
            stats.got_it += 1
        elif r is Rating.UNSURE:
            stats.unsure += 1
        else:
            stats.missed += 1
    return stats


def test_paths_are_redirected_into_temp_dir(data_dir):
    assert storage.HISTORY_FILE.is_relative_to(data_dir)
    assert storage.DATA_DIR == data_dir
    assert not storage.HISTORY_FILE.exists()


def test_save_session_round_trip(data_dir):
    save = _stats(Rating.GOT_IT, Rating.UNSURE, Rating.MISSED)
    storage.save_session(save)

    assert storage.HISTORY_FILE.exists()
    sessions = json.loads(storage.HISTORY_FILE.read_text())
    assert len(sessions) == 1
    s = sessions[0]
    assert (s["total"], s["got_it"], s["unsure"], s["missed"]) == (3, 1, 1, 1)
    assert isinstance(s["timestamp"], float)
    ratings = {r["card_id"]: r["rating"] for r in s["results"]}
    assert ratings == {"card_0": "got_it", "card_1": "unsure", "card_2": "missed"}
    assert all(r["category"] == "Algorithms" for r in s["results"])
    assert storage._load_raw() == sessions


def test_save_session_appends():
    storage.save_session(_stats(Rating.GOT_IT))
    storage.save_session(_stats(Rating.MISSED, Rating.MISSED))
    assert len(storage._load_raw()) == 2


def test_lifetime_stats():
    assert storage.lifetime_stats() == {"sessions": 0, "cards": 0, "pct_known": 0.0}
    storage.save_session(_stats(Rating.GOT_IT, Rating.GOT_IT, Rating.MISSED))
    storage.save_session(_stats(Rating.GOT_IT, Rating.MISSED))
    lt = storage.lifetime_stats()
    assert lt["sessions"] == 2
    assert lt["cards"] == 5
    assert lt["pct_known"] == pytest.approx(3 / 5)


def test_card_weights_formula():
    assert storage.card_weights() == {}
    storage.save_session(_stats(Rating.GOT_IT, Rating.UNSURE, Rating.MISSED))
    w = storage.card_weights()
    assert w["card_0"] == pytest.approx(0.1)   # always known → floor
    assert w["card_1"] == pytest.approx(0.5)
    assert w["card_2"] == pytest.approx(1.0)   # always missed → max
    assert "card_99" not in w


def test_card_weights_average_across_sessions():
    storage.save_session(_stats(Rating.GOT_IT))
    storage.save_session(_stats(Rating.MISSED))
    # Both sessions are "now", so equal time weights → ease 0.5 → weight 0.5
    assert storage.card_weights()["card_0"] == pytest.approx(0.5, abs=1e-6)


def test_corrupt_history_is_ignored(data_dir):
    data_dir.mkdir(parents=True)
    storage.HISTORY_FILE.write_text("{ this is not json")
    assert storage._load_raw() == []
    assert storage.lifetime_stats()["sessions"] == 0
    assert storage.card_weights() == {}


def test_flag_round_trip(data_dir):
    assert not storage.load_flagged()
    assert storage.toggle_flag("alg_x") is True
    assert "alg_x" in storage.load_flagged()
    assert storage.toggle_flag("alg_x") is False
    assert "alg_x" not in storage.load_flagged()

    storage.save_flagged({"b", "a", "c"})
    assert set(storage.load_flagged()) == {"a", "b", "c"}
    assert any(p.is_file() for p in data_dir.iterdir()), "flags were not written to the temp data dir"


def test_flag_entries_follow_the_flagging_contract(data_dir):
    """flagged_cards.json holds {"id","label","category","app","timestamp"} dicts."""
    from cards import all_cards

    card = all_cards()[0]
    before = time.time()
    assert storage.toggle_flag(card.id) is True
    raw = json.loads(storage._FLAGGED_FILE.read_text())
    assert isinstance(raw, list) and len(raw) == 1
    entry = raw[0]
    assert set(entry) == {"id", "label", "category", "app", "timestamp"}
    assert entry["id"] == card.id
    assert entry["label"] == card.front
    assert entry["category"] == card.category
    assert entry["app"] == "flashcard-drill"
    assert before <= entry["timestamp"] <= time.time()

    # An id with no card still gets a well-formed entry (label falls back to the id).
    storage.toggle_flag("ghost_card")
    ghost = json.loads(storage._FLAGGED_FILE.read_text())[1]
    assert ghost["id"] == ghost["label"] == "ghost_card" and ghost["category"] == ""

    # Toggle again removes exactly that entry; the other keeps its timestamp.
    assert storage.toggle_flag(card.id) is False
    raw = json.loads(storage._FLAGGED_FILE.read_text())
    assert [e["id"] for e in raw] == ["ghost_card"]
    assert raw[0]["timestamp"] == ghost["timestamp"]


def test_legacy_bare_id_flag_file_is_read_and_upgraded(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    storage._FLAGGED_FILE.write_text(json.dumps(["old_a", "old_b", "old_a", "", 7]))
    assert storage.load_flagged() == {"old_a", "old_b"}
    entries = storage.load_flagged_entries()
    assert [e["id"] for e in entries] == ["old_a", "old_b"]
    assert all(e["app"] == "flashcard-drill" for e in entries)

    storage.toggle_flag("new_c")
    raw = json.loads(storage._FLAGGED_FILE.read_text())
    assert [e["id"] for e in raw] == ["old_a", "old_b", "new_c"]
    assert all(set(e) == {"id", "label", "category", "app", "timestamp"} for e in raw)


def test_save_flagged_preserves_existing_entries(data_dir):
    storage.toggle_flag("keep_me")
    ts = storage.load_flagged_entries()[0]["timestamp"]
    storage.save_flagged({"keep_me", "added"})
    entries = {e["id"]: e for e in storage.load_flagged_entries()}
    assert set(entries) == {"keep_me", "added"}
    assert entries["keep_me"]["timestamp"] == ts
    storage.save_flagged(set())
    assert storage.load_flagged() == set()
    assert json.loads(storage._FLAGGED_FILE.read_text()) == []


def test_corrupt_flag_file_is_ignored(data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    storage._FLAGGED_FILE.write_text("{ nope")
    assert storage.load_flagged() == set()
    storage._FLAGGED_FILE.write_text(json.dumps({"id": "not-a-list"}))
    assert storage.load_flagged() == set()


def test_save_session_records_elapsed_secs_when_present(data_dir):
    stats = SessionStats(total=2, got_it=2)
    stats.results.append(CardResult("c0", "Algorithms", Rating.GOT_IT, elapsed_secs=3.456))
    stats.results.append(CardResult("c1", "Algorithms", Rating.GOT_IT))
    storage.save_session(stats)
    results = storage._load_raw()[0]["results"]
    assert results[0]["elapsed_secs"] == 3.46
    assert "elapsed_secs" not in results[1]
