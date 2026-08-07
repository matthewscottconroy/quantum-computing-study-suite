"""App-wide constants."""
from pathlib import Path

APP_NAME            = "Paper Drill"
DATA_DIR            = Path.home() / ".local" / "share" / "quantum-study"
HISTORY_FILE        = DATA_DIR / "paper_history.json"
LIBRARY_FILE        = DATA_DIR / "paper_library.json"
API_KEY_FILE        = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL               = "claude-sonnet-4-6"
DEFAULT_Q_COUNT     = 5
MAX_PAPER_CHARS     = 12_000     # hard truncation before sending to Claude
WINDOW_TITLE        = "Paper Drill — Quantum Computing"
WINDOW_MIN_SIZE     = (900, 650)
