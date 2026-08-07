"""App-wide constants."""
from pathlib import Path

APP_NAME              = "VQA Trainer"
DATA_DIR              = Path.home() / ".local" / "share" / "quantum-study"
HISTORY_FILE          = DATA_DIR / "vqa_history.json"
API_KEY_FILE          = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL                 = "claude-sonnet-4-6"
DEFAULT_PROBLEM_COUNT = 8
WINDOW_TITLE          = "VQA Trainer — Variational Quantum Algorithms"
WINDOW_MIN_SIZE       = (920, 660)
