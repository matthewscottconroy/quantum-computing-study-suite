"""Tests for dashboard.py — cross-app mastery report.

dashboard.py only ever reads history files; tests point its ``_FILES`` map at
a temporary directory (conftest ``data_dir`` / ``synthetic_dir``).
"""

from __future__ import annotations

import json
import math
import os
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
