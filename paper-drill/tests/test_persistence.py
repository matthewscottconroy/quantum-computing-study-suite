"""Persistence round-trips against a temp dir (never the real data dir)."""
import json
from datetime import datetime

import pytest

import persistence
from core.models import SessionStats


def test_save_session_creates_dir_and_writes_schema(data_dir):
    stats = SessionStats(title="Paper A", total=3, scores=[10, 7, 4])
    persistence.save_session(stats)

    history = data_dir / "paper_history.json"
    assert persistence.HISTORY_FILE == history
    assert history.exists()
    entries = json.loads(history.read_text())
    assert len(entries) == 1
    entry = entries[0]
    assert set(entry) >= {"title", "total", "average", "scores"}
    assert entry["title"] == "Paper A"
    assert entry["total"] == 3
    assert entry["scores"] == [10, 7, 4]
    assert entry["average"] == pytest.approx(7.0)


def test_save_session_appends_in_order(data_dir):
    persistence.save_session(SessionStats(title="one", total=1, scores=[5]))
    persistence.save_session(SessionStats(title="two", total=1, scores=[9]))
    assert [e["title"] for e in persistence._load_raw()] == ["one", "two"]


def test_corrupt_history_is_treated_as_empty(data_dir):
    data_dir.mkdir(parents=True)
    persistence.HISTORY_FILE.write_text("{not json")
    assert persistence._load_raw() == []
    persistence.save_session(SessionStats(title="x", total=1, scores=[1]))
    assert len(persistence._load_raw()) == 1


def test_library_save_load_delete_round_trip(data_dir):
    assert persistence.load_library() == []

    pid1 = persistence.save_paper("Title 1", "text one", 5)
    pid2 = persistence.save_paper("Title 2", "text two", 8)
    assert pid1 != pid2
    assert len(pid1) == 8

    library = persistence.load_library()
    assert [p["id"] for p in library] == [pid1, pid2]
    paper = library[0]
    assert set(paper) >= {"id", "title", "text", "q_count", "saved_at"}
    assert (paper["title"], paper["text"], paper["q_count"]) == ("Title 1", "text one", 5)
    datetime.fromisoformat(paper["saved_at"])  # ISO-8601 timestamp

    persistence.delete_paper(pid1)
    assert [p["id"] for p in persistence.load_library()] == [pid2]
    persistence.delete_paper("no-such-id")  # unknown id is a no-op
    assert len(persistence.load_library()) == 1
    assert (data_dir / "paper_library.json").exists()


def test_corrupt_library_is_treated_as_empty(data_dir):
    data_dir.mkdir(parents=True)
    persistence.LIBRARY_FILE.write_text("[1, 2")
    assert persistence.load_library() == []
