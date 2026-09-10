"""Flag-for-review contract (dojo_flagged.json): entry schema, toggle
semantics, robustness against corrupt/foreign files, and coach.py discovery.

Everything goes through the ``data_dir`` fixture — the real
~/.local/share/quantum-study is never touched.
"""
from __future__ import annotations

import fnmatch
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

import persistence
from core.models import Kata

APP_ROOT = Path(__file__).resolve().parent.parent
COACH = APP_ROOT.parent / "coach.py"
CONTRACT_KEYS = {"id", "label", "category", "app", "timestamp"}


def _kata(kid: str = "cc_bell_state", title: str = "Build a Bell state",
          section: str = "Create circuits") -> Kata:
    return Kata(id=kid, section=section, title=title, difficulty="beginner",
                prompt="p", starter_code="", test_code="", solution_code="")


def _read(data_dir: Path) -> list:
    return json.loads((data_dir / "dojo_flagged.json").read_text())


def test_flagged_file_follows_suite_naming(data_dir):
    assert persistence.FLAGGED_FILE == data_dir / "dojo_flagged.json"
    # coach.py --review discovers review files with this glob; the prefix is
    # the app's history-file prefix ("dojo").
    assert fnmatch.fnmatch(persistence.FLAGGED_FILE.name, "*_flagged.json")
    assert persistence.HISTORY_FILE.name.split("_")[0] == "dojo"


def test_toggle_writes_exactly_the_contract_entry(data_dir):
    k = _kata()
    before = time.time()
    assert not persistence.FLAGGED_FILE.exists()

    assert persistence.toggle_flag(k) is True

    entries = _read(data_dir)
    assert len(entries) == 1
    e = entries[0]
    assert set(e) == CONTRACT_KEYS
    assert e["id"] == k.id
    assert e["label"] == k.title
    assert e["category"] == k.section
    assert e["app"] == "qiskit-dojo"
    assert isinstance(e["timestamp"], float)
    assert before - 1 <= e["timestamp"] <= time.time() + 1
    assert persistence.is_flagged(k.id) is True
    assert persistence.flagged_ids() == {k.id}


def test_second_toggle_unflags_and_leaves_empty_list(data_dir):
    k = _kata()
    assert persistence.toggle_flag(k) is True
    assert persistence.toggle_flag(k) is False
    assert _read(data_dir) == []
    assert persistence.is_flagged(k.id) is False
    assert persistence.load_flagged() == []


def test_toggle_keeps_other_entries_in_insertion_order(data_dir):
    for kid in ("a", "b", "c"):
        assert persistence.toggle_flag(_kata(kid)) is True
    assert persistence.toggle_flag(_kata("b")) is False
    assert [e["id"] for e in _read(data_dir)] == ["a", "c"]
    assert [e["id"] for e in persistence.load_flagged()] == ["a", "c"]  # oldest first
    assert persistence.flagged_ids() == {"a", "c"}


def test_unflag_is_a_noop_for_absent_ids(data_dir):
    persistence.unflag("nothing")
    assert not persistence.FLAGGED_FILE.exists()      # no file conjured up

    persistence.toggle_flag(_kata("a"))
    raw = persistence.FLAGGED_FILE.read_text()
    persistence.unflag("nothing")
    assert persistence.FLAGGED_FILE.read_text() == raw  # byte-identical

    persistence.unflag("a")
    assert _read(data_dir) == []
    assert persistence.is_flagged("a") is False


def test_corrupt_file_reads_as_empty_and_is_recreated_on_flag(data_dir):
    data_dir.mkdir(parents=True)
    persistence.FLAGGED_FILE.write_text("{not json at all")
    assert persistence.load_flagged() == []
    assert persistence.flagged_ids() == set()
    assert persistence.is_flagged("a") is False

    assert persistence.toggle_flag(_kata("a")) is True
    assert [e["id"] for e in _read(data_dir)] == ["a"]


def test_foreign_shapes_are_filtered_not_fatal(data_dir):
    data_dir.mkdir(parents=True)
    persistence.FLAGGED_FILE.write_text(json.dumps({"id": "x"}))   # dict, not list
    assert persistence.load_flagged() == []

    persistence.FLAGGED_FILE.write_text(json.dumps([
        {"id": "keep", "label": "K", "category": "S", "app": "qiskit-dojo", "timestamp": 1.0},
        {"label": "no id"}, "junk", None, 42, {"id": ""},
    ]))
    assert [e["id"] for e in persistence.load_flagged()] == ["keep"]
    assert persistence.is_flagged("keep") is True


def test_data_dir_is_created_on_first_flag(data_dir):
    assert not data_dir.exists()
    persistence.toggle_flag(_kata("a"))
    assert data_dir.is_dir()
    assert sorted(p.name for p in data_dir.iterdir()) == ["dojo_flagged.json"]


@pytest.mark.skipif(not COACH.exists(), reason="coach.py not present in this checkout")
def test_coach_review_discovers_dojo_flags(data_dir):
    """Integration: coach.py --review (pointed at the temp dir) lists our flag."""
    k = _kata()
    persistence.toggle_flag(k)
    env = {kk: v for kk, v in os.environ.items() if kk != "ANTHROPIC_API_KEY"}
    env["QUANTUM_STUDY_DATA_DIR"] = str(data_dir)
    proc = subprocess.run(
        [sys.executable, str(COACH), "--review"],
        cwd=str(COACH.parent), env=env, capture_output=True, text=True, timeout=120,
    )
    assert proc.returncode == 0, proc.stderr
    assert "qiskit-dojo" in proc.stdout
    assert k.title in proc.stdout
    # read-only: the coach must not have added files to the data dir
    assert sorted(p.name for p in data_dir.iterdir()) == ["dojo_flagged.json"]
