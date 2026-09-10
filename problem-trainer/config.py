"""App-wide constants."""
import os
from pathlib import Path

APP_NAME        = "Problem Trainer"
# Shared suite data directory. QUANTUM_STUDY_DATA_DIR overrides it (the same
# override coach.py and launch.py honour) so tests and sandboxed sessions never
# touch the real history/flag files; the default is unchanged.
DATA_DIR        = Path(os.environ.get("QUANTUM_STUDY_DATA_DIR")
                       or (Path.home() / ".local" / "share" / "quantum-study"))
HISTORY_FILE    = DATA_DIR / "problems_history.json"
FLAGGED_FILE    = DATA_DIR / "problems_flagged.json"   # "flag for review" entries
API_KEY_FILE    = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL           = "claude-sonnet-4-6"
MAX_STEP_TRIES  = 2          # failed tries before "show model step" is offered
WINDOW_TITLE    = "Problem Trainer — Textbook Problems & Guided Derivations"
WINDOW_MIN_SIZE = (960, 680)
