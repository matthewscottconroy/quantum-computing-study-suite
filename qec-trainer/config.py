"""App-wide constants."""
import os
from pathlib import Path

APP_NAME              = "QEC Trainer"
APP_DIR_NAME          = "qec-trainer"    # stamped into shared cross-app records

# Shared suite data directory. QUANTUM_STUDY_DATA_DIR overrides it (the same
# override coach.py, launch.py and the other apps honour) so tests and sandboxed
# sessions never touch the real history/flag files; the default is unchanged.
DATA_DIR              = Path(os.environ.get("QUANTUM_STUDY_DATA_DIR")
                             or (Path.home() / ".local" / "share" / "quantum-study"))
HISTORY_FILE          = DATA_DIR / "qec_history.json"
FLAGGED_FILE          = DATA_DIR / "qec_flagged.json"

# Cross-app study-analytics files, shared by every app in the suite (schema is
# the suite-wide contract; entries carry an "app" field).
MISTAKES_FILE         = DATA_DIR / "mistakes.json"
CONFIDENCE_FILE       = DATA_DIR / "confidence.json"
# This app's own small settings blob (e.g. the confidence-prompt opt-out).
SETTINGS_FILE         = DATA_DIR / "qec_settings.json"

API_KEY_FILE          = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL                 = "claude-sonnet-4-6"
DEFAULT_PROBLEM_COUNT = 10
WINDOW_TITLE          = "QEC Trainer — Quantum Error Correction"
WINDOW_MIN_SIZE       = (900, 650)
