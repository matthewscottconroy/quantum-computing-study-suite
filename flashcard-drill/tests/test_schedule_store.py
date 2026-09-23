"""flashcard_schedule.json: round-trips, migration from history, failure modes.

The load-bearing constraint is that this is a *new* file: flashcard_history.json
and flagged_cards.json (parsed by coach.py / dashboard.py) must come out of every
schedule operation byte-for-byte unchanged.
"""
from __future__ import annotations

import json
import time
from datetime import date, timedelta

import pytest

import config
import persistence.schedule_store as store
import persistence.storage as storage
from core.models import CardResult, Rating, SessionStats
from core.scheduler import CardState, Grade, review

TODAY = date(2026, 9, 16)


def _session(ratings: dict[str, str], when: date, category: str = "Algorithms") -> None:
    stats = SessionStats(total=len(ratings))
    for card_id, rating in ratings.items():
        stats.results.append(CardResult(card_id=card_id, category=category, rating=rating))
        if rating == "got_it":
            stats.got_it += 1
        elif rating == "unsure":
            stats.unsure += 1
        else:
            stats.missed += 1
    storage.save_session(stats)
    # Re-date the session we just appended (save_session stamps "now").
    sessions = json.loads(storage.HISTORY_FILE.read_text())
    sessions[-1]["timestamp"] = time.mktime(when.timetuple())
    storage.HISTORY_FILE.write_text(json.dumps(sessions, indent=2))


# ---------------------------------------------------------------------------
# Location / isolation
# ---------------------------------------------------------------------------

def test_schedule_lives_in_the_data_dir_under_its_own_name(data_dir):
    assert store.schedule_path() == data_dir / "flashcard_schedule.json"
    assert store.schedule_path() == config.SCHEDULE_FILE
    assert not store.schedule_exists()
    assert store.load_states() == {}


def test_recording_a_rating_creates_only_the_schedule_file(data_dir):
    outcome = store.record_rating("card_a", Rating.GOT_IT, TODAY)
    assert outcome is not None and outcome.after.interval_days == 1
    assert store.schedule_exists()
    assert not storage.HISTORY_FILE.exists()
    assert not storage._FLAGGED_FILE.exists()
    assert [p.name for p in data_dir.iterdir()] == ["flashcard_schedule.json"]


def test_on_disk_shape_matches_the_documented_schema(data_dir):
    store.record_rating("card_a", "got_it", TODAY)
    store.record_rating("card_a", "got_it", TODAY + timedelta(days=1))
    raw = json.loads(store.schedule_path().read_text())
    assert list(raw) == ["card_a"]
    entry = raw["card_a"]
    assert set(entry) == {"n", "ef", "interval_days", "due_iso", "last_seen_iso", "lapses"}
    assert entry == {"n": 2, "ef": 2.5, "interval_days": 6,
                     "due_iso": "2026-09-23", "last_seen_iso": "2026-09-17", "lapses": 0}


def test_save_and_load_round_trip(data_dir):
    states = {
        "a": review(CardState("a"), Grade.GOOD, TODAY),
        "b": review(CardState("b"), Grade.AGAIN, TODAY),
        "c": CardState("c"),
    }
    store.save_states(states)
    assert store.load_states() == states


def test_ratings_accumulate_across_calls(data_dir):
    for day, rating in enumerate(["got_it", "got_it", "unsure", "missed"]):
        store.record_rating("card_a", rating, TODAY + timedelta(days=day))
    state = store.state_for("card_a")
    assert state.n == 0 and state.lapses == 1          # the miss reset it
    assert state.interval_days == 1
    assert state.ef == pytest.approx(2.15)             # 2.5 +.1 +.1 (capped) -.15 -.2
    assert state.due == TODAY + timedelta(days=4)


def test_other_cards_are_untouched_by_one_rating(data_dir):
    store.save_states({"keep": review(CardState("keep"), Grade.GOOD, TODAY)})
    store.record_rating("other", "missed", TODAY)
    states = store.load_states()
    assert set(states) == {"keep", "other"}
    assert states["keep"] == review(CardState("keep"), Grade.GOOD, TODAY)


# ---------------------------------------------------------------------------
# Migration (first run with history, no schedule)
# ---------------------------------------------------------------------------

def test_bootstrap_replays_history_into_a_schedule(data_dir):
    _session({"old_card": "got_it"}, TODAY - timedelta(days=30))
    _session({"old_card": "got_it", "hard_card": "unsure"}, TODAY - timedelta(days=20))
    _session({"missed_card": "missed"}, TODAY - timedelta(days=2))
    before = storage.HISTORY_FILE.read_bytes()

    assert not store.schedule_exists()
    states = store.ensure_states(TODAY)

    assert set(states) == {"old_card", "hard_card", "missed_card"}
    # Two Goods -> n=2, 6-day interval measured from the day it was answered.
    assert states["old_card"].n == 2
    assert states["old_card"].interval_days == 6
    assert states["old_card"].due == TODAY - timedelta(days=14)     # overdue: due now
    assert states["hard_card"].ef == pytest.approx(2.35)
    assert states["missed_card"].interval_days == 1

    # Migration is persisted, and history is byte-for-byte untouched.
    assert store.schedule_exists()
    assert store.load_states() == states
    assert storage.HISTORY_FILE.read_bytes() == before


def test_bootstrap_runs_once_and_then_the_file_wins(data_dir):
    _session({"card_a": "got_it"}, TODAY - timedelta(days=5))
    first = store.ensure_states(TODAY)
    assert set(first) == {"card_a"}

    _session({"card_b": "got_it"}, TODAY)          # later session, schedule already exists
    again = store.ensure_states(TODAY)
    assert set(again) == {"card_a"}                # not re-derived from history


def test_no_history_means_no_schedule_file_yet(data_dir):
    assert store.ensure_states(TODAY) == {}
    assert not store.schedule_exists()              # setup screen keeps free drill as default


@pytest.mark.parametrize("sessions", [
    "not a list",
    [],
    [{"results": "nope"}],
    [{"results": [{"card_id": "a"}]}],                       # no rating
    [{"results": [{"rating": "got_it"}]}],                   # no card id
    [{"results": [{"card_id": "a", "rating": "shrug"}]}],    # unknown rating
    [{"results": [{"card_id": "", "rating": "got_it"}]}],
    [{"timestamp": "yesterday", "results": [{"card_id": "a", "rating": "got_it"}]}],
    [{"timestamp": 10 ** 18, "results": [{"card_id": "a", "rating": "got_it"}]}],
    [None, 42, {"results": [None, 42]}],
])
def test_bootstrap_survives_malformed_history(data_dir, sessions):
    states = store.bootstrap_states(sessions if isinstance(sessions, list) else [], TODAY)
    assert all(isinstance(s, CardState) for s in states.values())
    for st in states.values():
        assert st.due is not None and st.due <= TODAY + timedelta(days=400)


def test_bootstrap_never_dates_a_review_in_the_future(data_dir):
    _session({"card_a": "got_it"}, TODAY + timedelta(days=900))   # clock skew
    states = store.ensure_states(TODAY)
    assert states["card_a"].last_seen == TODAY


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", ["", "{", "null", "[1, 2, 3]", '"a string"', '{"a": 5}'])
def test_corrupt_schedule_reads_as_empty_and_is_repaired_on_write(data_dir, text):
    data_dir.mkdir(parents=True, exist_ok=True)
    store.schedule_path().write_text(text)
    assert store.load_states() in ({}, {"a": CardState("a")})

    assert store.record_rating("card_a", "got_it", TODAY) is not None
    states = store.load_states()
    assert states["card_a"].interval_days == 1


def test_unwritable_schedule_never_raises_into_a_drill(data_dir, monkeypatch):
    data_dir.mkdir(parents=True, exist_ok=True)
    blocker = data_dir / "not-a-dir"
    blocker.write_text("")                       # a *file* where a directory is needed
    monkeypatch.setattr(config, "SCHEDULE_FILE", blocker / "flashcard_schedule.json")
    assert store.load_states() == {}
    assert store.record_rating("card_a", "got_it", TODAY) is None


def test_blank_card_ids_are_ignored(data_dir):
    assert store.record_rating("", "got_it", TODAY) is None
    assert store.record_rating("   ", "got_it", TODAY) is None
    assert store.record_rating(None, "got_it", TODAY) is None
    assert not store.schedule_exists()


def test_unknown_rating_is_not_persisted(data_dir):
    assert store.record_rating("card_a", "brilliant", TODAY) is None
    assert store.load_states() == {}
