"""History screen: flagged-for-review list (newest first, Unflag) and stat cards."""
from __future__ import annotations

import json
import time

import pytest

import persistence
from core.models import Evaluation, Question, QuestionRecord, SessionStats


def _seed_flags(entries: list) -> None:
    persistence._FLAGGED_FILE.parent.mkdir(parents=True, exist_ok=True)
    persistence._FLAGGED_FILE.write_text(json.dumps(entries))


def _flag_file() -> list:
    return json.loads(persistence._FLAGGED_FILE.read_text())


def _stats(*records: tuple[str, str, int]) -> SessionStats:
    stats = SessionStats(answered=len(records))
    for subject, topic, score in records:
        q = Question(subject=subject, topic=topic, difficulty="beginner",
                     question_type="conceptual explanation", text=f"Q about {topic}")
        e = Evaluation(score=score, verdict="v", feedback="f", model_answer="m")
        stats.history.append(QuestionRecord(q, "ans", e, question_id=f"{subject}::{topic}"))
    return stats


@pytest.fixture
def screen(qapp):
    from ui.screens.history_screen import HistoryScreen
    s = HistoryScreen()
    s.resize(1000, 700)
    s.show()
    yield s
    s.close()


def test_flagged_list_is_newest_first_and_unflag_rewrites_file(screen, qapp):
    now = time.time()
    older = {"id": "A::a::1111111111", "label": "Older question", "category": "Qiskit",
             "app": "quantum-quiz", "timestamp": now - 3600}
    newer = {"id": "B::b::2222222222", "label": "Newer question", "category": "QASM",
             "app": "quantum-quiz", "timestamp": now}
    _seed_flags([older, newer])

    screen.refresh()
    qapp.processEvents()
    assert screen.flagged_labels() == ["Newer question", "Older question"]
    assert screen._flag_count_lbl.text() == "2 flagged"
    assert [r.flag_id for r in screen._flagged_rows] == [newer["id"], older["id"]]

    screen._flagged_rows[0]._unflag_btn.click()          # unflag the newest
    qapp.processEvents()
    assert _flag_file() == [older]
    assert screen.flagged_labels() == ["Older question"]
    assert screen._flag_count_lbl.text() == "1 flagged"

    screen._flagged_rows[0]._unflag_btn.click()
    qapp.processEvents()
    assert _flag_file() == []
    assert screen.flagged_labels() == [] and screen._flag_count_lbl.text() == ""


def test_flagged_list_handles_missing_corrupt_and_malformed_files(screen, data_dir):
    screen.refresh()                                     # no file at all
    assert screen.flagged_labels() == [] and screen._flag_count_lbl.text() == ""

    data_dir.mkdir(parents=True, exist_ok=True)
    persistence._FLAGGED_FILE.write_text("not json")
    screen.refresh()
    assert screen.flagged_labels() == []

    _seed_flags([{"id": "only::id"}, {"label": "no id"}, "junk", 7,
                 {"id": "x::y::z", "label": "Labelled", "timestamp": "not-a-number"}])
    screen.refresh()
    # entries without an id are not shown; an id without a label falls back to the id
    assert screen.flagged_labels() == ["Labelled", "only::id"]
    assert screen._flag_count_lbl.text() == "2 flagged"


def test_stat_cards_and_charts_reflect_saved_sessions(screen, qapp):
    screen.refresh()
    assert screen._sessions_card._val.text() == "0"
    assert screen._questions_card._val.text() == "0"
    assert screen._avg_card._val.text() == "—"
    assert not screen._empty_lbl.isHidden()

    persistence.save_session(_stats(("Qiskit", "a", 8), ("QASM", "b", 4)))
    persistence.save_session(_stats(("Qiskit", "c", 9)))
    screen.refresh()
    qapp.processEvents()
    assert screen._sessions_card._val.text() == "2"
    assert screen._questions_card._val.text() == "3"
    assert screen._avg_card._val.text() == "7.5/10"      # mean of session averages 6.0 and 9.0
    assert screen._empty_lbl.isHidden()
    assert screen._trend_slot.count() == 1 and screen._subj_slot.count() == 1
