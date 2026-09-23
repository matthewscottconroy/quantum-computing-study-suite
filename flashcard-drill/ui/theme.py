"""Dark theme — the shared suite palette plus this app's own vocabulary.

The twelve palette constants and the base stylesheet now come from
:mod:`common.ui.theme` (they were byte-identical in all ten apps, so nothing
was compromised to share them), and with them the accessibility rules this
copy did not have: a visible focus ring on every control, sized so tabbing
never shifts the layout.

What stays here is what is genuinely this app's: the per-category colour map,
the rating colours, and the handful of rules for widgets only this app has
(the card frame, the three rating buttons, the cause-note field).  The
confidence-strip and mistake-cause buttons use the shared ``#pill`` rules —
the same design, previously duplicated here as ``#conf_btn`` / ``#cause_btn``.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QApplication

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.theme import *          # noqa: F401,F403  (palette + QSS + alpha)
from common.ui.theme import ACCENT, ACCENT2, BG, BORDER, ERROR, SUCCESS, \
    SURFACE, SURFACE2, TEXT, TEXT_MUTED, WARNING
from common.ui.theme import apply as _apply
from common.ui.theme import extend

CATEGORY_COLORS = {
    "Pauli Matrices":       "#6e40c9",
    "Gate Unitaries":       "#1f6feb",
    "Commutators":          "#2da44e",
    "Complexity":           "#b08800",
    "Theorems":             "#cf222e",
    "Quantum Info":         "#0969da",
    "Algorithms":           "#8250df",
    "Quantum Circuits":     "#3fb950",
    "Error Correction":     "#f778ba",
    "States & Measurement": "#d29922",
    "Quantum Hardware":     "#f0883e",
    "Quantum Optics":       "#39c5cf",
    "Many-Body Physics":    "#a371f7",
    "Qiskit API":           "#58a6ff",
}

RATING_COLORS = {
    "got_it":  SUCCESS,
    "unsure":  WARNING,
    "missed":  ERROR,
}

#: Rules for the widgets only this app has.  Everything else — buttons, focus
#: rings, pills, inputs, scrollbars, the card frame, the separator — is in the
#: shared base stylesheet.
_EXTRA = f"""
QPushButton#got_it {{
    background-color: {SUCCESS}; color: {BG};
    border: none; font-weight: bold; font-size: 14px; padding: 10px 24px; border-radius: 6px;
}}
QPushButton#got_it:hover {{ background-color: #2da44e; }}
QPushButton#got_it:focus {{ border: 2px solid {TEXT}; padding: 8px 22px; }}
QPushButton#unsure {{
    background-color: {WARNING}; color: {BG};
    border: none; font-weight: bold; font-size: 14px; padding: 10px 24px; border-radius: 6px;
}}
QPushButton#unsure:hover {{ background-color: #b08800; }}
QPushButton#unsure:focus {{ border: 2px solid {TEXT}; padding: 8px 22px; }}
QPushButton#missed {{
    background-color: {ERROR}; color: white;
    border: none; font-weight: bold; font-size: 14px; padding: 10px 24px; border-radius: 6px;
}}
QPushButton#missed:hover {{ background-color: #cf222e; }}
QPushButton#missed:focus {{ border: 2px solid {TEXT}; padding: 8px 22px; }}

/* Review feedback: the "Don't ask" / "Dismiss" links beside the pills.
   State is never colour-only — the pills themselves carry a "○ / ●" glyph. */
QPushButton#conf_opt_out, QPushButton#cause_dismiss {{
    background: transparent; color: {TEXT_MUTED};
    border: 1px solid transparent; border-radius: 6px;
    padding: 5px 10px; font-size: 12px;
}}
QPushButton#conf_opt_out:hover, QPushButton#cause_dismiss:hover {{
    color: {TEXT}; border-color: {BORDER};
}}
QPushButton#conf_opt_out:focus, QPushButton#cause_dismiss:focus {{
    border: 2px solid {ACCENT}; padding: 4px 9px;
}}
QLineEdit#cause_note {{ font-size: 12px; padding: 5px 8px; }}
QLineEdit#cause_note:focus {{ border: 2px solid {ACCENT}; padding: 4px 7px; }}
QCheckBox#conf_pref {{ border: 1px solid transparent; border-radius: 4px; padding: 2px; }}
QCheckBox#conf_pref:focus {{ border-color: {ACCENT}; }}

QLabel#card_front {{
    font-size: 20px; font-weight: bold; color: {TEXT};
    qproperty-alignment: AlignCenter;
}}
QLabel#card_back {{
    font-size: 16px; color: {TEXT};
    qproperty-alignment: AlignCenter;
}}

/* The browse / history screens read long text out of a QTextBrowser inside a
   surface panel, so they keep the framed look the shared (borderless,
   transparent) rule drops. */
QTextBrowser {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    font-size: 14px; selection-background-color: {ACCENT2};
}}
QListWidget {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; outline: none; padding: 4px;
}}
QListWidget::item {{ padding: 6px 8px; border-radius: 4px; }}
QListWidget::item:hover {{ background: {SURFACE2}; }}
QListWidget::item:selected {{ background: {ACCENT2}; color: white; }}
QSplitter::handle {{ background: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 1px; margin: 0 6px; }}
"""

#: The full stylesheet this app applies: the shared base plus :data:`_EXTRA`.
QSS = extend(_EXTRA)


def apply(app: QApplication) -> None:
    """Apply the shared theme plus this app's rules to *app*."""
    _apply(app, QSS)
