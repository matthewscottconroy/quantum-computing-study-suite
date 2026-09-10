"""exam_history.json / exam_missed.json round-trips in a temp dir."""
import json
import time

import persistence
from core.models import ExamAttempt, ExamResult, Question

HISTORY_KEYS = {"timestamp", "mode", "total", "correct", "duration_secs", "sections"}
MISSED_KEYS = {"question_id", "section", "question", "correct_answer", "chosen", "timestamp"}


def _q(qid: str, section: str = "Sampler", correct: int = 1) -> Question:
    return Question(id=qid, section=section, question=f"Question {qid}?",
                    options=["opt-a", "opt-b", "opt-c", "opt-d"], correct_index=correct,
                    explanation="because", difficulty="easy")


def _result(mode: str = "sprint") -> ExamResult:
    return ExamResult(mode=mode, attempts=[
        ExamAttempt(_q("s1", "Sampler"), chosen_index=1),
        ExamAttempt(_q("s2", "Sampler"), chosen_index=3),
        ExamAttempt(_q("e1", "Estimator"), chosen_index=None),
    ], duration_secs=42.0)


def test_save_result_writes_history_schema(data_dir):
    before = time.time()
    persistence.save_result(_result("full"))

    path = data_dir / "exam_history.json"
    assert persistence.HISTORY_FILE == path
    history = json.loads(path.read_text())
    assert len(history) == 1
    entry = history[0]
    assert set(entry) >= HISTORY_KEYS
    assert isinstance(entry["timestamp"], float) and entry["timestamp"] >= before - 1
    assert entry["mode"] == "full"
    assert (entry["total"], entry["correct"]) == (3, 1)
    assert entry["duration_secs"] == 42.0
    assert entry["sections"] == {
        "Sampler": {"total": 2, "correct": 1},
        "Estimator": {"total": 1, "correct": 0},
    }


def test_history_appends_and_load_history_round_trips(data_dir):
    assert persistence.load_history() == []
    persistence.save_result(_result("sprint"))
    persistence.save_result(_result("full"))
    assert [e["mode"] for e in persistence.load_history()] == ["sprint", "full"]


def test_record_miss_writes_missed_schema(data_dir):
    persistence.record_miss(_q("s2"), chosen_index=3)
    missed = json.loads((data_dir / "exam_missed.json").read_text())
    assert len(missed) == 1
    entry = missed[0]
    assert set(entry) >= MISSED_KEYS
    assert entry["question_id"] == "s2"
    assert entry["section"] == "Sampler"
    assert entry["question"] == "Question s2?"
    assert entry["correct_answer"] == "opt-b"
    assert entry["chosen"] == "opt-d"
    assert isinstance(entry["timestamp"], float)


def test_record_miss_dedupes_by_question_id(data_dir):
    persistence.record_miss(_q("s2"), chosen_index=3)
    first_ts = persistence.load_missed()[0]["timestamp"]
    persistence.record_miss(_q("other"), chosen_index=0)
    persistence.record_miss(_q("s2"), chosen_index=2)

    missed = persistence.load_missed()
    assert [e["question_id"] for e in missed] == ["other", "s2"]  # latest miss moves last
    s2 = missed[-1]
    assert s2["chosen"] == "opt-c"
    assert s2["timestamp"] >= first_ts


def test_record_miss_unanswered_has_empty_chosen(data_dir):
    persistence.record_miss(_q("e1"), chosen_index=None)
    assert persistence.load_missed()[0]["chosen"] == ""


def test_resolve_missed_removes_only_target(data_dir):
    persistence.record_miss(_q("a"), 0)
    persistence.record_miss(_q("b"), 0)
    persistence.resolve_missed("a")
    assert [e["question_id"] for e in persistence.load_missed()] == ["b"]
    persistence.resolve_missed("never-missed")  # no-op
    assert [e["question_id"] for e in persistence.load_missed()] == ["b"]


def test_record_misses_records_only_incorrect_attempts(data_dir):
    persistence.record_misses(_result())
    assert sorted(e["question_id"] for e in persistence.load_missed()) == ["e1", "s2"]


def test_corrupt_or_non_list_files_are_treated_as_empty(data_dir):
    data_dir.mkdir(parents=True)
    persistence.HISTORY_FILE.write_text("{oops")
    persistence.MISSED_FILE.write_text(json.dumps({"not": "a list"}))
    assert persistence.load_history() == []
    assert persistence.load_missed() == []
