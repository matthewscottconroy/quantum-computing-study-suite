"""App-wide constants.

The data directory and the file names come from :mod:`common.datadir`, which
is the one resolver the whole suite (all ten apps, ``coach.py``,
``dashboard.py``, ``launch.py`` and ``tools/``) honours:
``QUANTUM_STUDY_DATA_DIR`` if it is set and non-blank, else
``~/.local/share/quantum-study``.

The constants below are an **import-time snapshot** of that resolution, kept
because they are this app's long-standing published names.  Everything that
actually reads or writes resolves the path again at call time (see
``persistence.py``), so setting ``QUANTUM_STUDY_DATA_DIR`` is enough to move
the whole app — no monkeypatching of constants required.
"""
import common_path  # noqa: F401  (puts the repo root on sys.path)

from pathlib import Path

from common import datadir

APP_NAME              = "VQA Trainer"
APP_DIR_NAME          = "vqa-trainer"   # "app" field in the shared journal files
DATA_DIR              = datadir.data_dir()
HISTORY_FILE          = datadir.app_file(APP_DIR_NAME, "history")
FLAGGED_FILE          = datadir.app_file(APP_DIR_NAME, "flagged")
MISTAKES_FILE         = datadir.mistakes_file()      # shared suite mistake journal
CONFIDENCE_FILE       = datadir.confidence_file()    # shared suite calibration log
SETTINGS_FILE         = datadir.app_file(APP_DIR_NAME, "settings")
API_KEY_FILE          = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL                 = "claude-sonnet-4-6"
DEFAULT_PROBLEM_COUNT = 8
WINDOW_TITLE          = "VQA Trainer — Variational Quantum Algorithms"
WINDOW_MIN_SIZE       = (920, 660)
