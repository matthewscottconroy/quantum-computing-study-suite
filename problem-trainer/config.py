"""App-wide constants."""
from pathlib import Path

APP_NAME        = "Problem Trainer"
DATA_DIR        = Path.home() / ".local" / "share" / "quantum-study"
HISTORY_FILE    = DATA_DIR / "problems_history.json"
API_KEY_FILE    = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL           = "claude-sonnet-4-6"
MAX_STEP_TRIES  = 2          # failed tries before "show model step" is offered
WINDOW_TITLE    = "Problem Trainer — Textbook Problems & Guided Derivations"
WINDOW_MIN_SIZE = (960, 680)
