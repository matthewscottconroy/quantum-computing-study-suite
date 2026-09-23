"""App-wide constants and the paths of every file this app writes.

Paths are **resolved at call time** through :mod:`common.datadir`, which reads
``QUANTUM_STUDY_DATA_DIR`` on every call (blank = no override, ``~`` expanded).
They used to be module constants frozen at import, which is why the test suite
had to relocate each one by hand; ``monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR",
tmp_path)`` is now all that is needed, anywhere, at any time.

The file *names* are not invented here: they come from
``common.datadir.APP_FILES["flashcard-drill"]``, which is where the suite
records them, because ``coach.py`` and ``dashboard.py`` parse
``flashcard_history.json`` and ``flagged_cards.json`` by name.  Those schemas
are load-bearing and unchanged by the migration.
"""
from __future__ import annotations

from pathlib import Path

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common import datadir

#: The app directory name — the identity ``coach.py``/``dashboard.py`` group by
#: and the owner recorded in every row this app writes to a shared file.
APP = "flashcard-drill"

APP_NAME            = "Flashcard Drill"
DEFAULT_CARD_COUNT  = 20
DEFAULT_TIMER_SECS  = 0          # 0 = no timer
WINDOW_TITLE        = "Flashcard Drill — Quantum Computing"
WINDOW_MIN_SIZE     = (800, 600)


def data_dir() -> Path:
    """The suite data directory, resolved now (honours the env override)."""
    return datadir.data_dir()


def ensure_data_dir() -> Path:
    """:func:`data_dir`, created if it does not exist."""
    return datadir.ensure_data_dir()


def history_file() -> Path:
    """``flashcard_history.json`` — parsed by coach.py/dashboard.py."""
    return datadir.app_file(APP, "history")


def flagged_file() -> Path:
    """``flagged_cards.json`` — this app predates the ``<prefix>_flagged`` name,
    and coach.py maps the legacy one explicitly, so it stays."""
    return datadir.app_file(APP, "flagged")


def schedule_file() -> Path:
    """``flashcard_schedule.json`` — the SM-2 schedule, private to this app."""
    return datadir.app_file(APP, "schedule")


def settings_file() -> Path:
    """``flashcard_settings.json`` — this app's preferences."""
    return datadir.app_file(APP, "settings")


def mistakes_file() -> Path:
    """``mistakes.json`` — shared with the other nine apps."""
    return datadir.mistakes_file()


def confidence_file() -> Path:
    """``confidence.json`` — shared with the other nine apps."""
    return datadir.confidence_file()


__all__ = [
    "APP", "APP_NAME", "DEFAULT_CARD_COUNT", "DEFAULT_TIMER_SECS",
    "WINDOW_TITLE", "WINDOW_MIN_SIZE",
    "data_dir", "ensure_data_dir", "history_file", "flagged_file",
    "schedule_file", "settings_file", "mistakes_file", "confidence_file",
]
