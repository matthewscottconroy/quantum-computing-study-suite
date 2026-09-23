"""Dark theme for exam-sim.

The palette, the base stylesheet and ``apply()`` are :mod:`common.ui.theme` —
the twelve colour constants were byte-identical in all ten apps before the
extraction, so nothing about the look changed.  What stays here is exam-sim's
own vocabulary: the section colour map, and the handful of widget rules that
only this app uses (the question navigator's square buttons, the confidence /
cause chips, the history tables).
"""
from __future__ import annotations

import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.theme import *          # noqa: F401,F403  (palette + helpers)
# BASE_QSS keeps the unextended shared stylesheet reachable after QSS below
# shadows the star-imported one.
from common.ui.theme import QSS as BASE_QSS  # noqa: F401
from common.ui.theme import apply as _apply, extend

# Exam section -> badge colour.  This app's words, not shared style.
SECTION_COLORS = {
    "Create circuits":    "#6e40c9",
    "Quantum operations": "#1f6feb",
    "Run circuits":       "#2da44e",
    "Sampler":            "#b08800",
    "Estimator":          "#bf3989",
    "Visualization":      "#0969da",
    "Results analysis":   "#cf222e",
    "OpenQASM":           "#57606a",
}

# Rules the base stylesheet has no reason to carry.  #chip is exam-sim's name
# for the small pill used by the confidence strip and the mistake-cause row
# (the base ships the same design under #pill); a checked chip also gains a
# "✓" glyph in its text, so its state never depends on colour alone.
_EXTRA = f"""
QScrollBar:horizontal {{ background: {SURFACE}; height: 8px; border-radius: 4px; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 4px; min-width: 24px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QPushButton#nav {{
    padding: 0; min-width: 34px; max-width: 34px; min-height: 30px; max-height: 30px;
    font-size: 12px; border-radius: 4px;
}}
QPushButton#chip {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 11px;
    padding: 3px 10px; font-size: 12px;
}}
QPushButton#chip:hover {{ border-color: {ACCENT}; }}
QPushButton#chip:checked {{
    background-color: {ACCENT}; color: {BG};
    border-color: {ACCENT}; font-weight: bold;
}}
/* Visible keyboard focus. Border width grows by 1px and padding shrinks by
   1px, so focusing a control never shifts the layout. */
QPushButton#chip:focus {{ border: 2px solid {TEXT}; padding: 2px 9px; }}
QPushButton#nav:focus {{ border: 2px solid {TEXT}; padding: 0; }}
QRadioButton {{ spacing: 10px; color: {TEXT}; font-size: 14px; }}
QRadioButton::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {BORDER}; border-radius: 8px; background: {SURFACE2};
}}
QRadioButton::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QLineEdit {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QTableWidget {{
    background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px;
    gridline-color: {BORDER}; font-size: 13px;
}}
QTableWidget::item {{ padding: 4px 8px; }}
QHeaderView::section {{
    background-color: {SURFACE2}; color: {TEXT_MUTED};
    border: none; border-bottom: 1px solid {BORDER};
    padding: 6px 8px; font-size: 12px; font-weight: bold;
}}
QTableCornerButton::section {{ background-color: {SURFACE2}; border: none; }}
QListWidget {{
    background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 6px;
    font-size: 13px; outline: none;
}}
QListWidget::item {{ padding: 6px 8px; border-bottom: 1px solid {SURFACE2}; }}
QListWidget::item:selected {{ background-color: {ACCENT2}; color: white; }}
QListWidget::item:hover:!selected {{ background-color: {SURFACE2}; }}
QSplitter::handle {{ background-color: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 1px; }}
"""

#: The stylesheet exam-sim actually applies: the shared base plus the rules
#: above.  Kept as a module constant because the accessibility tests read it.
QSS = extend(_EXTRA)


def apply(app) -> None:
    """Apply the shared theme plus exam-sim's own rules to a QApplication."""
    _apply(app, QSS)
