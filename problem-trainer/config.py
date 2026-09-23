"""App-wide constants.

The data-directory rule (``QUANTUM_STUDY_DATA_DIR`` if set and non-blank,
otherwise ``~/.local/share/quantum-study``) now comes from
:mod:`common.datadir`, which is the one implementation the whole suite shares —
so a blank override is no override and ``~`` is expanded, neither of which this
app's own copy used to do.

The constants below are resolved **at import time** and are kept because they
are this app's published surface (``config.DATA_DIR`` &c.).  Everything that
*writes* resolves its path at call time through ``persistence``, so setting
``QUANTUM_STUDY_DATA_DIR`` in an already-running process relocates the files
without a reload.
"""
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import datadir

APP_NAME        = "Problem Trainer"
#: Key used in the "app" field of every shared-journal / flag row, and the
#: directory name ``coach.py`` and ``dashboard.py`` group by.
APP_KEY         = "problem-trainer"
# Shared suite data directory. QUANTUM_STUDY_DATA_DIR overrides it (the same
# override coach.py and launch.py honour) so tests and sandboxed sessions never
# touch the real history/flag files; the default is unchanged.
DATA_DIR        = datadir.data_dir()
HISTORY_FILE    = datadir.app_file(APP_KEY, "history")   # problems_history.json
FLAGGED_FILE    = datadir.app_file(APP_KEY, "flagged")   # "flag for review" entries
# Suite-wide study-analytics files, shared by every app (entries carry an "app"
# field); see persistence.py for the schemas.
MISTAKES_FILE   = datadir.mistakes_file()                # mistake journal
CONFIDENCE_FILE = datadir.confidence_file()              # confidence calibration
SETTINGS_FILE   = datadir.app_file(APP_KEY, "settings")  # this app's own UI prefs
API_KEY_FILE    = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL           = "claude-sonnet-4-6"
MAX_STEP_TRIES  = 2          # failed tries before "show model step" is offered
WINDOW_TITLE    = "Problem Trainer — Textbook Problems & Guided Derivations"
WINDOW_MIN_SIZE = (960, 680)
