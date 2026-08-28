"""App-wide constants for exam-sim."""
from pathlib import Path

APP_NAME        = "Exam Sim"
DATA_DIR        = Path.home() / ".local" / "share" / "quantum-study"
HISTORY_FILE    = DATA_DIR / "exam_history.json"
MISSED_FILE     = DATA_DIR / "exam_missed.json"

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


def section_weight(section: str) -> float:
    """Exam weight of a section as a fraction of the whole exam."""
    return SECTIONS.get(section, 0) / BANK_SIZE


def pass_mark_for(total: int) -> int:
    """Pass mark scaled to a session of `total` questions (47/68 for the full exam)."""
    if total == EXAM_QUESTION_COUNT:
        return PASS_MARK
    import math
    return math.ceil(total * PASS_MARK / EXAM_QUESTION_COUNT)
