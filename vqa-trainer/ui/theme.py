"""Dark theme for vqa-trainer.

The palette and the base stylesheet live in :mod:`common.ui.theme` — they were
byte-identical in all ten apps, so nothing was compromised to share them.  What
stays here is this app's own vocabulary: the problem-category colours, and the
three widget rules ``#chip`` / ``#linkbtn`` / ``#note`` that only the VQA
trainer's confidence strip and mistake row use.

``theme.QSS`` is still the *complete* stylesheet this app applies, so anything
that inspects it (the accessibility test, for one) sees the app's rules too.
"""
import common_path  # noqa: F401  (puts the repo root on sys.path)

from PyQt6.QtWidgets import QApplication

# Named rather than star-imported so the re-export is explicit: mypy does not
# forward names that arrived through `import *`, and a reader can see at a
# glance what this module hands on unchanged.
from common.ui.theme import (
    ACCENT, ACCENT2, BG, BORDER, ERROR, FLAG, FOCUS, FOCUS_ON_ACCENT, PARTIAL,
    SUCCESS, SURFACE, SURFACE2, TEXT, TEXT_MUTED, WARNING,
    CODE_FG, MONO, MONO_FAMILIES, UI_FONT, alpha, extend,
    apply as _apply,
)

#: This app's problem categories.  App vocabulary, not shared style.
CATEGORY_COLORS = {
    "VQE Fundamentals":  "#6e40c9",
    "QAOA":              "#1f6feb",
    "Parameter Shift":   "#2da44e",
    "Ansatz Design":     "#b08800",
    "Barren Plateaus":   "#cf222e",
    "Noise & Mitigation":"#0969da",
}

_EXTRA = f"""
/* This app sizes its text inputs a notch larger than the suite default. */
QPlainTextEdit, QLineEdit {{
    padding: 8px; font-size: 14px;
}}
QLineEdit:focus {{ border: 1px solid {ACCENT}; padding: 8px; }}

/* Small toggle chips: confidence levels and mistake causes.
   Every state is carried by text + shape as well as colour, and the keyboard
   focus ring is drawn in a hue that clears 4.5:1 against both chip fills. */
QPushButton#chip {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 12px;
    padding: 4px 12px; font-size: 12px; text-align: center;
}}
QPushButton#chip:hover {{ background-color: {BORDER}; border-color: {ACCENT}; }}
QPushButton#chip:checked {{
    background-color: {ACCENT}; color: {FOCUS_ON_ACCENT};
    border-color: {ACCENT}; font-weight: bold;
}}
QPushButton#chip:focus {{ border: 2px solid {FOCUS}; padding: 3px 11px; }}
QPushButton#chip:checked:focus {{ border: 2px solid {FOCUS_ON_ACCENT}; padding: 3px 11px; }}
QPushButton#linkbtn {{
    background: transparent; border: 1px solid transparent;
    color: {ACCENT}; padding: 4px 8px; font-size: 12px; border-radius: 6px;
}}
QPushButton#linkbtn:hover {{ color: {TEXT}; border-color: {BORDER}; }}
QPushButton#linkbtn:focus {{ border: 2px solid {FOCUS}; padding: 3px 7px; }}
QLineEdit#note:focus {{ border: 2px solid {FOCUS}; padding: 7px; }}
"""

#: The complete stylesheet this app applies: the suite base plus the rules above.
QSS = extend(_EXTRA)


def apply(app: QApplication) -> None:
    """Apply the suite theme plus this app's own rules."""
    _apply(app, QSS)


__all__ = [
    # re-exported from common.ui.theme, unchanged
    "BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2", "TEXT",
    "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL", "FLAG",
    "FOCUS", "FOCUS_ON_ACCENT", "CODE_FG", "MONO", "MONO_FAMILIES", "UI_FONT",
    "alpha", "extend",
    # this app's own
    "CATEGORY_COLORS", "QSS", "apply",
]
