"""App-wide constants."""
import os
from pathlib import Path

APP_NAME            = "Flashcard Drill"
# Shared suite data directory. QUANTUM_STUDY_DATA_DIR overrides it (same override
# coach.py honours) so tests and experiments never touch the real history.
DATA_DIR            = Path(os.environ.get("QUANTUM_STUDY_DATA_DIR")
                           or (Path.home() / ".local" / "share" / "quantum-study"))
HISTORY_FILE        = DATA_DIR / "flashcard_history.json"
# SM-2 schedule (own file: flashcard_history.json / flagged_cards.json are parsed
# by coach.py and dashboard.py and must keep their schemas).
SCHEDULE_FILE       = DATA_DIR / "flashcard_schedule.json"
# Suite-wide review contract (shared with the other nine apps; every row carries
# an "app" field and this app only ever rewrites its own).
MISTAKES_FILE       = DATA_DIR / "mistakes.json"
CONFIDENCE_FILE     = DATA_DIR / "confidence.json"
# This app's own preferences (currently just the confidence-strip opt-out).
SETTINGS_FILE       = DATA_DIR / "flashcard_settings.json"
DEFAULT_CARD_COUNT  = 20
DEFAULT_TIMER_SECS  = 0          # 0 = no timer
WINDOW_TITLE        = "Flashcard Drill — Quantum Computing"
WINDOW_MIN_SIZE     = (800, 600)
