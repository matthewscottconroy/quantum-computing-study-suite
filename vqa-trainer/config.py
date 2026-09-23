"""App-wide constants."""
import os
from pathlib import Path

APP_NAME              = "VQA Trainer"
APP_DIR_NAME          = "vqa-trainer"   # "app" field in the shared journal files
# Shared suite data directory. QUANTUM_STUDY_DATA_DIR overrides it (the same
# override coach.py, launch.py and the other apps honour) so tests and sandboxed
# sessions never touch the real history; the default is unchanged. Read once at
# import time, like every other app in the suite.
_DATA_OVERRIDE        = os.environ.get("QUANTUM_STUDY_DATA_DIR", "").strip()
DATA_DIR              = (
    Path(_DATA_OVERRIDE).expanduser() if _DATA_OVERRIDE
    else Path.home() / ".local" / "share" / "quantum-study"
)
HISTORY_FILE          = DATA_DIR / "vqa_history.json"
FLAGGED_FILE          = DATA_DIR / "vqa_flagged.json"
MISTAKES_FILE         = DATA_DIR / "mistakes.json"      # shared suite mistake journal
CONFIDENCE_FILE       = DATA_DIR / "confidence.json"    # shared suite calibration log
SETTINGS_FILE         = DATA_DIR / "vqa_settings.json"  # this app's own preferences
API_KEY_FILE          = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL                 = "claude-sonnet-4-6"
DEFAULT_PROBLEM_COUNT = 8
WINDOW_TITLE          = "VQA Trainer — Variational Quantum Algorithms"
WINDOW_MIN_SIZE       = (920, 660)
