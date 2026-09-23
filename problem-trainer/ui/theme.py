"""Dark theme — the suite palette from :mod:`common.ui.theme`, plus this app's
own vocabulary.

The twelve palette constants and the bulk of the stylesheet were byte-identical
in all ten apps and now live in ``common.ui.theme``; ``from ... import *``
re-exports them so ``theme.ACCENT``, ``theme.SURFACE`` &c. still resolve here
exactly as before.  What stays is what is genuinely this app's: the topic
colour map, the flag-button labels, and the handful of widget rules the shared
base does not carry (the item list, the step progress bar, the splitter and the
``#flag`` toggle).
"""
from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.theme import *          # noqa: F401,F403  (the shared palette)
# Named explicitly as well as via the star import: the f-strings below and the
# app's own widgets use these, and a type checker cannot follow a star import.
from common.ui.theme import (
    ACCENT, ACCENT2, BORDER, ERROR, MONO, PARTIAL, QSS as BASE_QSS, SUCCESS,
    SURFACE, SURFACE2, TEXT, TEXT_MUTED, WARNING, alpha, apply as _apply,
    extend,
)

TOPIC_COLORS = {
    "Linear Algebra & QM Math": "#6e40c9",
    "Circuits & Gates":         "#1f6feb",
    "Algorithms":               "#2da44e",
    "Error Correction":         "#cf222e",
    "VQA":                      "#b08800",
    "Information Theory":       "#0969da",
    "Derivation":               "#d29922",
}

# Labels for the "flag for review" toggle — shared by the problem, derivation
# and summary screens so the same button reads the same way everywhere.
FLAG_ON_TEXT  = "⚑ Flagged for review"
FLAG_OFF_TEXT = "⚑ Flag for review"

# Rules the shared base does not carry, because only some apps have these
# widgets: the Setup item list, the derivation step progress bar, the Reference
# splitter, and the "⚑ Flag for review" toggle.  The base's QPlainTextEdit /
# QLineEdit padding is also restored to this app's roomier answer-box sizing.
_EXTRA = f"""
QListWidget {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 4px;
}}
QListWidget::item {{ padding: 8px 10px; border-radius: 4px; }}
QListWidget::item:selected {{ background-color: {ACCENT2}; color: white; }}
QListWidget::item:hover {{ background-color: {SURFACE2}; }}
QProgressBar {{
    background: {SURFACE2}; border: none; border-radius: 4px;
    height: 8px; text-align: center; color: transparent;
}}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 4px; }}
QRadioButton {{ spacing: 8px; color: {TEXT}; }}
QRadioButton::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {BORDER}; border-radius: 8px; background: {SURFACE2};
}}
QRadioButton::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QComboBox:hover {{ border-color: {ACCENT}; }}
QSplitter::handle {{ background: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 1px; }}
QPlainTextEdit, QTextEdit, QLineEdit {{ padding: 8px; font-size: 14px; }}
QLineEdit:focus {{ border: 2px solid {ACCENT}; padding: 7px; }}
QPushButton#flag {{
    background: transparent; border: 1px solid {BORDER};
    color: {TEXT_MUTED}; padding: 6px 12px;
}}
QPushButton#flag:hover {{ border-color: {WARNING}; color: {WARNING}; }}
QPushButton#flag:checked {{ border-color: {WARNING}; color: {WARNING}; font-weight: bold; }}
QPushButton#flag:focus {{ border: 2px solid {ACCENT}; padding: 5px 11px; }}
"""

#: The full stylesheet this app applies (base + the rules above).  Kept under
#: the old name so anything that read ``theme.QSS`` still gets what is applied.
QSS = extend(_EXTRA)


def apply(app) -> None:
    """Apply the suite theme plus this app's extra rules to a QApplication."""
    _apply(app, QSS)
