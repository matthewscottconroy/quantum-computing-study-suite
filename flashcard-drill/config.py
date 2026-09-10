"""App-wide constants."""
import os
from pathlib import Path

APP_NAME            = "Flashcard Drill"
# Shared suite data directory. QUANTUM_STUDY_DATA_DIR overrides it (same override
# coach.py honours) so tests and experiments never touch the real history.
DATA_DIR            = Path(os.environ.get("QUANTUM_STUDY_DATA_DIR")
                           or (Path.home() / ".local" / "share" / "quantum-study"))
HISTORY_FILE        = DATA_DIR / "flashcard_history.json"
DEFAULT_CARD_COUNT  = 20
DEFAULT_TIMER_SECS  = 0          # 0 = no timer
WINDOW_TITLE        = "Flashcard Drill — Quantum Computing"
WINDOW_MIN_SIZE     = (800, 600)
