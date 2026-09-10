"""App-wide constants."""
import os
from pathlib import Path

APP_NAME           = "Qiskit Dojo"
APP_DIR_NAME       = "qiskit-dojo"          # "app" field in flagged entries (coach.py)
_DATA_OVERRIDE     = os.environ.get("QUANTUM_STUDY_DATA_DIR", "").strip()
DATA_DIR           = (
    Path(_DATA_OVERRIDE).expanduser() if _DATA_OVERRIDE
    else Path.home() / ".local" / "share" / "quantum-study"
)
HISTORY_FILE       = DATA_DIR / "dojo_history.json"
FLAGGED_FILE       = DATA_DIR / "dojo_flagged.json"
API_KEY_FILE       = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL              = "claude-sonnet-4-6"
DEFAULT_KATA_COUNT = 8
RUN_TIMEOUT_SECS   = 20
WINDOW_TITLE       = "Qiskit Dojo — Hands-On Qiskit Katas"
WINDOW_MIN_SIZE    = (1080, 700)
