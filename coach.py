"""Quantum Study Coach — daily prescription engine across all study apps.

Turns cross-app history (see dashboard.py for schemas) into a concrete,
rules-based plan for today.  Deterministic given the data; no network, no API.

Usage:
    python coach.py                # today's plan (default)
    python coach.py --diagnostic   # 20-question placement quiz
    python coach.py --badges      # IBM Quantum Learning badge checklist
    python coach.py --review      # unified SRS review queue

Data dir defaults to dashboard.DATA_DIR (~/.local/share/quantum-study/)
and can be overridden with the QUANTUM_STUDY_DATA_DIR environment variable.
Coach state is stored in <data dir>/coach_state.json:

    {
      "activity_dates": ["YYYY-MM-DD", ...],   # days with real study activity
      "current_streak": int,
      "best_streak": int,
      "badges": {"<badge name>": "not_started"|"in_progress"|"earned"},
      "diagnostic": {"timestamp": float,
                     "rungs": {"<rung>": {"total": n, "correct": n}},
                     "recommended_rung": "<rung>"},
      "last_plan_date": "YYYY-MM-DD"
    }
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Reuse dashboard's schema knowledge + half-life weighting.  Import the module
# (not individual names) so its helpers stay in one place.
import dashboard

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = Path(os.environ.get("QUANTUM_STUDY_DATA_DIR") or dashboard.DATA_DIR)
STATE_PATH = DATA_DIR / "coach_state.json"

_NOW = time.time()
_TODAY = datetime.now().strftime("%Y-%m-%d")

STALE_DAYS = 7            # category untouched longer than this is "stale"
REVIEW_WINDOW_DAYS = 30   # low-score attempts newer than this are reviewable
REVIEW_LOW_SCORE = 5.0    # attempts scoring below this go to the review queue
REVIEW_CAP = 20
EXAM_PASS_CORRECT = 47    # C1000-179 style pass line
EXAM_PASS_TOTAL = 68

# History files the coach reads (relative to DATA_DIR).  App keys are the
# runnable app names printed in plans.
_HISTORY_FILES = {
    "qec-trainer":     "qec_history.json",
    "vqa-trainer":     "vqa_history.json",
    "flashcard-drill": "flashcard_history.json",
    "circuit-trainer": "trainer_history.json",
    "math-quiz":       "math_history.json",
    "quantum-quiz":    "quiz_history.json",
    "paper-drill":     "paper_history.json",
    "qiskit-dojo":     "dojo_history.json",
    "exam-sim":        "exam_history.json",
    "problem-trainer": "problems_history.json",
}

_FLAGGED_FILES = {
    "flashcard-drill": "flagged_cards.json",
    "qec-trainer":     "qec_flagged.json",
    "vqa-trainer":     "vqa_flagged.json",
}

# Curriculum rungs, in docs-ladder order, with their docs dir + practice app.
RUNGS = [
    ("math",       "docs/01_mathematical_foundations",   "math-quiz"),
    ("qm",         "docs/02_quantum_mechanics",          "quantum-quiz"),
    ("circuits",   "docs/03_quantum_gates_and_circuits", "circuit-trainer"),
    ("algorithms", "docs/04_quantum_algorithms",         "quantum-quiz"),
    ("qec",        "docs/05_quantum_error_correction",   "qec-trainer"),
    ("vqa",        "docs/06_variational_quantum_algorithms", "vqa-trainer"),
    ("hardware",   "docs/07_quantum_hardware",           "flashcard-drill"),
    ("qiskit-api", "docs/08_advanced_topics",            "qiskit-dojo"),
]
RUNG_ORDER = [r[0] for r in RUNGS]

BADGES = [
    "Basics of Quantum Information",
    "Fundamentals of Quantum Algorithms",
    "General Formulation of Quantum Information",
    "Foundations of Quantum Error Correction",
    "Variational Algorithm Design",
    "Quantum Computing in Practice",
    "C1000-179 Certification (Qiskit Associate Developer)",
]
BADGE_STATUSES = ["not_started", "in_progress", "earned"]
_BADGE_LABEL = {"not_started": "not started", "in_progress": "IN PROGRESS",
                "earned": "EARNED"}


# ---------------------------------------------------------------------------
# 20-question diagnostic (2-3 per rung; answer index is 0-based)
# ---------------------------------------------------------------------------

DIAGNOSTIC_QUESTIONS = [
    # -- math (3) --
    {"rung": "math", "q": "The inner product <0|1> equals:",
     "choices": ["0", "1", "1/sqrt(2)", "-1"], "answer": 0},
    {"rung": "math", "q": "The eigenvalues of the Pauli Z matrix are:",
     "choices": ["0 and 1", "+1 and -1", "+i and -i", "+1 only"], "answer": 1},
    {"rung": "math", "q": "A matrix U is unitary when:",
     "choices": ["U = U^T", "U^dagger U = I", "det(U) = 0", "U^2 = I"],
     "answer": 1},
    # -- qm (3) --
    {"rung": "qm", "q": "For a valid qubit state a|0> + b|1>, which must hold?",
     "choices": ["a + b = 1", "|a| + |b| = 1", "|a|^2 + |b|^2 = 1",
                 "a^2 + b^2 = 1 (no absolute values)"], "answer": 2},
    {"rung": "qm", "q": "Measuring |+> = (|0>+|1>)/sqrt(2) in the computational "
                        "basis yields outcome 0 with probability:",
     "choices": ["0", "1/4", "1/2", "1"], "answer": 2},
    {"rung": "qm", "q": "Which two-qubit state is maximally entangled?",
     "choices": ["|00>", "(|00>+|11>)/sqrt(2)", "(|0>+|1>)|0>/sqrt(2)",
                 "|01>"], "answer": 1},
    # -- circuits (3) --
    {"rung": "circuits", "q": "Applying a Hadamard gate to |0> gives:",
     "choices": ["|1>", "(|0>+|1>)/sqrt(2)", "(|0>-|1>)/sqrt(2)", "|0>"],
     "answer": 1},
    {"rung": "circuits", "q": "CNOT applied to |10> (control=1, target=0) gives:",
     "choices": ["|10>", "|00>", "|11>", "|01>"], "answer": 2},
    {"rung": "circuits", "q": "The Pauli X gate acts as:",
     "choices": ["a phase flip", "a bit flip (|0> <-> |1>)",
                 "a measurement", "the identity"], "answer": 1},
    # -- algorithms (3) --
    {"rung": "algorithms", "q": "Grover search over N unstructured items needs "
                                "how many oracle queries?",
     "choices": ["O(N)", "O(log N)", "O(sqrt(N))", "O(1)"], "answer": 2},
    {"rung": "algorithms", "q": "Shor's algorithm provides an exponential "
                                "speedup for:",
     "choices": ["sorting", "integer factoring", "matrix multiplication",
                 "graph coloring"], "answer": 1},
    {"rung": "algorithms", "q": "Deutsch-Jozsa decides, with a single oracle "
                                "query, whether f is:",
     "choices": ["injective or not", "constant or balanced",
                 "periodic or not", "linear or not"], "answer": 1},
    # -- qec (2) --
    {"rung": "qec", "q": "The 3-qubit repetition (bit-flip) code can correct:",
     "choices": ["any single-qubit error", "one bit-flip (X) error",
                 "one phase-flip (Z) error", "two bit-flip errors"],
     "answer": 1},
    {"rung": "qec", "q": "The surface code's error threshold is roughly:",
     "choices": ["~1e-6", "~0.01 (1%)", "~0.5 (50%)", "~0.25 (25%)"],
     "answer": 1},
    # -- vqa (2) --
    {"rung": "vqa", "q": "VQE is designed to estimate:",
     "choices": ["a Hamiltonian's ground-state energy",
                 "the period of a function", "a database index",
                 "an error syndrome"], "answer": 0},
    {"rung": "vqa", "q": "A 'barren plateau' in variational training means:",
     "choices": ["the ansatz is too shallow",
                 "gradients vanish exponentially with system size",
                 "the optimizer found the global minimum",
                 "measurement noise is zero"], "answer": 1},
    # -- hardware (2) --
    {"rung": "hardware", "q": "A qubit's T1 time characterizes:",
     "choices": ["dephasing", "energy relaxation (|1> decaying to |0>)",
                 "gate speed", "readout fidelity"], "answer": 1},
    {"rung": "hardware", "q": "A transmon qubit is best described as:",
     "choices": ["a trapped ion", "a superconducting anharmonic oscillator",
                 "a photonic cavity", "a nitrogen-vacancy center"],
     "answer": 1},
    # -- qiskit-api (2) --
    {"rung": "qiskit-api", "q": "In Qiskit, adding a Hadamard on qubit 0 of "
                                "circuit qc is written:",
     "choices": ["qc.hadamard(0)", "qc.h(0)", "qc.H[0]", "qc.gate('h', 0)"],
     "answer": 1},
    {"rung": "qiskit-api", "q": "Which Qiskit primitive computes expectation "
                                "values of observables?",
     "choices": ["Sampler", "Estimator", "Transpiler", "Provider"],
     "answer": 1},
]


# ---------------------------------------------------------------------------
# Loading (tolerant of missing / empty / corrupt files)
# ---------------------------------------------------------------------------

def _path(filename: str) -> Path:
    return DATA_DIR / filename


def _load_list(filename: str) -> list:
    """Like dashboard._load but rooted at the coach's (overridable) DATA_DIR."""
    path = _path(filename)
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text())
        return data if isinstance(data, list) else []
    except Exception:
        return []


def load_state() -> dict:
    default = {
        "activity_dates": [],
        "current_streak": 0,
        "best_streak": 0,
        "badges": {},
        "diagnostic": None,
        "last_plan_date": None,
    }
    try:
        raw = json.loads(STATE_PATH.read_text())
        if isinstance(raw, dict):
            default.update(raw)
    except Exception:
        pass
    return default


def save_state(state: dict) -> None:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, indent=2))
    except Exception:
        pass  # never crash the plan over an unwritable state file


# ---------------------------------------------------------------------------
# Per-(app, category) mastery with recency decay
# ---------------------------------------------------------------------------

def _clean_sessions(sessions: list) -> list[dict]:
    return [s for s in sessions if isinstance(s, dict)]


def build_category_stats(histories: dict[str, list]) -> dict[tuple[str, str], dict]:
    """Return {(app, category): {"w_sum", "ws", "last_ts", "n"}}.

    Scores are on a 0-10 scale, weighted by dashboard's 14-day half-life.
    """
    stats: dict[tuple[str, str], dict] = {}

    def add(app: str, cat: str, weight: float, score: float,
            ts: Optional[float]) -> None:
        cat = str(cat).strip()
        if not cat:
            return
        entry = stats.setdefault((app, cat),
                                 {"w_sum": 0.0, "ws": 0.0, "last_ts": 0.0,
                                  "n": 0})
        entry["w_sum"] += weight * score
        entry["ws"] += weight
        entry["n"] += 1
        if ts and ts > entry["last_ts"]:
            entry["last_ts"] = ts

    _ease = {"got_it": 10.0, "unsure": 5.0, "missed": 0.0}

    for app, sessions in histories.items():
        for s in _clean_sessions(sessions):
            w = dashboard._session_weight(s)
            ts = dashboard._session_timestamp(s)
            if app in ("qec-trainer", "vqa-trainer", "circuit-trainer"):
                for a in s.get("attempts", []):
                    if isinstance(a, dict):
                        add(app, a.get("category", ""), w,
                            _num(a.get("score", 0)), ts)
            elif app == "flashcard-drill":
                for r in s.get("results", []):
                    if isinstance(r, dict):
                        add(app, r.get("category", ""), w,
                            _ease.get(r.get("rating", ""), 5.0), ts)
            elif app in ("math-quiz", "quantum-quiz"):
                for r in s.get("records", []):
                    if isinstance(r, dict):
                        cat = r.get("topic") or r.get("subject") or ""
                        add(app, cat, w, _num(r.get("score", 0)), ts)
            elif app == "qiskit-dojo":
                for a in s.get("attempts", []):
                    if isinstance(a, dict):
                        add(app, a.get("section", ""), w,
                            10.0 if a.get("passed") else 0.0, ts)
            elif app == "exam-sim":
                sections = s.get("sections", {})
                if isinstance(sections, dict):
                    for name, sec in sections.items():
                        if isinstance(sec, dict):
                            tot = _num(sec.get("total", 0))
                            cor = _num(sec.get("correct", 0))
                            if tot > 0:
                                add(app, name, w * tot, cor / tot * 10.0, ts)
            elif app == "problem-trainer":
                for a in s.get("attempts", []):
                    if isinstance(a, dict):
                        cat = a.get("kind") or a.get("problem_id") or ""
                        add(app, cat, w, _num(a.get("score", 0)), ts)
            # paper-drill has no categories

    return stats


def _num(x, default: float = 0.0) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def weakest_categories(stats: dict[tuple[str, str], dict],
                       top_n: int = 3) -> list[tuple[str, str, float]]:
    """Top-N weakest (app, category, weighted_avg), deterministic order."""
    rows = [(app, cat, e["w_sum"] / e["ws"])
            for (app, cat), e in stats.items() if e["ws"] > 1e-9]
    rows.sort(key=lambda r: (r[2], r[0], r[1]))
    return rows[:top_n]


def stale_categories(stats: dict[tuple[str, str], dict]
                     ) -> list[tuple[str, str, int]]:
    """Categories touched before, but not in the last STALE_DAYS days."""
    cutoff = _NOW - STALE_DAYS * 86400.0
    out = []
    for (app, cat), e in stats.items():
        if 0 < e["last_ts"] < cutoff:
            days = int((_NOW - e["last_ts"]) / 86400.0)
            out.append((app, cat, days))
    out.sort(key=lambda r: (-r[2], r[0], r[1]))   # most stale first
    return out


# ---------------------------------------------------------------------------
# Exam readiness
# ---------------------------------------------------------------------------

def exam_readiness(exam_sessions: list) -> Optional[dict]:
    """Latest full-exam score vs the pass line, plus weakest sections."""
    fulls = [s for s in _clean_sessions(exam_sessions)
             if s.get("mode") == "full" and _num(s.get("total", 0)) > 0]
    if not fulls:
        return None
    latest = max(fulls, key=lambda s: _num(s.get("timestamp", 0)))
    total = _num(latest.get("total", 0))
    correct = _num(latest.get("correct", 0))
    pct = correct / total * 100.0 if total else 0.0
    pass_pct = EXAM_PASS_CORRECT / EXAM_PASS_TOTAL * 100.0

    sections = []
    secs = latest.get("sections", {})
    if isinstance(secs, dict):
        for name, sec in secs.items():
            if isinstance(sec, dict) and _num(sec.get("total", 0)) > 0:
                sections.append(
                    (name, _num(sec.get("correct", 0))
                     / _num(sec.get("total", 1)) * 100.0))
    sections.sort(key=lambda r: (r[1], r[0]))

    return {
        "correct": int(correct),
        "total": int(total),
        "pct": pct,
        "passing": correct / total >= EXAM_PASS_CORRECT / EXAM_PASS_TOTAL,
        "pass_pct": pass_pct,
        "weakest_sections": sections[:3],
        "timestamp": _num(latest.get("timestamp", 0)),
    }


def dojo_weakest_section(dojo_sessions: list) -> Optional[tuple[str, float]]:
    """(section, pass_rate_pct) with the lowest pass rate."""
    buckets: dict[str, list[bool]] = {}
    for s in _clean_sessions(dojo_sessions):
        for a in s.get("attempts", []):
            if isinstance(a, dict):
                sec = str(a.get("section", "")).strip()
                if sec:
                    buckets.setdefault(sec, []).append(bool(a.get("passed")))
    if not buckets:
        return None
    rates = [(sec, sum(v) / len(v) * 100.0) for sec, v in buckets.items()]
    rates.sort(key=lambda r: (r[1], r[0]))
    return rates[0]


# ---------------------------------------------------------------------------
# Unified review queue (--review, also counted in the default plan)
# ---------------------------------------------------------------------------

def _flag_entry(item, app: str) -> Optional[dict]:
    """Normalize a flagged-file entry (string id or dict) into a queue item."""
    if isinstance(item, str) and item.strip():
        return {"app": app, "label": item.strip(), "ts": 0.0, "score": 0.0,
                "why": "flagged"}
    if isinstance(item, dict):
        ident = (item.get("card_id") or item.get("problem_id")
                 or item.get("id") or item.get("question_id"))
        if ident is None:
            return None
        return {"app": app, "label": str(ident),
                "ts": _num(item.get("timestamp", 0)), "score": 0.0,
                "why": "flagged"}
    return None


def build_review_queue(histories: dict[str, list]) -> list[dict]:
    """Merge flagged cards, exam misses, and recent low scores.

    Sorted oldest+worst first (timestamp asc, score asc); capped at REVIEW_CAP.
    Each item: {app, label, ts, score, why}.
    """
    items: list[dict] = []
    seen: set[tuple[str, str, str]] = set()

    def push(item: Optional[dict]) -> None:
        if not item:
            return
        key = (item["app"], item["label"], item["why"])
        if key in seen:
            return
        seen.add(key)
        items.append(item)

    # 1. Flagged cards / problems
    for app, fname in _FLAGGED_FILES.items():
        for entry in _load_list(fname):
            push(_flag_entry(entry, app))

    # 2. Missed exam questions
    for m in _load_list("exam_missed.json"):
        if isinstance(m, dict):
            ident = m.get("question_id")
            if ident is None:
                continue
            sec = str(m.get("section", "")).strip()
            label = f"{ident} ({sec})" if sec else str(ident)
            push({"app": "exam-sim", "label": label,
                  "ts": _num(m.get("timestamp", 0)), "score": 0.0,
                  "why": "missed exam question"})

    # 3. Low-scoring quiz / problem attempts in the last 30 days
    cutoff = _NOW - REVIEW_WINDOW_DAYS * 86400.0
    for app in ("math-quiz", "quantum-quiz"):
        for s in _clean_sessions(histories.get(app, [])):
            ts = dashboard._session_timestamp(s)
            if not ts or ts < cutoff:
                continue
            for r in s.get("records", []):
                if isinstance(r, dict):
                    score = _num(r.get("score", 10))
                    if score < REVIEW_LOW_SCORE:
                        topic = r.get("topic") or r.get("subject") or "?"
                        push({"app": app, "label": str(topic), "ts": ts,
                              "score": score,
                              "why": f"scored {score:g}/10"})
    for s in _clean_sessions(histories.get("problem-trainer", [])):
        ts = dashboard._session_timestamp(s)
        if not ts or ts < cutoff:
            continue
        for a in s.get("attempts", []):
            if isinstance(a, dict):
                score = _num(a.get("score", 10))
                if score < REVIEW_LOW_SCORE:
                    ident = a.get("problem_id") or a.get("kind") or "?"
                    push({"app": "problem-trainer", "label": str(ident),
                          "ts": ts, "score": score,
                          "why": f"scored {score:g}/10"})

    items.sort(key=lambda i: (i["ts"], i["score"], i["app"], i["label"]))
    return items[:REVIEW_CAP]


# ---------------------------------------------------------------------------
# Streak (real activity only — coach running does NOT count)
# ---------------------------------------------------------------------------

def latest_activity_dates(histories: dict[str, list]) -> set[str]:
    """Every YYYY-MM-DD (local) on which any history session was recorded."""
    days: set[str] = set()
    for sessions in histories.values():
        for s in _clean_sessions(sessions):
            ts = dashboard._session_timestamp(s)
            if ts:
                days.add(datetime.fromtimestamp(ts).strftime("%Y-%m-%d"))
    return days


def _compute_streaks(dates: list[str]) -> tuple[int, int]:
    """(current, best) streak from a list of YYYY-MM-DD strings."""
    if not dates:
        return 0, 0
    parsed = sorted({datetime.strptime(d, "%Y-%m-%d").date()
                     for d in dates if _valid_date(d)})
    if not parsed:
        return 0, 0
    best = run = 1
    for prev, cur in zip(parsed, parsed[1:]):
        run = run + 1 if (cur - prev).days == 1 else 1
        best = max(best, run)
    today = datetime.now().date()
    current = 0
    check = today
    dateset = set(parsed)
    if today not in dateset and (today - timedelta(days=1)) in dateset:
        check = today - timedelta(days=1)   # streak still alive from yesterday
    while check in dateset:
        current += 1
        check -= timedelta(days=1)
    return current, best


def _valid_date(d) -> bool:
    try:
        datetime.strptime(d, "%Y-%m-%d")
        return True
    except (TypeError, ValueError):
        return False


def update_streak_state(state: dict, histories: dict[str, list]) -> None:
    """Record today as active only if history files show activity today."""
    dates = [d for d in state.get("activity_dates", []) if _valid_date(d)]
    dates = sorted(set(dates) | latest_activity_dates(histories))
    state["activity_dates"] = dates[-365:]        # keep a year of history
    cur, best = _compute_streaks(state["activity_dates"])
    state["current_streak"] = cur
    state["best_streak"] = max(best, int(state.get("best_streak", 0) or 0))


# ---------------------------------------------------------------------------
# Diagnostic scoring (pure functions, testable headlessly)
# ---------------------------------------------------------------------------

def score_diagnostic(answers: list[Optional[int]]) -> dict[str, dict]:
    """Score answers (0-based choice indices, None = skipped) per rung."""
    rungs: dict[str, dict] = {r: {"total": 0, "correct": 0}
                              for r in RUNG_ORDER}
    for q, a in zip(DIAGNOSTIC_QUESTIONS, answers):
        r = rungs[q["rung"]]
        r["total"] += 1
        if a is not None and a == q["answer"]:
            r["correct"] += 1
    return rungs


def recommended_rung(rungs: dict[str, dict]) -> str:
    """First rung (in ladder order) below 2/3 accuracy; else the weakest."""
    for name in RUNG_ORDER:
        r = rungs.get(name, {})
        total = r.get("total", 0)
        if total and r.get("correct", 0) / total < 2 / 3:
            return name
    # All rungs solid — recommend the (relatively) weakest one.
    scored = [(r.get("correct", 0) / r["total"], RUNG_ORDER.index(n), n)
              for n, r in rungs.items() if r.get("total", 0)]
    return min(scored)[2] if scored else RUNG_ORDER[0]


def rung_docs_dir(rung: str) -> str:
    for name, docs, _app in RUNGS:
        if name == rung:
            return docs
    return "docs/"


def rung_app(rung: str) -> str:
    for name, _docs, app in RUNGS:
        if name == rung:
            return app
    return "flashcard-drill"


def weak_rungs(rungs: dict[str, dict]) -> list[str]:
    """Rungs below 2/3 accuracy, in ladder order."""
    out = []
    for name in RUNG_ORDER:
        r = rungs.get(name, {})
        total = r.get("total", 0)
        if total and r.get("correct", 0) / total < 2 / 3:
            out.append(name)
    return out


# ---------------------------------------------------------------------------
# Plan builder (deterministic, rules-based)
# ---------------------------------------------------------------------------

def build_plan(histories: dict[str, list], state: dict) -> dict:
    """Compute everything the default view prints."""
    stats = build_category_stats(histories)
    weakest = weakest_categories(stats, top_n=3)
    stale = stale_categories(stats)
    exam = exam_readiness(histories.get("exam-sim", []))
    dojo = dojo_weakest_section(histories.get("qiskit-dojo", []))
    review = build_review_queue(histories)
    missed_count = sum(1 for m in _load_list("exam_missed.json")
                       if isinstance(m, dict) and m.get("question_id"))

    diag = state.get("diagnostic") or None
    diag_rungs = diag.get("rungs", {}) if isinstance(diag, dict) else {}
    weak_rung_list = weak_rungs(diag_rungs) if diag_rungs else []

    items: list[str] = []

    # 1. Review queue first — overdue material beats new material.
    if review:
        apps = sorted({i["app"] for i in review})
        items.append(
            f"review queue — {len(review)} item(s) due "
            f"({', '.join(apps)}): run `python coach.py --review`")

    # 2. Weakest categories, grouped per app.
    by_app: dict[str, list[tuple[str, float]]] = {}
    for app, cat, avg in weakest:
        by_app.setdefault(app, []).append((cat, avg))
    for app in sorted(by_app):
        cats = ", ".join(c for c, _ in by_app[app])
        worst = min(a for _, a in by_app[app])
        items.append(f"{app} — 15 min, focus: {cats} "
                     f"(weakest, avg {worst:.1f}/10)")

    def _planned_apps() -> set[str]:
        return {i.split(" — ")[0] for i in items}

    # 3. Exam readiness.
    if exam and "exam-sim" not in _planned_apps():
        if exam["weakest_sections"]:
            sec, pct = exam["weakest_sections"][0]
            items.append(f"exam-sim — Sprint: {sec} "
                         f"({pct:.0f}% on last full exam)")
        elif not exam["passing"]:
            items.append(f"exam-sim — full exam retake "
                         f"(last: {exam['correct']}/{exam['total']}, "
                         f"need {EXAM_PASS_CORRECT}/{EXAM_PASS_TOTAL})")

    # 4. Dojo lowest pass-rate section (unless already covered above).
    if dojo and "qiskit-dojo" not in _planned_apps():
        sec, rate = dojo
        items.append(f"qiskit-dojo — 2 katas in '{sec}' "
                     f"({rate:.0f}% pass rate, lowest)")

    # 5. Diagnostic bias: hit the weakest rung with its practice app.
    if weak_rung_list:
        rung = weak_rung_list[0]
        r = diag_rungs.get(rung, {})
        items.append(f"{rung_app(rung)} — 1 session on rung '{rung}' "
                     f"(diagnostic: {r.get('correct', 0)}/{r.get('total', 0)}"
                     f"; read {rung_docs_dir(rung)})")

    # 6. Stale categories (skip apps already planned above).
    for app, cat, days in stale:
        if app not in _planned_apps():
            items.append(f"{app} — 1 short session: {cat} "
                         f"(untouched {days} days)")
            break

    # Cap at 5; pad to 3 with sensible defaults.
    items = items[:5]
    defaults = [
        "flashcard-drill — 10 min mixed deck (keep the streak alive)",
        "quantum-quiz — 5 questions, mixed topics",
        "read one docs section from the ladder (start: docs/01_...)",
    ]
    for d in defaults:
        if len(items) >= 3:
            break
        items.append(d)

    return {
        "items": items,
        "weakest": weakest,
        "stale": stale,
        "exam": exam,
        "dojo": dojo,
        "review_count": len(review),
        "missed_count": missed_count,
        "diagnostic": diag,
        "weak_rungs": weak_rung_list,
    }


# ---------------------------------------------------------------------------
# Rendering (rich if available, plain text otherwise)
# ---------------------------------------------------------------------------

def _console():
    """Return a rich Console or None (plain-text fallback)."""
    try:
        from rich.console import Console
        return Console()
    except ImportError:
        return None


def _heading(console, text: str) -> None:
    if console:
        console.rule(f"[bold cyan]{text}[/bold cyan]")
    else:
        print()
        print("=" * 62)
        print(f"  {text}")
        print("=" * 62)


def _line(console, text: str, style: str = "") -> None:
    if console and style:
        console.print(f"[{style}]{text}[/{style}]")
    elif console:
        console.print(text)
    else:
        print(text)


def render_plan(plan: dict, state: dict) -> None:
    console = _console()
    _heading(console, f"Quantum Study Coach — plan for {_TODAY}")
    print()

    # Situation report
    if plan["weakest"]:
        _line(console, "Weakest categories (recency-weighted):", "bold")
        for app, cat, avg in plan["weakest"]:
            _line(console, f"  - {cat} [{app}] — {avg:.1f}/10")
    else:
        _line(console, "No scored history yet — starter plan below.", "dim")

    if plan["stale"]:
        names = ", ".join(f"{c} ({d}d)" for _a, c, d in plan["stale"][:5])
        _line(console, f"Stale (> {STALE_DAYS} days untouched): {names}")

    exam = plan["exam"]
    if exam:
        verdict = "PASSING" if exam["passing"] else "below pass line"
        _line(console,
              f"Exam readiness: {exam['correct']}/{exam['total']} "
              f"({exam['pct']:.0f}%) on last full exam — {verdict} "
              f"(pass = {EXAM_PASS_CORRECT}/{EXAM_PASS_TOTAL}, "
              f"{exam['pass_pct']:.0f}%)")
        if exam["weakest_sections"]:
            secs = ", ".join(f"{n} ({p:.0f}%)"
                             for n, p in exam["weakest_sections"])
            _line(console, f"  weakest sections: {secs}")
    if plan["missed_count"]:
        _line(console,
              f"Missed exam questions due for review: {plan['missed_count']}")

    diag = plan["diagnostic"]
    if isinstance(diag, dict) and diag.get("recommended_rung"):
        rung = diag["recommended_rung"]
        _line(console,
              f"Docs ladder: start at rung '{rung}' -> {rung_docs_dir(rung)}"
              + (f" (weak rungs: {', '.join(plan['weak_rungs'])})"
                 if plan["weak_rungs"] else ""))
    else:
        _line(console,
              "No diagnostic on file — run `python coach.py --diagnostic` "
              "to calibrate the docs ladder.", "dim")

    # The plan itself
    print()
    _line(console, "TODAY'S PLAN", "bold green")
    for i, item in enumerate(plan["items"], 1):
        _line(console, f"  {i}. {item}")

    # Streak + badges summary
    print()
    cur = state.get("current_streak", 0)
    best = state.get("best_streak", 0)
    flame = " *" if cur >= 7 else ""
    _line(console, f"Streak: {cur} day(s) (best: {best}){flame}",
          "bold yellow")

    badges = state.get("badges", {})
    earned = sum(1 for b in BADGES if badges.get(b) == "earned")
    in_prog = sum(1 for b in BADGES if badges.get(b) == "in_progress")
    _line(console,
          f"Badges: {earned}/{len(BADGES)} earned, {in_prog} in progress "
          f"(`python coach.py --badges`)")
    print()


def render_review(queue: list[dict]) -> None:
    console = _console()
    _heading(console, "Review Today — unified SRS queue")
    print()
    if not queue:
        _line(console, "Nothing due for review. Nice.", "green")
        print()
        return
    _line(console, f"{len(queue)} item(s), oldest & worst first "
                   f"(capped at {REVIEW_CAP}):", "bold")
    for i, item in enumerate(queue, 1):
        when = (datetime.fromtimestamp(item["ts"]).strftime("%Y-%m-%d")
                if item["ts"] else "undated")
        _line(console,
              f"  {i:2}. [{item['app']}] {item['label']} — "
              f"{item['why']} ({when})")
    print()
    apps = sorted({i["app"] for i in queue})
    _line(console, f"Open these apps to clear the queue: {', '.join(apps)}")
    print()


# ---------------------------------------------------------------------------
# Interactive modes
# ---------------------------------------------------------------------------

def run_diagnostic(state: dict) -> None:
    console = _console()
    _heading(console, "Placement Diagnostic — 20 questions")
    print()
    _line(console, "Answer a/b/c/d (or 1-4). Press Enter to skip.", "dim")
    print()

    answers: list[Optional[int]] = []
    for i, q in enumerate(DIAGNOSTIC_QUESTIONS, 1):
        _line(console, f"Q{i}/20 [{q['rung']}]  {q['q']}", "bold")
        for j, choice in enumerate(q["choices"]):
            _line(console, f"    {'abcd'[j]}) {choice}")
        ans = _read_choice(len(q["choices"]))
        answers.append(ans)
        print()

    rungs = score_diagnostic(answers)
    rec = recommended_rung(rungs)
    state["diagnostic"] = {
        "timestamp": _NOW,
        "rungs": rungs,
        "recommended_rung": rec,
    }
    save_state(state)

    total = sum(r["total"] for r in rungs.values())
    correct = sum(r["correct"] for r in rungs.values())
    _line(console, f"Score: {correct}/{total}", "bold green")
    print()
    for name in RUNG_ORDER:
        r = rungs[name]
        mark = "weak" if (r["total"] and r["correct"] / r["total"] < 2 / 3) \
            else "ok"
        _line(console,
              f"  {name:<12} {r['correct']}/{r['total']}  [{mark}]")
    print()
    _line(console,
          f"Recommended docs-ladder starting rung: '{rec}' "
          f"-> {rung_docs_dir(rec)}", "bold")
    _line(console, "Future plans will bias toward your weak rungs.", "dim")
    print()


def _read_choice(n_choices: int) -> Optional[int]:
    """Read one MC answer from stdin; None means skipped/EOF."""
    letters = "abcd"[:n_choices]
    while True:
        try:
            raw = input("  > ").strip().lower()
        except EOFError:
            return None
        if raw == "":
            return None
        if raw in letters:
            return letters.index(raw)
        if raw.isdigit() and 1 <= int(raw) <= n_choices:
            return int(raw) - 1
        print(f"    (enter one of: {', '.join(letters)} / 1-{n_choices}, "
              f"or Enter to skip)")


def cycle_badge(state: dict, badge: str) -> str:
    """Advance a badge's status (not_started -> in_progress -> earned -> ...)."""
    badges = state.setdefault("badges", {})
    cur = badges.get(badge, "not_started")
    if cur not in BADGE_STATUSES:
        cur = "not_started"
    nxt = BADGE_STATUSES[(BADGE_STATUSES.index(cur) + 1) % len(BADGE_STATUSES)]
    badges[badge] = nxt
    return nxt


def run_badges(state: dict) -> None:
    console = _console()
    _heading(console, "IBM Quantum Learning — badge tracker")
    print()
    _line(console,
          "Enter a number to cycle its status "
          "(not started -> in progress -> earned). q to quit.", "dim")
    while True:
        print()
        badges = state.get("badges", {})
        for i, name in enumerate(BADGES, 1):
            status = badges.get(name, "not_started")
            label = _BADGE_LABEL.get(status, status)
            _line(console, f"  {i}. [{label:<11}] {name}")
        print()
        try:
            raw = input("badge # (q to quit) > ").strip().lower()
        except EOFError:
            break
        if raw in ("q", "quit", "exit", ""):
            break
        if raw.isdigit() and 1 <= int(raw) <= len(BADGES):
            name = BADGES[int(raw) - 1]
            new = cycle_badge(state, name)
            save_state(state)
            _line(console, f"  -> {name}: {_BADGE_LABEL[new]}")
        else:
            _line(console, "  (enter 1-7 or q)")
    save_state(state)
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def load_histories() -> dict[str, list]:
    return {app: _load_list(fname) for app, fname in _HISTORY_FILES.items()}


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Quantum Study Coach — daily plan from cross-app history")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--diagnostic", action="store_true",
                      help="20-question placement quiz")
    mode.add_argument("--badges", action="store_true",
                      help="IBM Quantum Learning badge checklist")
    mode.add_argument("--review", action="store_true",
                      help="unified SRS review queue")
    args = parser.parse_args(argv)

    state = load_state()

    if args.diagnostic:
        run_diagnostic(state)
        return
    if args.badges:
        run_badges(state)
        return

    histories = load_histories()

    if args.review:
        render_review(build_review_queue(histories))
        return

    # Default: today's plan.
    update_streak_state(state, histories)
    plan = build_plan(histories, state)
    state["last_plan_date"] = _TODAY
    save_state(state)
    render_plan(plan, state)


if __name__ == "__main__":
    main()
