"""Dark theme palette and QSS stylesheet."""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# ── Palette ───────────────────────────────────────────────────────────────────
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


QSS = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "Inter", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 14px;
}}
QScrollArea, QScrollArea > QWidget > QWidget {{
    background-color: {BG};
    border: none;
}}
QScrollBar:vertical {{
    background: {SURFACE};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 4px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QPushButton {{
    background-color: {SURFACE2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 18px;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: {BORDER};
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background-color: {ACCENT2};
    color: white;
}}
QPushButton:disabled {{
    color: {TEXT_MUTED};
    border-color: {SURFACE2};
}}
QPushButton#accent {{
    background-color: {ACCENT};
    color: {BG};
    border: none;
    font-weight: bold;
    font-size: 14px;
    padding: 10px 28px;
}}
QPushButton#accent:hover {{ background-color: {ACCENT2}; }}
QPushButton#accent:disabled {{
    background-color: {SURFACE2};
    color: {TEXT_MUTED};
}}
QPushButton#flat {{
    background: transparent;
    border: none;
    color: {ACCENT};
    padding: 4px 8px;
}}
QPushButton#flat:hover {{ color: {TEXT}; }}
QPlainTextEdit, QTextEdit {{
    background-color: {SURFACE};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px;
    font-size: 14px;
    selection-background-color: {ACCENT2};
}}
QPlainTextEdit:focus, QTextEdit:focus {{ border-color: {ACCENT}; }}
QTextBrowser {{
    background-color: transparent;
    color: {TEXT};
    border: none;
    font-size: 15px;
}}
QLabel {{ background: transparent; }}
QLabel#heading {{
    font-size: 22px;
    font-weight: bold;
    color: {TEXT};
}}
QLabel#subheading {{
    font-size: 15px;
    color: {TEXT_MUTED};
}}
QLabel#muted {{
    color: {TEXT_MUTED};
    font-size: 12px;
}}
QFrame#card {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QFrame#separator {{
    background-color: {BORDER};
    max-height: 1px;
}}
QComboBox {{
    background-color: {SURFACE2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE2};
    color: {TEXT};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT2};
}}
QSpinBox {{
    background-color: {SURFACE2};
    color: {TEXT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 10px;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {SURFACE2};
    border: none;
    width: 18px;
}}
QCheckBox {{
    spacing: 8px;
    color: {TEXT};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {BORDER};
    border-radius: 3px;
    background: {SURFACE2};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
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
"""


def apply(app: QApplication) -> None:
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
