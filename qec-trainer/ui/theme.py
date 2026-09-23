"""Dark theme for qec-trainer.

The palette and the base stylesheet are :mod:`common.ui.theme` — they were
byte-identical in all ten apps, so nothing here is a compromise.  What stays is
this app's own vocabulary: the colour it gives each QEC topic.

``from common.ui.theme import *`` re-exports ``BG``/``SURFACE``/``ACCENT``/…,
``QSS``, ``alpha()`` and ``extend()``, so every ``theme.X`` reference in this
app's screens keeps working unchanged.
"""
from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from PyQt6.QtWidgets import QApplication

from common.ui.theme import *          # noqa: F401,F403  (the shared palette)
from common.ui.theme import QSS, apply as _apply, extend  # noqa: F401

#: This app's vocabulary: one colour per QEC topic.  Used by the setup screen's
#: mastery bars, the problem header and the history chart.
CATEGORY_COLORS = {
    "Repetition Code":       "#6e40c9",
    "Stabilizer Formalism":  "#1f6feb",
    "Steane Code":           "#2da44e",
    "Surface Code":          "#b08800",
    "Fault Tolerance":       "#cf222e",
}


# `import *` brings the shared `apply` in; shadowing it deliberately is the
# documented pattern (common/README.md §2), so the redefinition is expected.
def apply(app: QApplication) -> None:                # type: ignore[no-redef]
    """Apply the suite theme to *app* (qec-trainer adds no rules of its own)."""
    _apply(app, extend())
