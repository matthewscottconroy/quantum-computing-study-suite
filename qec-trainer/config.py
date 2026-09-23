"""App-wide constants for qec-trainer.

Where the data lives is no longer decided here: :mod:`common.datadir` owns the
one rule the whole suite follows (``QUANTUM_STUDY_DATA_DIR`` if set and
non-blank, else ``~/.local/share/quantum-study``) and the file names live in
``common.datadir.APP_FILES["qec-trainer"]``, beside the other nine apps.

Every path below is resolved **at call time**, never frozen at import.  The
module-level names (``DATA_DIR``, ``HISTORY_FILE``, …) are kept as a
backwards-compatible surface — ``config.DATA_DIR`` still works everywhere it
did — but they are computed on each attribute access through PEP 562's module
``__getattr__``.  That is what makes ``monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR",
tmp)`` sufficient on its own: nothing has to be reloaded or re-patched.
"""
from __future__ import annotations

from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import datadir

APP_NAME              = "QEC Trainer"
APP_DIR_NAME          = "qec-trainer"    # stamped into shared cross-app records

API_KEY_FILE          = Path.home() / ".config" / "quantum-study" / "api_key.txt"
MODEL                 = "claude-sonnet-4-6"
DEFAULT_PROBLEM_COUNT = 10
WINDOW_TITLE          = "QEC Trainer — Quantum Error Correction"
WINDOW_MIN_SIZE       = (900, 650)


# ── Paths (resolved now, on every call) ───────────────────────────────────────

def data_dir() -> Path:
    """The suite data directory — honours ``QUANTUM_STUDY_DATA_DIR``."""
    return datadir.data_dir()


def history_file() -> Path:
    """``qec_history.json`` — this app's own, load-bearing session history."""
    return datadir.app_file(APP_DIR_NAME, "history")


def flagged_file() -> Path:
    """``qec_flagged.json`` — this app's flag-for-review store."""
    return datadir.app_file(APP_DIR_NAME, "flagged")


def settings_file() -> Path:
    """``qec_settings.json`` — this app's small local settings blob."""
    return datadir.app_file(APP_DIR_NAME, "settings")


def mistakes_file() -> Path:
    """``mistakes.json`` — the suite-wide mistake journal (all ten apps)."""
    return datadir.mistakes_file()


def confidence_file() -> Path:
    """``confidence.json`` — the suite-wide calibration log (all ten apps)."""
    return datadir.confidence_file()


#: Backwards-compatible constant names -> the function that resolves them.
_PATHS = {
    "DATA_DIR":        data_dir,
    "HISTORY_FILE":    history_file,
    "FLAGGED_FILE":    flagged_file,
    "SETTINGS_FILE":   settings_file,
    "MISTAKES_FILE":   mistakes_file,
    "CONFIDENCE_FILE": confidence_file,
}


def __getattr__(name: str) -> Path:            # PEP 562
    """``config.DATA_DIR`` &c., resolved at the moment they are read."""
    try:
        return _PATHS[name]()
    except KeyError:
        raise AttributeError(
            f"module {__name__!r} has no attribute {name!r}") from None


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(_PATHS))
