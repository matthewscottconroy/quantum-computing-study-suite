"""Tests for coach.py — the deterministic daily-plan engine.

Every test runs against a temporary data directory (conftest ``data_dir`` /
``synthetic_dir``); the real ~/.local/share/quantum-study/ is never touched.
Only pure logic and file-loading surfaces are asserted on; rendering is
smoke-tested at most.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, time as dtime, timedelta, timezone
from pathlib import Path

import pytest

import coach

ROOT = Path(__file__).resolve().parent.parent
DAY = 86400.0
TODAY = datetime.now().date()
approx = pytest.approx


def days_ago(n: int) -> str:
    return (TODAY - timedelta(days=n)).strftime("%Y-%m-%d")


def noon_days_ago(n: int) -> float:
    """Local-noon Unix timestamp n days ago (clear of midnight/DST edges)."""
    return datetime.combine(TODAY - timedelta(days=n), dtime(12, 0)).timestamp()


def empty_histories() -> dict[str, list]:
    return {app: [] for app in coach._HISTORY_FILES}


def write_json(directory: Path, name: str, data) -> Path:
    path = directory / name
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Data directory + tolerant loading
# ---------------------------------------------------------------------------

class TestLoading:
    def test_data_dir_comes_from_env_var_not_home(self):
        # conftest exports QUANTUM_STUDY_DATA_DIR before coach is imported
        assert coach.DATA_DIR == Path(os.environ["QUANTUM_STUDY_DATA_DIR"])
        assert coach.STATE_PATH.parent == coach.DATA_DIR
        assert not str(coach.DATA_DIR).startswith(
            str(Path.home() / ".local" / "share" / "quantum-study"))

    def test_missing_files_load_as_empty(self, data_dir):
        assert coach._load_list("qec_history.json") == []
        histories = coach.load_histories()
        assert set(histories) == set(coach._HISTORY_FILES)
        assert all(v == [] for v in histories.values())

    @pytest.mark.parametrize("content",
                             ["", "{not json", "{}", "null", "42", '"str"'])
    def test_corrupt_or_wrong_shape_files_load_as_empty(self, data_dir, content):
        (data_dir / "vqa_history.json").write_text(content)
        assert coach._load_list("vqa_history.json") == []
        assert coach.load_histories()["vqa-trainer"] == []

    def test_load_state_defaults(self, data_dir):
        state = coach.load_state()
        assert state["activity_dates"] == []
        assert state["current_streak"] == 0 and state["best_streak"] == 0
        assert state["badges"] == {}
        assert state["diagnostic"] is None and state["last_plan_date"] is None

    @pytest.mark.parametrize("content", ["{{{", "[1, 2]", "", "null"])
    def test_load_state_tolerates_corrupt_file(self, data_dir, content):
        coach.STATE_PATH.write_text(content)
        state = coach.load_state()
        assert state["badges"] == {} and state["current_streak"] == 0

    def test_state_roundtrip(self, data_dir):
        state = coach.load_state()
        state["badges"] = {coach.BADGES[0]: "earned"}
        state["diagnostic"] = {"timestamp": 1.0,
                               "rungs": {"math": {"total": 3, "correct": 1}},
                               "recommended_rung": "math"}
        state["activity_dates"] = [days_ago(1), days_ago(0)]
        coach.save_state(state)
        assert coach.STATE_PATH == data_dir / "coach_state.json"
        assert coach.STATE_PATH.is_file()
        assert coach.load_state() == state

    def test_save_state_swallows_write_errors(self, data_dir, monkeypatch):
        blocker = data_dir / "blocker"
        blocker.write_text("a regular file, not a directory")
        monkeypatch.setattr(coach, "DATA_DIR", blocker)
        monkeypatch.setattr(coach, "STATE_PATH", blocker / "coach_state.json")
        coach.save_state({"x": 1})   # must not raise


# ---------------------------------------------------------------------------
# Category stats / weakest / stale / exam / dojo
# ---------------------------------------------------------------------------

class TestCategoryStats:
    def test_stats_follow_each_app_schema(self, now):
        today = days_ago(0)
        histories = {
            "qec-trainer": [{"timestamp": now, "attempts": [
                {"category": "stab", "score": 4}, {"category": "stab", "score": 8}]}],
            "vqa-trainer": [{"timestamp": now, "attempts": [
                {"category": "ansatz", "score": 6}]}],
            "circuit-trainer": [{"date": today, "attempts": [
                {"category": "cx", "score": 7}]}],
            "flashcard-drill": [{"timestamp": now, "results": [
                {"category": "hw", "rating": "got_it"},
                {"category": "hw", "rating": "missed"},
                {"category": "hw", "rating": "unsure"},
                {"category": "hw", "rating": "weird"}]}],
            "math-quiz": [{"date": today, "records": [
                {"topic": "eig", "score": 3}, {"subject": "alg", "score": 5}]}],
            "quantum-quiz": [{"date": today, "records": [
                {"subject": "qm", "topic": "", "score": 9}]}],
            "qiskit-dojo": [{"timestamp": now, "attempts": [
                {"section": "prim", "passed": True},
                {"section": "prim", "passed": False}]}],
            "exam-sim": [{"timestamp": now, "sections": {
                "P": {"total": 10, "correct": 4}, "Z": {"total": 0, "correct": 0}}}],
            "problem-trainer": [{"timestamp": now, "attempts": [
                {"problem_id": "p1", "kind": "derivation", "score": 6},
                {"problem_id": "p2", "score": 2}]}],
            "paper-drill": [{"title": "t", "scores": [1, 2]}],
        }
        stats = coach.build_category_stats(histories)

        def avg(app, cat):
            e = stats[(app, cat)]
            return e["w_sum"] / e["ws"]

        assert avg("qec-trainer", "stab") == approx(6.0)
        assert stats[("qec-trainer", "stab")]["n"] == 2
        assert stats[("qec-trainer", "stab")]["last_ts"] == approx(now)
        assert avg("vqa-trainer", "ansatz") == approx(6.0)
        assert avg("circuit-trainer", "cx") == approx(7.0)
        assert avg("flashcard-drill", "hw") == approx(5.0)     # (10+0+5+5)/4
        assert avg("math-quiz", "eig") == approx(3.0)
        assert avg("math-quiz", "alg") == approx(5.0)          # subject fallback
        assert avg("quantum-quiz", "qm") == approx(9.0)        # empty topic
        assert avg("qiskit-dojo", "prim") == approx(5.0)       # pass -> 10/0
        assert avg("exam-sim", "P") == approx(4.0)
        assert ("exam-sim", "Z") not in stats                  # total 0 skipped
        assert avg("problem-trainer", "derivation") == approx(6.0)
        assert avg("problem-trainer", "p2") == approx(2.0)
        assert not any(app == "paper-drill" for app, _ in stats)

    def test_weakest_categories_sorted_with_stable_ties(self):
        row = lambda ws, w: {"w_sum": ws, "ws": w, "last_ts": 0.0, "n": 1}
        stats = {("b-app", "z"): row(2.0, 1.0), ("a-app", "y"): row(2.0, 1.0),
                 ("a-app", "x"): row(9.0, 1.0), ("c-app", "w"): row(0.0, 0.0)}
        assert coach.weakest_categories(stats, top_n=3) == [
            ("a-app", "y", 2.0), ("b-app", "z", 2.0), ("a-app", "x", 9.0)]
        assert coach.weakest_categories(stats, top_n=1) == [("a-app", "y", 2.0)]
        assert coach.weakest_categories({}) == []

    def test_stale_categories_only_old_activity(self):
        now = coach._NOW
        row = lambda ts: {"w_sum": 1.0, "ws": 1.0, "last_ts": ts, "n": 1}
        stats = {("qec-trainer", "old"): row(now - 12 * DAY - 3600),
                 ("qec-trainer", "older"): row(now - 20 * DAY - 3600),
                 ("vqa-trainer", "fresh"): row(now - 3600),
                 ("math-quiz", "undated"): row(0.0)}
        assert coach.stale_categories(stats) == [
            ("qec-trainer", "older", 20), ("qec-trainer", "old", 12)]
        assert coach.STALE_DAYS == 7

    def test_exam_readiness_uses_latest_full_exam(self, now):
        older = {"timestamp": now - 5 * DAY, "mode": "full", "total": 68,
                 "correct": 60, "sections": {}}
        latest = {"timestamp": now - DAY, "mode": "full", "total": 68,
                  "correct": 46, "sections": {
                      "A": {"total": 10, "correct": 9},
                      "B": {"total": 10, "correct": 2},
                      "C": {"total": 10, "correct": 5},
                      "D": {"total": 10, "correct": 1},
                      "E": {"total": 0, "correct": 0}}}
        sprint = {"timestamp": now, "mode": "sprint", "total": 10, "correct": 10}
        r = coach.exam_readiness([older, sprint, latest, "junk", None])
        assert (r["correct"], r["total"]) == (46, 68)
        assert r["passing"] is False
        assert r["pct"] == approx(46 / 68 * 100)
        assert r["pass_pct"] == approx(coach.EXAM_PASS_CORRECT
                                       / coach.EXAM_PASS_TOTAL * 100)
        assert r["weakest_sections"] == [("D", 10.0), ("B", 20.0), ("C", 50.0)]
        assert r["timestamp"] == approx(now - DAY)
        assert coach.exam_readiness([sprint]) is None
        assert coach.exam_readiness([]) is None
        assert coach.exam_readiness([dict(latest, correct=47)])["passing"] is True

    def test_dojo_weakest_section(self, now):
        sessions = [{"timestamp": now, "attempts": [
            {"section": "A", "passed": True}, {"section": "A", "passed": False},
            {"section": "B", "passed": True},
            {"section": "C", "passed": False}, {"section": "C", "passed": False},
            {"section": "", "passed": False}, "junk"]}]
        assert coach.dojo_weakest_section(sessions) == ("C", 0.0)
        assert coach.dojo_weakest_section([]) is None
        assert coach.dojo_weakest_section([{"attempts": []}]) is None


# ---------------------------------------------------------------------------
# Plan builder
# ---------------------------------------------------------------------------

class TestPlan:
    def test_plan_is_deterministic(self, synthetic_dir):
        first = coach.build_plan(coach.load_histories(), coach.load_state())
        second = coach.build_plan(coach.load_histories(), coach.load_state())
        assert first == second
        assert json.dumps(first, sort_keys=True, default=str) == \
            json.dumps(second, sort_keys=True, default=str)

    def test_plan_mentions_weakest_categories(self, synthetic_dir):
        histories = coach.load_histories()
        plan = coach.build_plan(histories, coach.load_state())
        expected = coach.weakest_categories(
            coach.build_category_stats(histories), top_n=3)
        assert plan["weakest"] == expected
        # lowest three across the synthetic data
        assert [(a, c) for a, c, _ in expected] == [
            ("qiskit-dojo", "Transpiler"), ("quantum-quiz", "grover"),
            ("math-quiz", "eigenvalues")]
        assert [round(v, 6) for *_, v in expected] == [0.0, 1.0, 2.0]
        text = "\n".join(plan["items"])
        for app, cat, _ in expected:
            assert cat in text and app in text
        assert 3 <= len(plan["items"]) <= 5

    def test_plan_structure_on_synthetic_data(self, synthetic_dir):
        plan = coach.build_plan(coach.load_histories(), coach.load_state())
        items = plan["items"]
        assert len(items) == 5                          # capped at 5
        assert items[0].startswith("review queue — 9 item(s) due")
        assert "5 flagged across 4 app(s)" in items[0]
        assert plan["review_count"] == plan["review_total"] == 9
        assert plan["review_dropped"] == 0
        assert plan["flagged_total"] == 5
        assert plan["flagged_by_app"] == {"flashcard-drill": 2,
                                          "qec-trainer": 1,
                                          "quantum-quiz": 1,
                                          "vqa-trainer": 1}
        assert plan["missed_count"] == 1
        assert plan["dojo"] == ("Transpiler", 0.0)
        assert plan["exam"]["passing"] is False
        assert plan["exam"]["weakest_sections"][0] == ("Primitives", 30.0)
        assert plan["stale"] == [("qec-trainer", "decoders", 10)]
        assert plan["diagnostic"] is None and plan["weak_rungs"] == []
        # exam-sim is not among the weakest apps -> sprint on weakest section
        assert any(i.startswith("exam-sim — Sprint: Primitives") for i in items)

    def test_plan_falls_back_to_starter_items(self, data_dir):
        plan = coach.build_plan(coach.load_histories(), coach.load_state())
        assert plan["weakest"] == [] and plan["stale"] == []
        assert plan["exam"] is None and plan["dojo"] is None
        assert plan["review_count"] == 0 and plan["flagged_total"] == 0
        assert len(plan["items"]) == 3
        assert plan["items"][0].startswith("flashcard-drill")

    def test_plan_uses_exam_and_diagnostic_signals(self, data_dir, now):
        h = empty_histories()
        h["exam-sim"] = [{"timestamp": now - 100, "mode": "full", "total": 68,
                          "correct": 30, "duration_secs": 1, "sections": {
                              "Primitives": {"total": 20, "correct": 5},
                              "Circuits": {"total": 48, "correct": 25}}}]
        state = coach.load_state()
        state["diagnostic"] = {"timestamp": now, "recommended_rung": "circuits",
                               "rungs": {"math": {"total": 3, "correct": 3},
                                         "circuits": {"total": 3, "correct": 1}}}
        plan = coach.build_plan(h, state)
        items = plan["items"]
        assert plan["weak_rungs"] == ["circuits"]
        assert any(i.startswith("exam-sim") and "Primitives" in i for i in items)
        assert any(i.startswith("circuit-trainer") and "rung 'circuits'" in i
                   and "docs/03_quantum_gates_and_circuits" in i for i in items)

    def test_plan_exam_retake_when_failing_without_sections(self, data_dir, now):
        h = empty_histories()
        h["exam-sim"] = [{"timestamp": now, "mode": "full", "total": 68,
                          "correct": 30}]
        plan = coach.build_plan(h, coach.load_state())
        assert any(i.startswith("exam-sim — full exam retake")
                   and "30/68" in i and "47/68" in i for i in plan["items"])

    def test_plan_reports_review_overflow(self, data_dir):
        write_json(data_dir, "flagged_cards.json",
                   [f"card_{i:02d}" for i in range(30)])
        plan = coach.build_plan(empty_histories(), coach.load_state())
        assert (plan["review_total"], plan["review_count"],
                plan["review_dropped"]) == (30, 20, 10)
        assert "past the cap of 20" in plan["items"][0]

    def test_plan_tolerates_malformed_sessions(self, data_dir, now):
        h = empty_histories()
        h["qec-trainer"] = [None, 3, "x", {"timestamp": "bad", "attempts": [
            None, {"category": "s", "score": "abc"}, {"category": "", "score": 5}]}]
        h["exam-sim"] = [{"mode": "full", "total": "x", "correct": 1},
                         {"mode": "full", "total": 68, "correct": 50,
                          "sections": "oops"}]
        h["math-quiz"] = [{"date": "not-a-date",
                           "records": [{"topic": "t", "score": 1}, 7]}]
        h["qiskit-dojo"] = [{"timestamp": now, "attempts": [
            {"section": "", "passed": True}, "nope"]}]
        h["flashcard-drill"] = [{"timestamp": now, "results": "not-a-list"}]
        plan = coach.build_plan(h, coach.load_state())
        assert 3 <= len(plan["items"]) <= 5
        assert plan["exam"]["passing"] is True and plan["dojo"] is None


# ---------------------------------------------------------------------------
# Diagnostic
# ---------------------------------------------------------------------------

class TestDiagnostic:
    def test_question_bank_well_formed(self):
        qs = coach.DIAGNOSTIC_QUESTIONS
        assert len(qs) == 20
        for q in qs:
            assert q["rung"] in coach.RUNG_ORDER
            assert len(q["choices"]) == 4
            assert 0 <= q["answer"] < len(q["choices"])
            assert q["q"].strip()
        counts = Counter(q["rung"] for q in qs)
        assert set(counts) == set(coach.RUNG_ORDER)
        assert min(counts.values()) >= 2
        assert len({q["q"] for q in qs}) == 20

    def test_all_correct(self):
        rungs = coach.score_diagnostic([q["answer"] for q in coach.DIAGNOSTIC_QUESTIONS])
        assert list(rungs) == coach.RUNG_ORDER
        assert all(r["correct"] == r["total"] for r in rungs.values())
        assert sum(r["total"] for r in rungs.values()) == 20
        assert coach.weak_rungs(rungs) == []
        assert coach.recommended_rung(rungs) == "math"   # all solid -> ladder start

    def test_all_skipped(self):
        rungs = coach.score_diagnostic([None] * 20)
        assert all(r["correct"] == 0 for r in rungs.values())
        assert sum(r["total"] for r in rungs.values()) == 20
        assert coach.weak_rungs(rungs) == coach.RUNG_ORDER
        assert coach.recommended_rung(rungs) == "math"

    def test_short_answer_list_scores_only_answered(self):
        rungs = coach.score_diagnostic([])
        assert all(r["total"] == 0 for r in rungs.values())
        assert coach.recommended_rung(rungs) == "math"
        rungs = coach.score_diagnostic([coach.DIAGNOSTIC_QUESTIONS[0]["answer"]])
        assert rungs["math"] == {"total": 1, "correct": 1}

    def test_recommended_rung_is_first_weak_in_ladder(self):
        answers = [((q["answer"] + 1) % 4) if q["rung"] in ("qec", "hardware")
                   else q["answer"] for q in coach.DIAGNOSTIC_QUESTIONS]
        rungs = coach.score_diagnostic(answers)
        assert coach.weak_rungs(rungs) == ["qec", "hardware"]
        assert coach.recommended_rung(rungs) == "qec"

    def test_recommended_rung_all_solid_picks_relative_weakest(self):
        answers, flipped = [], False
        for q in coach.DIAGNOSTIC_QUESTIONS:
            if q["rung"] == "qm" and not flipped:
                answers.append((q["answer"] + 1) % 4)   # exactly one miss: 2/3
                flipped = True
            else:
                answers.append(q["answer"])
        rungs = coach.score_diagnostic(answers)
        assert rungs["qm"] == {"total": 3, "correct": 2}
        assert coach.weak_rungs(rungs) == []            # 2/3 is not below 2/3
        assert coach.recommended_rung(rungs) == "qm"

    def test_recommended_rung_partial_and_empty_inputs(self):
        assert coach.recommended_rung({}) == "math"
        assert coach.recommended_rung({"vqa": {"total": 2, "correct": 0}}) == "vqa"
        assert coach.recommended_rung({"vqa": {"total": 2, "correct": 2},
                                       "qec": {"total": 2, "correct": 2}}) == "qec"

    def test_rung_tables(self):
        assert coach.RUNG_ORDER == [r[0] for r in coach.RUNGS]
        assert len(set(coach.RUNG_ORDER)) == len(coach.RUNGS) == 8
        for name, docs, app in coach.RUNGS:
            assert (ROOT / docs).is_dir(), docs
            assert app in coach._HISTORY_FILES
            assert coach.rung_docs_dir(name) == docs
            assert coach.rung_app(name) == app
        assert coach.rung_docs_dir("nope") == "docs/"
        assert coach.rung_app("nope") == "flashcard-drill"


# ---------------------------------------------------------------------------
# Badges
# ---------------------------------------------------------------------------

class TestBadges:
    def test_cycle_wraps_around(self):
        state, badge = {}, coach.BADGES[0]
        assert coach.cycle_badge(state, badge) == "in_progress"
        assert coach.cycle_badge(state, badge) == "earned"
        assert coach.cycle_badge(state, badge) == "not_started"
        assert state["badges"] == {badge: "not_started"}
        assert coach.BADGE_STATUSES == ["not_started", "in_progress", "earned"]

    def test_cycle_repairs_unknown_status(self):
        state = {"badges": {"X": "bogus"}}
        assert coach.cycle_badge(state, "X") == "in_progress"

    def test_badge_list_and_persistence(self, data_dir):
        assert len(coach.BADGES) == 7 and len(set(coach.BADGES)) == 7
        assert any("C1000-179" in b for b in coach.BADGES)
        state = coach.load_state()
        for b in coach.BADGES:
            coach.cycle_badge(state, b)
        coach.save_state(state)
        assert coach.load_state()["badges"] == {b: "in_progress" for b in coach.BADGES}


# ---------------------------------------------------------------------------
# Review queue
# ---------------------------------------------------------------------------

REVIEW_KEYS = {"app", "id", "label", "category", "ts", "score", "why"}


class TestReviewQueue:
    def test_merges_all_sources_on_synthetic_data(self, synthetic_dir, now):
        queue = coach.build_review_queue(coach.load_histories())
        assert all(set(i) == REVIEW_KEYS for i in queue)
        got = {(i["app"], i["id"], i["why"]) for i in queue}
        assert len(queue) == len(got) == 9
        assert got == {
            ("quantum-quiz", "Algorithms::grover", "flagged"),   # contract file
            ("flashcard-drill", "fc_bloch", "flagged"),          # legacy files
            ("flashcard-drill", "fc_t1", "flagged"),
            ("qec-trainer", "qec_steane", "flagged"),
            ("vqa-trainer", "vqa_qaoa", "flagged"),
            ("exam-sim", "ex_017", "missed exam question"),
            ("math-quiz", "eigenvalues", "scored 2/10"),
            ("quantum-quiz", "grover", "scored 1/10"),
            ("problem-trainer", "p_grover_1", "scored 3/10"),
        }
        by_id = {i["id"]: i for i in queue}
        # contract-shaped entry: label / category / app / timestamp carried over
        flagged_q = by_id["Algorithms::grover"]
        assert flagged_q["label"].startswith("How many Grover iterations")
        assert flagged_q["category"] == "Algorithms"
        assert flagged_q["ts"] == approx(now - 500, abs=1)
        assert by_id["ex_017"]["category"] == "Primitives"
        assert by_id["ex_017"]["ts"] == approx(now - 3600, abs=1)
        assert by_id["eigenvalues"]["category"] == "Linear Algebra"
        assert by_id["p_grover_1"]["category"] == "problem"
        # bare string ids (legacy files) fall back to the file mtime (just now)
        for legacy in ("fc_bloch", "fc_t1", "qec_steane", "vqa_qaoa"):
            assert by_id[legacy]["ts"] == approx(now, abs=60), legacy
            assert by_id[legacy]["label"] == legacy and by_id[legacy]["category"] == ""
        timestamps = [i["ts"] for i in queue]
        assert timestamps == sorted(timestamps)
        # oldest first: exam miss (now-3600) < contract flag (now-500) < the
        # legacy ids stamped with the file mtime (~now).  The low-score items
        # carry their own session timestamps (problem-trainer now-300; math /
        # quantum-quiz parse the ISO string, ~now), so they normally land
        # between the contract flag and the legacy ids; only the relations
        # asserted below are contractual.
        pos = {i["id"]: k for k, i in enumerate(queue)}
        assert pos["ex_017"] < pos["Algorithms::grover"]
        assert all(pos["Algorithms::grover"] < pos[x]
                   for x in ("fc_bloch", "fc_t1", "qec_steane", "vqa_qaoa"))

    def test_flag_entry_normalization(self):
        assert coach._flag_entry("  x1 ", "qec-trainer") == {
            "app": "qec-trainer", "id": "x1", "label": "x1", "category": "",
            "ts": 0.0, "score": 0.0, "why": "flagged"}
        assert coach._flag_entry("x1", "a", fallback_ts=5.0)["ts"] == 5.0
        legacy = coach._flag_entry({"problem_id": "p9", "timestamp": "12.5"}, "a")
        assert (legacy["id"], legacy["label"], legacy["ts"]) == ("p9", "p9", 12.5)
        assert coach._flag_entry({"problem_id": 7}, "a")["id"] == "7"
        full = coach._flag_entry({"id": "c1", "label": "  Bloch   sphere ",
                                  "category": "qm", "app": "quantum-quiz",
                                  "timestamp": 1_700_000_000_000}, "flashcard-drill")
        assert full == {"app": "quantum-quiz", "id": "c1", "label": "Bloch sphere",
                        "category": "qm", "ts": 1_700_000_000.0, "score": 0.0,
                        "why": "flagged"}
        assert coach._flag_entry({"id": "c2"}, "a", fallback_ts=7.0)["ts"] == 7.0
        assert coach._flag_entry({"id": "c2", "timestamp": -5}, "a", 7.0)["ts"] == 7.0
        long_label = coach._flag_entry({"id": "c3", "label": "x" * 200}, "a")["label"]
        assert len(long_label) == coach._LABEL_MAX and long_label.endswith("…")
        for bad in ("", "   ", None, 3, [], {}, {"x": 1}, {"id": "  "}, {"id": None}):
            assert coach._flag_entry(bad, "a") is None

    def test_epoch_and_short_helpers(self):
        assert coach._epoch(None) == 0.0 and coach._epoch("abc") == 0.0
        assert coach._epoch(-1) == 0.0 and coach._epoch(0) == 0.0
        assert coach._epoch(1.7e9) == 1.7e9
        assert coach._epoch("1700000000") == 1.7e9
        assert coach._epoch(1.7e12) == approx(1.7e9)      # milliseconds
        assert coach._short("  a \n b\tc ") == "a b c"

    def test_flag_files_are_discovered_by_name(self, data_dir):
        for name in ("qec_flagged.json", "quiz_flagged.json", "weird_flagged.json",
                     "flagged_cards.json", "notes.json"):
            write_json(data_dir, name, ["x"])
        (data_dir / "dir_flagged.json").mkdir()
        found = coach.discover_flagged_files()
        assert [(app, p.name) for app, p in found] == [
            ("flashcard-drill", "flagged_cards.json"),
            ("qec-trainer", "qec_flagged.json"),
            ("quantum-quiz", "quiz_flagged.json"),
            ("weird", "weird_flagged.json")]
        assert coach._app_for_flag_file(Path("problems_flagged.json")) == "problem-trainer"
        assert coach._app_for_flag_file(Path("trainer_flagged.json")) == "circuit-trainer"
        assert coach._app_for_flag_file(Path("dojo_flagged.json")) == "qiskit-dojo"
        assert coach.discover_flagged_files.__doc__   # sanity: public helper
        (data_dir / "qec_flagged.json").unlink()
        assert len(coach.discover_flagged_files()) == 3

    def test_string_and_dict_flag_entries_with_dedupe(self, data_dir):
        write_json(data_dir, "flagged_cards.json", [
            "card_a", " card_a ", {"card_id": "card_b", "timestamp": 5},
            "", 42, None, {"note": "no id"}, {"id": "card_c"},
            {"question_id": "card_d"}, {"id": "card_a", "timestamp": 1}])
        notes: list[str] = []
        items = coach.load_flagged_items(notes)
        assert [i["id"] for i in items] == ["card_a", "card_b", "card_c", "card_d"]
        assert all(i["app"] == "flashcard-drill" for i in items)
        assert notes == ["flagged_cards.json: ignored 4 malformed entries"]
        queue = coach.build_review_queue({})
        assert [i["id"] for i in queue] == ["card_b", "card_a", "card_c", "card_d"]

    def test_dedupe_across_files_and_app_override(self, data_dir):
        write_json(data_dir, "qec_flagged.json",
                   ["a", {"id": "a"}, {"id": "b", "app": "vqa-trainer"}])
        write_json(data_dir, "vqa_flagged.json", ["b", "c"])
        (data_dir / "bad_flagged.json").write_text("{")
        notes: list[str] = []
        items = coach.load_flagged_items(notes)
        assert sorted((i["app"], i["id"]) for i in items) == [
            ("qec-trainer", "a"), ("vqa-trainer", "b"), ("vqa-trainer", "c")]
        assert coach.flagged_counts(items) == {"qec-trainer": 1, "vqa-trainer": 2}
        assert any("bad_flagged.json" in n for n in notes)

    def test_exam_missed_entries(self, data_dir, now):
        write_json(data_dir, "exam_missed.json", [
            {"question_id": "q1", "section": "Primitives", "timestamp": now},
            {"question_id": "q1", "section": "Primitives"},
            {"question_id": "q2"}, {"section": "x"}, "q3", None])
        queue = coach.build_review_queue({})
        assert [(i["id"], i["category"], i["why"]) for i in queue] == [
            ("q2", "", "missed exam question"),
            ("q1", "Primitives", "missed exam question")]
        assert queue[1]["ts"] == approx(now)

    def test_low_scores_window_and_threshold(self, data_dir, now):
        h = {
            "math-quiz": [
                {"timestamp": now - DAY, "records": [
                    {"subject": "Linear Algebra", "topic": "eig", "score": 4.9},
                    {"subject": "Linear Algebra", "topic": "eig", "score": 4.9},
                    {"topic": "ok", "score": 5.0},
                    {"subject": "alg", "score": 0}]},
                {"timestamp": now - 31 * DAY, "records": [{"topic": "ancient", "score": 0}]},
                {"records": [{"topic": "undated", "score": 0}]},
            ],
            "quantum-quiz": [{"date": days_ago(0),
                              "records": [{"topic": "grover", "score": 2}]}],
            "problem-trainer": [{"timestamp": now, "attempts": [
                {"problem_id": "p1", "kind": "problem", "score": 1},
                {"kind": "derivation", "score": 2},
                {"problem_id": "p_ok", "score": 8}]}],
        }
        queue = coach.build_review_queue(h)
        assert {(i["app"], i["id"]) for i in queue} == {
            ("math-quiz", "eig"), ("math-quiz", "alg"), ("quantum-quiz", "grover"),
            ("problem-trainer", "p1"), ("problem-trainer", "derivation")}
        assert len(queue) == 5                       # identical eig rows deduped
        eig = next(i for i in queue if i["id"] == "eig")
        assert eig["why"] == "scored 4.9/10" and eig["score"] == 4.9
        assert eig["category"] == "Linear Algebra"
        p1 = next(i for i in queue if i["id"] == "p1")
        assert p1["category"] == "problem"
        assert coach.REVIEW_LOW_SCORE == 5.0 and coach.REVIEW_WINDOW_DAYS == 30

    def test_queue_capped_at_20_deterministically(self, data_dir):
        write_json(data_dir, "flagged_cards.json",
                   [f"card_{i:02d}" for i in range(30)])
        everything = coach.collect_review_items({})
        queue = coach.build_review_queue({})
        assert coach.REVIEW_CAP == 20
        assert len(everything) == 30 and len(queue) == 20
        assert [i["id"] for i in queue] == [f"card_{i:02d}" for i in range(20)]

    # Every flag source in the suite's flagging contract: <prefix>_flagged.json
    # for the six apps that follow it, plus the three legacy filenames.
    ALL_FLAG_FILES = {
        "quiz_flagged.json":     "quantum-quiz",
        "math_flagged.json":     "math-quiz",
        "trainer_flagged.json":  "circuit-trainer",
        "paper_flagged.json":    "paper-drill",
        "dojo_flagged.json":     "qiskit-dojo",
        "problems_flagged.json": "problem-trainer",
        "flagged_cards.json":    "flashcard-drill",   # legacy
        "qec_flagged.json":      "qec-trainer",       # legacy
        "vqa_flagged.json":      "vqa-trainer",       # legacy
    }

    @pytest.mark.parametrize("form", ["string-list", "dict-list"])
    def test_every_contract_flag_source_is_merged(self, data_dir, now, form):
        files = sorted(self.ALL_FLAG_FILES.items())
        for i, (fname, app) in enumerate(files):
            ident = f"{app}-item"
            if form == "string-list":
                payload = [ident, f" {ident} "]                 # in-file duplicate
            else:
                payload = [{"id": ident, "label": f"Label {i}",
                            "category": f"cat{i}", "app": app,
                            "timestamp": now - (i + 1) * DAY},
                           {"id": ident, "app": app}]           # in-file duplicate
            write_json(data_dir, fname, payload)

        assert [(a, p.name) for a, p in coach.discover_flagged_files()] == \
            [(app, fname) for fname, app in files]

        notes: list[str] = []
        items = coach.load_flagged_items(notes)
        assert notes == []
        expected = {(app, f"{app}-item") for app in self.ALL_FLAG_FILES.values()}
        assert {(i["app"], i["id"]) for i in items} == expected
        assert len(items) == len(expected) == 9                 # deduped per file
        assert coach.flagged_counts(items) == \
            {app: 1 for app in self.ALL_FLAG_FILES.values()}

        queue = coach.build_review_queue(empty_histories())
        assert len(queue) == 9 and all(i["why"] == "flagged" for i in queue)
        by_app = {i["app"]: i for i in queue}
        if form == "string-list":
            # bare ids: app comes from the filename, ts from the file mtime
            for app, item in by_app.items():
                assert item["label"] == f"{app}-item" and item["category"] == ""
                assert item["ts"] == approx(now, abs=60)
        else:
            for i, (fname, app) in enumerate(files):
                item = by_app[app]
                assert (item["label"], item["category"]) == (f"Label {i}", f"cat{i}")
                assert item["ts"] == approx(now - (i + 1) * DAY)
            assert [i["ts"] for i in queue] == sorted(i["ts"] for i in queue)

        plan = coach.build_plan(empty_histories(), coach.load_state())
        assert plan["flagged_total"] == 9 and len(plan["flagged_by_app"]) == 9
        assert plan["items"][0].startswith("review queue — 9 item(s) due")
        assert "9 flagged across 9 app(s)" in plan["items"][0]
        assert plan["review_dropped"] == 0

    def test_cap_applies_after_merging_all_sources(self, data_dir, now):
        # 5 old exam misses + 8 dated quiz flags + 8 undated math flags = 21 > 20
        write_json(data_dir, "exam_missed.json",
                   [{"question_id": f"ex_{k}", "section": "S",
                     "timestamp": now - (100 + k) * DAY} for k in range(5)])
        write_json(data_dir, "quiz_flagged.json",
                   [{"id": f"q_{k}", "label": f"Quiz {k}", "category": "Algorithms",
                     "app": "quantum-quiz", "timestamp": now - (10 - k) * DAY}
                    for k in range(8)])
        write_json(data_dir, "math_flagged.json",
                   [f"m_{k:02d}" for k in range(8)])            # ts = file mtime
        everything = coach.collect_review_items(empty_histories())
        queue = coach.build_review_queue(empty_histories())
        assert len(everything) == 21 and len(queue) == coach.REVIEW_CAP == 20
        assert [i["id"] for i in queue[:5]] == [f"ex_{k}" for k in (4, 3, 2, 1, 0)]
        assert [i["id"] for i in queue[5:13]] == [f"q_{k}" for k in range(8)]
        # equal-timestamp tail (file mtime) is ordered by label -> deterministic
        assert [i["id"] for i in queue[13:]] == [f"m_{k:02d}" for k in range(7)]
        assert everything[-1]["id"] == "m_07"                    # the dropped one
        plan = coach.build_plan(empty_histories(), coach.load_state())
        assert (plan["review_total"], plan["review_count"],
                plan["review_dropped"]) == (21, 20, 1)
        assert plan["flagged_total"] == 16 and plan["missed_count"] == 5
        assert plan["flagged_by_app"] == {"math-quiz": 8, "quantum-quiz": 8}

    @pytest.mark.parametrize("content", ["", "{", "null", "{}", "\"str\"", "[]"])
    def test_corrupt_or_empty_flag_and_missed_files_are_tolerated(
            self, data_dir, content):
        for fname in (*self.ALL_FLAG_FILES, "exam_missed.json"):
            (data_dir / fname).write_text(content)
        notes: list[str] = []
        assert coach.load_flagged_items(notes) == []
        expected_notes = 0 if content == "[]" else len(self.ALL_FLAG_FILES)
        assert len(notes) == expected_notes
        assert all(n.startswith("skipped ") and n.endswith("not a readable JSON list")
                   for n in notes)
        assert coach.collect_review_items(empty_histories(), notes) == []
        plan = coach.build_plan(coach.load_histories(), coach.load_state())
        assert plan["review_count"] == plan["flagged_total"] == plan["missed_count"] == 0
        assert len(plan["items"]) == 3                            # starter plan

    def test_render_review_smoke(self, synthetic_dir, capsys):
        notes: list[str] = []
        items = coach.collect_review_items(coach.load_histories(), notes)
        coach.render_review(items, notes)
        out = capsys.readouterr().out
        for i in items:
            assert i["label"] in out
        coach.render_review([], [])
        assert "Nothing due" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Streak
# ---------------------------------------------------------------------------

class TestStreak:
    def test_empty(self):
        assert coach._compute_streaks([]) == (0, 0)
        assert coach._compute_streaks(["garbage"]) == (0, 0)

    def test_today_only(self):
        assert coach._compute_streaks([days_ago(0)]) == (1, 1)

    def test_alive_from_yesterday(self):
        assert coach._compute_streaks([days_ago(1)]) == (1, 1)
        assert coach._compute_streaks([days_ago(3), days_ago(2), days_ago(1)]) == (3, 3)

    def test_broken_when_gap_before_today(self):
        assert coach._compute_streaks([days_ago(3), days_ago(2)]) == (0, 2)

    def test_best_run_tracked_separately(self):
        dates = [days_ago(0), days_ago(5), days_ago(6), days_ago(7), days_ago(8)]
        assert coach._compute_streaks(dates) == (1, 4)

    def test_duplicates_and_invalid_dates_ignored(self):
        dates = [days_ago(0), days_ago(0), "garbage", "2026-13-40", None, 5]
        assert coach._compute_streaks(dates) == (1, 1)
        assert coach._valid_date(days_ago(0)) and not coach._valid_date("x")

    def test_activity_dates_derived_from_history_timestamps(self):
        h = {"a": [{"timestamp": noon_days_ago(2)}, {"date": "bad"}, 3],
             "b": [{"timestamp": noon_days_ago(0), "attempts": []}]}
        assert coach.latest_activity_dates(h) == {days_ago(2), days_ago(0)}

    @pytest.fixture
    def local_tz(self, monkeypatch):
        """Switch this process's local timezone for one test, then restore."""
        if not hasattr(time, "tzset"):
            pytest.skip("time.tzset() is not available on this platform")

        def _set(name: str) -> None:
            monkeypatch.setenv("TZ", name)
            time.tzset()

        yield _set
        monkeypatch.undo()
        time.tzset()

    # circuit-trainer, math-quiz and quantum-quiz record a local "date" plus an
    # ISO-8601 "timestamp" *string*.  Regression guard: whatever the local
    # timezone, a session dated today must be credited to today -- not
    # yesterday (west of UTC) or tomorrow -- because coach._session_day
    # prefers the session's own "date" string over round-tripping a UTC
    # midnight through datetime.fromtimestamp().
    @pytest.mark.parametrize("tz", [
        "UTC",
        "America/Los_Angeles",
        "Pacific/Kiritimati",
    ])
    def test_date_only_sessions_count_on_their_own_date(self, local_tz, tz):
        local_tz(tz)
        today = datetime.now().strftime("%Y-%m-%d")
        iso = datetime.now(timezone.utc).isoformat()
        h = {"math-quiz": [{"date": today, "timestamp": iso, "records": []}],
             "quantum-quiz": [{"date": today, "timestamp": iso, "records": []}],
             "circuit-trainer": [{"date": today, "timestamp": iso,
                                  "attempts": []}]}
        assert coach.latest_activity_dates(h) == {today}, (
            f"TZ={tz}: sessions dated {today} were credited to another day; "
            "coach._session_day must prefer the session's own 'date' string")
        state = {"activity_dates": [], "current_streak": 0, "best_streak": 0}
        coach.update_streak_state(state, h)
        assert state["activity_dates"] == [today]
        assert (state["current_streak"], state["best_streak"]) == (1, 1)

    def test_today_counts_only_with_activity_today(self, data_dir, now):
        state = coach.load_state()
        coach.update_streak_state(
            state, {"qec-trainer": [{"timestamp": noon_days_ago(3), "attempts": []}]})
        assert state["activity_dates"] == [days_ago(3)]
        assert (state["current_streak"], state["best_streak"]) == (0, 1)

        coach.update_streak_state(
            state, {"vqa-trainer": [{"timestamp": now, "attempts": []}]})
        assert days_ago(0) in state["activity_dates"]
        assert state["current_streak"] == 1

    def test_running_the_coach_is_not_activity(self, data_dir):
        state = coach.load_state()
        coach.update_streak_state(state, coach.load_histories())   # empty dir
        assert state["activity_dates"] == [] and state["current_streak"] == 0
        coach.main([])
        saved = coach.load_state()
        assert saved["last_plan_date"] == coach._TODAY
        assert saved["activity_dates"] == [] and saved["current_streak"] == 0

    def test_synthetic_history_gives_current_streak(self, synthetic_dir):
        state = coach.load_state()
        coach.update_streak_state(state, coach.load_histories())
        assert days_ago(0) in state["activity_dates"]
        assert state["current_streak"] >= 1

    def test_best_streak_preserved_and_history_capped(self, data_dir):
        state = coach.load_state()
        state["best_streak"] = 9
        state["activity_dates"] = [days_ago(0), "bad-date"]
        coach.update_streak_state(state, {})
        assert state["activity_dates"] == [days_ago(0)]
        assert (state["current_streak"], state["best_streak"]) == (1, 9)

        state["activity_dates"] = [days_ago(i) for i in range(400, 0, -1)]
        coach.update_streak_state(state, {})
        assert len(state["activity_dates"]) == 365
        assert state["activity_dates"][-1] == days_ago(1)
        assert (state["current_streak"], state["best_streak"]) == (365, 365)


# ---------------------------------------------------------------------------
# CLI (fresh interpreter, QUANTUM_STUDY_DATA_DIR honoured)
# ---------------------------------------------------------------------------

class TestCLI:
    def _run(self, args, tmp_path, stdin=None):
        # COLUMNS pins rich's console width when stdout is a pipe, so the
        # substring checks below do not depend on the caller's terminal.
        env = dict(os.environ, QUANTUM_STUDY_DATA_DIR=str(tmp_path),
                   COLUMNS="200")
        return subprocess.run([sys.executable, *args], cwd=ROOT, env=env,
                              stdin=stdin, capture_output=True, text=True,
                              timeout=60)

    def test_env_var_selects_data_dir(self, tmp_path):
        r = self._run(["-c", "import coach; print(coach.DATA_DIR)"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert Path(r.stdout.strip()) == tmp_path

    def test_plan_and_review_run_on_empty_dir(self, tmp_path):
        # The subprocess stamps its own local date; bracket the call so a run
        # that straddles local midnight accepts either day.
        before = datetime.now().strftime("%Y-%m-%d")
        r = self._run(["coach.py"], tmp_path)
        after = datetime.now().strftime("%Y-%m-%d")
        assert r.returncode == 0, r.stderr
        assert "flashcard-drill" in r.stdout                # starter plan
        state = json.loads((tmp_path / "coach_state.json").read_text())
        assert state["last_plan_date"] in {before, after}
        assert state["activity_dates"] == [] and state["current_streak"] == 0
        assert sorted(p.name for p in tmp_path.iterdir()) == ["coach_state.json"]

        r = self._run(["coach.py", "--review"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert "Nothing due" in r.stdout

    def test_diagnostic_on_eof_stdin_records_all_skipped(self, tmp_path):
        r = self._run(["coach.py", "--diagnostic"], tmp_path,
                      stdin=subprocess.DEVNULL)
        assert r.returncode == 0, r.stderr
        assert "Score: 0/20" in r.stdout
        assert "Recommended docs-ladder starting rung: 'math'" in r.stdout
        state = json.loads((tmp_path / "coach_state.json").read_text())
        diag = state["diagnostic"]
        assert diag["recommended_rung"] == "math"
        assert list(diag["rungs"]) == coach.RUNG_ORDER
        assert sum(r["total"] for r in diag["rungs"].values()) == 20
        assert sum(r["correct"] for r in diag["rungs"].values()) == 0
        assert diag["timestamp"] == approx(time.time(), abs=120)
        # a diagnostic run is not study activity
        assert state["activity_dates"] == [] and state["current_streak"] == 0

    def test_badges_on_eof_stdin_exits_cleanly(self, tmp_path):
        r = self._run(["coach.py", "--badges"], tmp_path,
                      stdin=subprocess.DEVNULL)
        assert r.returncode == 0, r.stderr
        assert "badge tracker" in r.stdout
        for badge in coach.BADGES:
            assert badge in r.stdout, badge
        assert r.stdout.count("[not started]") == len(coach.BADGES)
        state = json.loads((tmp_path / "coach_state.json").read_text())
        assert state["badges"] == {}             # nothing cycled on EOF
        assert sorted(p.name for p in tmp_path.iterdir()) == ["coach_state.json"]

    def test_plan_prints_weakest_categories(self, synthetic_dir, capsys):
        coach.main([])
        out = capsys.readouterr().out
        for cat in ("Transpiler", "grover", "eigenvalues"):
            assert cat in out
        assert coach.load_state()["last_plan_date"] == coach._TODAY


# ---------------------------------------------------------------------------
# Tier-4: exam readiness (--readiness), SM-2 calibration (--calibrate)
# and the default plan's one-line teaser.
#
# Everything is exercised against synthetic data at three densities — none,
# below the thresholds, and rich — because the real data dir is empty.
# ---------------------------------------------------------------------------

# One full C1000-179 exam, split across the eight official sections in
# proportion to their weights (sums to 68).
FULL_EXAM_COUNTS = {"Create circuits": 12, "Quantum operations": 11,
                    "Run circuits": 10, "Sampler": 8, "Estimator": 8,
                    "Visualization": 8, "Results analysis": 7, "OpenQASM": 4}


def full_exam(ts: float, accuracy: float = 0.8, mode: str = "full") -> dict:
    sections, total, correct = {}, 0, 0
    for name, n in FULL_EXAM_COUNTS.items():
        c = int(round(n * accuracy))
        sections[name] = {"total": n, "correct": c}
        total += n
        correct += c
    return {"timestamp": ts, "mode": mode, "total": total, "correct": correct,
            "duration_secs": 4800, "sections": sections}


def dojo_session(ts: float, rows) -> dict:
    attempts = [{"kata_id": f"{sec[:3]}_{i}", "section": sec,
                 "passed": passed, "tries": 1}
                for i, (sec, passed) in enumerate(rows)]
    return {"timestamp": ts, "total": len(attempts),
            "passed": sum(1 for a in attempts if a["passed"]),
            "attempts": attempts}


def fc_session(ts: float, rows) -> dict:
    results = [{"card_id": cid, "category": cat, "rating": rating}
               for cid, cat, rating in rows]
    return {"total": len(results), "timestamp": ts,
            "got_it": sum(1 for r in results if r["rating"] == "got_it"),
            "unsure": sum(1 for r in results if r["rating"] == "unsure"),
            "missed": sum(1 for r in results if r["rating"] == "missed"),
            "results": results}


def rich_histories(now: float) -> dict[str, list]:
    """Multi-week history across all ten apps, dense enough for every view."""
    h = empty_histories()
    h["exam-sim"] = [full_exam(now - d * DAY, acc)
                     for d, acc in ((40, 0.65), (20, 0.75), (4, 0.85))]
    h["qiskit-dojo"] = [
        dojo_session(now - d * DAY,
                     [(sec, (i + j) % 3 != 0)
                      for j, sec in enumerate(FULL_EXAM_COUNTS)]
                     + [("Debugging", True)])
        for i, d in enumerate((35, 21, 14, 7, 2))]
    weeks = [now - d * DAY for d in (2, 9, 16, 23, 30, 37)]
    fc = []
    for i, ts in enumerate(weeks):
        rows = [(f"api_{c}", "Qiskit API",
                 "got_it" if (i + c) % 4 else "missed") for c in range(8)]
        rows += [(f"hw_{c}", "Quantum Hardware", "unsure") for c in range(3)]
        fc.append(fc_session(ts, rows))
    for k in range(3):                     # short-gap repeats
        fc.append(fc_session(now - (1 + k) * DAY,
                             [(f"api_{c}", "Qiskit API", "got_it")
                              for c in range(8)]))
    h["flashcard-drill"] = fc
    h["qec-trainer"] = [{"timestamp": now - 9 * DAY, "attempts": [
        {"problem_id": "q1", "category": "stabilizers", "score": 4}]}]
    h["problem-trainer"] = [{"timestamp": now - 3 * DAY, "attempts": [
        {"problem_id": "p1", "kind": "derivation", "score": 6}]}]
    return h


def write_histories(directory: Path, histories: dict[str, list]) -> None:
    for app, sessions in histories.items():
        if sessions:
            write_json(directory, coach._HISTORY_FILES[app], sessions)


# ---------------------------------------------------------------------------
# Exam readiness
# ---------------------------------------------------------------------------

class TestReadinessWeights:
    def test_official_weights_match_the_certification_blueprint(self):
        assert coach.EXAM_SECTION_WEIGHTS == [
            ("Create circuits", 18), ("Quantum operations", 16),
            ("Run circuits", 15), ("Sampler", 12), ("Estimator", 12),
            ("Visualization", 11), ("Results analysis", 10), ("OpenQASM", 6)]
        assert coach.EXAM_WEIGHT_TOTAL == 100
        assert coach.EXAM_PASS_TOTAL == 68 and coach.EXAM_PASS_CORRECT == 47

    def test_every_section_has_a_next_action(self):
        for name, _w in coach.EXAM_SECTION_WEIGHTS:
            assert coach._SECTION_ACTIONS[name].strip()

    def test_canonical_section_matches_the_real_apps(self):
        # exam-sim/config.py SECTIONS and qiskit-dojo kata sections
        for name, _w in coach.EXAM_SECTION_WEIGHTS:
            assert coach.canonical_section(name) == name
        assert coach.canonical_section("openqasm") == "OpenQASM"
        assert coach.canonical_section("  Create Circuits  ") == "Create circuits"
        assert coach.canonical_section("visualisation") == "Visualization"
        assert coach.canonical_section("qiskit_api") is None
        # dojo has two sections that are not exam sections: never guessed
        assert coach.canonical_section("Debugging") is None
        assert coach.canonical_section("Modernization") is None
        # conftest's synthetic names are not C1000-179 sections
        for bogus in ("Primitives", "Transpiler", "Circuits", "", None, 42):
            assert coach.canonical_section(bogus) is None, bogus

    def test_norm_name_collapses_punctuation_and_case(self):
        assert coach._norm_name("Qiskit API") == "qiskit api"
        assert coach._norm_name("qiskit_api") == "qiskit api"
        assert coach._norm_name(" Qiskit-API  ") == "qiskit api"
        assert coach._norm_name(None) == "none"


class TestSectionEvidence:
    def test_counts_exam_dojo_and_flashcards_separately(self, now):
        h = empty_histories()
        h["exam-sim"] = [full_exam(now - DAY, 0.5)]
        h["qiskit-dojo"] = [dojo_session(now, [("Sampler", True),
                                               ("Sampler", False),
                                               ("Debugging", True)])]
        h["flashcard-drill"] = [fc_session(now, [
            ("a", "Qiskit API", "got_it"), ("b", "qiskit_api", "missed"),
            ("c", "Quantum Hardware", "got_it")])]
        ev = coach.section_evidence(h)
        assert ev["exam"]["Sampler"].n == 8
        assert ev["exam"]["Sampler"].accuracy == approx(0.5)
        assert ev["dojo"]["Sampler"].n == 2
        assert ev["dojo"]["Sampler"].accuracy == approx(0.5)
        # only the qiskit_api category counts, both spellings
        assert ev["flashcard"].n == 2
        assert ev["flashcard"].accuracy == approx(0.5)
        assert ev["unmapped"] == {"Debugging": (1, ["qiskit-dojo"])}

    def test_unmapped_exam_sections_are_reported_not_guessed(self, now):
        h = empty_histories()
        h["exam-sim"] = [{"timestamp": now, "mode": "full", "total": 30,
                          "correct": 15, "sections": {
                              "Primitives": {"total": 20, "correct": 10},
                              "Sampler": {"total": 10, "correct": 5}}}]
        ev = coach.section_evidence(h)
        assert set(ev["exam"]) == {"Sampler"}
        assert ev["unmapped"] == {"Primitives": (20, ["exam-sim"])}

    def test_tolerates_malformed_sessions(self, now):
        h = empty_histories()
        h["exam-sim"] = [None, 5, {"sections": "oops"},
                         {"timestamp": now, "sections": {"Sampler": "nope",
                                                         "Estimator": {}}}]
        h["qiskit-dojo"] = [{"timestamp": now, "attempts": ["x", None, {}]}]
        h["flashcard-drill"] = [{"timestamp": now, "results": "nope"}]
        ev = coach.section_evidence(h)
        assert ev["exam"] == {} and ev["dojo"] == {}
        assert ev["flashcard"].n == 0

    def test_effective_sample_size_discounts_old_sessions(self, now):
        fresh = coach._Evidence()
        fresh.add(1.0, 8.0, 10)
        assert fresh.n == 10 and fresh.n_eff == approx(10.0)
        assert fresh.accuracy == approx(0.8)
        mixed = coach._Evidence()
        mixed.add(1.0, 5.0, 10)     # recent
        mixed.add(0.1, 0.0, 10)     # old, all wrong
        assert mixed.n == 20
        assert mixed.n_eff < 20                     # old evidence counts less
        assert mixed.accuracy > 0.25                # ... and is down-weighted
        empty = coach._Evidence()
        assert empty.accuracy is None and empty.n_eff == 0.0


class TestBuildReadiness:
    def test_empty_history_refuses_a_number(self, data_dir):
        r = coach.build_readiness(empty_histories())
        assert r["confident"] is False
        assert r["projected"] is None and r["low"] is None and r["high"] is None
        assert r["verdict"] == "not enough evidence for a projected score"
        assert r["covered_weight"] == 0 and r["total_direct"] == 0
        assert len(r["thin"]) == 8 and r["measured"] == []
        assert len(r["reasons"]) == 3
        assert all(s["accuracy"] is None for s in r["sections"])

    def test_thin_history_refuses_and_says_what_is_missing(self, data_dir, now):
        h = empty_histories()
        h["exam-sim"] = [{"timestamp": now, "mode": "sprint", "total": 10,
                          "correct": 6, "sections": {
                              "Sampler": {"total": 5, "correct": 3},
                              "Estimator": {"total": 5, "correct": 3}}}]
        r = coach.build_readiness(h)
        assert r["confident"] is False
        assert r["total_direct"] == 10
        assert r["covered_weight"] == 0          # 5 obs each, below the floor
        reasons = " ".join(r["reasons"])
        assert "30 more" in reasons              # 40 - 10
        assert "60 needed" in reasons
        assert {s["name"] for s in r["thin"]} == \
            {name for name, _w in coach.EXAM_SECTION_WEIGHTS}

    def test_one_full_exam_is_enough_for_a_number(self, data_dir, now):
        r = coach.build_readiness({**empty_histories(),
                                   "exam-sim": [full_exam(now - DAY, 0.8)]})
        assert r["confident"] is True
        assert r["total_direct"] == 68
        assert r["covered_weight"] >= coach.READINESS_MIN_COVERED_WEIGHT
        assert r["low"] < r["projected"] < r["high"]
        assert 0.0 <= r["low"] and r["high"] <= 68
        assert r["projected"] == approx(0.8 * 68, abs=4.0)
        # OpenQASM only had 4 questions -> still unmeasured, still flagged
        assert [s["name"] for s in r["thin"]] == ["Results analysis",
                                                  "OpenQASM"]

    def test_two_full_exams_measure_every_section(self, data_dir, now):
        # OpenQASM is only 4 questions per exam, so it is the last section to
        # clear the 8-observation floor -- exactly the honesty it is there for.
        h = {**empty_histories(),
             "exam-sim": [full_exam(now - 10 * DAY, 0.8),
                          full_exam(now - DAY, 0.8)]}
        r = coach.build_readiness(h)
        assert r["confident"] is True
        assert r["thin"] == [] and r["stale_sections"] == []
        assert r["covered_weight"] == 100
        assert r["total_direct"] == 136
        assert all(s["measured"] for s in r["sections"])

    def test_stale_evidence_stops_counting(self, data_dir, now):
        fresh = coach.build_readiness(
            {**empty_histories(), "exam-sim": [full_exam(now - DAY, 0.8)]})
        stale = coach.build_readiness(
            {**empty_histories(),
             "exam-sim": [full_exam(now - 200 * DAY, 0.8)]})
        assert fresh["confident"] is True
        assert stale["confident"] is False
        assert stale["total_direct"] == 68           # raw count is unchanged
        assert stale["covered_weight"] == 0
        assert stale["measured"] == []
        # ... and it is called stale, not thin-on-questions
        names = [s["name"] for s in stale["stale_sections"]]
        assert "Create circuits" in names and "OpenQASM" not in names
        assert "too old to trust" in " ".join(stale["reasons"])
        for s in stale["sections"]:
            if s["n_direct"] >= coach.READINESS_MIN_SECTION_OBS:
                assert s["stale"] is True
                assert s["age_days"] == approx(200, rel=0.05)

    def test_freshness_helpers(self):
        assert coach._evidence_age_days(1.0) == 0.0
        assert coach._evidence_age_days(0.5) == approx(14.0)
        assert coach._evidence_age_days(0.125) == approx(42.0)
        assert coach._evidence_age_days(0.0) == float("inf")
        assert coach._fmt_age(0.0) == "0d"
        assert coach._fmt_age(42.4) == "42d"
        assert coach._fmt_age(float("inf")) == ">1y"
        assert coach.READINESS_MAX_AGE_DAYS == approx(
            coach._evidence_age_days(coach.READINESS_MIN_FRESHNESS))

    def test_band_narrows_as_evidence_grows(self, data_dir, now):
        one = coach.build_readiness({**empty_histories(),
                                     "exam-sim": [full_exam(now - DAY, 0.8)]})
        many = coach.build_readiness(
            {**empty_histories(),
             "exam-sim": [full_exam(now - d * DAY, 0.8)
                          for d in (1, 2, 3, 4, 5, 6)]})
        assert (many["high"] - many["low"]) < (one["high"] - one["low"])

    def test_verdicts_track_the_pass_line(self, data_dir, now):
        strong = coach.build_readiness(
            {**empty_histories(),
             "exam-sim": [full_exam(now - d * DAY, 0.95) for d in (1, 3, 5)]})
        assert strong["verdict"] == "on track to pass"
        weak = coach.build_readiness(
            {**empty_histories(),
             "exam-sim": [full_exam(now - d * DAY, 0.30) for d in (1, 3, 5)]})
        assert weak["verdict"] == "below the pass line"
        borderline = coach.build_readiness(
            {**empty_histories(),
             "exam-sim": [full_exam(now - DAY, 47 / 68)]})
        assert borderline["verdict"] == "too close to call"

    def test_dojo_and_flashcards_are_blended_in(self, data_dir, now):
        base = {**empty_histories(), "exam-sim": [full_exam(now - DAY, 0.5)]}
        plain = coach.build_readiness(base)
        with_dojo = coach.build_readiness({
            **base,
            "qiskit-dojo": [dojo_session(now, [("Sampler", True)] * 6)]})
        sampler_plain = next(s for s in plain["sections"]
                             if s["name"] == "Sampler")
        sampler_dojo = next(s for s in with_dojo["sections"]
                            if s["name"] == "Sampler")
        assert sampler_dojo["accuracy"] > sampler_plain["accuracy"]
        assert sampler_dojo["sources"] == ["exam-sim", "qiskit-dojo"]
        assert sampler_dojo["n_direct"] == 8 + 6

        with_fc = coach.build_readiness({
            **base,
            "flashcard-drill": [fc_session(now, [(f"c{i}", "Qiskit API",
                                                  "got_it")
                                                 for i in range(20)])]})
        sampler_fc = next(s for s in with_fc["sections"]
                          if s["name"] == "Sampler")
        assert sampler_fc["accuracy"] > sampler_plain["accuracy"]
        assert "flashcard-drill" in sampler_fc["sources"]
        # ... but flashcards alone never make a section measurable
        only_fc = coach.build_readiness({
            **empty_histories(),
            "flashcard-drill": [fc_session(now, [(f"c{i}", "Qiskit API",
                                                  "got_it")
                                                 for i in range(50)])]})
        assert only_fc["confident"] is False
        assert all(not s["measured"] for s in only_fc["sections"])
        assert only_fc["total_direct"] == 0

    def test_rich_history_gives_a_number_with_a_band(self, data_dir, now):
        r = coach.build_readiness(rich_histories(now))
        assert r["confident"] is True
        assert r["thin"] == [] and r["covered_weight"] == 100
        assert 0 <= r["low"] < r["projected"] < r["high"] <= 68
        assert r["unmapped"] == {"Debugging": (5, ["qiskit-dojo"])}
        assert r["flashcard_n"] > 0
        for s in r["sections"]:
            assert s["se"] >= coach.READINESS_MIN_SE
            assert 0.0 <= s["accuracy"] <= 1.0

    def test_weak_sections_are_listed_worst_first_with_actions(self, data_dir,
                                                               now):
        h = {**empty_histories(),
             "exam-sim": [full_exam(now - d * DAY, 0.9) for d in (1, 2, 3)]}
        # tank one section
        for session in h["exam-sim"]:
            session["sections"]["OpenQASM"]["correct"] = 0
            session["sections"]["Sampler"]["correct"] = 2
        r = coach.build_readiness(h)
        names = [s["name"] for s in r["weak"]]
        assert names[:2] == ["OpenQASM", "Sampler"]
        for s in r["weak"]:
            assert s["accuracy"] < coach.READINESS_WEAK_ACC
            assert s["action"] == coach._SECTION_ACTIONS[s["name"]]


class TestReadinessRendering:
    @pytest.mark.parametrize("scenario", ["empty", "thin", "stale", "rich"])
    def test_renders_without_crashing(self, data_dir, now, scenario, capsys):
        if scenario == "empty":
            h = empty_histories()
        elif scenario == "thin":
            h = {**empty_histories(),
                 "exam-sim": [full_exam(now - DAY, 0.7, mode="sprint")]}
            h["exam-sim"][0]["sections"] = {"Sampler": {"total": 5,
                                                        "correct": 3}}
        elif scenario == "stale":
            h = {**empty_histories(),
                 "exam-sim": [full_exam(now - 200 * DAY, 0.8)]}
        else:
            h = rich_histories(now)
        coach.render_readiness(coach.build_readiness(h))
        out = capsys.readouterr().out
        assert "Exam Readiness" in out
        for name, _w in coach.EXAM_SECTION_WEIGHTS:
            assert name in out
        if scenario == "rich":
            assert "Projected score" in out
            assert "No projected score" not in out
        else:
            assert "No projected score" in out
            assert "To earn a number" in out
        if scenario == "stale":
            assert f"stale (> {coach.READINESS_MAX_AGE_DAYS}d old)" in out
            assert "too old to trust" in out
            assert "(stale, n=" in out


# ---------------------------------------------------------------------------
# SM-2 calibration
# ---------------------------------------------------------------------------

def recall_history(now: float, gaps_and_ratings) -> list:
    """One session per (gap, rating) chain for a single card per chain."""
    sessions: dict[float, list] = {}
    for idx, (gap, rating) in enumerate(gaps_and_ratings):
        card = f"card_{idx}"
        first, second = now - (gap + 1) * DAY, now - 1 * DAY
        sessions.setdefault(first, []).append((card, "Qiskit API", "got_it"))
        sessions.setdefault(second, []).append((card, "Qiskit API", rating))
    return [fc_session(ts, rows) for ts, rows in sorted(sessions.items())]


class TestRecallObservations:
    def test_pairs_consecutive_reviews_of_the_same_card(self, now):
        sessions = [
            fc_session(now - 20 * DAY, [("a", "Qiskit API", "got_it")]),
            fc_session(now - 10 * DAY, [("a", "Qiskit API", "missed"),
                                        ("b", "Qiskit API", "got_it")]),
            fc_session(now - 2 * DAY, [("a", "Qiskit API", "unsure")]),
        ]
        obs = coach.flashcard_recall_observations(sessions)
        assert [(o["card_id"], round(o["gap_days"]), o["rating"])
                for o in obs] == [("a", 8, "unsure"), ("a", 10, "missed")]
        assert all(o["category"] == "Qiskit API" for o in obs)

    def test_single_sightings_and_junk_yield_nothing(self, now):
        assert coach.flashcard_recall_observations([]) == []
        assert coach.flashcard_recall_observations(
            [fc_session(now, [("a", "c", "got_it")])]) == []
        assert coach.flashcard_recall_observations(
            [None, 4, {"results": "x"},
             {"timestamp": now, "results": [None, {"card_id": "  "},
                                            {"rating": "got_it"}]}]) == []

    def test_sessions_without_timestamps_are_skipped(self):
        assert coach.flashcard_recall_observations(
            [{"results": [{"card_id": "a", "rating": "got_it"}]},
             {"results": [{"card_id": "a", "rating": "missed"}]}]) == []

    def test_bucket_recall_counts_lapses_and_judges_only_at_n(self, now):
        obs = ([{"gap_days": 5.0, "rating": "missed"}] * 3
               + [{"gap_days": 5.0, "rating": "got_it"}] * 5
               + [{"gap_days": 20.0, "rating": "got_it"}] * 2)
        rows = coach.bucket_recall(obs)
        by_label = {r["label"]: r for r in rows}
        assert set(by_label) == {"3-7d", "14-30d"}
        short = by_label["3-7d"]
        assert (short["n"], short["lapses"]) == (8, 3)
        assert short["lapse_rate"] == approx(3 / 8)
        assert short["judged"] is True
        assert short["verdict"] == "intervals too long"
        long = by_label["14-30d"]
        assert long["judged"] is False
        assert long["verdict"] == f"too few (n<{coach.CALIBRATE_MIN_BUCKET_OBS})"

    def test_unsure_is_half_a_success_and_not_a_lapse(self):
        rows = coach.bucket_recall([{"gap_days": 5.0, "rating": "unsure"}] * 10)
        assert rows[0]["lapses"] == 0
        assert rows[0]["lapse_rate"] == 0.0
        assert rows[0]["recall"] == approx(0.5)
        assert rows[0]["verdict"] == "intervals too short"


class TestScheduleFile:
    def test_absent_file_is_tolerated(self, data_dir):
        assert coach.load_schedule() is None
        assert coach.summarise_schedule(None) is None

    @pytest.mark.parametrize("content",
                             ["", "{bad", "null", "[]", '["a"]', "42", '"s"'])
    def test_unreadable_or_wrong_shape_file_is_tolerated(self, data_dir,
                                                         content):
        (data_dir / coach.SCHEDULE_FILE).write_text(content)
        assert coach.load_schedule() is None

    def test_normalises_fields_and_survives_junk_values(self, data_dir, now):
        due = datetime.fromtimestamp(now - DAY, tz=timezone.utc).isoformat()
        write_json(data_dir, coach.SCHEDULE_FILE, {
            "good": {"n": 3, "ef": 2.35, "interval_days": 12.5,
                     "due_iso": due, "last_seen_iso": due, "lapses": 1},
            "junk": {"n": "x", "ef": None, "interval_days": "NaN",
                     "due_iso": 7, "last_seen_iso": [], "lapses": 1e400},
            "not-a-dict": "nope",
        })
        sched = coach.load_schedule()
        assert set(sched) == {"good", "junk"}
        assert sched["good"] == {"n": 3, "ef": approx(2.35),
                                 "interval_days": approx(12.5),
                                 "due_iso": due, "last_seen_iso": due,
                                 "lapses": 1}
        assert sched["junk"]["n"] == 0
        assert sched["junk"]["ef"] == approx(coach.SM2_DEFAULT_EF)
        assert sched["junk"]["interval_days"] == 0.0
        assert sched["junk"]["due_iso"] is None
        assert sched["junk"]["lapses"] == 0

        summary = coach.summarise_schedule(sched)
        assert summary["cards"] == 2
        assert summary["scheduled"] == 1
        assert summary["overdue"] == 1            # "good" is due in the past
        assert summary["lapses"] == 1
        assert summary["relearning"] == 1         # "junk" has n = 0
        assert summary["median_interval"] == approx(12.5)

    def test_median_helper(self):
        assert coach._median([]) is None
        assert coach._median([3.0]) == 3.0
        assert coach._median([1.0, 3.0]) == 2.0
        assert coach._median([5.0, 1.0, 3.0]) == 3.0


class TestBuildCalibration:
    def test_empty_history_refuses_a_verdict(self, data_dir):
        c = coach.build_calibration(empty_histories())
        assert c["confident"] is False
        assert c["n_obs"] == 0 and c["buckets"] == []
        assert c["schedule"] is None and c["schedule_present"] is False
        assert c["schedule_unreadable"] is False
        assert c["stability_days"] is None and c["suggested_ef"] is None
        assert c["verdict"] == "not enough repeat reviews to judge the schedule"
        assert "20 more" in " ".join(c["reasons"])

    def test_thin_history_shows_counts_but_no_verdict(self, data_dir, now):
        h = empty_histories()
        h["flashcard-drill"] = recall_history(
            now, [(5.0, "got_it"), (5.0, "missed"), (5.0, "got_it")])
        c = coach.build_calibration(h)
        assert c["n_obs"] == 3 and c["n_cards"] == 3
        assert c["confident"] is False
        assert [b["n"] for b in c["buckets"]] == [3]
        assert c["buckets"][0]["judged"] is False
        assert "17 more" in " ".join(c["reasons"])

    def test_long_intervals_are_called_out(self, data_dir, now):
        h = empty_histories()
        pairs = ([(2.0, "got_it")] * 10
                 + [(20.0, "missed")] * 8 + [(20.0, "got_it")] * 2)
        h["flashcard-drill"] = recall_history(now, pairs)
        c = coach.build_calibration(h)
        assert c["confident"] is True
        assert c["n_obs"] == 20
        by_label = {b["label"]: b for b in c["buckets"]}
        assert by_label["14-30d"]["verdict"] == "intervals too long"
        assert by_label["1-3d"]["verdict"] == "intervals too short"
        assert c["verdict"] in ("intervals look too long",
                                "intervals look too short",
                                "intervals look about right")
        assert c["observed_interval_days"] is not None

    def test_schedule_is_compared_and_an_ef_is_suggested(self, data_dir, now):
        h = empty_histories()
        pairs = ([(2.0, "got_it")] * 12 + [(2.0, "missed")] * 2
                 + [(20.0, "missed")] * 8 + [(20.0, "got_it")] * 2)
        h["flashcard-drill"] = recall_history(now, pairs)
        write_json(data_dir, coach.SCHEDULE_FILE,
                   {f"card_{i}": {"n": 3, "ef": 2.5, "interval_days": 20.0,
                                  "due_iso": None, "last_seen_iso": None,
                                  "lapses": 1}
                    for i in range(len(pairs))})
        c = coach.build_calibration(h)
        assert c["schedule_present"] is True
        assert c["schedule"]["cards"] == len(pairs)
        assert c["schedule_interval_days"] == approx(20.0)
        assert c["current_ef"] == approx(2.5)
        if c["stability_days"]:
            assert c["schedule_factor"] == approx(
                c["optimal_interval_days"] / 20.0)
            assert coach.SM2_MIN_EF <= c["suggested_ef"] <= coach.SM2_MAX_EF
            assert c["suggested_ef"] < 2.5        # 20d is far too long
        assert c["verdict"] == "intervals look too long"

    def test_refuses_the_fit_when_recall_does_not_track_the_interval(
            self, data_dir, now):
        h = empty_histories()
        # identical recall at every interval: nothing to fit
        pairs = [(2.0, "got_it")] * 10 + [(20.0, "got_it")] * 10
        h["flashcard-drill"] = recall_history(now, pairs)
        c = coach.build_calibration(h)
        assert c["confident"] is True
        assert c["stability_days"] is None
        assert c["suggested_ef"] is None
        assert c["verdict"] == "intervals look too short"   # 0% lapse rate

    def test_thresholds_are_the_documented_ones(self):
        assert coach.CALIBRATE_MIN_OBS == 20
        assert coach.CALIBRATE_MIN_BUCKET_OBS == 8
        assert coach.SM2_TARGET_RECALL == 0.90
        assert coach.CALIBRATE_MIN_R2 == 0.50


class TestCalibrationRendering:
    @pytest.mark.parametrize("scenario", ["empty", "thin", "rich", "corrupt"])
    def test_renders_without_crashing(self, data_dir, now, scenario, capsys):
        h = empty_histories()
        if scenario == "thin":
            h["flashcard-drill"] = recall_history(now, [(5.0, "got_it")] * 3)
        elif scenario in ("rich", "corrupt"):
            h["flashcard-drill"] = recall_history(
                now, [(2.0, "got_it")] * 12 + [(20.0, "missed")] * 10)
            if scenario == "corrupt":
                (data_dir / coach.SCHEDULE_FILE).write_text("[not a dict]")
            else:
                write_json(data_dir, coach.SCHEDULE_FILE,
                           {"card_0": {"n": 2, "ef": 2.4,
                                       "interval_days": 9.0,
                                       "due_iso": None,
                                       "last_seen_iso": None, "lapses": 0}})
        coach.render_calibration(coach.build_calibration(h))
        out = capsys.readouterr().out
        assert "SM-2 Calibration" in out
        assert "Verdict:" in out
        if scenario == "corrupt":
            assert "present but not a readable" in out
        elif scenario == "rich":
            assert "Schedule file:" in out
        else:
            assert "No flashcard_schedule.json yet" in out


# ---------------------------------------------------------------------------
# Default-plan teaser + CLI wiring
# ---------------------------------------------------------------------------

class TestPlanTeaser:
    def test_absent_without_data(self, data_dir):
        assert coach.plan_teaser(empty_histories()) is None
        plan = coach.build_plan(empty_histories(), coach.load_state())
        assert plan["teaser"] is None

    def test_mentions_readiness_gap_when_evidence_is_thin(self, data_dir, now):
        h = {**empty_histories(),
             "exam-sim": [{"timestamp": now, "mode": "sprint", "total": 6,
                           "correct": 3,
                           "sections": {"Sampler": {"total": 6,
                                                    "correct": 3}}}]}
        teaser = coach.plan_teaser(h)
        assert "readiness not scoreable yet" in teaser
        assert "6 obs" in teaser
        assert "--readiness" in teaser

    def test_reports_a_projection_once_it_exists(self, data_dir, now):
        h = {**empty_histories(),
             "exam-sim": [full_exam(now - DAY, 0.8),
                          full_exam(now - 5 * DAY, 0.8)]}
        teaser = coach.plan_teaser(h)
        assert teaser.startswith("readiness ~")
        assert "/68" in teaser and "pass 47" in teaser

    def test_includes_retention_when_items_repeat(self, data_dir, now):
        teaser = coach.plan_teaser(rich_histories(now))
        assert "half-life" in teaser or "this week" in teaser
        assert "`dashboard.py`" in teaser

    def test_plan_stays_deterministic_with_the_teaser(self, data_dir, now):
        h = rich_histories(now)
        write_histories(data_dir, h)
        first = coach.build_plan(coach.load_histories(), coach.load_state())
        second = coach.build_plan(coach.load_histories(), coach.load_state())
        assert first == second
        assert json.dumps(first, sort_keys=True, default=str) == \
            json.dumps(second, sort_keys=True, default=str)
        assert first["teaser"]

    def test_rendered_plan_shows_the_teaser(self, data_dir, now, capsys):
        write_histories(data_dir, rich_histories(now))
        coach.main([])
        out = capsys.readouterr().out
        assert "readiness" in out
        assert "coach.py --readiness" in out


class TestTier4CLI(TestCLI):
    def test_readiness_and_calibrate_run_on_an_empty_dir(self, tmp_path):
        for flag, marker in (("--readiness", "No projected score"),
                             ("--calibrate", "SM-2 Calibration")):
            r = self._run(["coach.py", flag], tmp_path)
            assert r.returncode == 0, r.stderr
            assert marker in r.stdout
        # read-only modes: nothing written, not even coach_state.json
        assert list(tmp_path.iterdir()) == []

    def test_readiness_on_rich_data_prints_a_projection(self, tmp_path, now):
        write_histories(tmp_path, rich_histories(now))
        r = self._run(["coach.py", "--readiness"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert "Projected score:" in r.stdout
        assert "/68" in r.stdout and "pass mark 47/68" in r.stdout
        for name, _w in coach.EXAM_SECTION_WEIGHTS:
            assert name in r.stdout

    def test_calibrate_on_rich_data_prints_buckets(self, tmp_path, now):
        write_histories(tmp_path, rich_histories(now))
        r = self._run(["coach.py", "--calibrate"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert "Measured recall from flashcard_history.json" in r.stdout
        assert "lapse rate" in r.stdout

    def test_modes_remain_mutually_exclusive(self, tmp_path):
        r = self._run(["coach.py", "--readiness", "--calibrate"], tmp_path)
        assert r.returncode != 0
        assert "not allowed with" in r.stderr

    def test_existing_flags_still_work(self, tmp_path):
        for flag in ("--review", "--diagnostic", "--badges"):
            r = self._run(["coach.py", flag], tmp_path,
                          stdin=subprocess.DEVNULL)
            assert r.returncode == 0, (flag, r.stderr)


def test_nan_and_infinity_in_json_never_reach_the_readiness_maths(data_dir,
                                                                  now):
    # json.loads accepts NaN / Infinity, so a hand-edited file can hold them
    sessions = json.loads(
        '[{"timestamp": 1.0, "mode": "full", "total": NaN, "correct": NaN,'
        ' "sections": {"Sampler": {"total": NaN, "correct": 1},'
        '              "Estimator": {"total": 4, "correct": Infinity}}}]')
    ev = coach.section_evidence({**empty_histories(), "exam-sim": sessions})
    assert "Sampler" not in ev["exam"]                  # NaN total dropped
    # timestamp 1.0 is 1970: the 14-day half-life decays its weight to zero,
    # so the questions are still counted but carry no signal
    assert ev["exam"]["Estimator"].n == 4
    assert ev["exam"]["Estimator"].n_eff == 0.0
    assert ev["exam"]["Estimator"].accuracy is None
    assert coach._safe_float(float("nan")) == 0.0
    assert coach._safe_float(float("inf"), 2.5) == 2.5
    assert coach._safe_int(float("nan")) == 0
    r = coach.build_readiness({**empty_histories(), "exam-sim": sessions})
    assert r["confident"] is False
    assert r["total_direct"] == 4
    estimator = next(s for s in r["sections"] if s["name"] == "Estimator")
    assert estimator["freshness"] == 0.0
    assert estimator["measured"] is False


# ---------------------------------------------------------------------------
# Tier-5 signals: --mistakes (error analysis), --calibration (confidence vs
# accuracy) and --item-analysis (exam-bank question difficulty).
#
# The schema and the tolerant loaders live in dashboard.py and are tested
# there; what is asserted here is the ANALYSIS -- the cause breakdown, the
# trend, the confidently-wrong list, the item states, and the way unresolved
# mistakes join the review queue.  Every path is exercised at three
# densities (absent, thin, rich) because the real data dir is empty.
# ---------------------------------------------------------------------------

# The coach snapshots "now" once, at import, into coach._NOW; every trend
# window is measured from it.  Anchoring the fixtures to the same instant
# keeps the windows deterministic for the whole run.
T5_NOW = coach._NOW


def m_entry(ident, app="quantum-quiz", cause="misread", ts=T5_NOW,
            resolved=False, category="Algorithms", **kw):
    return coach.make_mistake_entry(id=ident, app=app, category=category,
                                    cause=cause, timestamp=ts,
                                    resolved=resolved, **kw)


def c_entry(ident, level, correct, app="exam-sim", category="Sampler",
            ts=T5_NOW):
    return coach.make_confidence_entry(id=ident, app=app, category=category,
                                       confidence=level, correct=correct,
                                       timestamp=ts)


def run_coach(args, tmp_path, stdin=None):
    """coach.py in a subprocess against *tmp_path* as the data dir."""
    env = dict(os.environ, QUANTUM_STUDY_DATA_DIR=str(tmp_path),
               COLUMNS="200")
    return subprocess.run([sys.executable, *args], cwd=ROOT, env=env,
                          stdin=stdin, capture_output=True, text=True,
                          timeout=120)


@pytest.fixture
def thin_signals(data_dir):
    """A handful of entries: real, but under every reporting threshold."""
    write_json(data_dir, "mistakes.json", [
        m_entry("Algorithms::grover", cause="misread", ts=T5_NOW - 3 * DAY,
                question="How many Grover iterations for N=4?",
                note="counted the oracle twice"),
        m_entry("cc_depth", app="exam-sim", category="Create circuits",
                cause="didnt_know", ts=T5_NOW - 2 * DAY),
        m_entry("fc_t1", app="flashcard-drill", category="Quantum Hardware",
                cause=None, ts=T5_NOW - DAY),
    ])
    write_json(data_dir, "confidence.json", [
        c_entry("Algorithms::grover", 4, False, app="quantum-quiz",
                category="Algorithms"),
        c_entry("cc_depth", 2, False, category="Create circuits"),
        c_entry("fc_t1", 1, False, app="flashcard-drill",
                category="Quantum Hardware"),
    ])
    return data_dir


@pytest.fixture
def rich_signals(data_dir):
    """Weeks of data: over every threshold, with a shrinking cause."""
    entries = []
    for week in range(4):                       # week 0 oldest
        ts = T5_NOW - (28 - week * 7) * DAY
        for k in range(6 - week):               # misread shrinks 6 -> 3
            entries.append(m_entry(f"mis_{week}_{k}", cause="misread", ts=ts))
        for k in range(2):
            entries.append(m_entry(f"dk_{week}_{k}", app="exam-sim",
                                   category="Sampler", cause="didnt_know",
                                   ts=ts, resolved=(week == 0)))
        entries.append(m_entry(f"un_{week}", app="math-quiz",
                               category="Linear Algebra", cause=None, ts=ts))
    write_json(data_dir, "mistakes.json", entries)

    obs = []
    for i in range(40):                         # level 4: 60% (overconfident)
        obs.append(c_entry(f"c4_{i}", 4, i % 5 < 3, category="Estimator"))
    for i in range(20):                         # level 3: 40% on one topic
        obs.append(c_entry(f"c3_{i}", 3, i % 5 < 2, category="Sampler"))
    for i in range(10):                         # level 1: 20%, calibrated
        obs.append(c_entry(f"c1_{i}", 1, i < 2, category="OpenQASM"))
    write_json(data_dir, "confidence.json", obs)
    return data_dir


class TestSignalLoadingInTheCoach:
    def test_the_coach_reads_its_own_data_dir(self, thin_signals):
        assert coach._path(coach.MISTAKES_FILE).parent == coach.DATA_DIR
        assert [e["id"] for e in coach.load_mistakes()] \
            == ["Algorithms::grover", "cc_depth", "fc_t1"]
        assert len(coach.load_confidence()) == 3

    def test_absent_and_corrupt_files_never_crash_a_report(self, data_dir):
        assert coach.load_mistakes() == [] and coach.load_confidence() == []
        (data_dir / "mistakes.json").write_text("{not json")
        (data_dir / "confidence.json").write_text('{"nope": 1}')
        assert coach.load_mistakes() == [] and coach.load_confidence() == []
        assert coach.build_mistake_report()["n"] == 0
        assert coach.build_confidence_report()["n"] == 0
        assert coach.build_item_analysis()["n_observed"] == 0

    def test_the_schema_helpers_are_the_dashboard_ones(self):
        assert coach.make_mistake_entry is coach.dashboard.make_mistake_entry
        assert coach.MISTAKE_CAUSES == coach.dashboard.MISTAKE_CAUSES
        assert coach.CONFIDENCE_MIN_OBS == 20


class TestMistakeReport:
    def test_empty_report_says_nothing_is_logged(self, data_dir):
        r = coach.build_mistake_report()
        assert r["n"] == 0 and r["by_cause"] == [] and r["concepts"] == []
        assert r["unresolved"] == [] and r["dominant"] is None
        assert any("no mistakes.json" in n for n in r["notes"])

    def test_thin_report_refuses_a_dominant_cause(self, thin_signals):
        r = coach.build_mistake_report()
        assert r["n"] == 3 and r["n_categorised"] == 2
        assert r["dominant"] is None           # < MISTAKE_MIN_DOMINANT
        assert any("are needed before" in n for n in r["notes"])
        assert r["trend"]["judged"] is False

    def test_rich_report_names_the_dominant_cause_and_its_fix(self,
                                                              rich_signals):
        r = coach.build_mistake_report()
        assert r["n"] == 30
        assert r["dominant"] == "misread"
        top = r["by_cause"][0]
        assert (top["cause"], top["n"]) == ("misread", 18)
        assert top["advice"] == coach.CAUSE_ADVICE["misread"]
        assert {row["cause"] for row in r["by_cause"]} \
            == {"misread", "didnt_know", coach.UNCATEGORISED}

    def test_each_cause_lists_the_categories_underneath_it(self,
                                                           rich_signals):
        r = coach.build_mistake_report()
        dk = next(row for row in r["by_cause"] if row["cause"] == "didnt_know")
        assert dk["categories"] == [("Sampler [exam-sim]", 8)]

    def test_every_cause_has_a_what_this_means_line(self):
        for cause in coach.MISTAKE_CAUSES + (coach.UNCATEGORISED,):
            assert coach.CAUSE_ADVICE[cause].strip()
            assert coach.CAUSE_LABELS[cause].strip()
        # the three the brief calls out by name say the right thing
        assert "re-read" in coach.CAUSE_ADVICE["misread"].lower()
        assert "drilling" in coach.CAUSE_ADVICE["knew_but_slipped"]
        assert "chapter" in coach.CAUSE_ADVICE["didnt_know"]

    def test_trend_compares_two_windows_and_names_the_direction(self):
        entries = ([m_entry(f"r{i}", cause="misread", ts=T5_NOW - DAY)
                    for i in range(2)]
                   + [m_entry(f"p{i}", cause="misread", ts=T5_NOW - 20 * DAY)
                      for i in range(5)]
                   + [m_entry(f"g{i}", cause="confused", ts=T5_NOW - 2 * DAY)
                      for i in range(3)])
        trend = coach.mistake_trend(entries, now=T5_NOW)
        rows = {row["cause"]: row for row in trend["rows"]}
        assert trend["judged"] is True and trend["n_dated"] == 10
        assert (rows["misread"]["previous"], rows["misread"]["recent"]) == (5, 2)
        assert rows["misread"]["direction"] == "shrinking"
        assert rows["confused"]["direction"] == "growing"

    def test_trend_ignores_undated_entries_and_ancient_ones(self):
        entries = [m_entry("undated", ts=0.0),
                   m_entry("ancient", ts=T5_NOW - 400 * DAY),
                   m_entry("now", ts=T5_NOW - DAY)]
        trend = coach.mistake_trend(entries, now=T5_NOW)
        assert trend["n_dated"] == 1 and trend["judged"] is False
        r = coach.build_mistake_report(entries)
        assert any("no usable timestamp" in n for n in r["notes"])

    def test_a_flat_cause_is_called_flat(self):
        entries = [m_entry("a", ts=T5_NOW - DAY), m_entry("b", ts=T5_NOW - DAY),
                   m_entry("c", ts=T5_NOW - 20 * DAY),
                   m_entry("d", ts=T5_NOW - 20 * DAY)]
        rows = coach.mistake_trend(entries, now=T5_NOW)["rows"]
        assert rows[0]["direction"] == "flat" and rows[0]["delta"] == 0

    def test_recurring_concepts_rank_repetition_not_recency(self):
        entries = ([m_entry(f"a{i}", category="Algorithms") for i in range(4)]
                   + [m_entry("m1", app="math-quiz",
                              category="Linear Algebra", resolved=True),
                      m_entry("m2", app="math-quiz",
                              category="Linear Algebra")])
        rows = coach.recurring_concepts(entries)
        assert [(r["concept"], r["n"]) for r in rows] \
            == [("Algorithms", 4), ("Linear Algebra", 2)]
        assert rows[0]["n_items"] == 4 and rows[0]["top_cause"] == "misread"
        assert rows[1]["unresolved"] == 1

    def test_an_entry_without_a_category_still_gets_a_concept_row(self):
        rows = coach.recurring_concepts([m_entry("lonely", category="")])
        assert rows[0]["concept"] == "item lonely"

    def test_unresolved_are_listed_oldest_first_and_capped(self, data_dir):
        entries = [m_entry(f"q{i}", ts=T5_NOW - (40 - i) * DAY)
                   for i in range(25)]
        r = coach.build_mistake_report(entries)
        assert len(r["unresolved"]) == 25
        assert len(r["unresolved_shown"]) == coach.MISTAKE_LIST_CAP
        assert r["unresolved_dropped"] == 25 - coach.MISTAKE_LIST_CAP
        stamps = [e["timestamp"] for e in r["unresolved_shown"]]
        assert stamps == sorted(stamps)

    def test_re_answering_correctly_clears_an_item(self, data_dir):
        entries = [m_entry("q1", ts=T5_NOW - 2 * DAY),
                   m_entry("q1", ts=T5_NOW - DAY, resolved=True)]
        r = coach.build_mistake_report(entries)
        assert r["n"] == 2 and r["n_items"] == 1
        assert r["unresolved"] == [] and r["panel"]["n_resolved"] == 1

    @pytest.mark.parametrize("fixture", ["data_dir", "thin_signals",
                                         "rich_signals"])
    def test_renders_at_every_density_without_crashing(self, fixture, request,
                                                       capsys):
        request.getfixturevalue(fixture)
        coach.render_mistake_report(coach.build_mistake_report())
        out = capsys.readouterr().out
        assert "Mistake Journal" in out

    def test_rendered_report_carries_the_analysis(self, rich_signals, capsys):
        coach.render_mistake_report(coach.build_mistake_report())
        out = capsys.readouterr().out
        for marker in ("BY CAUSE", "TOP RECURRING CONCEPTS", "TREND",
                       "UNRESOLVED, OLDEST FIRST", "WHAT THIS MEANS",
                       "misread the question", "shrinking"):
            assert marker in out, marker
        assert coach.CAUSE_ADVICE["misread"].split(".")[0] in out


class TestConfidenceReport:
    def test_empty_report_is_honest(self, data_dir):
        c = coach.build_confidence_report()
        assert c["n"] == 0 and c["confidently_wrong"] == []
        assert c["enough"] is False and c["overconfidence"] is None
        assert any("no confidence.json" in n for n in c["notes"])

    def test_refuses_an_index_below_the_documented_floor(self, thin_signals):
        c = coach.build_confidence_report()
        assert c["n"] == 3 and c["enough"] is False
        assert c["min_obs"] == 20 and "20 needed" in c["verdict"]
        assert all(not row["judged"] for row in c["levels"])
        # the confidently-wrong list is still reported: it is fact
        assert c["n_confidently_wrong"] == 1
        assert c["confidently_wrong"][0]["category"] == "Algorithms"

    def test_rich_data_measures_accuracy_per_level(self, rich_signals):
        c = coach.build_confidence_report()
        assert c["n"] == 70 and c["enough"] is True
        rows = {row["level"]: row for row in c["levels"]}
        assert rows[4]["n"] == 40 and rows[4]["accuracy"] == approx(0.6)
        assert rows[4]["judged"] and rows[4]["gap"] == approx(-0.35)
        assert rows[3]["accuracy"] == approx(0.4)
        assert rows[1]["accuracy"] == approx(0.2)
        assert rows[2]["n"] == 0 and rows[2]["judged"] is False
        assert c["verdict"] == "overconfident"
        assert c["overconfidence"] > 20
        assert 0.0 <= c["brier"] <= 1.0

    def test_confidently_wrong_topics_are_the_headline(self, rich_signals):
        c = coach.build_confidence_report()
        top = c["confidently_wrong"][0]
        assert top["category"] == "Estimator" and top["app"] == "exam-sim"
        assert top["n"] == 16 and top["mean_confidence"] == approx(4.0)
        assert c["n_confidently_wrong"] == 16 + 12
        assert c["confident_error_rate"] == approx(28 / 60)
        assert c["worst_items"][0]["max_confidence"] >= coach.CONFIDENT_LEVEL

    def test_a_well_calibrated_learner_is_told_so(self, data_dir):
        obs = ([c_entry(f"a{i}", 4, i < 19) for i in range(20)]
               + [c_entry(f"b{i}", 2, i < 5) for i in range(10)])
        c = coach.build_confidence_report(obs)
        assert c["verdict"] == "well calibrated"
        assert abs(c["overconfidence"]) < 10
        # "well calibrated" is not "never wrong": the one confident miss is
        # still named, because that is the list worth reading.
        assert [(r["category"], r["n"]) for r in c["confidently_wrong"]] \
            == [("Sampler", 1)]
        assert c["confident_error_rate"] == approx(1 / 20)

    def test_lists_are_capped_with_the_overflow_reported(self, data_dir):
        obs = [c_entry(f"q{i}", 4, False, category=f"topic{i}")
               for i in range(30)]
        c = coach.build_confidence_report(obs)
        assert len(c["confidently_wrong"]) == 30
        assert len(c["confidently_wrong_shown"]) == coach.CONFIDENTLY_WRONG_CAP
        assert c["confidently_wrong_dropped"] == 30 - coach.CONFIDENTLY_WRONG_CAP

    @pytest.mark.parametrize("fixture", ["data_dir", "thin_signals",
                                         "rich_signals"])
    def test_renders_at_every_density_without_crashing(self, fixture, request,
                                                       capsys):
        request.getfixturevalue(fixture)
        coach.render_confidence_report(coach.build_confidence_report())
        assert "Confidence Calibration" in capsys.readouterr().out

    def test_rendered_report_shows_the_table_and_the_money_list(
            self, rich_signals, capsys):
        coach.render_confidence_report(coach.build_confidence_report())
        out = capsys.readouterr().out
        assert "CONFIDENTLY WRONG" in out and "unknown unknowns" in out
        assert "OVERconfident" in out          # judgement in text, not colour
        assert "overconfidence index" in out
        assert "25/50/75/95%" in out
        assert "Estimator" in out

    def test_a_thin_render_states_the_floor_rather_than_a_number(
            self, thin_signals, capsys):
        coach.render_confidence_report(coach.build_confidence_report())
        out = capsys.readouterr().out
        assert "20 needed" in out
        assert "not judged" in out
        assert "overconfidence index" not in out


class TestExamBank:
    def test_the_real_bank_parses_to_three_hundred_questions(self):
        bank = coach.load_exam_bank()
        assert len(bank) == 300
        assert len({q["id"] for q in bank}) == 300
        assert len({q["section"] for q in bank}) == 8
        assert all(q["n_options"] == 4 for q in bank)
        assert all(q["difficulty"] in ("easy", "medium", "hard") for q in bank)

    def test_a_missing_bank_is_not_an_error(self, tmp_path):
        assert coach.load_exam_bank(tmp_path / "nope") == []

    def test_questions_are_parsed_not_imported(self, tmp_path):
        section = tmp_path / "sec"
        section.mkdir()
        (section / "__init__.py").write_text("raise RuntimeError('never')")
        (section / "q1.py").write_text(
            "import does_not_exist\n"
            "from core.models import Question\n"
            "QUESTION = Question(id='q1', section='Sampler',\n"
            "                    options=['a', 'b', 'c', 'd'],\n"
            "                    correct_index=0, question='?',\n"
            "                    explanation='', difficulty='hard')\n")
        (section / "broken.py").write_text("def (((")
        (section / "notaquestion.py").write_text("X = 1\n")
        bank = coach.load_exam_bank(tmp_path)
        assert bank == [{"id": "q1", "section": "Sampler",
                         "difficulty": "hard", "n_options": 4}]

    def test_a_question_built_from_non_literals_is_skipped(self, tmp_path):
        section = tmp_path / "sec"
        section.mkdir()
        (section / "q.py").write_text(
            "QUESTION = Question(id=SOME_CONSTANT, section='Sampler')\n")
        assert coach.load_exam_bank(tmp_path) == []


class TestItemAnalysis:
    BANK = [{"id": "q_missed", "section": "Sampler", "difficulty": "hard",
             "n_options": 4},
            {"id": "q_easy", "section": "Sampler", "difficulty": "easy",
             "n_options": 4},
            {"id": "q_mixed", "section": "Estimator", "difficulty": "medium",
             "n_options": 4},
            {"id": "q_thin", "section": "OpenQASM", "difficulty": "easy",
             "n_options": 4},
            {"id": "q_unseen", "section": "OpenQASM", "difficulty": "easy",
             "n_options": 4}]

    def analysis(self, **kw):
        kw.setdefault("bank", self.BANK)
        kw.setdefault("confidence", [])
        kw.setdefault("mistakes", [])
        kw.setdefault("missed", [])
        return coach.build_item_analysis(**kw)

    def test_no_attempts_means_every_item_is_never_attempted(self):
        a = self.analysis()
        assert len(a["never_attempted"]) == 5 and a["n_observed"] == 0
        assert a["always_missed"] == [] and a["always_correct"] == []
        assert any("no per-question exam attempts" in n for n in a["notes"])

    def test_the_four_states_are_separated(self):
        obs = ([c_entry("q_missed", 3, False) for _ in range(4)]
               + [c_entry("q_easy", 4, True) for _ in range(3)]
               + [c_entry("q_mixed", 2, i % 2 == 0, category="Estimator")
                  for i in range(4)]
               + [c_entry("q_thin", 2, False, category="OpenQASM")])
        a = self.analysis(confidence=obs)
        assert [r["id"] for r in a["always_missed"]] == ["q_missed"]
        assert [r["id"] for r in a["always_correct"]] == ["q_easy"]
        assert [r["id"] for r in a["mixed"]] == ["q_mixed"]
        assert [r["id"] for r in a["needs_more"]] == ["q_thin"]
        assert [r["id"] for r in a["never_attempted"]] == ["q_unseen"]
        assert a["min_attempts"] == 3
        missed = a["always_missed"][0]
        assert (missed["attempts"], missed["correct"]) == (4, 0)
        assert missed["p_value"] == 0.0 and missed["difficulty"] == "hard"

    def test_two_attempts_is_never_a_verdict(self):
        a = self.analysis(confidence=[c_entry("q_missed", 3, False)
                                      for _ in range(2)])
        assert [r["id"] for r in a["needs_more"]] == ["q_missed"]
        assert a["always_missed"] == []

    def test_only_exam_sim_rows_count(self):
        obs = [c_entry("q_missed", 3, False, app="quantum-quiz")
               for _ in range(4)]
        a = self.analysis(confidence=obs)
        assert a["n_observed"] == 0

    def test_the_journal_fills_in_for_ungraded_items(self):
        mistakes = [m_entry("q_missed", app="exam-sim", category="Sampler",
                            cause="didnt_know"),
                    m_entry("q_easy", app="exam-sim", category="Sampler",
                            resolved=True)]
        a = self.analysis(mistakes=mistakes,
                          missed=[{"question_id": "q_mixed",
                                   "section": "Estimator",
                                   "timestamp": T5_NOW}])
        rows = {r["id"]: r for r in a["items"]}
        assert (rows["q_missed"]["attempts"], rows["q_missed"]["correct"]) \
            == (1, 0)
        assert (rows["q_easy"]["attempts"], rows["q_easy"]["correct"]) == (2, 1)
        assert rows["q_mixed"]["attempts"] == 1
        assert rows["q_missed"]["sources"] == ["mistakes.json"]
        assert rows["q_mixed"]["sources"] == ["exam_missed.json"]
        assert a["n_graded"] == 0
        assert any("journal evidence" in n for n in a["notes"])

    def test_graded_attempts_win_over_journal_evidence(self):
        obs = [c_entry("q_missed", 3, True) for _ in range(3)]
        a = self.analysis(confidence=obs,
                          mistakes=[m_entry("q_missed", app="exam-sim")],
                          missed=[{"question_id": "q_missed",
                                   "timestamp": T5_NOW}])
        row = next(r for r in a["items"] if r["id"] == "q_missed")
        assert (row["attempts"], row["correct"], row["graded"]) == (3, 3, 3)
        assert row["sources"] == ["confidence.json"]

    def test_an_id_that_left_the_bank_is_reported_not_hidden(self):
        a = self.analysis(confidence=[c_entry("q_retired", 4, False)
                                      for _ in range(3)])
        assert a["unknown_ids"] == ["q_retired"]
        row = next(r for r in a["items"] if r["id"] == "q_retired")
        assert row["in_bank"] is False and row["section"] == "Sampler"
        assert any("not in the bank" in n for n in a["notes"])

    def test_section_rollup_counts_coverage_and_accuracy(self):
        obs = ([c_entry("q_missed", 3, False) for _ in range(4)]
               + [c_entry("q_easy", 4, True) for _ in range(4)])
        a = self.analysis(confidence=obs)
        sampler = next(s for s in a["sections"] if s["section"] == "Sampler")
        assert (sampler["items"], sampler["attempted"]) == (2, 2)
        assert (sampler["attempts"], sampler["correct"]) == (8, 4)
        assert sampler["p_value"] == approx(0.5)

    def test_an_absent_bank_still_analyses_what_was_answered(self):
        a = self.analysis(bank=[],
                          confidence=[c_entry("q_x", 3, False)
                                      for _ in range(3)])
        assert a["bank_present"] is False and a["bank_size"] == 0
        assert [r["id"] for r in a["always_missed"]] == ["q_x"]
        assert any("exam bank not found" in n for n in a["notes"])

    def test_runs_against_the_real_bank_and_an_empty_dir(self, data_dir):
        a = coach.build_item_analysis()
        assert a["bank_size"] == 300 and a["bank_present"] is True
        assert len(a["never_attempted"]) == 300

    @pytest.mark.parametrize("fixture", ["data_dir", "thin_signals",
                                         "rich_signals"])
    def test_renders_at_every_density_without_crashing(self, fixture, request,
                                                       capsys):
        request.getfixturevalue(fixture)
        coach.render_item_analysis(coach.build_item_analysis())
        out = capsys.readouterr().out
        assert "Item Analysis" in out
        for marker in ("ALWAYS MISSED", "ALWAYS CORRECT", "MIXED",
                       "NEEDS MORE ATTEMPTS", "NEVER ATTEMPTED"):
            assert marker in out, marker


class TestMistakesInTheReviewQueue:
    def test_unresolved_mistakes_join_the_queue(self, data_dir):
        write_json(data_dir, "mistakes.json",
                   [m_entry("open_one", ts=T5_NOW - 5 * DAY),
                    m_entry("closed_one", ts=T5_NOW - 4 * DAY, resolved=True)])
        items = coach.collect_review_items(empty_histories())
        assert [(i["app"], i["id"]) for i in items] \
            == [("quantum-quiz", "open_one")]
        assert items[0]["why"] == "mistake: misread the question"
        assert items[0]["category"] == "Algorithms"

    def test_an_uncategorised_mistake_still_reaches_the_queue(self, data_dir):
        write_json(data_dir, "mistakes.json", [m_entry("q", cause=None)])
        items = coach.collect_review_items(empty_histories())
        assert items[0]["why"] == "mistake: cause not set"

    def test_the_question_text_becomes_the_label(self, data_dir):
        write_json(data_dir, "mistakes.json",
                   [m_entry("id_only"),
                    m_entry("with_q", question="Why is this wrong?")])
        labels = {i["id"]: i["label"]
                  for i in coach.collect_review_items(empty_histories())}
        assert labels == {"id_only": "id_only",
                          "with_q": "Why is this wrong?"}

    def test_a_flagged_item_is_not_repeated_as_a_mistake(self, data_dir):
        write_json(data_dir, "quiz_flagged.json",
                   [{"id": "dup", "label": "Grover count",
                     "category": "Algorithms", "app": "quantum-quiz",
                     "timestamp": T5_NOW - 9 * DAY}])
        write_json(data_dir, "mistakes.json",
                   [m_entry("dup", ts=T5_NOW - DAY),
                    m_entry("fresh", ts=T5_NOW - DAY)])
        items = coach.collect_review_items(empty_histories())
        assert [i["id"] for i in items] == ["dup", "fresh"]
        assert items[0]["why"] == "flagged"        # the flag kept its row
        assert items[1]["why"].startswith("mistake: ")

    def test_an_exam_miss_is_not_repeated_as_a_mistake(self, data_dir):
        write_json(data_dir, "exam_missed.json",
                   [{"question_id": "ex_7", "section": "Sampler",
                     "timestamp": T5_NOW - 3 * DAY}])
        write_json(data_dir, "mistakes.json",
                   [m_entry("ex_7", app="exam-sim", category="Sampler",
                            ts=T5_NOW - DAY)])
        items = coach.collect_review_items(empty_histories())
        assert len(items) == 1 and items[0]["why"] == "missed exam question"

    def test_the_plan_counts_and_advertises_the_journal(self, data_dir):
        write_json(data_dir, "mistakes.json",
                   [m_entry(f"q{i}", ts=T5_NOW - i * DAY) for i in range(3)])
        plan = coach.build_plan(empty_histories(), coach.load_state())
        assert plan["mistake_total"] == 3 and plan["mistake_unresolved"] == 3
        assert "3 from the mistake journal" in plan["items"][0]

    def test_the_synthetic_queue_is_unchanged_without_a_journal(
            self, synthetic_dir):
        plan = coach.build_plan(coach.load_histories(), coach.load_state())
        assert plan["review_count"] == plan["review_total"] == 9
        assert plan["mistake_total"] == 0 and plan["signals"] is None


class TestSignalsTeaser:
    def test_absent_without_data(self, data_dir):
        assert coach.signals_teaser() is None
        plan = coach.build_plan(empty_histories(), coach.load_state())
        assert plan["signals"] is None
        assert plan["confidently_wrong"] == 0

    def test_leads_with_the_confidently_wrong_count(self, data_dir):
        write_json(data_dir, "confidence.json",
                   [c_entry("a", 4, False, category="Sampler"),
                    c_entry("b", 4, False, category="Estimator"),
                    c_entry("c", 3, False, category="OpenQASM"),
                    c_entry("d", 4, True, category="OpenQASM")])
        teaser = coach.signals_teaser()
        assert "3 confidently-wrong topic(s)" in teaser
        assert "`coach.py --calibration`" in teaser

    def test_mentions_the_mistake_journal_and_its_top_cause(self, data_dir):
        write_json(data_dir, "mistakes.json",
                   [m_entry("a", cause="knew_but_slipped"),
                    m_entry("b", cause="knew_but_slipped"),
                    m_entry("c", cause="confused")])
        teaser = coach.signals_teaser()
        assert "3 unresolved mistake(s)" in teaser
        assert "top cause: knew it but slipped (2)" in teaser
        assert "`coach.py --mistakes`" in teaser

    def test_clean_confidence_data_still_says_something(self, data_dir):
        write_json(data_dir, "confidence.json",
                   [c_entry(f"q{i}", 4, True) for i in range(3)])
        assert "none confidently wrong" in coach.signals_teaser()

    def test_the_rendered_plan_shows_the_line(self, rich_signals, capsys):
        plan = coach.build_plan(empty_histories(), coach.load_state())
        coach.render_plan(plan, coach.load_state())
        out = capsys.readouterr().out
        assert plan["signals"] in out
        assert "Signals:" in out

    def test_the_plan_stays_deterministic(self, rich_signals):
        state = coach.load_state()
        first = coach.build_plan(coach.load_histories(), state)
        second = coach.build_plan(coach.load_histories(), state)
        assert first == second


class TestTier5CLI:
    FLAGS = ("--mistakes", "--calibration", "--item-analysis")

    @pytest.mark.parametrize("flag,marker", [
        ("--mistakes", "Mistake Journal"),
        ("--calibration", "Confidence Calibration"),
        ("--confidence", "Confidence Calibration"),
        ("--item-analysis", "Item Analysis"),
    ])
    def test_every_new_flag_runs_on_an_empty_dir(self, tmp_path, flag,
                                                 marker):
        r = run_coach(["coach.py", flag], tmp_path)
        assert r.returncode == 0, r.stderr
        assert marker in r.stdout
        # read-only modes: not even coach_state.json is written
        assert list(tmp_path.iterdir()) == []

    def test_the_new_modes_are_mutually_exclusive_with_the_old(self,
                                                               tmp_path):
        r = run_coach(["coach.py", "--mistakes", "--readiness"], tmp_path)
        assert r.returncode != 0 and "not allowed with" in r.stderr
        r = run_coach(["coach.py", "--calibration", "--calibrate"], tmp_path)
        assert r.returncode != 0 and "not allowed with" in r.stderr

    def test_calibrate_and_calibration_stay_distinct(self, tmp_path):
        sm2 = run_coach(["coach.py", "--calibrate"], tmp_path)
        conf = run_coach(["coach.py", "--calibration"], tmp_path)
        assert sm2.returncode == 0 and conf.returncode == 0
        assert "SM-2 Calibration" in sm2.stdout
        assert "SM-2 Calibration" not in conf.stdout
        assert "did you know that you knew" in conf.stdout

    def test_every_pre_existing_flag_still_works(self, tmp_path):
        for flag in ("--review", "--readiness", "--calibrate", "--badges",
                     "--diagnostic"):
            r = run_coach(["coach.py", flag], tmp_path,
                          stdin=subprocess.DEVNULL)
            assert r.returncode == 0, (flag, r.stderr)

    def test_end_to_end_on_a_populated_dir(self, tmp_path):
        write_json(tmp_path, "mistakes.json",
                   [m_entry(f"q{i}", cause="misread", ts=T5_NOW - i * DAY)
                    for i in range(6)])
        write_json(tmp_path, "confidence.json",
                   [c_entry(f"e{i}", 4, i < 5, category="Estimator")
                    for i in range(25)])
        r = run_coach(["coach.py", "--mistakes"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert "misread the question" in r.stdout
        assert "Slow down and re-read" in r.stdout

        r = run_coach(["coach.py", "--calibration"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert "overconfident" in r.stdout
        assert "Estimator" in r.stdout

        r = run_coach(["coach.py", "--review"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert "mistake: misread the question" in r.stdout

        r = run_coach(["coach.py"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert "Signals:" in r.stdout
        # only the coach's own state file is ever written
        assert sorted(p.name for p in tmp_path.iterdir()) == [
            "coach_state.json", "confidence.json", "mistakes.json"]

    def test_dashboard_renders_the_panels_end_to_end(self, tmp_path):
        write_json(tmp_path, "mistakes.json", [m_entry("a", cause="confused")])
        write_json(tmp_path, "confidence.json",
                   [c_entry("q", 4, False, category="Sampler")])
        r = run_coach(["dashboard.py", "--no-retention"], tmp_path)
        assert r.returncode == 0, r.stderr
        assert "MISTAKES BY CAUSE" in r.stdout
        assert "CONFIDENCE CALIBRATION" in r.stdout
        assert sorted(p.name for p in tmp_path.iterdir()) == [
            "confidence.json", "mistakes.json"]
