"""math-quiz's slice of the shared dark theme.

The twelve palette constants, the base stylesheet and ``alpha()`` now live in
:mod:`common.ui.theme` — they were byte-identical in all ten apps.  What stays
here is this app's own *vocabulary* (one colour per mathematical subject, one
per difficulty level) and the handful of widget rules only this app draws:
lists, tables, splitters, tooltips and the status bar.

``from common.ui.theme import *`` re-exports the palette, so every existing
``theme.SURFACE2`` / ``theme.ACCENT`` reference in the app is unchanged.
"""

from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.theme import *          # noqa: F401,F403  (palette, QSS, alpha)
from common.ui.theme import (
    ACCENT2, BORDER, SURFACE, SURFACE2, TEXT, TEXT_MUTED,
    apply as _apply, extend,
)

DIFFICULTY_COLORS = {
    "beginner":     "#1f6feb",
    "intermediate": "#388bfd",
    "advanced":     "#d29922",
    "expert":       "#f85149",
}

# One colour per subject
_SUBJECT_COLORS: dict[str, str] = {
    "Linear Algebra":              "#6e40c9",
    "Abstract Algebra":            "#1f6feb",
    "Representation Theory":       "#2da44e",
    "Complex Analysis":            "#b08800",
    "Calculus & Real Analysis":    "#cf222e",
    "Ordinary Differential Equations": "#0969da",
    "Partial Differential Equations":  "#8250df",
    "Functional Analysis":         "#bf8700",
    "Probability Theory":          "#116329",
    "Fourier Analysis":            "#953800",
    "Number Theory":               "#1a7f37",
    "Topology & Geometry":         "#9a3800",
    "Quantum Connections":         "#1a7f7a",
}

_FALLBACK_PALETTE = [
    "#6e40c9", "#1f6feb", "#2da44e", "#b08800",
    "#cf222e", "#0969da", "#8250df", "#bf8700",
]


def subject_color(subject: str) -> str:
    if subject in _SUBJECT_COLORS:
        return _SUBJECT_COLORS[subject]
    idx = hash(subject) % len(_FALLBACK_PALETTE)
    return _FALLBACK_PALETTE[idx]


#: Rules the base stylesheet does not carry: this app is the one with a
#: history table, a flagged-questions list and a status bar.
_EXTRA = f"""
QLabel#muted {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
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
QTableWidget {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    gridline-color: {BORDER};
}}
QTableWidget::item {{ padding: 6px 10px; }}
QTableWidget::item:selected {{ background-color: {ACCENT2}; }}
QHeaderView::section {{
    background-color: {SURFACE2};
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px 10px;
    font-size: 12px;
    font-weight: bold;
}}
QSplitter::handle {{ background-color: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 1px; }}
QSplitter::handle:vertical {{ height: 1px; }}
QToolTip {{
    background-color: {SURFACE2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 4px;
    padding: 4px 8px;
}}
QStatusBar {{
    background-color: {SURFACE};
    color: {TEXT};
    border-top: 1px solid {BORDER};
    font-size: 12px;
}}
QStatusBar::item {{
    border: none;
}}
"""

#: The app's full stylesheet: the shared base plus the rules above.
QSS = extend(_EXTRA)


def apply(app) -> None:
    """Apply the shared theme plus math-quiz's own rules to a ``QApplication``."""
    _apply(app, QSS)
