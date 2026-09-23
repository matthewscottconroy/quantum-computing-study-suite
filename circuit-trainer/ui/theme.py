"""Circuit Trainer's theme: the shared suite palette plus this app's vocabulary.

The twelve palette constants (``BG`` … ``PARTIAL``) and the base stylesheet now
come from :mod:`common.ui.theme`, where they were byte-identical in all ten
apps before the extraction — so nothing here is a compromise, it is what this
app already used.  ``PURPLE`` and ``TEAL`` were circuit-trainer's own additions
and were promoted with it.

What stays here is what is genuinely this app's: the two colour maps keyed by
*this* app's words (``ProblemCategory`` values and the three difficulty names),
and the handful of stylesheet rules for widgets only this app has — the
multiple-choice buttons in their four graded states, the confidence strip, the
"What went wrong?" cause buttons, the history table, and the teal focus ring
those controls use.  ``extend()`` appends them to the shared base, so the
accessibility rules and the pill rules in the base are inherited rather than
re-stated.
"""

import common_path  # noqa: F401  (puts the repo root on sys.path)

from PyQt6.QtWidgets import QApplication

from common.ui.theme import *            # noqa: F403  (the shared palette)
from common.ui.theme import (            # noqa: F401  (names used below)
    ACCENT, ACCENT2, BORDER, ERROR, SUCCESS, SURFACE, SURFACE2, TEAL, TEXT,
    MONO, TEXT_MUTED, WARNING, alpha, extend,
)
from common.ui.theme import apply as _apply

CATEGORY_COLORS = {
    "Single-gate output":         "#1f6feb",
    "Gate sequence":              "#388bfd",
    "Measurement probabilities":  "#2da44e",
    "Gate / matrix identification": "#8250df",
    "Circuit unitary":            "#bf8700",
    "Entanglement detection":     "#cf222e",
    "Multi-qubit circuit output": "#0969da",
    "Circuit equivalence":        "#6e40c9",
    "Notation reading":           "#116329",
    "Circuit composition":        "#953800",
    "Noise channel":              "#9a6700",
    "Circuit explanation":        "#1a7f37",
}

DIFFICULTY_COLORS = {
    "beginner":     "#1f6feb",
    "intermediate": "#d29922",
    "advanced":     "#f85149",
}

#: Rules for the widgets only Circuit Trainer has.  Appended to the shared
#: base stylesheet by :data:`QSS`.
EXTRA_QSS = f"""
QPushButton#choice {{
    background-color: {SURFACE}; color: {TEXT};
    border: 2px solid {BORDER}; border-radius: 8px;
    padding: 12px 16px; font-size: 14px; text-align: left;
}}
QPushButton#choice:hover {{ border-color: {ACCENT}; background-color: {SURFACE2}; }}
QPushButton#choice_correct {{
    background-color: {alpha(SUCCESS, 13)}; color: {SUCCESS};
    border: 2px solid {SUCCESS}; border-radius: 8px; padding: 12px 16px; font-size: 14px; text-align: left;
}}
QPushButton#choice_wrong {{
    background-color: {alpha(ERROR, 13)}; color: {ERROR};
    border: 2px solid {ERROR}; border-radius: 8px; padding: 12px 16px; font-size: 14px; text-align: left;
}}
QPushButton#choice_missed {{
    background-color: {alpha(WARNING, 13)}; color: {WARNING};
    border: 2px solid {WARNING}; border-radius: 8px; padding: 12px 16px; font-size: 14px; text-align: left;
}}
/* ── Confidence strip + mistake-journal causes ───────────────────────────────
   Both use text labels (never colour alone) for meaning; the selected state
   adds a ✓ glyph as well as the accent colour. */
QPushButton#confidence, QPushButton#cause {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 6px 10px; font-size: 12px;
}}
QPushButton#confidence:hover, QPushButton#cause:hover {{
    background-color: {BORDER}; border-color: {ACCENT};
}}
QPushButton#confidence_on, QPushButton#cause_on {{
    background-color: {SURFACE2}; color: {ACCENT};
    border: 2px solid {ACCENT}; border-radius: 6px;
    padding: 5px 9px; font-size: 12px; font-weight: bold;
}}
/* Visible keyboard focus ring on every interactive control.  The shared base
   already draws one in ACCENT; this app's is teal, so it reads against the
   accent fill a selected pill uses. */
QPushButton:focus, QPushButton#accent:focus, QPushButton#flat:focus,
QPushButton#choice:focus, QPushButton#confidence:focus,
QPushButton#confidence_on:focus, QPushButton#cause:focus,
QPushButton#cause_on:focus {{
    border: 2px solid {TEAL};
}}
/* The padding shrinks by the pixel the border grows, so focusing a field
   never nudges the layout. */
QLineEdit:focus {{ border: 2px solid {TEAL}; padding: 4px 7px; }}
QPlainTextEdit:focus, QTextEdit:focus {{ border: 2px solid {TEAL}; padding: 7px; }}
QCheckBox:focus {{ color: {TEAL}; }}
QCheckBox::indicator:focus {{ border: 2px solid {TEAL}; }}
QLabel#muted {{ color: {TEXT_MUTED}; font-size: 12px; }}
QLabel#mono {{ font-family: {MONO}; font-size: 13px; }}
QTableWidget {{
    background-color: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 6px; gridline-color: {BORDER};
}}
QTableWidget::item {{ padding: 6px 10px; }}
QTableWidget::item:selected {{ background-color: {ACCENT2}; }}
QHeaderView::section {{
    background-color: {SURFACE2}; color: {TEXT_MUTED};
    border: none; border-bottom: 1px solid {BORDER};
    padding: 6px 10px; font-size: 12px; font-weight: bold;
}}
QSplitter::handle:horizontal {{ width: 1px; background: {BORDER}; }}
QSplitter::handle:vertical {{ height: 1px; background: {BORDER}; }}
QToolTip {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 4px; padding: 4px 8px;
}}
"""

#: The whole stylesheet this app applies: the shared base plus EXTRA_QSS.
QSS = extend(EXTRA_QSS)


def apply(app: QApplication) -> None:
    """Apply the suite theme with this app's extra rules."""
    _apply(app, QSS)
