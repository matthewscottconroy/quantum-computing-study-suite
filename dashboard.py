"""Quantum Study Dashboard — unified mastery view across all study apps.

Run standalone:
    python dashboard.py

Import as a module:
    from dashboard import build_report, AppStats
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = Path.home() / ".local" / "share" / "quantum-study"

# Actual filenames written by each app's persistence layer
_FILES = {
    "QEC Trainer":       DATA_DIR / "qec_history.json",
    "VQA Trainer":       DATA_DIR / "vqa_history.json",
    "Flashcard Drill":   DATA_DIR / "flashcard_history.json",
    "Circuit Trainer":   DATA_DIR / "trainer_history.json",
    "Math Quiz":         DATA_DIR / "math_history.json",
    "Quantum Quiz":      DATA_DIR / "quiz_history.json",
    "Paper Drill":       DATA_DIR / "paper_history.json",
    "Qiskit Dojo":       DATA_DIR / "dojo_history.json",
    "Exam Simulator":    DATA_DIR / "exam_history.json",
    "Problem Trainer":   DATA_DIR / "problems_history.json",
}

_HALF_LIFE_DAYS = 14.0   # score weight halves every 14 days (matches app SRS)
_NOW = time.time()       # snapshot once so all comparisons are consistent


# ---------------------------------------------------------------------------
# Schema notes (verified against each app's persistence.py)
#
# qec_history / vqa_history:
#   [ { total, correct, accuracy, timestamp,
#       attempts: [ {problem_id, category, difficulty, score, verdict,
#                    hints_used, elapsed_secs} ] } ]
#
# flashcard_history:
#   [ { total, got_it, unsure, missed, timestamp,
#       results: [ {card_id, category, rating} ] } ]
#   rating in {"got_it", "unsure", "missed"}
#
# trainer_history (Circuit Trainer):
#   [ { date, total, correct, accuracy,
#       attempts: [ {category, difficulty, score} ] } ]
#   (no session-level timestamp — uses "date" string)
#
# math_history / quiz_history (Math Quiz / Quantum Quiz):
#   [ { date, answered, average_score,
#       records: [ {subject, topic, score} ] } ]
#   (no session-level timestamp — uses "date" string)
#
# paper_history:
#   [ { title, total, average, scores: [float, ...] } ]
#   (no timestamp at all)
#
# dojo_history (Qiskit Dojo):
#   [ { timestamp, total, passed,
#       attempts: [ {kata_id, section, passed: bool, tries} ] } ]
#
# exam_history (Exam Simulator):
#   [ { timestamp, mode: "full"|"sprint", total, correct, duration_secs,
#       sections: { "<name>": {total, correct} } } ]
#
# problems_history (Problem Trainer):
#   [ { timestamp, total, avg_score,
#       attempts: [ {problem_id, kind: "problem"|"derivation", score} ] } ]
# ---------------------------------------------------------------------------


def _session_weight(session: dict) -> float:
    """14-day half-life decay.  Missing/unparseable timestamp → weight 0.1."""
    ts = session.get("timestamp")
    if ts is not None:
        try:
            days = (_NOW - float(ts)) / 86400.0
            return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)
        except (TypeError, ValueError):
            pass
    # Try ISO date string ("date" key used by circuit/math/quiz apps)
    date_str = session.get("date")
    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            days = (_NOW - d.timestamp()) / 86400.0
            return math.exp(-days * math.log(2) / _HALF_LIFE_DAYS)
        except (TypeError, ValueError):
            pass
    return 0.1   # very old / unknown age


def _session_timestamp(session: dict) -> Optional[float]:
    """Best-effort Unix timestamp for a session (None if totally unknown)."""
    ts = session.get("timestamp")
    if ts is not None:
        try:
            return float(ts)
        except (TypeError, ValueError):
            pass
    date_str = session.get("date")
    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            return d.timestamp()
        except (TypeError, ValueError):
            pass
    return None


def _load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Per-app extraction helpers
# ---------------------------------------------------------------------------

def _extract_qec_vqa(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Return (session_count, total_attempts, weighted_avg, timestamps,
               all_scores, all_weights) for qec or vqa."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for a in s.get("attempts", []):
            score = a.get("score", 0)
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_flashcard(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Flashcard uses rating strings; map to 0–10 scores."""
    _ease = {"got_it": 10.0, "unsure": 5.0, "missed": 0.0}
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for r in s.get("results", []):
            score = _ease.get(r.get("rating", ""), 5.0)
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_circuit(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Circuit trainer: attempts[].score (0–10 scale from app)."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for a in s.get("attempts", []):
            score = a.get("score", 0)
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_math_quiz(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Math / Quantum Quiz: records[].score with session-level date."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for r in s.get("records", []):
            score = r.get("score", 0)
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_paper(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Paper drill: each session is a quiz on one paper; scores list + average."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    # Paper has no timestamp; all sessions treated as weight 0.1
    for s in sessions:
        w = _session_weight(s)   # will return 0.1 (no timestamp/date key)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for score in s.get("scores", []):
            total_attempts += 1
            w_sum += w * float(score)
            ws_sum += w
            all_scores.append(float(score))
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_dojo(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Qiskit Dojo: attempts[].passed bool → 10.0 / 0.0 score."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for a in s.get("attempts", []):
            score = 10.0 if a.get("passed") else 0.0
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_exam(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Exam Simulator: session-level total/correct → per-question 10/0 scores."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        try:
            total = int(s.get("total", 0))
            correct = int(s.get("correct", 0))
        except (TypeError, ValueError):
            continue
        if total <= 0:
            continue
        correct = max(0, min(correct, total))
        total_attempts += total
        w_sum += w * correct * 10.0
        ws_sum += w * total
        all_scores.extend([10.0] * correct + [0.0] * (total - correct))
        all_weights.extend([w] * total)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


def _extract_problems(sessions: list[dict]) -> tuple[int, int, float, list[float], list[float], list[float]]:
    """Problem Trainer: attempts[].score (0–10 scale)."""
    total_attempts = 0
    w_sum = 0.0
    ws_sum = 0.0
    timestamps: list[float] = []
    all_scores: list[float] = []
    all_weights: list[float] = []
    for s in sessions:
        w = _session_weight(s)
        ts = _session_timestamp(s)
        if ts:
            timestamps.append(ts)
        for a in s.get("attempts", []):
            try:
                score = float(a.get("score", 0))
            except (TypeError, ValueError):
                score = 0.0
            total_attempts += 1
            w_sum += w * score
            ws_sum += w
            all_scores.append(score)
            all_weights.append(w)
    weighted_avg = w_sum / ws_sum if ws_sum else 0.0
    return len(sessions), total_attempts, weighted_avg, timestamps, all_scores, all_weights


# ---------------------------------------------------------------------------
# Topic-level weak-spot analysis (qec, vqa, flashcard)
# ---------------------------------------------------------------------------

def _topic_scores_qec_vqa(sessions: list[dict]) -> dict[str, tuple[float, float]]:
    """Return {category: (weighted_sum, weight_sum)} from qec/vqa data."""
    buckets: dict[str, list[tuple[float, float]]] = {}
    for s in sessions:
        w = _session_weight(s)
        for a in s.get("attempts", []):
            cat = a.get("category", "").strip()
            if cat:
                buckets.setdefault(cat, []).append((w, a.get("score", 0)))
    return {
        cat: (sum(w * sc for w, sc in pairs), sum(w for w, _ in pairs))
        for cat, pairs in buckets.items()
    }


def _topic_scores_flashcard(sessions: list[dict]) -> dict[str, tuple[float, float]]:
    _ease = {"got_it": 10.0, "unsure": 5.0, "missed": 0.0}
    buckets: dict[str, list[tuple[float, float]]] = {}
    for s in sessions:
        w = _session_weight(s)
        for r in s.get("results", []):
            cat = r.get("category", "").strip()
            if cat:
                score = _ease.get(r.get("rating", ""), 5.0)
                buckets.setdefault(cat, []).append((w, score))
    return {
        cat: (sum(w * sc for w, sc in pairs), sum(w for w, _ in pairs))
        for cat, pairs in buckets.items()
    }


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class AppStats:
    name: str
    sessions: int
    total_attempts: int
    weighted_avg: float       # 0–10
    timestamps: list[float]   # Unix timestamps of sessions (may be empty)
    file_present: bool


@dataclass
class DashboardReport:
    apps: list[AppStats]
    weakest_topics: list[tuple[str, float]]    # (label, avg_score) sorted asc, top 5
    recent_apps: dict[str, int]                # app_name -> problems in last 7 days
    streak_days: int


# ---------------------------------------------------------------------------
# Core build function
# ---------------------------------------------------------------------------

def build_report() -> DashboardReport:
    """Load all history files and compute the dashboard report."""

    raw: dict[str, list[dict]] = {}
    for app_name, path in _FILES.items():
        raw[app_name] = _load(path)

    # ── Per-app stats ─────────────────────────────────────────────────────
    app_stats: list[AppStats] = []

    extractors = {
        "QEC Trainer":     (_extract_qec_vqa,    _FILES["QEC Trainer"]),
        "VQA Trainer":     (_extract_qec_vqa,    _FILES["VQA Trainer"]),
        "Flashcard Drill": (_extract_flashcard,  _FILES["Flashcard Drill"]),
        "Circuit Trainer": (_extract_circuit,    _FILES["Circuit Trainer"]),
        "Math Quiz":       (_extract_math_quiz,  _FILES["Math Quiz"]),
        "Quantum Quiz":    (_extract_math_quiz,  _FILES["Quantum Quiz"]),
        "Paper Drill":     (_extract_paper,      _FILES["Paper Drill"]),
        "Qiskit Dojo":     (_extract_dojo,       _FILES["Qiskit Dojo"]),
        "Exam Simulator":  (_extract_exam,       _FILES["Exam Simulator"]),
        "Problem Trainer": (_extract_problems,   _FILES["Problem Trainer"]),
    }

    for app_name, (fn, path) in extractors.items():
        sessions = raw[app_name]
        file_present = path.exists()
        if not sessions:
            app_stats.append(AppStats(
                name=app_name, sessions=0, total_attempts=0,
                weighted_avg=0.0, timestamps=[], file_present=file_present,
            ))
            continue
        n_sess, n_att, w_avg, tss, _, _ = fn(sessions)
        app_stats.append(AppStats(
            name=app_name,
            sessions=n_sess,
            total_attempts=n_att,
            weighted_avg=w_avg,
            timestamps=tss,
            file_present=file_present,
        ))

    # ── Weakest topics (qec + vqa + flashcard) ────────────────────────────
    merged: dict[str, tuple[float, float]] = {}

    def _merge(buckets: dict[str, tuple[float, float]], prefix: str) -> None:
        for cat, (ws, w) in buckets.items():
            label = f"[{prefix}] {cat}"
            if label in merged:
                old_ws, old_w = merged[label]
                merged[label] = (old_ws + ws, old_w + w)
            else:
                merged[label] = (ws, w)

    _merge(_topic_scores_qec_vqa(raw["QEC Trainer"]),     "QEC")
    _merge(_topic_scores_qec_vqa(raw["VQA Trainer"]),     "VQA")
    _merge(_topic_scores_flashcard(raw["Flashcard Drill"]), "FC")

    topic_avgs = [
        (label, ws / w)
        for label, (ws, w) in merged.items()
        if w > 0
    ]
    topic_avgs.sort(key=lambda x: x[1])
    weakest_topics = topic_avgs[:5]

    # ── Recent activity (last 7 days) ─────────────────────────────────────
    cutoff = _NOW - 7 * 86400.0
    recent_apps: dict[str, int] = {}

    def _recent_count_attempts(sessions: list[dict], key: str) -> int:
        count = 0
        for s in sessions:
            ts = _session_timestamp(s)
            if ts and ts >= cutoff:
                count += len(s.get(key, []))
        return count

    def _recent_count_paper(sessions: list[dict]) -> int:
        count = 0
        for s in sessions:
            ts = _session_timestamp(s)
            # Paper has no timestamp; skip from recent count
            if ts and ts >= cutoff:
                count += len(s.get("scores", []))
        return count

    for app_name, sessions in raw.items():
        if app_name in ("QEC Trainer", "VQA Trainer"):
            n = _recent_count_attempts(sessions, "attempts")
        elif app_name == "Flashcard Drill":
            n = _recent_count_attempts(sessions, "results")
        elif app_name == "Circuit Trainer":
            n = _recent_count_attempts(sessions, "attempts")
        elif app_name in ("Math Quiz", "Quantum Quiz"):
            n = _recent_count_attempts(sessions, "records")
        elif app_name == "Paper Drill":
            n = _recent_count_paper(sessions)
        elif app_name in ("Qiskit Dojo", "Problem Trainer"):
            n = _recent_count_attempts(sessions, "attempts")
        elif app_name == "Exam Simulator":
            n = 0
            for s in sessions:
                ts = _session_timestamp(s)
                if ts and ts >= cutoff:
                    try:
                        n += int(s.get("total", 0))
                    except (TypeError, ValueError):
                        pass
        else:
            n = 0
        if n > 0:
            recent_apps[app_name] = n

    # ── Streak (consecutive days with any activity) ───────────────────────
    all_ts: list[float] = []
    for app_stats_item in app_stats:
        all_ts.extend(app_stats_item.timestamps)

    active_days: set[str] = set()
    for ts in all_ts:
        d = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        active_days.add(d)

    streak_days = 0
    check = datetime.now(tz=timezone.utc).date()
    while True:
        if check.strftime("%Y-%m-%d") in active_days:
            streak_days += 1
            check -= timedelta(days=1)
        else:
            break

    return DashboardReport(
        apps=app_stats,
        weakest_topics=weakest_topics,
        recent_apps=recent_apps,
        streak_days=streak_days,
    )


# ---------------------------------------------------------------------------
# Rendering helpers (shared by rich and plain-text renderers)
# ---------------------------------------------------------------------------

def _bar(score: float, max_score: float = 10.0, width: int = 10) -> tuple[str, int]:
    """Return (bar_string, pct) for a score on a 0..max_score scale."""
    pct = int(round(score / max_score * 100)) if max_score else 0
    pct = max(0, min(100, pct))
    filled = round(pct / 100 * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return bar, pct


# ---------------------------------------------------------------------------
# Rich renderer
# ---------------------------------------------------------------------------

def _render_rich(report: DashboardReport) -> None:
    from rich.console import Console
    from rich.table import Table
    from rich import box
    from rich.panel import Panel
    from rich.text import Text

    console = Console()
    console.print()
    console.rule("[bold cyan]Quantum Study Dashboard[/bold cyan]")
    console.print()

    # ── Section 1: Overall mastery ─────────────────────────────────────────
    table = Table(
        title="[bold]Overall Mastery[/bold]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
        expand=False,
    )
    table.add_column("App", style="cyan", no_wrap=True)
    table.add_column("Sessions", justify="right")
    table.add_column("Problems", justify="right")
    table.add_column("Avg Score", justify="right")
    table.add_column("Mastery", no_wrap=True)
    table.add_column("%", justify="right")

    for app in report.apps:
        bar_str, pct = _bar(app.weighted_avg)
        if not app.file_present:
            status = "[dim]no history[/dim]"
            bar_display = "[dim]not started[/dim]"
            avg_display = "[dim]—[/dim]"
        else:
            if pct >= 70:
                color = "green"
            elif pct >= 40:
                color = "yellow"
            else:
                color = "red"
            bar_display = f"[{color}]{bar_str}[/{color}]"
            avg_display = f"{app.weighted_avg:.1f}"
            status = str(app.sessions)

        table.add_row(
            app.name,
            status if app.file_present else "[dim]—[/dim]",
            str(app.total_attempts) if app.file_present else "[dim]—[/dim]",
            avg_display,
            bar_display,
            f"{pct}%" if app.file_present else "[dim]—[/dim]",
        )

    console.print(table)
    console.print()

    # ── Section 2: Weakest topics ─────────────────────────────────────────
    if report.weakest_topics:
        wtable = Table(
            title="[bold]Weakest Topics (QEC + VQA + Flashcard)[/bold]",
            box=box.SIMPLE_HEAD,
            header_style="bold red",
        )
        wtable.add_column("Topic", style="cyan")
        wtable.add_column("Weighted Avg", justify="right")
        wtable.add_column("Bar", no_wrap=True)

        for label, avg in report.weakest_topics:
            bar_str, pct = _bar(avg)
            wtable.add_row(label, f"{avg:.1f}/10", f"[red]{bar_str}[/red] {pct}%")

        console.print(wtable)
    else:
        console.print("[dim]No topic data yet (QEC, VQA, Flashcard not used).[/dim]")
    console.print()

    # ── Section 3: Recent activity ─────────────────────────────────────────
    console.print("[bold]Recent Activity[/bold] — last 7 days")
    if report.recent_apps:
        for app_name, count in sorted(report.recent_apps.items()):
            console.print(f"  [green]●[/green] [cyan]{app_name}[/cyan]: {count} problem(s)")
    else:
        console.print("  [dim]No activity in the last 7 days.[/dim]")
    console.print()

    # ── Section 4: Streak ─────────────────────────────────────────────────
    streak = report.streak_days
    if streak == 0:
        streak_msg = "[red]0 days[/red] — no current streak"
    elif streak == 1:
        streak_msg = "[yellow]1 day[/yellow] streak"
    elif streak < 7:
        streak_msg = f"[yellow]{streak} days[/yellow] streak"
    else:
        streak_msg = f"[green]{streak} days[/green] streak \U0001f525"

    console.print(Panel(
        f"[bold]Study Streak:[/bold] {streak_msg}",
        box=box.ROUNDED,
        expand=False,
    ))
    console.print()


# ---------------------------------------------------------------------------
# Plain-text renderer (fallback when rich is not installed)
# ---------------------------------------------------------------------------

def _render_plain(report: DashboardReport) -> None:
    SEP = "=" * 62

    print()
    print(SEP)
    print("       QUANTUM STUDY DASHBOARD")
    print(SEP)
    print()

    # Section 1
    print("OVERALL MASTERY")
    print("-" * 62)
    fmt = "{:<18} {:>8} {:>8} {:>6}  {} {:>4}"
    print(fmt.format("App", "Sessions", "Problems", "Avg", "Mastery   ", "  %"))
    print("-" * 62)
    for app in report.apps:
        bar_str, pct = _bar(app.weighted_avg)
        if not app.file_present:
            print(f"  {app.name:<16} {'(no history)':>40}")
        else:
            avg_str = f"{app.weighted_avg:.1f}"
            print(fmt.format(
                app.name,
                app.sessions,
                app.total_attempts,
                avg_str,
                bar_str,
                f"{pct}%",
            ))
    print()

    # Section 2
    print("WEAKEST TOPICS  (QEC + VQA + Flashcard)")
    print("-" * 62)
    if report.weakest_topics:
        for label, avg in report.weakest_topics:
            bar_str, pct = _bar(avg)
            print(f"  {label:<32} {avg:4.1f}/10  {bar_str} {pct}%")
    else:
        print("  No topic data yet.")
    print()

    # Section 3
    print("RECENT ACTIVITY  (last 7 days)")
    print("-" * 62)
    if report.recent_apps:
        for app_name, count in sorted(report.recent_apps.items()):
            print(f"  * {app_name}: {count} problem(s)")
    else:
        print("  No activity in the last 7 days.")
    print()

    # Section 4
    print("STREAK")
    print("-" * 62)
    streak = report.streak_days
    print(f"  {streak} consecutive day(s) of study activity")
    print()
    print(SEP)
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    report = build_report()

    try:
        import rich  # noqa: F401
        _render_rich(report)
    except ImportError:
        _render_plain(report)


if __name__ == "__main__":
    main()
