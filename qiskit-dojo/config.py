"""App-wide constants."""
from pathlib import Path

APP_NAME           = "Qiskit Dojo"
DATA_DIR           = Path.home() / ".local" / "share" / "quantum-study"
HISTORY_FILE       = DATA_DIR / "dojo_history.json"
API_KEY_FILE       = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL              = "claude-sonnet-4-6"
DEFAULT_KATA_COUNT = 8
RUN_TIMEOUT_SECS   = 20
WINDOW_TITLE       = "Qiskit Dojo — Hands-On Qiskit Katas"
WINDOW_MIN_SIZE    = (1080, 700)
