"""The suite's dark theme: palette, stylesheet, and ``apply()``.

All ten apps carried a ``ui/theme.py``.  The **twelve palette constants were
byte-identical in all ten** — the divergence was entirely in what each added
on top, and in a handful of stylesheet rules that one app had and the others
had not.  So the palette below is not a compromise; it is what every app
already used.

Reconciled divergences
======================
* ``PARTIAL`` vs ``FLAG`` — exam-sim called ``#e3b341`` ``FLAG``; the other
  nine called it ``PARTIAL``.  Both names are exported, same value.
* ``PURPLE`` / ``TEAL`` (circuit-trainer only) and ``FOCUS`` /
  ``FOCUS_ON_ACCENT`` (vqa-trainer only) are kept: they name real, used
  colours and cost nothing.
* ``MONO`` (exam-sim) vs ``MONO_FAMILY`` (qiskit-dojo) — one font stack,
  exported under both names, and also as a list for ``setFontFamilies()``.
* The **focus-visible rules** (``QPushButton:focus`` &c., which keep a widget
  the same size focused and unfocused so tabbing never shifts the layout)
  existed in qec-trainer and vqa-trainer only.  They are an accessibility
  requirement, not a preference: they are in the base stylesheet for everyone.
* The ``QPushButton#pill`` rules (confidence strip, mistake-cause buttons)
  existed in five apps.  Every app has those controls now, so they are in the
  base too.

Per-app colour maps (``CATEGORY_COLORS``, ``DIFFICULTY_COLORS``,
``SECTION_COLORS``, ``TOPIC_COLORS``, ``QTYPE_COLORS``) are **not** here: they
are genuinely per-app vocabulary, not shared style.  Keep them in the app's
own ``ui/theme.py``, which should now be a dozen lines that do
``from common.ui.theme import *`` and add its own map.  :func:`extend` builds
the app's stylesheet from the base plus any extra rules.
"""
from __future__ import annotations

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

# ── Palette (identical in all ten apps before the extraction) ────────────────
BG         = "#0d1117"
SURFACE    = "#161b22"
SURFACE2   = "#21262d"
BORDER     = "#30363d"
ACCENT     = "#58a6ff"
ACCENT2    = "#388bfd"
TEXT       = "#e6edf3"
TEXT_MUTED = "#8b949e"
SUCCESS    = "#3fb950"
WARNING    = "#d29922"
ERROR      = "#f85149"
PARTIAL    = "#e3b341"

#: exam-sim's name for :data:`PARTIAL`.
FLAG = PARTIAL

# ── Additions that only one app had, kept because they name real colours ─────
PURPLE = "#bc8cff"          # circuit-trainer
TEAL   = "#39d0d8"          # circuit-trainer
FOCUS           = "#f0f6fc"  # vqa-trainer: focus ring on a dark surface
FOCUS_ON_ACCENT = "#0d1117"  # vqa-trainer: focus ring on an accent fill

#: Code / formula foreground on the dark surface (reference screen, code fences).
CODE_FG = "#a5d6ff"

# ── Fonts ────────────────────────────────────────────────────────────────────
#: Monospace stack, as a CSS value (exam-sim's ``MONO``, qiskit-dojo's
#: ``MONO_FAMILY``) and as a list for ``QTextCharFormat.setFontFamilies()``.
MONO_FAMILIES: list[str] = ["JetBrains Mono", "Fira Code", "DejaVu Sans Mono",
                            "Menlo", "Consolas", "monospace"]
MONO = ", ".join(f'"{f}"' if " " in f else f for f in MONO_FAMILIES)
MONO_FAMILY = MONO

UI_FAMILIES: list[str] = ["Inter", "Segoe UI", "Helvetica Neue", "sans-serif"]
UI_FONT = ", ".join(f'"{f}"' if " " in f else f for f in UI_FAMILIES)

#: Animation durations several apps kept in their own ``config.py``.
COLLAPSIBLE_ANIMATION_MS = 250
SCORE_BAR_ANIMATION_MS = 700


def alpha(color: str, percent: int) -> str:
    """``alpha("#58a6ff", 13)`` -> ``"#58a6ff22"`` — an 8-digit hex colour.

    Qt stylesheets accept ``#RRGGBBAA``; the pill badge and several highlight
    rules built these by hand with magic suffixes (``f"{color}22"``).  This
    names the intent instead.
    """
    value = max(0, min(100, int(percent)))
    return f"{color}{round(value * 255 / 100):02x}"


# ── Base stylesheet ──────────────────────────────────────────────────────────
QSS = f"""
QWidget {{
    background-color: {BG}; color: {TEXT};
    font-family: {UI_FONT};
    font-size: 14px;
}}
QScrollArea, QScrollArea > QWidget > QWidget {{ background-color: {BG}; border: none; }}
QScrollBar:vertical {{ background: {SURFACE}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QPushButton {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 8px 18px; font-size: 13px;
}}
QPushButton:hover {{ background-color: {BORDER}; border-color: {ACCENT}; }}
QPushButton:pressed {{ background-color: {ACCENT2}; color: white; }}
QPushButton:disabled {{ color: {TEXT_MUTED}; border-color: {SURFACE2}; }}
QPushButton#accent {{
    background-color: {ACCENT}; color: {BG};
    border: none; font-weight: bold; font-size: 14px; padding: 10px 28px;
}}
QPushButton#accent:hover {{ background-color: {ACCENT2}; }}
QPushButton#accent:disabled {{ background-color: {SURFACE2}; color: {TEXT_MUTED}; }}
QPushButton#flat {{ background: transparent; border: none; color: {ACCENT}; padding: 4px 8px; }}
QPushButton#flat:hover {{ color: {TEXT}; }}

/* Keyboard focus must always be visible.  Each rule keeps the widget the same
   size as its unfocused state (border grows, padding shrinks by the same
   pixel) so tabbing never shifts the layout. */
QPushButton:focus {{ border: 2px solid {ACCENT}; padding: 7px 17px; }}
QPushButton#accent:focus {{ border: 2px solid {TEXT}; padding: 8px 26px; }}
QPushButton#flat:focus {{ border: 2px solid {ACCENT}; border-radius: 4px; padding: 2px 6px; color: {TEXT}; }}
QRadioButton:focus {{ border: 1px dashed {ACCENT}; border-radius: 4px; }}
QCheckBox:focus {{ border: 1px dashed {ACCENT}; border-radius: 4px; }}
QComboBox:focus, QSpinBox:focus {{ border-color: {ACCENT}; }}

QLineEdit {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 5px 8px; font-size: 13px; selection-background-color: {ACCENT2};
}}
QLineEdit:focus {{ border: 2px solid {ACCENT}; padding: 4px 7px; }}

/* Confidence strip and mistake-journal cause pills.  Both are plain buttons so
   they are tab-reachable; the chosen one is marked with a glyph in its text as
   well as the accent fill, never by colour alone. */
QPushButton#pill {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 12px;
    padding: 5px 12px; font-size: 12px;
}}
QPushButton#pill:hover {{ background-color: {BORDER}; border-color: {ACCENT}; }}
QPushButton#pill:checked {{
    background-color: {ACCENT}; color: {BG};
    border-color: {ACCENT}; font-weight: bold;
}}
QPushButton#pill:focus {{ border: 2px solid {ACCENT}; padding: 4px 11px; }}
QPushButton#pill:disabled {{ color: {TEXT_MUTED}; border-color: {SURFACE2}; }}

QPlainTextEdit, QTextEdit {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 8px; font-size: 14px; selection-background-color: {ACCENT2};
}}
QPlainTextEdit:focus, QTextEdit:focus {{ border-color: {ACCENT}; }}
QTextBrowser {{ background-color: transparent; color: {TEXT}; border: none; font-size: 15px; }}
QLabel {{ background: transparent; }}
QLabel#heading {{ font-size: 22px; font-weight: bold; color: {TEXT}; }}
QLabel#subheading {{ font-size: 15px; color: {TEXT_MUTED}; }}
QFrame#card {{ background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
QFrame#separator {{ background-color: {BORDER}; max-height: 1px; }}
QCheckBox {{ spacing: 8px; color: {TEXT}; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {BORDER}; border-radius: 3px; background: {SURFACE2}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QComboBox {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; selection-background-color: {ACCENT2};
}}
QSpinBox {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QSpinBox::up-button, QSpinBox::down-button {{ background: {SURFACE2}; border: none; width: 18px; }}
"""


def extend(extra: str = "") -> str:
    """The base stylesheet plus an app's own rules.

    An app's ``ui/theme.py`` keeps whatever is genuinely its own (a category
    colour map, one widget rule) and calls ``apply(app, extend(MY_RULES))``.
    """
    return QSS if not extra else f"{QSS}\n{extra}\n"


def apply(app: QApplication, stylesheet: str | None = None) -> None:
    """Apply the theme to a ``QApplication``.

    Pass *stylesheet* (usually :func:`extend`'s result) to add app-specific
    rules; omit it for the base theme alone.
    """
    app.setStyleSheet(QSS if stylesheet is None else stylesheet)
    font = QFont(UI_FAMILIES[0], 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)


__all__ = [
    "BG", "SURFACE", "SURFACE2", "BORDER", "ACCENT", "ACCENT2", "TEXT",
    "TEXT_MUTED", "SUCCESS", "WARNING", "ERROR", "PARTIAL", "FLAG",
    "PURPLE", "TEAL", "FOCUS", "FOCUS_ON_ACCENT", "CODE_FG",
    "MONO", "MONO_FAMILY", "MONO_FAMILIES", "UI_FONT", "UI_FAMILIES",
    "COLLAPSIBLE_ANIMATION_MS", "SCORE_BAR_ANIMATION_MS",
    "alpha", "QSS", "extend", "apply",
]
