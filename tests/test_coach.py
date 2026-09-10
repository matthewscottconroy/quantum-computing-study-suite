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
