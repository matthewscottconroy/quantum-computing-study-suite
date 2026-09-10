"""App-wide constants."""
import os
from pathlib import Path

APP_NAME            = "Paper Drill"
APP_ID              = "paper-drill"   # app directory name — recorded in flagged entries
# Shared suite data directory. QUANTUM_STUDY_DATA_DIR overrides it (the same
# override coach.py and tools/run_tests.sh use) so tests and experiments never
# touch the real study history.
DATA_DIR            = Path(os.environ.get("QUANTUM_STUDY_DATA_DIR")
                           or (Path.home() / ".local" / "share" / "quantum-study"))
HISTORY_FILE        = DATA_DIR / "paper_history.json"
LIBRARY_FILE        = DATA_DIR / "paper_library.json"
FLAGGED_FILE        = DATA_DIR / "paper_flagged.json"
API_KEY_FILE        = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL               = "claude-sonnet-4-6"
DEFAULT_Q_COUNT     = 5
MAX_PAPER_CHARS     = 12_000     # hard truncation before sending to Claude
WINDOW_TITLE        = "Paper Drill — Quantum Computing"
WINDOW_MIN_SIZE     = (900, 650)
