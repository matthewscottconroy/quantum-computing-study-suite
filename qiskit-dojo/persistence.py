"""Persistence for qiskit-dojo.

Session history schema (integrated against by the coach app — do not change):
    list of {
        "timestamp": <epoch float>,
        "total": int,
        "passed": int,
        "attempts": [
            {"kata_id": str, "section": str, "passed": bool, "tries": int}
        ],
    }
"""
from __future__ import annotations
import json
import time
from config import HISTORY_FILE, DATA_DIR
from core.models import SessionStats


def _load_raw() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except Exception:
        return []


def save_session(stats: SessionStats) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    sessions = _load_raw()
    sessions.append({
        "timestamp": time.time(),
        "total":     stats.total,
        "passed":    stats.passed,
        "attempts": [
            {
                "kata_id": a.kata.id,
                "section": a.kata.section,
                "passed":  a.passed,
                "tries":   a.tries,
            }
            for a in stats.attempts
        ],
    })
    HISTORY_FILE.write_text(json.dumps(sessions, indent=2))


def pass_rates_by_section() -> dict[str, float]:
    """Lifetime pass rate per section, 0.0–1.0."""
    buckets: dict[str, list[bool]] = {}
    for s in _load_raw():
        for a in s.get("attempts", []):
            sec = a.get("section", "")
            if sec:
                buckets.setdefault(sec, []).append(bool(a.get("passed", False)))
    return {
        sec: sum(vals) / len(vals)
        for sec, vals in buckets.items()
        if vals
    }


def kata_weights() -> dict[str, float]:
    """Per-kata selection weight: katas failed recently come up more often."""
    stats: dict[str, list[bool]] = {}
    for s in _load_raw():
        for a in s.get("attempts", []):
            kid = a.get("kata_id", "")
            if kid:
                stats.setdefault(kid, []).append(bool(a.get("passed", False)))
    weights: dict[str, float] = {}
    for kid, results in stats.items():
        recent = results[-3:]
        rate = sum(recent) / len(recent)
        weights[kid] = max(0.5, 2.0 - rate * 1.5)   # 2.0 never-passed → 0.5 solid
    return weights
