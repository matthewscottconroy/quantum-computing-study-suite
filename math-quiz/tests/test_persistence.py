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
                     question_type="calculation", text=f"Q about {topic}")
        e = Evaluation(score=score, verdict="v", feedback="f", model_answer="m")
        stats.history.append(QuestionRecord(q, "my answer", e,
                                            question_id=f"{subject}::{topic}",
                                            elapsed_seconds=30))
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
    persistence.save_session(_stats(("Number Theory", "primes", 8), ("Fourier Analysis", "DFT", 4)))
    history = json.loads(persistence._HISTORY_FILE.read_text())
    assert len(history) == 1
    s = history[0]
    assert s["answered"] == 2 and s["average_score"] == 6.0
    assert s["date"] and s["timestamp"]
    recs = s["records"]
    assert [r["question_id"] for r in recs] == ["Number Theory::primes", "Fourier Analysis::DFT"]
    assert [(r["subject"], r["topic"], r["score"], r["elapsed_seconds"]) for r in recs] == [
        ("Number Theory", "primes", 8, 30), ("Fourier Analysis", "DFT", 4, 30),
    ]
    persistence.save_session(_stats(("Number Theory", "primes", 2)))
    assert len(persistence._load_raw()) == 2


def test_draft_round_trip_and_cleared_by_save_session():
    stats = _stats(("Linear Algebra", "SVD", 9))
    persistence.save_draft(stats)
    assert persistence.has_draft() is True
    draft = json.loads(persistence._DRAFT_FILE.read_text())
    assert draft["answered"] == 1
    assert draft["questions"][0]["question"] == "Q about SVD"
    assert draft["questions"][0]["answer"] == "my answer"
    persistence.save_session(stats)
    assert persistence.has_draft() is False
    persistence.save_draft(stats)
    persistence.clear_draft()
    assert persistence.has_draft() is False
    persistence.clear_draft()  # idempotent


def test_time_decayed_averages_by_subject_and_topic():
    persistence.save_session(_stats(("Number Theory", "primes", 10), ("Number Theory", "CRT", 4)))
    persistence.save_session(_stats(("Number Theory", "primes", 6), ("Fourier Analysis", "DFT", 2)))
    by_subject = persistence.avg_scores_by_subject()
    assert by_subject["Number Theory"] == pytest.approx((10 + 4 + 6) / 3, abs=1e-6)
    assert by_subject["Fourier Analysis"] == pytest.approx(2.0, abs=1e-6)
    by_topic = persistence.avg_scores_by_topic()
    assert set(by_topic) == {"Number Theory::primes", "Number Theory::CRT", "Fourier Analysis::DFT"}
    assert by_topic["Number Theory::primes"] == pytest.approx(8.0, abs=1e-6)


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


# ── Flag for review ───────────────────────────────────────────────────────────

import os
import pathlib
import subprocess
import sys
import textwrap
import time

APP_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _question(subject="Linear Algebra", topic="spectral theorem", text=None) -> Question:
    return Question(subject=subject, topic=topic, difficulty="beginner",
                    question_type="calculation",
                    text=text if text is not None else f"Q about {topic}")


def test_flagged_file_is_redirected_and_named_for_the_app(data_dir):
    assert persistence._FLAGGED_FILE.is_relative_to(data_dir)
    assert persistence._FLAGGED_FILE.name == "math_flagged.json"
    assert persistence.load_flagged() == []
    assert persistence.flagged_ids() == set()
    assert persistence.is_flagged(_question()) is False


def test_toggle_flag_writes_suite_schema():
    q = _question(text="Let V be an inner product space. " + "Prove things. " * 20)
    before = time.time()
    assert persistence.toggle_flag(q) is True
    raw = json.loads(persistence._FLAGGED_FILE.read_text(encoding="utf-8"))
    assert isinstance(raw, list) and len(raw) == 1
    e = raw[0]
    assert set(e) == {"id", "label", "category", "app", "timestamp"}
    assert e["app"] == "math-quiz"
    assert e["category"] == q.subject
    assert isinstance(e["timestamp"], float) and before <= e["timestamp"] <= time.time()
    prefix = f"{q.subject}::{q.topic}#"
    assert e["id"].startswith(prefix)
    digest = e["id"][len(prefix):]
    assert len(digest) == 8 and all(c in "0123456789abcdef" for c in digest)
    assert len(e["label"]) <= 80 and e["label"].endswith("…")
    assert e["label"].startswith("Let V be an inner product space.")
    assert e["id"] == persistence.flag_id_for(q)
    assert e["label"] == persistence.flag_label_for(q)
    assert persistence.is_flagged(q) is True
    assert persistence.is_flagged(e["id"]) is True


def test_flag_id_distinguishes_questions_on_one_topic_and_collapses_whitespace():
    a = _question(text="First question")
    b = _question(text="Second question")
    assert persistence.flag_id_for(a) != persistence.flag_id_for(b)
    assert persistence.flag_id_for(a) == persistence.flag_id_for(_question(text="  First question \n"))
    multi = _question(text="line one\n\n   line two\tend")
    assert persistence.flag_label_for(multi) == "line one line two end"


def test_toggle_twice_removes_and_third_time_reflags():
    q = _question()
    assert persistence.toggle_flag(q) is True
    assert persistence.toggle_flag(q) is False
    assert json.loads(persistence._FLAGGED_FILE.read_text(encoding="utf-8")) == []
    assert persistence.is_flagged(q) is False
    assert persistence.toggle_flag(q) is True
    assert len(persistence.load_flagged()) == 1


def test_toggle_keeps_other_entries_and_accepts_prepared_dict():
    q1, q2 = _question(text="one"), _question(subject="Number Theory", topic="primes", text="two")
    persistence.toggle_flag(q1)
    persistence.toggle_flag(q2)
    assert persistence.flagged_ids() == {persistence.flag_id_for(q1), persistence.flag_id_for(q2)}
    assert persistence.toggle_flag(q1) is False
    assert persistence.flagged_ids() == {persistence.flag_id_for(q2)}
    # A prepared dict gets app/timestamp defaults filled in.
    assert persistence.toggle_flag({"id": "X::y#00000000", "label": "L", "category": "X"}) is True
    added = next(e for e in persistence.load_flagged() if e["id"] == "X::y#00000000")
    assert added["app"] == "math-quiz" and isinstance(added["timestamp"], float)


def test_toggle_flag_rejects_dict_without_id():
    with pytest.raises(ValueError, match="needs an 'id'"):
        persistence.toggle_flag({"label": "no id"})
    with pytest.raises(ValueError):
        persistence.toggle_flag({"id": "   "})
    assert not persistence._FLAGGED_FILE.exists()


def test_unflag_return_values():
    q = _question()
    assert persistence.unflag(q) is False          # nothing flagged yet
    persistence.toggle_flag(q)
    assert persistence.unflag("no-such-id") is False
    assert persistence.unflag(q) is True
    assert persistence.unflag(q) is False
    persistence.toggle_flag(q)
    assert persistence.unflag(persistence.flag_id_for(q)) is True   # by id string


def test_corrupt_and_non_list_flag_files_load_as_empty(data_dir):
    data_dir.mkdir(parents=True)
    q = _question()
    persistence._FLAGGED_FILE.write_text("{not a list", encoding="utf-8")
    assert persistence.load_flagged() == []
    assert persistence.toggle_flag(q) is True                 # recreates the file
    assert [e["id"] for e in persistence.load_flagged()] == [persistence.flag_id_for(q)]
    persistence._FLAGGED_FILE.write_text('{"a": 1}', encoding="utf-8")
    assert persistence.load_flagged() == []
    # Malformed entries inside an otherwise valid list are skipped.
    persistence.save_flagged([{"garbage": True}, "str", {"id": "", "label": "x"},
                              {"id": "ok::t#0", "label": "kept"}])
    assert [e["id"] for e in persistence.load_flagged()] == ["ok::t#0"]


def test_flag_and_history_files_are_utf8_and_written_atomically(data_dir, monkeypatch):
    q = _question(subject="Calculus & Real Analysis", topic="ε-δ definitions",
                  text="Let f: ℝ → ℝ. " + "x" * 100)
    persistence.toggle_flag(q)
    raw = persistence._FLAGGED_FILE.read_bytes()
    assert "ε-δ" in raw.decode("utf-8")           # written as UTF-8, not escaped
    assert persistence.load_flagged()[0]["id"].startswith("Calculus & Real Analysis::ε-δ definitions#")
    persistence.save_session(_stats(("Calculus & Real Analysis", "ε-δ definitions", 7)))
    assert persistence.avg_scores_by_topic() == {"Calculus & Real Analysis::ε-δ definitions": pytest.approx(7.0)}
    # No temp files left behind after successful writes.
    assert sorted(p.name for p in data_dir.iterdir()) == ["math_flagged.json", "math_history.json"]

    # A failing write must leave the existing file intact and clean up its temp file.
    good = persistence._FLAGGED_FILE.read_bytes()

    def boom(*_a, **_k):
        raise OSError("disk full")
    monkeypatch.setattr(persistence.os, "replace", boom)
    with pytest.raises(OSError):
        persistence.toggle_flag(_question(text="another"))
    assert persistence._FLAGGED_FILE.read_bytes() == good
    assert not list(data_dir.glob("*.tmp"))


def test_flag_round_trip_under_non_utf8_locale(data_dir, tmp_path):
    """Regression: with a C/ASCII locale (stand-in for Windows cp1252) the
    flagged file used to load as [] and toggle_flag() truncated it mid-write."""
    script = tmp_path / "locale_probe.py"
    script.write_text(textwrap.dedent('''
        import json, locale
        import persistence
        from core.models import Question
        print("ENC", locale.getpreferredencoding(False))
        q = Question(subject="Calculus & Real Analysis", topic="ε-δ definitions",
                     difficulty="beginner", question_type="calculation",
                     text="Let f: ℝ → ℝ. " + "x" * 100)
        assert persistence.toggle_flag(q) is True
        entries = persistence.load_flagged()
        assert len(entries) == 1, entries
        assert entries[0]["id"].startswith("Calculus & Real Analysis::ε-δ definitions#"), entries
        assert entries[0]["label"].endswith("\\u2026"), entries
        assert persistence.toggle_flag(q) is False
        assert json.loads(persistence._FLAGGED_FILE.read_text(encoding="utf-8")) == []
        print("OK")
    '''), encoding="utf-8")
    env = {**os.environ, "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0",
           "LC_ALL": "C", "LANG": "C", "PYTHONPATH": str(APP_ROOT),
           "QUANTUM_STUDY_DATA_DIR": str(data_dir)}
    env.pop("PYTHONIOENCODING", None)
    proc = subprocess.run([sys.executable, str(script)], env=env, cwd=str(APP_ROOT),
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip().endswith("OK")
    enc = proc.stdout.split("ENC", 1)[1].split()[0].lower().replace("-", "")
    if enc == "utf8":
        pytest.skip("platform forces UTF-8 even under LC_ALL=C; locale regression not exercised")
