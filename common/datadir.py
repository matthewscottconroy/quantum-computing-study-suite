"""Where the suite keeps its data.

One rule, honoured by all ten apps, ``coach.py``, ``dashboard.py``,
``launch.py`` and ``tools/``:

    ``QUANTUM_STUDY_DATA_DIR`` if it is set and non-blank,
    otherwise ``~/.local/share/quantum-study``.

**Read at call time, never cached.**  The ten copies this replaces all
resolved the directory at *import* time into a module constant, which is why
every app test that wanted a scratch directory had to monkeypatch a different
private name (``persistence._DATA_DIR``, ``config.DATA_DIR``,
``review_store.config.DATA_DIR`` …).  Resolving on each call means
``monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", tmp_path)`` is enough, in any
process, at any point, and a test can never leak into the real study history.

Reconciled divergences (the ten copies did not agree):

* ``.strip()`` on the override — qiskit-dojo and vqa-trainer had it, the other
  eight did not, so ``QUANTUM_STUDY_DATA_DIR=" "`` gave eight apps a directory
  literally named " " and two the default.  **Kept:** a blank override is no
  override.
* ``.expanduser()`` — circuit-trainer, qiskit-dojo and vqa-trainer had it, the
  other seven did not, so ``QUANTUM_STUDY_DATA_DIR=~/scratch`` (unexpanded by
  a shell that did not expand it, e.g. from a config file or a systemd unit)
  created a directory called ``~`` in the working directory for seven of them.
  **Kept:** expand it.
* No ``.resolve()``: a relative override stays relative, which is what a test
  that sets it to ``tmp_path`` and then chdirs elsewhere expects to break
  loudly rather than silently follow.
"""
from __future__ import annotations

import os
from pathlib import Path

#: The environment variable every part of the suite honours.
ENV_VAR = "QUANTUM_STUDY_DATA_DIR"

#: Where the data lives when the variable is unset or blank.
DEFAULT_SUBPATH = (".local", "share", "quantum-study")


def default_data_dir() -> Path:
    """``~/.local/share/quantum-study`` — the location with no override."""
    return Path.home().joinpath(*DEFAULT_SUBPATH)


def data_dir() -> Path:
    """The suite data directory, resolved now.

    Never creates anything: a read-only caller must not bring a directory into
    being.  Use :func:`ensure_data_dir` when you are about to write.
    """
    override = (os.environ.get(ENV_VAR) or "").strip()
    if override:
        return Path(override).expanduser()
    return default_data_dir()


def ensure_data_dir() -> Path:
    """:func:`data_dir`, created (with parents) if it does not exist."""
    target = data_dir()
    target.mkdir(parents=True, exist_ok=True)
    return target


def data_file(name: str) -> Path:
    """Path of one file inside the data directory, resolved now.

    ``name`` is a bare file name (``"mistakes.json"``); a path separator in it
    is a programming error and raises, because a data file outside the data
    directory is never intended.
    """
    if not name or "/" in name or "\\" in name or name in (".", ".."):
        raise ValueError(f"data_file() takes a bare file name, got {name!r}")
    return data_dir() / name


#: The two suite-wide journal files (see :mod:`common.journal`).
MISTAKES_FILE = "mistakes.json"
CONFIDENCE_FILE = "confidence.json"


def mistakes_file() -> Path:
    """Path of the shared mistake journal, resolved now."""
    return data_file(MISTAKES_FILE)


def confidence_file() -> Path:
    """Path of the shared confidence-calibration log, resolved now."""
    return data_file(CONFIDENCE_FILE)


#: Per-app file names, keyed by the app directory name.  These schemas are
#: load-bearing — ``coach.py`` and ``dashboard.py`` parse them — so the names
#: are recorded here rather than being reinvented per app.  ``flashcard-drill``
#: predates the ``<prefix>_flagged.json`` convention; coach.py maps its legacy
#: name explicitly, so it stays.
APP_FILES: dict[str, dict[str, str]] = {
    "circuit-trainer": {"history": "trainer_history.json",
                        "flagged": "trainer_flagged.json",
                        "settings": "trainer_prefs.json"},
    "exam-sim":        {"history": "exam_history.json",
                        "missed":  "exam_missed.json",
                        "settings": "exam_settings.json"},
    "flashcard-drill": {"history": "flashcard_history.json",
                        "flagged": "flagged_cards.json",      # legacy name
                        "schedule": "flashcard_schedule.json",
                        "settings": "flashcard_settings.json"},
    "math-quiz":       {"history": "math_history.json",
                        "flagged": "math_flagged.json",
                        "draft":   "math_draft.json",
                        "settings": "math_settings.json"},
    "paper-drill":     {"history": "paper_history.json",
                        "flagged": "paper_flagged.json",
                        "library": "paper_library.json",
                        "settings": "paper_settings.json"},
    "problem-trainer": {"history": "problems_history.json",
                        "flagged": "problems_flagged.json",
                        "settings": "problems_settings.json"},
    "qec-trainer":     {"history": "qec_history.json",
                        "flagged": "qec_flagged.json",
                        "settings": "qec_settings.json"},
    "qiskit-dojo":     {"history": "dojo_history.json",
                        "flagged": "dojo_flagged.json",
                        "settings": "dojo_settings.json"},
    "quantum-quiz":    {"history": "quiz_history.json",
                        "flagged": "quiz_flagged.json",
                        "draft":   "quiz_draft.json",
                        "settings": "quiz_settings.json"},
    "vqa-trainer":     {"history": "vqa_history.json",
                        "flagged": "vqa_flagged.json",
                        "settings": "vqa_settings.json"},
}

#: Every app directory name, in the order the suite lists them.
APPS: tuple[str, ...] = tuple(sorted(APP_FILES))


def app_file(app: str, kind: str) -> Path:
    """Path of one of *app*'s own files, e.g. ``app_file("qec-trainer", "flagged")``.

    Raises KeyError for an unknown app or an unknown kind, which is what you
    want from a typo in a file name that ``coach.py`` also parses.
    """
    try:
        name = APP_FILES[app][kind]
    except KeyError:
        known = ", ".join(sorted(APP_FILES.get(app, {}))) or ", ".join(APPS)
        raise KeyError(f"no {kind!r} file for app {app!r} (known: {known})") from None
    return data_file(name)


__all__ = [
    "ENV_VAR", "DEFAULT_SUBPATH", "MISTAKES_FILE", "CONFIDENCE_FILE",
    "APP_FILES", "APPS",
    "default_data_dir", "data_dir", "ensure_data_dir", "data_file",
    "mistakes_file", "confidence_file", "app_file",
]
