"""``quantum_study.common`` — the code the ten study apps share.

Before this package existed each of the ten PyQt6 apps
(circuit-trainer, exam-sim, flashcard-drill, math-quiz, paper-drill,
problem-trainer, qec-trainer, qiskit-dojo, quantum-quiz, vqa-trainer)
carried its own near-identical copy of the data-directory resolver, the
mistake/confidence journal, the flag-for-review store, the theme palette and
an ~900-line docs Reference screen.  Roughly ten thousand duplicated lines, in
which every cross-cutting fix was a ten-way edit — the data-loss race in the
journal had to be fixed ten times — and any one app could silently drift.

Layout
------
``common.datadir``    where the suite's data files live (env-overridable).
``common.jsonio``     atomic JSON writes and forgiving JSON reads.
``common.locking``    the cross-process advisory lock (``fcntl.flock``).
``common.schema``     schema versions, forward migration, rotating backups.
``common.journal``    mistakes.json / confidence.json — the shared journal.
``common.flags``      <prefix>_flagged.json — the flag-for-review store.
``common.errata``     prefilled GitHub issue URLs for wrong study items.
``common.choices``    shuffled display order for multiple-choice options.
``common.llm``        the Claude model id, named once.
``common.testing``    test support behind the repository's root conftest.py.
``common.ui.*``       Qt-dependent pieces: theme, widgets, Reference screen.

Nothing outside ``common.ui`` imports PyQt6, so ``coach.py``, ``dashboard.py``
and ``tools/`` can use this package headlessly.
"""
from __future__ import annotations

#: Version of the *shared API*, not of the suite.  Bump the minor when a
#: function is added, the major when one changes shape or disappears.
__version__ = "1.1.0"

__all__ = ["__version__"]
