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

Flagged-for-review schema (dojo_flagged.json, shared flagging contract —
read by coach.py's review queue):
    list of {
        "id": str,            # kata id
        "label": str,         # kata title
        "category": str,      # kata section
        "app": "qiskit-dojo",
        "timestamp": <epoch float>,
    }
Flagging is a toggle: flagging an already-flagged kata removes it.
"""
from __future__ import annotations
import json
import time
from config import HISTORY_FILE, DATA_DIR, FLAGGED_FILE, APP_DIR_NAME
from core.models import Kata, SessionStats


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


# ---------------------------------------------------------------------------
# Flag for review (dojo_flagged.json)
# ---------------------------------------------------------------------------

def load_flagged() -> list[dict]:
    """Flagged katas, oldest first.  A missing or corrupt file reads as empty."""
    if not FLAGGED_FILE.exists():
        return []
    try:
        data = json.loads(FLAGGED_FILE.read_text())
    except Exception:
        return []
    if not isinstance(data, list):
        return []
    return [e for e in data if isinstance(e, dict) and e.get("id")]


def _save_flagged(entries: list[dict]) -> None:
    FLAGGED_FILE.parent.mkdir(parents=True, exist_ok=True)
    FLAGGED_FILE.write_text(json.dumps(entries, indent=2))


def flagged_ids() -> set[str]:
    return {str(e["id"]) for e in load_flagged()}


def is_flagged(kata_id: str) -> bool:
    return kata_id in flagged_ids()


def toggle_flag(kata: Kata) -> bool:
    """Flag `kata` for review, or unflag it if already flagged.

    Returns the new state (True = now flagged).
    """
    entries = load_flagged()
    if any(e.get("id") == kata.id for e in entries):
        _save_flagged([e for e in entries if e.get("id") != kata.id])
        return False
    entries.append({
        "id":        kata.id,
        "label":     kata.title,
        "category":  kata.section,
        "app":       APP_DIR_NAME,
        "timestamp": time.time(),
    })
    _save_flagged(entries)
    return True


def unflag(kata_id: str) -> None:
    """Remove a kata from the flagged list (no-op if it is not flagged)."""
    entries = load_flagged()
    remaining = [e for e in entries if e.get("id") != kata_id]
    if len(remaining) != len(entries):
        _save_flagged(remaining)
