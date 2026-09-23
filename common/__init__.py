"""``common`` — the code the ten study apps genuinely share.

Before this package existed each of the ten PyQt6 apps
(circuit-trainer, exam-sim, flashcard-drill, math-quiz, paper-drill,
problem-trainer, qec-trainer, qiskit-dojo, quantum-quiz, vqa-trainer)
carried its own near-identical copy of the data-directory resolver, the
mistake/confidence journal, the flag-for-review store, the theme palette and
an ~900-line docs Reference screen.  Roughly ten thousand duplicated lines, in
which every cross-cutting fix was a ten-way edit — the data-loss race in the
journal had to be fixed ten times — and any one app could silently drift.

Import contract
---------------
The apps are **not** packages: each is run as ``cd <app> && python main.py``
and several define the same top-level module names (``config``, ``core``,
``ui``, ``persistence``), so the repository root is not importable by default.
Copy ``common/app_shim.py`` to ``<app>/common_path.py`` and import it before
anything from ``common``::

    import common_path            # noqa: F401  (puts the repo root on sys.path)
    from common import journal

See ``common/README.md`` for the full contract; it is what the migration
agents follow verbatim.

Layout
------
``common.datadir``    where the suite's data files live (env-overridable).
``common.jsonio``     atomic JSON writes and forgiving JSON reads.
``common.locking``    the cross-process advisory lock (``fcntl.flock``).
``common.schema``     schema versions, forward migration, rotating backups.
``common.journal``    mistakes.json / confidence.json — the shared journal.
``common.flags``      <prefix>_flagged.json — the flag-for-review store.
``common.errata``     prefilled GitHub issue URLs for wrong study items.
``common.ui.*``       Qt-dependent pieces: theme, widgets, Reference screen.

Nothing outside ``common.ui`` imports PyQt6, so ``coach.py``, ``dashboard.py``
and ``tools/`` can use this package headlessly.
"""
from __future__ import annotations

#: Version of the *shared API*, not of the suite.  Bump the minor when a
#: function is added, the major when one changes shape or disappears.
__version__ = "1.0.0"

__all__ = ["__version__"]
