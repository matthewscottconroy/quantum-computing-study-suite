"""This app's slice of the shared dark theme.

The twelve palette constants, the base stylesheet, the focus rings and
:func:`alpha` now live in :mod:`common.ui.theme` (they were byte-identical in
all ten apps).  What stays here is quantum-quiz's own vocabulary — the subject
and difficulty colour maps — plus the handful of widget rules the base theme
has no opinion about.
"""

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.theme import *          # noqa: F401,F403  (palette + helpers)
from common.ui.theme import apply as _apply, extend

# ── This app's vocabulary ─────────────────────────────────────────────────────

# Difficulty pill colours
DIFFICULTY_COLORS = {
    "beginner":     "#1f6feb",
    "intermediate": "#388bfd",
    "advanced":     "#d29922",
    "expert":       "#f85149",
}

# Subject pill colours — one distinct slot per curriculum subject.  The list
# is derived from core.topics.TOPICS so a subject added to the curriculum gets
# its own colour instead of silently sharing slot 0.  Keep the palette at
# least as long as TOPICS (asserted in tests/test_topics_and_contexts.py).
_SUBJECT_PALETTE = [
    "#6e40c9", "#1f6feb", "#2da44e", "#b08800",
    "#cf222e", "#0969da", "#8250df", "#bf8700",
    "#116329", "#953800", "#1b7c83", "#a40e4c",
]


def _subject_order() -> list[str]:
    from core.topics import TOPICS   # local import: theme must stay Qt-only at import time
    return sorted(TOPICS)


def subject_color(subject: str) -> str:
    subjects = _subject_order()
    idx = subjects.index(subject) if subject in subjects else 0
    return _SUBJECT_PALETTE[idx % len(_SUBJECT_PALETTE)]


# ── Rules the base stylesheet does not carry ──────────────────────────────────
# The base has the confidence/cause pills under ``#pill``; this app has always
# called them ``#chip`` and its tests pin that, so the chip rules stay here.
# The list / table / splitter / tooltip rules are this app's alone.

_EXTRA = f"""
/* ── Chip buttons (confidence strip, mistake-cause row) ── */
QPushButton#chip {{
    background-color: {SURFACE2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 4px 14px;
    font-size: 12px;
}}
QPushButton#chip:hover {{
    border-color: {ACCENT};
}}
/* Selected chips also gain a ✓ in their label — never colour alone.  The font
   weight is deliberately unchanged: a bolder label would outgrow the width the
   layout measured for the unselected state and clip. */
QPushButton#chip:checked {{
    background-color: {ACCENT};
    color: {BG};
    border-color: {ACCENT};
}}
QPushButton#chip:focus, QPushButton#chip:checked:focus {{
    border: 1px solid {TEXT};
}}

/* ── Muted one-line hints and statuses ── */
QLabel#muted {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}

/* ── List widget ── */
QListWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px;
}}
QListWidget::item {{
    padding: 4px 8px;
    border-radius: 4px;
}}
QListWidget::item:selected {{
    background-color: {ACCENT2};
    color: white;
}}

/* ── Table widget ── */
QTableWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    gridline-color: {BORDER};
}}
QTableWidget::item {{
    padding: 6px 10px;
}}
QTableWidget::item:selected {{
    background-color: {ACCENT2};
}}
QHeaderView::section {{
    background-color: {SURFACE2};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px 10px;
    font-size: 12px;
    font-weight: bold;
}}

/* ── Splitter ── */
QSplitter::handle {{
    background-color: {BORDER};
}}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical {{ height: 1px; }}

/* ── Tool tip ── */
QToolTip {{
    background-color: {SURFACE2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
}}
"""

#: The full stylesheet this app applies: the shared base plus the rules above.
QSS = extend(_EXTRA)


def apply(app) -> None:
    _apply(app, QSS)
