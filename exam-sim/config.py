"""App-wide constants for exam-sim.

Paths live in the shared suite data directory and are resolved **at call
time** by :mod:`common.datadir` (``QUANTUM_STUDY_DATA_DIR`` if it is set and
non-blank, otherwise ``~/.local/share/quantum-study``).  Call time, not import
time: a test only has to ``monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", …)``
and every path below follows it, in this process and in any subprocess.

The historic upper-case constants (``DATA_DIR``, ``HISTORY_FILE``, …) are
still available and now resolve on each attribute access — see
:func:`__getattr__` at the bottom of the file.
"""
from __future__ import annotations

import math
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import datadir

APP_NAME        = "Exam Sim"

# Identifies this app inside the shared mistakes/confidence files, and keys its
# own file names in common.datadir.APP_FILES: the app directory name, exactly
# as the suite contract specifies.
APP_ID          = "exam-sim"

WINDOW_TITLE    = "Exam Sim — IBM C1000-179 Mock Exam"
WINDOW_MIN_SIZE = (1040, 700)

# Real-exam logistics (third-party-sourced; see README disclaimer)
EXAM_QUESTION_COUNT   = 68
EXAM_MINUTES          = 90
PASS_MARK             = 47          # correct answers needed out of 68

SPRINT_QUESTION_COUNT = 10
SPRINT_MINUTES        = 10

# Section -> question count in the bank (proportional to exam weights).
SECTIONS = {
    "Create circuits":    20,
    "Quantum operations": 18,
    "Run circuits":       16,
    "Sampler":            13,
    "Estimator":          13,
    "Visualization":      12,
    "Results analysis":   11,
    "OpenQASM":           7,
}

BANK_SIZE = sum(SECTIONS.values())  # 110


# ---------------------------------------------------------------- paths
def data_dir() -> Path:
    """The shared suite data directory, resolved now."""
    return datadir.data_dir()


def history_file() -> Path:
    """``exam_history.json`` — session history (read by coach.py/dashboard.py)."""
    return datadir.app_file(APP_ID, "history")


def missed_file() -> Path:
    """``exam_missed.json`` — the missed-question list Review mode re-serves."""
    return datadir.app_file(APP_ID, "missed")


def settings_file() -> Path:
    """``exam_settings.json`` — this app's own preferences; nothing else reads it."""
    return datadir.app_file(APP_ID, "settings")


def mistakes_file() -> Path:
    """``mistakes.json`` — the suite-wide cause-analysis journal."""
    return datadir.mistakes_file()


def confidence_file() -> Path:
    """``confidence.json`` — the suite-wide calibration log."""
    return datadir.confidence_file()


#: Legacy module constants -> the function that resolves them now.  Kept so
#: ``config.HISTORY_FILE`` (and ``from config import HISTORY_FILE``) still work
#: for anything outside this app that reads them, while the value is no longer
#: frozen at import time.
_LEGACY_PATHS = {
    "DATA_DIR":        data_dir,
    "HISTORY_FILE":    history_file,
    "MISSED_FILE":     missed_file,
    "SETTINGS_FILE":   settings_file,
    "MISTAKES_FILE":   mistakes_file,
    "CONFIDENCE_FILE": confidence_file,
}


def __getattr__(name: str):
    """PEP 562 module attribute hook for the legacy path constants."""
    resolver = _LEGACY_PATHS.get(name)
    if resolver is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return resolver()


def __dir__() -> list[str]:
    return sorted(list(globals()) + list(_LEGACY_PATHS))


# ------------------------------------------------------------- exam maths
def section_weight(section: str) -> float:
    """Exam weight of a section as a fraction of the whole exam."""
    return SECTIONS.get(section, 0) / BANK_SIZE


def pass_mark_for(total: int) -> int:
    """Pass mark scaled to a session of `total` questions (47/68 for the full exam)."""
    if total == EXAM_QUESTION_COUNT:
        return PASS_MARK
    return math.ceil(total * PASS_MARK / EXAM_QUESTION_COUNT)
