"""Dark theme for qiskit-dojo.

The palette, the base stylesheet and ``apply()`` are the suite's — see
``common/ui/theme.py``; the twelve colour constants were byte-identical in all
ten apps before the extraction, so nothing here is a compromise.  What stays
local is this app's own vocabulary (``SECTION_COLORS``, one colour per kata
section) and the handful of rules only a code dojo needs: a monospaced code /
output pane, a horizontal scrollbar, radio-button and splitter chrome.
"""
import common_path  # noqa: F401  (puts the repo root on sys.path)

from common.ui.theme import *          # noqa: F403  (palette, QSS, helpers)
from common.ui.theme import apply as _apply, extend

#: One colour per kata section — this app's vocabulary, not shared style.
SECTION_COLORS = {
    "Create circuits":   "#6e40c9",
    "Quantum operations":"#1f6feb",
    "Run circuits":      "#2da44e",
    "Sampler":           "#b08800",
    "Estimator":         "#0969da",
    "Visualization":     "#bf3989",
    "Results analysis":  "#d4a72c",
    "OpenQASM":          "#57606a",
    "Debugging":         "#cf222e",
    "Modernization":     "#8250df",
}

#: Rules the shared base has no reason to carry: the dojo is the only app with
#: a code editor and a program-output pane side by side in a splitter.
_EXTRA = f"""
QScrollBar:horizontal {{ background: {SURFACE}; height: 8px; border-radius: 4px; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 4px; min-width: 24px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QPlainTextEdit#code, QPlainTextEdit#output {{
    font-family: {MONO};
    font-size: 13px;
}}
QRadioButton {{ spacing: 8px; color: {TEXT}; }}
QRadioButton::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {BORDER}; border-radius: 8px; background: {SURFACE2};
}}
QRadioButton::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QSplitter::handle {{ background: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 2px; }}
QSplitter::handle:vertical {{ height: 2px; }}
"""

#: The stylesheet this app actually applies: the shared base plus ``_EXTRA``.
QSS = extend(_EXTRA)


def apply(app) -> None:
    """Apply the suite theme plus this app's extra rules to a QApplication."""
    _apply(app, QSS)
