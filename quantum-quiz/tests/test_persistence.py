"""History / draft persistence round-trips against a temp data dir."""
from __future__ import annotations

import json

import pytest

import common_path  # noqa: F401  (puts the repo root on sys.path)
from common import journal, schema

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
    # Paths resolve at call time from QUANTUM_STUDY_DATA_DIR (common.datadir),
    # so there is no module constant to patch any more.
    assert persistence.data_dir() == data_dir
    assert persistence.history_file().is_relative_to(data_dir)
    assert persistence.draft_file().is_relative_to(data_dir)
    assert persistence.history_file().name == "quiz_history.json"
    assert persistence.draft_file().name == "quiz_draft.json"
    assert not data_dir.exists()


def test_empty_history_yields_empty_results():
    assert persistence._load_raw() == []
    assert persistence.avg_scores_by_subject() == {}
    assert persistence.avg_scores_by_topic() == {}
    assert persistence.question_score_weights() == {}
    assert persistence.has_draft() is False


def test_save_session_round_trip():
    persistence.save_session(_stats(("Qiskit", "SamplerV2", 8), ("QASM", "qelib1", 4)))
    history = json.loads(persistence.history_file().read_text())
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
    draft = json.loads(persistence.draft_file().read_text())
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
    persistence.history_file().write_text("not json at all")
    assert persistence._load_raw() == []
    assert persistence.avg_scores_by_subject() == {}
    persistence.save_session(_stats(("A", "b", 5)))     # overwrites the corrupt file
    assert len(persistence._load_raw()) == 1


# ── Flag for review (FLAGGING CONTRACT) ───────────────────────────────────────

FLAG_KEYS = {"id", "label", "category", "app", "timestamp"}


def _flag_file() -> list:
    return json.loads(persistence.flagged_file().read_text())


def test_flagged_path_is_redirected_and_named_per_contract(data_dir):
    assert persistence.flagged_file().is_relative_to(data_dir)
    assert persistence.flagged_file().name == "quiz_flagged.json"   # prefix = history prefix
    assert persistence.APP_ID == "quantum-quiz"


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
    assert len(e["label"]) <= persistence.FLAG_LABEL_MAX
    assert e["label"].endswith("…") and "  " not in e["label"]
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
    mtime = persistence.flagged_file().stat().st_mtime_ns
    persistence.unflag("does-not-exist")            # no rewrite when nothing changes
    assert persistence.flagged_file().stat().st_mtime_ns == mtime
    persistence.unflag("a::b::2")
    assert _flag_file() == []


def test_make_flag_label_collapses_and_truncates():
    limit = persistence.FLAG_LABEL_MAX
    assert persistence.make_flag_label("  a \n b\t c ") == "a b c"
    assert persistence.make_flag_label("") == ""
    assert persistence.make_flag_label(None) == ""
    exact = "y" * limit
    assert persistence.make_flag_label(exact) == exact
    over = persistence.make_flag_label("word " * 40)
    assert len(over) == limit and over.endswith("…") and not over.endswith(" …")


def test_load_flagged_tolerates_missing_corrupt_and_malformed(data_dir):
    assert persistence.load_flagged() == [] and persistence.flagged_ids() == set()
    data_dir.mkdir(parents=True)
    persistence.flagged_file().write_text("not json")
    assert persistence.load_flagged() == []
    persistence.flagged_file().write_text(json.dumps({"id": "not-a-list"}))
    assert persistence.load_flagged() == []
    persistence.flagged_file().write_text(json.dumps(
        [{"id": "keep::me", "label": "x"}, {"label": "no id"}, "bare-string", 42, None]
    ))
    # common.flags reads the legacy bare-id shape three other apps still write,
    # so a bare string is a flag, not garbage; a row with no id cannot be one.
    assert [x["id"] for x in persistence.load_flagged()] == ["keep::me", "bare-string"]
    assert persistence.is_flagged("keep::me") and persistence.is_flagged("bare-string")
    # every row comes back in the contract shape, whatever it looked like on disk
    for entry in persistence.load_flagged():
        assert set(entry) == FLAG_KEYS and entry["app"] == "quantum-quiz"


def test_toggle_and_unflag_normalise_but_never_lose_a_real_flag(data_dir):
    data_dir.mkdir(parents=True)
    messy = [{"id": "keep::me", "label": "x"}, {"label": "no id"}, "bare-string", 42]
    persistence.flagged_file().write_text(json.dumps(messy))
    persistence.toggle_flag("new::one", "new", "Cat")
    after = _flag_file()
    # Every row that carries an identity survives, upgraded to the contract
    # shape; the two that carry none ({"label": ...} and 42) cannot be flags.
    assert [x["id"] for x in after] == ["keep::me", "bare-string", "new::one"]
    assert all(set(x) == FLAG_KEYS for x in after)
    assert after[0]["label"] == "x" and after[1]["label"] == "bare-string"

    persistence.toggle_flag("new::one", "new", "Cat")
    assert [x["id"] for x in _flag_file()] == ["keep::me", "bare-string"]
    persistence.unflag("keep::me")
    assert [x["id"] for x in _flag_file()] == ["bare-string"]      # only the target
    # a corrupt (non-JSON) file cannot be preserved; toggling replaces it cleanly
    persistence.flagged_file().write_text("not json")
    assert persistence.toggle_flag("x::y::z", "l", "c") is True
    assert [e["id"] for e in _flag_file()] == ["x::y::z"]


# ── Schema versioning, migration and backups ──────────────────────────────────

def _sidecar(path):
    return json.loads(schema.sidecar_path(path).read_text())


def test_every_file_this_app_writes_gets_a_version_sidecar(data_dir):
    persistence.save_session(_stats(("Qiskit", "a", 8)))
    persistence.save_draft(_stats(("Qiskit", "a", 8)))
    persistence.toggle_flag("a::b::1", "first", "A")
    persistence.set_confidence_prompt_enabled(False)
    persistence.log_mistake("m1", "Qiskit", "q", "a", "b")
    persistence.log_confidence("m1", "Qiskit", 3, False)

    for path, kind in [
        (persistence.history_file(), "history"),
        (persistence.draft_file(), persistence.DRAFT_KIND),
        (persistence.flagged_file(), "flagged"),
        (persistence.settings_file(), "settings"),
        (persistence.mistakes_file(), "mistakes"),
        (persistence.confidence_file(), "confidence"),
    ]:
        meta = _sidecar(path)
        assert meta["file"] == path.name and meta["kind"] == kind
        assert meta["schema"] == 1 and meta["written_by"].startswith("common/")
        # the data file itself is still a plain list / object — unchanged shape
        assert isinstance(json.loads(path.read_text()), (list, dict))


def test_an_unmarked_file_is_read_as_v1_and_stamped_on_the_next_write(data_dir):
    data_dir.mkdir(parents=True)
    legacy = [{"date": "2026-01-01", "timestamp": "2026-01-01T00:00:00+00:00",
               "answered": 1, "average_score": 5.0, "records": []}]
    persistence.history_file().write_text(json.dumps(legacy))
    assert not schema.sidecar_path(persistence.history_file()).exists()
    assert persistence.load_history() == legacy          # read, not converted
    assert schema.stored_version(persistence.history_file(), "history") == 1
    persistence.save_session(_stats(("Qiskit", "a", 8)))
    assert _sidecar(persistence.history_file())["schema"] == 1
    assert len(persistence.load_history()) == 2          # the old session kept


def test_a_newer_file_is_refused_not_downgraded(data_dir):
    data_dir.mkdir(parents=True)
    persistence.save_session(_stats(("Qiskit", "a", 8)))
    before = persistence.history_file().read_text()
    meta = schema.sidecar_path(persistence.history_file())
    meta.write_text(json.dumps({**json.loads(meta.read_text()), "schema": 99}))

    with pytest.raises(schema.SchemaTooNewError):
        persistence.save_session(_stats(("QASM", "b", 3)))
    assert persistence.history_file().read_text() == before     # untouched

    # the shared journal turns the same refusal into "nothing happened"
    persistence.log_mistake("m1", "Qiskit", "q", "a", "b")
    mmeta = schema.sidecar_path(persistence.mistakes_file())
    mmeta.write_text(json.dumps({**json.loads(mmeta.read_text()), "schema": 99}))
    rows_before = json.loads(persistence.mistakes_file().read_text())
    journal.clear_write_error()
    persistence.log_mistake("m2", "Qiskit", "q", "a", "b")
    assert json.loads(persistence.mistakes_file().read_text()) == rows_before
    assert isinstance(persistence.journal_write_error(), schema.SchemaTooNewError)
    journal.clear_write_error()


def test_the_previous_contents_are_kept_as_a_rotating_backup(data_dir):
    persistence.save_session(_stats(("Qiskit", "a", 8)))
    first = persistence.history_file().read_text()
    assert not persistence.history_file().with_suffix(".json.bak").exists()

    schema.reset_session()                       # = a new run of the app
    persistence.save_session(_stats(("QASM", "b", 3)))
    bak = schema.backup_paths(persistence.history_file())[0]
    assert bak.read_text() == first              # state this "session" started from

    schema.reset_session()
    persistence.save_session(_stats(("QASM", "c", 4)))
    gens = schema.backup_paths(persistence.history_file())
    assert gens[1].read_text() == first          # aged .bak -> .bak.1
    assert len(json.loads(gens[0].read_text())) == 2

    assert schema.restore_backup(persistence.history_file(), generation=1) is True
    assert persistence.history_file().read_text() == first
