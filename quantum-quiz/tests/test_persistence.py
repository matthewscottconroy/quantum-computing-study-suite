"""History / draft persistence round-trips against a temp data dir."""
from __future__ import annotations

import json

import pytest

import persistence
from core.models import Evaluation, Question, QuestionRecord, SessionStats


def _stats(*records: tuple[str, str, int]) -> SessionStats:
    stats = SessionStats(answered=len(records))
    for subject, topic, score in records:
        q = Question(subject=subject, topic=topic, difficulty="beginner",
                     question_type="conceptual explanation", text=f"Q about {topic}")
        e = Evaluation(score=score, verdict="v", feedback="f", model_answer="m")
        stats.history.append(QuestionRecord(q, "my answer", e,
                                            question_id=f"{subject}::{topic}",
                                            elapsed_seconds=25))
    return stats


def test_paths_are_redirected_into_temp_dir(data_dir):
    assert persistence._DATA_DIR == data_dir
    assert persistence._HISTORY_FILE.is_relative_to(data_dir)
    assert persistence._DRAFT_FILE.is_relative_to(data_dir)
    assert not data_dir.exists()


def test_empty_history_yields_empty_results():
    assert persistence._load_raw() == []
    assert persistence.avg_scores_by_subject() == {}
    assert persistence.avg_scores_by_topic() == {}
    assert persistence.question_score_weights() == {}
    assert persistence.has_draft() is False


def test_save_session_round_trip():
    persistence.save_session(_stats(("Qiskit", "SamplerV2", 8), ("QASM", "qelib1", 4)))
    history = json.loads(persistence._HISTORY_FILE.read_text())
    assert len(history) == 1
    s = history[0]
    assert s["answered"] == 2 and s["average_score"] == 6.0
    assert s["date"] and s["timestamp"]
    recs = s["records"]
    assert [r["question_id"] for r in recs] == ["Qiskit::SamplerV2", "QASM::qelib1"]
    assert [(r["subject"], r["topic"], r["score"], r["elapsed_seconds"]) for r in recs] == [
        ("Qiskit", "SamplerV2", 8, 25), ("QASM", "qelib1", 4, 25),
    ]
    persistence.save_session(_stats(("Qiskit", "SamplerV2", 2)))
    assert len(persistence._load_raw()) == 2


def test_draft_round_trip_and_cleared_by_save_session():
    stats = _stats(("Transpiling", "SABRE", 9))
    persistence.save_draft(stats)
    assert persistence.has_draft() is True
    draft = json.loads(persistence._DRAFT_FILE.read_text())
    assert draft["answered"] == 1
    assert draft["questions"][0]["question"] == "Q about SABRE"
    assert draft["questions"][0]["answer"] == "my answer"
    persistence.save_session(stats)
    assert persistence.has_draft() is False
    persistence.save_draft(stats)
    persistence.clear_draft()
    assert persistence.has_draft() is False
    persistence.clear_draft()  # idempotent


def test_time_decayed_averages_by_subject_and_topic():
    persistence.save_session(_stats(("Qiskit", "a", 10), ("Qiskit", "b", 4)))
    persistence.save_session(_stats(("Qiskit", "a", 6), ("QASM", "c", 2)))
    by_subject = persistence.avg_scores_by_subject()
    assert by_subject["Qiskit"] == pytest.approx((10 + 4 + 6) / 3, abs=1e-6)
    assert by_subject["QASM"] == pytest.approx(2.0, abs=1e-6)
    by_topic = persistence.avg_scores_by_topic()
    assert set(by_topic) == {"Qiskit::a", "Qiskit::b", "QASM::c"}
    assert by_topic["Qiskit::a"] == pytest.approx(8.0, abs=1e-6)


def test_question_score_weights_formula():
    persistence.save_session(_stats(("A", "perfect", 10), ("A", "zero", 0), ("A", "mid", 5)))
    w = persistence.question_score_weights()
    assert w["A::perfect"] == pytest.approx(0.5, abs=1e-6)    # floor
    assert w["A::zero"] == pytest.approx(2.0, abs=1e-6)
    assert w["A::mid"] == pytest.approx(1.25, abs=1e-6)


def test_corrupt_history_is_ignored(data_dir):
    data_dir.mkdir(parents=True)
    persistence._HISTORY_FILE.write_text("not json at all")
    assert persistence._load_raw() == []
    assert persistence.avg_scores_by_subject() == {}
    persistence.save_session(_stats(("A", "b", 5)))     # overwrites the corrupt file
    assert len(persistence._load_raw()) == 1


# ── Flag for review (FLAGGING CONTRACT) ───────────────────────────────────────

FLAG_KEYS = {"id", "label", "category", "app", "timestamp"}


def _flag_file() -> list:
    return json.loads(persistence._FLAGGED_FILE.read_text())


def test_flagged_path_is_redirected_and_named_per_contract(data_dir):
    assert persistence._FLAGGED_FILE.is_relative_to(data_dir)
    assert persistence._FLAGGED_FILE.name == "quiz_flagged.json"   # prefix = history prefix
    assert persistence._FLAG_APP == "quantum-quiz"


def test_question_flag_id_is_per_question_and_whitespace_stable():
    a = persistence.question_flag_id("Quantum Mechanics", "the Bloch sphere", "Derive   the\nBloch vector.")
    b = persistence.question_flag_id("Quantum Mechanics", "the Bloch sphere", "Derive the Bloch vector.")
    c = persistence.question_flag_id("Quantum Mechanics", "the Bloch sphere", "State the Bloch vector.")
    assert a == b                                   # same question, different whitespace
    assert a != c                                   # different question, same topic
    assert a.startswith("Quantum Mechanics::the Bloch sphere::")
    assert len(a.rsplit("::", 1)[1]) == 10


def test_toggle_flag_round_trip_matches_contract(data_dir):
    import time
    fid = persistence.question_flag_id("Quantum Mechanics", "the Bloch sphere", "Derive it.")
    long_label = "  Derive   the   Bloch " + "x" * 300
    assert persistence.toggle_flag(fid, long_label, "Quantum Mechanics") is True

    entries = _flag_file()
    assert len(entries) == 1
    e = entries[0]
    assert set(e) == FLAG_KEYS
    assert e["id"] == fid
    assert e["category"] == "Quantum Mechanics"
    assert e["app"] == "quantum-quiz"
    assert isinstance(e["timestamp"], float) and abs(e["timestamp"] - time.time()) < 60
    assert len(e["label"]) <= 100 and e["label"].endswith("…") and "  " not in e["label"]
    assert e["label"] == persistence.make_flag_label(long_label)
    assert persistence.is_flagged(fid) and persistence.flagged_ids() == {fid}
    assert persistence.load_flagged() == entries

    # flag is a toggle: second call removes the entry and reports the new state
    assert persistence.toggle_flag(fid, long_label, "Quantum Mechanics") is False
    assert _flag_file() == [] and not persistence.is_flagged(fid)
    assert persistence.toggle_flag(fid, "again", "Quantum Mechanics") is True
    assert [x["id"] for x in _flag_file()] == [fid]


def test_unflag_removes_only_that_id_and_is_idempotent(data_dir):
    persistence.toggle_flag("a::b::1", "first", "A")
    persistence.toggle_flag("a::b::2", "second", "A")
    persistence.unflag("a::b::1")
    assert [x["id"] for x in _flag_file()] == ["a::b::2"]
    mtime = persistence._FLAGGED_FILE.stat().st_mtime_ns
    persistence.unflag("does-not-exist")            # no rewrite when nothing changes
    assert persistence._FLAGGED_FILE.stat().st_mtime_ns == mtime
    persistence.unflag("a::b::2")
    assert _flag_file() == []


def test_make_flag_label_collapses_and_truncates():
    assert persistence.make_flag_label("  a \n b\t c ") == "a b c"
    assert persistence.make_flag_label("") == ""
    assert persistence.make_flag_label(None) == ""
    exact = "y" * 100
    assert persistence.make_flag_label(exact) == exact
    over = persistence.make_flag_label("word " * 40)
    assert len(over) == 100 and over.endswith("…") and not over.endswith(" …")


def test_load_flagged_tolerates_missing_corrupt_and_malformed(data_dir):
    assert persistence.load_flagged() == [] and persistence.flagged_ids() == set()
    data_dir.mkdir(parents=True)
    persistence._FLAGGED_FILE.write_text("not json")
    assert persistence.load_flagged() == []
    persistence._FLAGGED_FILE.write_text(json.dumps({"id": "not-a-list"}))
    assert persistence.load_flagged() == []
    persistence._FLAGGED_FILE.write_text(json.dumps(
        [{"id": "keep::me", "label": "x"}, {"label": "no id"}, "bare-string", 42, None]
    ))
    assert [x["id"] for x in persistence.load_flagged()] == ["keep::me"]
    assert persistence.is_flagged("keep::me")


def test_toggle_and_unflag_preserve_entries_they_do_not_understand(data_dir):
    data_dir.mkdir(parents=True)
    messy = [{"id": "keep::me", "label": "x"}, {"label": "no id"}, "bare-string", 42]
    persistence._FLAGGED_FILE.write_text(json.dumps(messy))
    persistence.toggle_flag("new::one", "new", "Cat")
    after = _flag_file()
    assert after[:4] == messy and after[4]["id"] == "new::one"     # nothing dropped
    persistence.toggle_flag("new::one", "new", "Cat")
    assert _flag_file() == messy
    persistence.unflag("keep::me")
    assert _flag_file() == messy[1:]                              # only the target removed
    # a corrupt (non-JSON) file cannot be preserved; toggling replaces it cleanly
    persistence._FLAGGED_FILE.write_text("not json")
    assert persistence.toggle_flag("x::y::z", "l", "c") is True
    assert [e["id"] for e in _flag_file()] == ["x::y::z"]
