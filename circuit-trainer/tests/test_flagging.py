"""Flag-for-review contract: trainer_flagged.json entries, toggle semantics,
stable ids, and tolerance of a corrupt file."""
from __future__ import annotations

import json
import time

import persistence
from core.models import AnswerFormat, Problem, ProblemCategory


def _problem(text: str = "Apply H to |0⟩. What is the output state?",
             cat: ProblemCategory = ProblemCategory.SINGLE_GATE_OUTPUT,
             pid: str | None = None) -> Problem:
    return Problem(
        category=cat, difficulty="beginner", question_text=text,
        answer_format=AnswerFormat.MULTIPLE_CHOICE, correct_answer="0",
        choices=["a", "b", "c", "d"], circuit_png=None, aux_circuit_png=None,
        matrix_str=None, state_str=None, solution_steps=["s"],
        key_concepts=["k"], problem_id=pid,
    )


def test_toggle_flag_writes_a_contract_entry(isolated_data_dir):
    assert persistence.load_flagged() == []
    p = _problem()
    assert persistence.toggle_flag(p) is True

    path = isolated_data_dir / "trainer_flagged.json"
    assert persistence.flagged_file() == path and path.exists()
    entries = json.loads(path.read_text())
    assert isinstance(entries, list) and len(entries) == 1
    e = entries[0]
    assert set(e) == {"id", "label", "category", "app", "timestamp"}
    assert e["id"] == persistence.flag_id_for(p)
    assert len(e["id"]) == 16 and int(e["id"], 16) >= 0        # SHA-1 fallback id
    assert e["app"] == "circuit-trainer"
    assert e["category"] == ProblemCategory.SINGLE_GATE_OUTPUT.value
    assert e["label"].startswith("Single-gate output: Apply H to |0⟩")
    assert abs(time.time() - float(e["timestamp"])) < 60
    assert persistence.is_flagged(e["id"])
    assert persistence.load_flagged() == entries


def test_toggle_twice_removes_the_entry(isolated_data_dir):
    p = _problem()
    assert persistence.toggle_flag(p) is True
    assert persistence.toggle_flag(p) is False
    assert persistence.load_flagged() == []
    assert json.loads((isolated_data_dir / "trainer_flagged.json").read_text()) == []
    assert not persistence.is_flagged(persistence.flag_id_for(p))


def test_toggle_keeps_other_entries(isolated_data_dir):
    a, b = _problem("question A"), _problem("question B", ProblemCategory.NOISE_CHANNEL)
    persistence.toggle_flag(a)
    persistence.toggle_flag(b)
    assert [e["id"] for e in persistence.load_flagged()] == [
        persistence.flag_id_for(a), persistence.flag_id_for(b)]
    persistence.toggle_flag(a)
    remaining = persistence.load_flagged()
    assert [e["id"] for e in remaining] == [persistence.flag_id_for(b)]
    assert remaining[0]["category"] == ProblemCategory.NOISE_CHANNEL.value


def test_flag_id_is_stable_and_prefers_problem_id():
    assert persistence.flag_id_for(_problem()) == persistence.flag_id_for(_problem())
    assert persistence.flag_id_for(_problem("x")) != persistence.flag_id_for(_problem("y"))
    assert persistence.flag_id_for(_problem("x")) != persistence.flag_id_for(
        _problem("x", ProblemCategory.GATE_SEQUENCE))
    assert persistence.flag_id_for(_problem(pid="gs:H-X-H:0")) == "gs:H-X-H:0"


def test_flag_label_is_category_plus_truncated_question():
    short = persistence.flag_label_for(_problem("What is  ⟨0|1⟩?\n\n(think)"))
    assert short == "Single-gate output: What is ⟨0|1⟩? (think)"
    long_text = "word " * 40
    label = persistence.flag_label_for(_problem(long_text))
    assert label.startswith("Single-gate output: word word")
    assert label.endswith("…") and len(label) <= len("Single-gate output: ") + 70


def test_unflag_returns_false_for_unknown_id(isolated_data_dir):
    assert persistence.unflag("nope") is False
    p = _problem()
    persistence.toggle_flag(p)
    assert persistence.unflag("nope") is False
    assert persistence.unflag(persistence.flag_id_for(p)) is True
    assert persistence.load_flagged() == []


def test_corrupt_or_malformed_file_is_treated_as_empty(isolated_data_dir):
    isolated_data_dir.mkdir(parents=True, exist_ok=True)
    path = isolated_data_dir / "trainer_flagged.json"

    path.write_text("{not json")
    assert persistence.load_flagged() == []
    assert persistence.is_flagged("anything") is False

    path.write_text(json.dumps({"id": "dict-not-list"}))
    assert persistence.load_flagged() == []

    path.write_text(json.dumps(["bare-string", {"no_id": 1}, {"id": "ok", "label": "L"}]))
    assert [e["id"] for e in persistence.load_flagged()] == ["ok"]

    # Recoverable: toggling on top of a corrupt file rewrites a valid list.
    path.write_text("{not json")
    assert persistence.toggle_flag(_problem()) is True
    assert len(json.loads(path.read_text())) == 1
