"""Tests for dashboard.py — cross-app mastery report.

dashboard.py only ever reads history files; tests point its ``_FILES`` map at
a temporary directory (conftest ``data_dir`` / ``synthetic_dir``).
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

import dashboard
from dashboard import AppStats, DashboardReport, build_report

DAY = 86400.0
approx = pytest.approx

APPS = ["QEC Trainer", "VQA Trainer", "Flashcard Drill", "Circuit Trainer",
        "Math Quiz", "Quantum Quiz", "Paper Drill", "Qiskit Dojo",
        "Exam Simulator", "Problem Trainer"]


# ---------------------------------------------------------------------------
# File map + build_report
# ---------------------------------------------------------------------------

def test_files_map_lists_ten_apps_under_data_dir():
    assert list(dashboard._FILES) == APPS
    assert len({p.name for p in dashboard._FILES.values()}) == 10
    assert all(p.parent == dashboard.DATA_DIR for p in dashboard._FILES.values())
    # Suite convention: ~/.local/share/quantum-study, overridable through
    # QUANTUM_STUDY_DATA_DIR (conftest exports it before import; coach.py and
    # the apps honour it).  Accept either so that aligning dashboard.py with
    # coach.py does not turn this test red.
    assert dashboard.DATA_DIR in (
        Path(os.environ["QUANTUM_STUDY_DATA_DIR"]),
        Path.home() / ".local" / "share" / "quantum-study")


def test_empty_dir_gives_graceful_empty_report(data_dir):
    report = build_report()
    assert isinstance(report, DashboardReport)
    assert [a.name for a in report.apps] == APPS
    for app in report.apps:
        assert isinstance(app, AppStats)
        assert (app.sessions, app.total_attempts, app.weighted_avg,
                app.timestamps, app.file_present) == (0, 0, 0.0, [], False)
    assert report.weakest_topics == []
    assert report.recent_apps == {}
    assert report.streak_days == 0


@pytest.mark.parametrize("content", ["{oops", "{}", "", "null"])
def test_corrupt_files_count_as_present_but_empty(data_dir, content):
    for path in dashboard._FILES.values():
        path.write_text(content)
    report = build_report()
    assert all(a.file_present for a in report.apps)
    assert all(a.sessions == 0 and a.total_attempts == 0 for a in report.apps)
    assert report.weakest_topics == [] and report.recent_apps == {}


def test_synthetic_dir_covers_all_ten_apps(synthetic_dir, payloads):
    report = build_report()
    by_name = {a.name: a for a in report.apps}
    assert list(by_name) == APPS
    for app in report.apps:
        assert app.file_present, app.name
        assert app.sessions >= 1 and app.total_attempts >= 1, app.name
        assert 0.0 <= app.weighted_avg <= 10.0, app.name

    def n_items(fname, key):
        return sum(len(s[key]) for s in payloads[fname])

    assert by_name["QEC Trainer"].total_attempts == n_items("qec_history.json", "attempts")
    assert by_name["VQA Trainer"].total_attempts == n_items("vqa_history.json", "attempts")
    assert by_name["Flashcard Drill"].total_attempts == n_items("flashcard_history.json", "results")
    assert by_name["Circuit Trainer"].total_attempts == n_items("trainer_history.json", "attempts")
    assert by_name["Math Quiz"].total_attempts == n_items("math_history.json", "records")
    assert by_name["Quantum Quiz"].total_attempts == n_items("quiz_history.json", "records")
    assert by_name["Paper Drill"].total_attempts == n_items("paper_history.json", "scores")
    assert by_name["Qiskit Dojo"].total_attempts == n_items("dojo_history.json", "attempts")
    assert by_name["Problem Trainer"].total_attempts == n_items("problems_history.json", "attempts")
    assert by_name["Exam Simulator"].total_attempts == sum(
        s["total"] for s in payloads["exam_history.json"])
    assert by_name["QEC Trainer"].sessions == len(payloads["qec_history.json"])
    assert by_name["Paper Drill"].timestamps == []        # schema has no timestamp
    assert by_name["Paper Drill"].weighted_avg == approx(6.0)
    # circuit-trainer / math-quiz / quantum-quiz write an ISO-8601 *string*
    # "timestamp" (rejected by float()) next to a local "date": every session
    # must still yield exactly one timestamp, via the "date" fallback, and a
    # near-full weight (dated today).
    for app, fname in (("Circuit Trainer", "trainer_history.json"),
                       ("Math Quiz", "math_history.json"),
                       ("Quantum Quiz", "quiz_history.json")):
        sessions = payloads[fname]
        assert all(isinstance(s["timestamp"], str) for s in sessions), fname
        expected = [dashboard._session_timestamp({"date": s["date"]})
                    for s in sessions]
        assert by_name[app].timestamps == expected, app
        assert len(by_name[app].timestamps) == len(sessions) == 1, app
        for s in sessions:
            assert dashboard._session_weight(s) == approx(
                dashboard._session_weight({"date": s["date"]}))
            assert dashboard._session_weight(s) > 0.9


def test_weakest_topics_sorted_and_prefixed(synthetic_dir):
    report = build_report()
    assert 1 <= len(report.weakest_topics) <= 5
    avgs = [avg for _, avg in report.weakest_topics]
    assert avgs == sorted(avgs)
    prefixes = {label.split("]")[0] + "]" for label, _ in report.weakest_topics}
    assert prefixes <= {"[QEC]", "[VQA]", "[FC]"}
    topics = dict(report.weakest_topics)
    assert topics["[QEC] stabilizers"] == approx(2.5)
    assert topics["[FC] hardware"] == approx(2.5)
    assert topics["[VQA] ansatz"] == approx(3.0)
    assert "[FC] algorithms" not in topics                # 10/10, cut by top-5


def test_recent_activity_window(synthetic_dir):
    report = build_report()
    assert set(report.recent_apps) == set(APPS) - {"Paper Drill"}
    assert report.recent_apps["QEC Trainer"] == 3         # 10-day-old session excluded
    assert report.recent_apps["Exam Simulator"] == 68 + 10
    assert report.recent_apps["Flashcard Drill"] == 3


def test_streak_counts_today(synthetic_dir):
    # dashboard bins activity days *and* "today" in UTC.  The synthetic
    # payload's newest timestamp is now-60 s and its date-only sessions map to
    # UTC midnight of the *local* date, so for ~60 s after 00:00 UTC on a
    # machine west of UTC none of them fall on today-UTC.  Add one session
    # anchored one second into today-UTC so the assertion holds at any time
    # of day in any timezone.
    start_of_today_utc = datetime.now(tz=timezone.utc).replace(
        hour=0, minute=0, second=1, microsecond=0).timestamp()
    dashboard._FILES["VQA Trainer"].write_text(json.dumps([
        {"timestamp": start_of_today_utc, "total": 1, "correct": 1,
         "attempts": [{"problem_id": "vqa_x", "category": "ansatz",
                       "score": 8}]}]))
    assert build_report().streak_days >= 1


def test_streak_zero_without_recent_activity(data_dir, now):
    dashboard._FILES["QEC Trainer"].write_text(
        '[{"timestamp": %f, "attempts": [{"category": "x", "score": 5}]}]'
        % (now - 3 * DAY))
    report = build_report()
    assert report.streak_days == 0
    assert report.recent_apps == {"QEC Trainer": 1}
    assert report.weakest_topics == [("[QEC] x", approx(5.0))]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def test_session_weight_half_life():
    now = dashboard._NOW
    assert dashboard._HALF_LIFE_DAYS == 14.0
    assert dashboard._session_weight({"timestamp": now}) == approx(1.0, abs=1e-6)
    assert dashboard._session_weight({"timestamp": now - 14 * DAY}) == approx(0.5, rel=1e-6)
    assert dashboard._session_weight({"timestamp": now - 28 * DAY}) == approx(0.25, rel=1e-6)
    assert dashboard._session_weight({}) == 0.1
    assert dashboard._session_weight({"title": "paper"}) == 0.1
    assert dashboard._session_weight({"timestamp": "abc", "date": "nope"}) == 0.1
    # Derive the date from _NOW itself (snapshotted at import) so the session's
    # UTC midnight is 0..1 days before _NOW by construction, even if the UTC
    # date rolled over between import and this test.
    today_utc = datetime.fromtimestamp(now, tz=timezone.utc).strftime("%Y-%m-%d")
    w = dashboard._session_weight({"timestamp": None, "date": today_utc})
    assert math.exp(-math.log(2) / 14) <= w <= 1.0


def test_session_timestamp_parsing():
    assert dashboard._session_timestamp({"timestamp": "123.5"}) == 123.5
    assert dashboard._session_timestamp({"timestamp": 7}) == 7.0
    expect = datetime(2026, 1, 2, tzinfo=timezone.utc).timestamp()
    assert dashboard._session_timestamp({"timestamp": None, "date": "2026-01-02"}) == expect
    assert dashboard._session_timestamp({"timestamp": "x", "date": "2026-01-02"}) == expect
    assert dashboard._session_timestamp({"date": "02/01/2026"}) is None
    assert dashboard._session_timestamp({}) is None


def test_bar_scales_and_clamps():
    assert dashboard._bar(0) == ("░" * 10, 0)
    assert dashboard._bar(10) == ("█" * 10, 100)
    assert dashboard._bar(5) == ("█" * 5 + "░" * 5, 50)
    assert dashboard._bar(12) == ("█" * 10, 100)
    assert dashboard._bar(-1) == ("░" * 10, 0)
    assert dashboard._bar(5, max_score=0) == ("░" * 10, 0)
    assert dashboard._bar(50, max_score=100, width=4) == ("██░░", 50)


def test_extract_exam_clamps_and_skips_bad_sessions():
    now = dashboard._NOW
    sessions = [{"timestamp": now, "total": 10, "correct": 12},
                {"timestamp": now, "total": 0, "correct": 0},
                {"timestamp": now, "total": "x"},
                {"timestamp": now, "total": 4, "correct": -2}]
    n_sess, n_att, avg, tss, scores, weights = dashboard._extract_exam(sessions)
    assert (n_sess, n_att) == (4, 14)
    assert scores.count(10.0) == 10 and scores.count(0.0) == 4
    assert len(weights) == 14
    assert avg == approx(100 / 14)


def test_extract_flashcard_rating_map():
    sessions = [{"timestamp": dashboard._NOW,
                 "results": [{"rating": r} for r in ("got_it", "unsure", "missed", "???")]}]
    _, n, avg, _, scores, _ = dashboard._extract_flashcard(sessions)
    assert n == 4 and scores == [10.0, 5.0, 0.0, 5.0] and avg == approx(5.0)


def test_extract_dojo_paper_and_problems():
    now = dashboard._NOW
    dojo = [{"timestamp": now, "attempts": [{"passed": True}, {"passed": False}, {}]}]
    assert dashboard._extract_dojo(dojo)[4] == [10.0, 0.0, 0.0]

    paper = [{"title": "a", "scores": [2, 4]}, {"title": "b", "scores": ["6"]}]
    n_sess, n_att, avg, tss, scores, weights = dashboard._extract_paper(paper)
    assert (n_sess, n_att, tss) == (2, 3, [])
    assert avg == approx(4.0) and set(weights) == {0.1}

    problems = [{"timestamp": now, "attempts": [{"score": "abc"}, {"score": "7"}]}]
    assert dashboard._extract_problems(problems)[4] == [0.0, 7.0]


def test_topic_scores_skip_blank_categories():
    now = dashboard._NOW
    qec = [{"timestamp": now, "attempts": [{"category": " ", "score": 1},
                                           {"category": "x", "score": 4},
                                           {"category": "x", "score": 6}]}]
    buckets = dashboard._topic_scores_qec_vqa(qec)
    assert set(buckets) == {"x"}
    assert buckets["x"][0] / buckets["x"][1] == approx(5.0)

    fc = [{"timestamp": now, "results": [{"category": "hw", "rating": "missed"},
                                         {"category": "", "rating": "got_it"}]}]
    fc_buckets = dashboard._topic_scores_flashcard(fc)
    assert set(fc_buckets) == {"hw"} and fc_buckets["hw"][0] == 0.0


# ---------------------------------------------------------------------------
# Rendering smoke (no layout assertions)
# ---------------------------------------------------------------------------

def test_render_plain_smoke(synthetic_dir, capsys):
    dashboard._render_plain(build_report())
    out = capsys.readouterr().out
    for name in APPS:
        assert name in out
    assert "stabilizers" in out


def test_main_runs_on_empty_dir(data_dir, capsys):
    dashboard.main()
    out = capsys.readouterr().out
    assert out.strip()
    assert "Paper Drill" in out


# ---------------------------------------------------------------------------
# Retention & forgetting (Tier-4)
#
# These exercise every path against synthetic data, because the real data dir
# is empty: no history at all, history too thin for a fit, and rich history.
# ---------------------------------------------------------------------------

NOW = dashboard._NOW


def _fc_session(ts, results):
    return {"total": len(results), "timestamp": ts,
            "results": [{"card_id": cid, "category": cat, "rating": rating}
                        for cid, cat, rating in results]}


def rich_retention_payloads(now: float = NOW) -> dict[str, list]:
    """Multi-week history for all ten apps, with genuine item repeats.

    Flashcards decay on a known exponential (one card class recalled at short
    gaps, missed at long ones) so a curve is fittable; the other apps supply
    weekly-table coverage.
    """
    weeks = [now - d * DAY for d in (2, 9, 16, 23, 30, 37)]
    fc = []
    for i, ts in enumerate(weeks):
        rows = []
        for c in range(6):                     # short-gap cards: well recalled
            rows.append((f"fc_short_{c}", "Qiskit API",
                         "got_it" if (i + c) % 5 else "unsure"))
        for c in range(4):                     # long-gap cards: seen every 3rd
            if i % 3 == 0:
                rows.append((f"fc_long_{c}", "Quantum Hardware",
                             "missed" if c % 2 else "unsure"))
        fc.append(_fc_session(ts, rows))
    # extra same-week repeats so the short bucket clears FORGET_MIN_BUCKET_OBS
    for k in range(3):
        fc.append(_fc_session(now - (1 + k) * DAY,
                              [(f"fc_short_{c}", "Qiskit API", "got_it")
                               for c in range(6)]))

    dojo = [{"timestamp": ts, "total": 3, "passed": 2, "attempts": [
        {"kata_id": f"k{j}", "section": "Sampler", "passed": j != 0,
         "tries": 1} for j in range(3)]} for ts in weeks]
    qec = [{"timestamp": ts, "total": 2, "correct": 1, "attempts": [
        {"problem_id": "q1", "category": "stabilizers", "score": 4},
        {"problem_id": "q2", "category": "decoders", "score": 8}]}
        for ts in weeks]
    exam = [{"timestamp": ts, "mode": "full", "total": 20, "correct": 14,
             "duration_secs": 900,
             "sections": {"Sampler": {"total": 10, "correct": 6},
                          "Estimator": {"total": 10, "correct": 8}}}
            for ts in weeks[:3]]
    iso = datetime.fromtimestamp(now - DAY, tz=timezone.utc).isoformat()
    return {
        "Flashcard Drill": fc,
        "Qiskit Dojo": dojo,
        "QEC Trainer": qec,
        "VQA Trainer": [{"timestamp": weeks[0], "attempts": [
            {"problem_id": "v1", "category": "ansatz", "score": 7}]}],
        "Circuit Trainer": [{"date": "2026-01-02", "timestamp": iso,
                             "attempts": [{"problem_id": "c1",
                                           "category": "entanglers",
                                           "score": 6}]}],
        "Math Quiz": [{"date": "2026-01-02", "timestamp": iso, "records": [
            {"question_id": "m1", "subject": "Linear Algebra",
             "topic": "eigenvalues", "score": 3, "timestamp": iso}]}],
        "Quantum Quiz": [{"date": "2026-01-02", "timestamp": iso, "records": [
            {"question_id": "q1", "subject": "Algorithms", "topic": "grover",
             "score": 9, "timestamp": iso}]}],
        "Paper Drill": [{"title": "Shor 1994", "scores": [4, 6]}],
        "Exam Simulator": exam,
        "Problem Trainer": [{"timestamp": weeks[0], "attempts": [
            {"problem_id": "p1", "kind": "derivation", "score": 5}]}],
    }


class TestRetentionHelpers:
    def test_parse_epoch_accepts_every_schema_variant(self):
        assert dashboard._parse_epoch(1234.5) == 1234.5
        assert dashboard._parse_epoch("1234.5") == 1234.5
        expect = datetime(2026, 1, 2, tzinfo=timezone.utc).timestamp()
        assert dashboard._parse_epoch("2026-01-02") == expect
        assert dashboard._parse_epoch("2026-01-02T00:00:00Z") == expect
        assert dashboard._parse_epoch("2026-01-02T00:00:00+00:00") == expect
        # naive ISO is read as UTC, matching what the apps write
        assert dashboard._parse_epoch("2026-01-02T00:00:00") == expect
        for bad in (None, True, "", "  ", "nope", "02/01/2026", [], {}):
            assert dashboard._parse_epoch(bad) is None, bad

    def test_retention_epoch_prefers_timestamp_then_date(self):
        assert dashboard._retention_epoch({"timestamp": 5.0, "date": "2026-01-02"}) == 5.0
        assert dashboard._retention_epoch({"timestamp": "x", "date": "2026-01-02"}) == \
            datetime(2026, 1, 2, tzinfo=timezone.utc).timestamp()
        assert dashboard._retention_epoch({}) is None

    def test_fraction_clamps_and_tolerates_junk(self):
        assert dashboard._fraction(10) == 1.0
        assert dashboard._fraction(5) == 0.5
        assert dashboard._fraction(-3) == 0.0
        assert dashboard._fraction(99) == 1.0
        assert dashboard._fraction("abc") == 0.0
        assert dashboard._fraction(None) == 0.0
        assert dashboard._fraction(float("nan")) == 0.0

    def test_week_labels_are_trailing_windows(self):
        assert dashboard.week_labels(3) == ["0-6d", "7-13d", "14-20d"]


class TestRetentionEvents:
    def test_every_app_but_paper_drill_yields_events(self):
        raw = rich_retention_payloads()
        events = dashboard.iter_retention_events(raw)
        apps = {e.app for e in events}
        assert apps == set(APPS) - {"Paper Drill"}
        assert all(e.total > 0 for e in events)
        assert all(0.0 <= e.correct <= e.total for e in events)
        # exam sections are aggregate (no item id, total > 1)
        exam_events = [e for e in events if e.app == "Exam Simulator"]
        assert exam_events and all(e.item is None and e.total == 10
                                   for e in exam_events)
        # everything else is item-level
        assert all(e.item is not None and e.total == 1.0
                   for e in events if e.app != "Exam Simulator")
        assert events == sorted(events, key=lambda e: (e.ts, e.label,
                                                       e.item or ""))

    def test_labels_reuse_the_dashboard_prefixes(self):
        events = dashboard.iter_retention_events(rich_retention_payloads())
        labels = {e.label for e in events}
        assert "[FC] Qiskit API" in labels
        assert "[DOJO] Sampler" in labels
        assert "[EXAM] Estimator" in labels
        assert "[QEC] stabilizers" in labels
        assert "[PT] derivation" in labels

    def test_malformed_sessions_are_skipped_not_fatal(self):
        raw = {"QEC Trainer": [None, 7, "x",
                               {"timestamp": "bad", "attempts": [None, 3]},
                               {"attempts": [{"category": "c", "score": 5}]}],
               "Exam Simulator": [{"timestamp": NOW, "sections": "oops",
                                   "total": "x"},
                                  {"timestamp": NOW, "sections": {},
                                   "total": 4, "correct": 2}],
               "Flashcard Drill": [{"timestamp": NOW, "results": "nope"}],
               "Qiskit Dojo": "not a list"}
        events = dashboard.iter_retention_events(raw)
        assert [(e.app, e.category, e.correct, e.total) for e in events] == \
            [("Exam Simulator", "whole exam", 2.0, 4.0)]

    def test_exam_sections_without_ids_are_excluded_from_gaps(self):
        raw = {"Exam Simulator": [
            {"timestamp": NOW - 10 * DAY, "total": 10, "correct": 5,
             "sections": {"Sampler": {"total": 10, "correct": 5}}},
            {"timestamp": NOW, "total": 10, "correct": 8,
             "sections": {"Sampler": {"total": 10, "correct": 8}}}]}
        events = dashboard.iter_retention_events(raw)
        assert len(events) == 2
        assert dashboard.gap_observations(events) == []

    def test_correct_is_clamped_to_total(self):
        raw = {"Exam Simulator": [{"timestamp": NOW, "total": 4, "correct": 99,
                                   "sections": {"Sampler": {"total": 4,
                                                            "correct": 99}}}]}
        e = dashboard.iter_retention_events(raw)[0]
        assert (e.correct, e.total) == (4.0, 4.0)


class TestWeeklyAccuracy:
    def test_buckets_by_trailing_week_with_counts(self):
        raw = {"Flashcard Drill": [
            _fc_session(NOW - 1 * DAY, [("a", "hw", "got_it"),
                                        ("b", "hw", "missed")]),
            _fc_session(NOW - 8 * DAY, [("a", "hw", "unsure")]),
            _fc_session(NOW - 99 * DAY, [("a", "hw", "got_it")])]}
        rows = dashboard.weekly_accuracy(
            dashboard.iter_retention_events(raw), weeks=3, now=NOW)
        assert len(rows) == 1
        row = rows[0]
        assert row.label == "[FC] hw"
        assert row.cells[0] == approx((0.5, 2))     # got_it + missed
        assert row.cells[1] == approx((0.5, 1))     # unsure = half credit
        assert row.cells[2] is None                 # 99 days ago: out of range
        assert row.total_n == 3                     # the old one is not counted

    def test_rows_sorted_by_observations_then_label(self):
        rows = dashboard.weekly_accuracy(
            dashboard.iter_retention_events(rich_retention_payloads()),
            weeks=6, now=NOW)
        counts = [r.total_n for r in rows]
        assert counts == sorted(counts, reverse=True)
        assert rows[0].total_n >= rows[-1].total_n
        for r in rows:
            assert r.total_n == sum(c[1] for c in r.cells if c)

    def test_future_timestamps_land_in_week_zero(self):
        raw = {"Flashcard Drill": [_fc_session(NOW + 3600,
                                               [("a", "hw", "got_it")])]}
        rows = dashboard.weekly_accuracy(
            dashboard.iter_retention_events(raw), weeks=2, now=NOW)
        assert rows[0].cells[0] == approx((1.0, 1))


class TestForgettingCurve:
    def test_gap_observations_pair_consecutive_encounters(self):
        raw = {"Flashcard Drill": [
            _fc_session(NOW - 20 * DAY, [("a", "hw", "got_it")]),
            _fc_session(NOW - 10 * DAY, [("a", "hw", "missed")]),
            _fc_session(NOW - 1 * DAY, [("a", "hw", "unsure"),
                                        ("b", "hw", "got_it")])]}
        obs = dashboard.gap_observations(dashboard.iter_retention_events(raw))
        assert [(round(g), a) for g, a, _ in obs] == [(9, 0.5), (10, 0.0)]
        assert all(label == "[FC] hw" for _g, _a, label in obs)

    def test_refuses_below_the_observation_floor(self):
        assert dashboard.FORGET_MIN_OBS == 20
        obs = [(3.0, 1.0, "x")] * 19
        curve = dashboard.fit_forgetting_curve(obs)
        assert not curve.fitted
        assert curve.half_life_days is None and curve.predicted_7d is None
        assert "19 of 20 repeat observations" in curve.note
        assert curve.n_obs == 19
        assert [b.label for b in curve.buckets] == ["3-7d"]
        assert all(not b.in_fit for b in curve.buckets)

    def test_refuses_when_only_one_bucket_is_populated(self):
        curve = dashboard.fit_forgetting_curve([(3.0, 1.0, "x")] * 40)
        assert not curve.fitted and "not enough spread" in curve.note

    def test_refuses_a_noisy_relationship(self):
        # a downward trend the points do not actually support (R^2 ~ 0.18)
        obs = []
        for gap, acc in ((1.0, 0.9), (5.0, 0.3), (10.0, 0.85), (20.0, 0.35)):
            hits = int(round(acc * 20))
            obs += [(gap, 1.0, "x")] * hits + [(gap, 0.0, "x")] * (20 - hits)
        curve = dashboard.fit_forgetting_curve(obs)
        assert not curve.fitted
        assert "too noisy to fit" in curve.note
        assert curve.r_squared is not None and curve.r_squared < 0.5

    def test_refuses_when_accuracy_does_not_decay(self):
        obs = ([(1.0, 0.5, "x")] * 10 + [(10.0, 0.9, "x")] * 10
               + [(20.0, 0.95, "x")] * 10)
        curve = dashboard.fit_forgetting_curve(obs)
        assert not curve.fitted and "no measurable decay" in curve.note

    def test_fits_a_clean_exponential_and_recovers_the_half_life(self):
        # R(t) = exp(-t/10): half-life = 10*ln2 = 6.93 days
        tau = 10.0
        obs = []
        for gap in (0.5, 2.0, 5.0, 10.0, 20.0, 40.0):
            p = math.exp(-gap / tau)
            n = 40
            hits = int(round(p * n))
            obs += [(gap, 1.0, "x")] * hits + [(gap, 0.0, "x")] * (n - hits)
        curve = dashboard.fit_forgetting_curve(obs)
        assert curve.fitted
        assert curve.half_life_days == approx(tau * math.log(2), rel=0.20)
        assert curve.baseline == approx(1.0, abs=0.12)
        assert curve.predicted_7d == approx(math.exp(-7 / tau), rel=0.20)
        assert curve.r_squared > 0.9
        assert sum(1 for b in curve.buckets if b.in_fit) >= 2
        assert "fitted to" in curve.note and "R^2" in curve.note

    def test_baseline_below_one_is_allowed_and_reported(self):
        # 70% ceiling decaying with tau = 20 days
        obs = []
        for gap in (1.0, 5.0, 12.0, 25.0, 45.0):
            p = 0.7 * math.exp(-gap / 20.0)
            n = 40
            hits = int(round(p * n))
            obs += [(gap, 1.0, "x")] * hits + [(gap, 0.0, "x")] * (n - hits)
        curve = dashboard.fit_forgetting_curve(obs)
        assert curve.fitted
        assert curve.baseline == approx(0.7, abs=0.15)
        assert curve.baseline <= 1.0
        assert "free baseline" in curve.note


class TestBuildRetention:
    def test_empty_dir_degrades_honestly(self, data_dir):
        report = dashboard.build_retention()
        assert report.n_events == 0 and report.n_gap_obs == 0
        assert report.week_rows == [] and report.category_curves == []
        assert report.week0 is None
        assert not report.curve.fitted
        assert "not enough data yet" in report.curve.note
        assert dashboard.retention_summary() is None

    def test_thin_data_shows_counts_but_no_curve(self, data_dir):
        dashboard._FILES["Flashcard Drill"].write_text(json.dumps([
            _fc_session(NOW - 8 * DAY, [("a", "hw", "got_it")]),
            _fc_session(NOW - 1 * DAY, [("a", "hw", "missed")])]))
        report = dashboard.build_retention()
        assert report.n_events == 2
        assert report.n_gap_obs == 1
        assert not report.curve.fitted
        assert "1 of 20 repeat observations" in report.curve.note
        assert report.category_curves == []
        # the raw numbers are still there, with their counts
        assert report.curve.buckets[0].n == 1
        summary = dashboard.retention_summary()
        assert summary["half_life_days"] is None
        assert summary["n_gap_obs"] == 1
        assert summary["week_acc"] == approx(0.0) and summary["week_n"] == 1

    def test_rich_data_fills_the_weekly_table(self, data_dir, write_payloads):
        raw = rich_retention_payloads()
        report = dashboard.build_retention(raw)
        assert report.n_events > 50 and report.n_gap_obs > 20
        assert report.week_labels == dashboard.week_labels(report.weeks)
        labels = {r.label for r in report.week_rows}
        assert "[FC] Qiskit API" in labels
        assert all(r.total_n >= dashboard.RETENTION_MIN_ROW_OBS
                   for r in report.week_rows)
        assert len(report.week_rows) <= dashboard.RETENTION_MAX_ROWS
        assert report.week0 is not None and report.week0[1] > 0
        notes = " ".join(report.notes)
        assert "Paper Drill is excluded" in notes
        assert "Exam Simulator sections" in notes

    def test_paper_drill_never_contributes(self):
        raw = {"Paper Drill": [{"title": "t", "scores": [1, 2, 3]}]}
        assert dashboard.iter_retention_events(raw) == []
        report = dashboard.build_retention(raw)
        assert report.n_events == 0

    def test_per_category_curves_only_when_supported(self):
        raw = rich_retention_payloads()
        report = dashboard.build_retention(raw)
        for label, curve in report.category_curves:
            assert curve.fitted
            assert curve.n_obs >= dashboard.FORGET_MIN_OBS
        n = [c.n_obs for _l, c in report.category_curves]
        assert n == sorted(n, reverse=True)

    def test_build_retention_reads_files_when_raw_is_omitted(self, data_dir):
        dashboard._FILES["Qiskit Dojo"].write_text(json.dumps([
            {"timestamp": NOW - 2 * DAY, "attempts": [
                {"kata_id": "k1", "section": "Sampler", "passed": True}]}]))
        report = dashboard.build_retention()
        assert report.n_events == 1
        assert report.week_rows == []       # 1 obs < RETENTION_MIN_ROW_OBS
        assert report.week0 == approx((1.0, 1))


class TestRetentionRendering:
    @pytest.mark.parametrize("renderer", ["plain", "rich"])
    def test_renders_empty_thin_and_rich_without_crashing(self, renderer,
                                                          capsys):
        render = (dashboard._render_retention_plain if renderer == "plain"
                  else dashboard._render_retention_rich)
        render(dashboard.build_retention({}))
        empty_out = capsys.readouterr().out
        assert "No timestamped, graded history yet" in empty_out

        render(dashboard.build_retention(
            {"Flashcard Drill": [_fc_session(NOW - 8 * DAY,
                                             [("a", "hw", "got_it")]),
                                 _fc_session(NOW, [("a", "hw", "missed")])]}))
        thin_out = capsys.readouterr().out
        assert "1 of 20 repeat observations" in thin_out

        render(dashboard.build_retention(rich_retention_payloads()))
        rich_out = capsys.readouterr().out
        assert "Qiskit API" in rich_out
        assert "Forgetting curve" in rich_out

    def test_plain_table_columns_line_up(self):
        report = dashboard.build_retention(rich_retention_payloads())
        import io
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            dashboard._render_retention_plain(report)
        lines = [ln for ln in buf.getvalue().splitlines()
                 if ln.startswith("  [")]
        assert lines
        assert len({len(ln.rstrip()) for ln in lines if "n=" in ln}) <= 2

    def test_cell_text_shows_accuracy_and_count(self):
        assert dashboard._cell_text(None) == "--"
        assert dashboard._cell_text((0.715, 14)) == "72%/14"
        assert dashboard._cell_text((1.0, 100)) == "100%/100"


class TestDashboardCLI:
    def test_main_accepts_no_flags_and_renders_both_views(self, data_dir,
                                                          capsys):
        dashboard.main()
        out = capsys.readouterr().out
        assert "Paper Drill" in out                 # mastery report
        assert "Retention" in out                   # retention view

    def test_retention_only(self, data_dir, capsys):
        dashboard.main(["--retention"])
        out = capsys.readouterr().out
        assert "Paper Drill" not in out
        assert "Retention" in out

    def test_no_retention(self, data_dir, capsys):
        dashboard.main(["--no-retention"])
        out = capsys.readouterr().out
        assert "Paper Drill" in out
        assert "Retention & Forgetting" not in out

    def test_flags_are_mutually_exclusive(self, data_dir):
        with pytest.raises(SystemExit):
            dashboard.main(["--retention", "--no-retention"])

    def test_end_to_end_subprocess_against_a_temp_data_dir(self, tmp_path):
        (tmp_path / "flashcard_history.json").write_text(json.dumps([
            _fc_session(NOW - 3 * DAY, [("a", "Qiskit API", "got_it")])]))
        env = dict(os.environ, QUANTUM_STUDY_DATA_DIR=str(tmp_path),
                   COLUMNS="200")
        root = Path(__file__).resolve().parent.parent
        r = subprocess.run([sys.executable, "dashboard.py", "--retention"],
                           cwd=root, env=env, capture_output=True, text=True,
                           timeout=60)
        assert r.returncode == 0, r.stderr
        assert "Qiskit API" in r.stdout or "Retention" in r.stdout
        # read-only: the dashboard must never write into the data dir
        assert list(tmp_path.iterdir()) == [tmp_path / "flashcard_history.json"]


def test_nan_and_infinity_in_json_never_reach_the_maths():
    # json.loads accepts NaN / Infinity, so history files can legally hold them
    raw_text = ('[{"timestamp": NaN, "attempts": [{"category": "a", '
                '"score": 5}]},'
                ' {"timestamp": Infinity, "attempts": [{"category": "b", '
                '"score": 5}]},'
                ' {"timestamp": 1.0, "attempts": [{"category": "c", '
                '"score": NaN}]}]')
    sessions = json.loads(raw_text)
    assert dashboard._parse_epoch(sessions[0]["timestamp"]) is None
    assert dashboard._parse_epoch(sessions[1]["timestamp"]) is None
    events = dashboard.iter_retention_events({"QEC Trainer": sessions})
    assert [(e.category, e.correct) for e in events] == [("c", 0.0)]
    exam = json.loads('[{"timestamp": 1.0, "total": NaN, "correct": NaN,'
                      ' "sections": {"S": {"total": NaN, "correct": 1}}}]')
    assert dashboard.iter_retention_events({"Exam Simulator": exam}) == []
    # and the whole view still builds
    report = dashboard.build_retention({"QEC Trainer": sessions,
                                        "Exam Simulator": exam})
    assert report.n_events == 1 and not report.curve.fitted
