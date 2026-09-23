"""App-wide constants.

Where the data lives is **not** decided here any more: ``common.datadir`` owns
that rule for the whole suite (``QUANTUM_STUDY_DATA_DIR``, else
``~/.local/share/quantum-study``) and resolves it **at call time**.  That is
why the paths below are functions rather than module constants: the ten apps
each used to freeze the directory into a constant at import time, so a test had
to reload the module or monkeypatch a private name to redirect it.  Now
``monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", tmp_path)`` is enough, anywhere,
at any point.

The *file names* stay here (and in ``common.datadir.APP_FILES``, which records
them for the suite) because they are load-bearing: ``coach.py`` and
``dashboard.py`` parse ``paper_history.json`` and ``paper_flagged.json`` by
name.
"""
from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import datadir

APP_NAME            = "Paper Drill"
APP_ID              = "paper-drill"   # app directory name — recorded in flagged entries

# File names inside the shared data directory.  Mirrored by
# common.datadir.APP_FILES["paper-drill"]; _check_app_files() below fails the
# import if the two ever drift, because coach.py reads the common list.
HISTORY_NAME        = "paper_history.json"
LIBRARY_NAME        = "paper_library.json"
FLAGGED_NAME        = "paper_flagged.json"
SETTINGS_NAME       = "paper_settings.json"

API_KEY_FILE        = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL               = "claude-sonnet-4-6"
DEFAULT_Q_COUNT     = 5
MAX_PAPER_CHARS     = 12_000     # hard truncation before sending to Claude
WINDOW_TITLE        = "Paper Drill — Quantum Computing"
WINDOW_MIN_SIZE     = (900, 650)


def data_dir() -> Path:
    """The shared suite data directory, resolved now."""
    return datadir.data_dir()


def history_file() -> Path:
    """``paper_history.json`` — sessions; parsed by coach.py and dashboard.py."""
    return datadir.data_file(HISTORY_NAME)


def library_file() -> Path:
    """``paper_library.json`` — saved papers (this app only)."""
    return datadir.data_file(LIBRARY_NAME)


def flagged_file() -> Path:
    """``paper_flagged.json`` — the flag-for-review queue coach.py --review reads."""
    return datadir.data_file(FLAGGED_NAME)


def settings_file() -> Path:
    """``paper_settings.json`` — per-app UI preferences (the confidence opt-out)."""
    return datadir.data_file(SETTINGS_NAME)


def mistakes_file() -> Path:
    """``mistakes.json`` — the suite-wide mistake journal (all ten apps)."""
    return datadir.mistakes_file()


def confidence_file() -> Path:
    """``confidence.json`` — the suite-wide calibration log (all ten apps)."""
    return datadir.confidence_file()


def _check_app_files() -> None:
    """Fail loudly if our names drift from ``common.datadir.APP_FILES``.

    ``coach.py`` finds this app's history through the common table, so a rename
    made in one place and not the other would quietly orphan the file.
    """
    known = datadir.APP_FILES.get(APP_ID, {})
    ours = {"history": HISTORY_NAME, "flagged": FLAGGED_NAME,
            "library": LIBRARY_NAME, "settings": SETTINGS_NAME}
    drift = {k: (v, known.get(k)) for k, v in ours.items() if known.get(k) != v}
    if drift:
        raise RuntimeError(
            f"config.py and common.datadir.APP_FILES[{APP_ID!r}] disagree: {drift}")


_check_app_files()
