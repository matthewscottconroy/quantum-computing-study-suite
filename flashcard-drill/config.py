"""App-wide constants."""
from pathlib import Path

APP_NAME            = "Flashcard Drill"
DATA_DIR            = Path.home() / ".local" / "share" / "quantum-study"
HISTORY_FILE        = DATA_DIR / "flashcard_history.json"
DEFAULT_CARD_COUNT  = 20
DEFAULT_TIMER_SECS  = 0          # 0 = no timer
WINDOW_TITLE        = "Flashcard Drill — Quantum Computing"
WINDOW_MIN_SIZE     = (800, 600)
