"""Dark theme for qiskit-dojo."""
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

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

MONO_FAMILY = '"JetBrains Mono", "Fira Code", "DejaVu Sans Mono", "Consolas", monospace'

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

QSS = f"""
QWidget {{
    background-color: {BG}; color: {TEXT};
    font-family: "Inter", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 14px;
}}
QScrollArea, QScrollArea > QWidget > QWidget {{ background-color: {BG}; border: none; }}
QScrollBar:vertical {{ background: {SURFACE}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ background: {SURFACE}; height: 8px; border-radius: 4px; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 4px; min-width: 24px; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
QPushButton {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 8px 18px; font-size: 13px;
}}
QPushButton:hover {{ background-color: {BORDER}; border-color: {ACCENT}; }}
QPushButton:pressed {{ background-color: {ACCENT2}; color: white; }}
QPushButton:disabled {{ color: {TEXT_MUTED}; border-color: {SURFACE2}; }}
/* Visible keyboard focus.  Every variant already reserves a 1px border (the
   flat and accent buttons paint theirs in the button colour), so taking focus
   only recolours it — the button never shifts by a pixel. */
QPushButton:focus {{ border: 1px solid {ACCENT}; background-color: {BORDER}; }}
QPushButton#accent {{
    background-color: {ACCENT}; color: {BG};
    border: 1px solid {ACCENT}; font-weight: bold; font-size: 14px; padding: 9px 27px;
}}
QPushButton#accent:hover {{ background-color: {ACCENT2}; border-color: {ACCENT2}; }}
QPushButton#accent:focus {{ background-color: {ACCENT}; border-color: {TEXT}; }}
QPushButton#accent:disabled {{
    background-color: {SURFACE2}; color: {TEXT_MUTED}; border-color: {SURFACE2};
}}
QPushButton#flat {{
    background: transparent; border: 1px solid transparent;
    color: {ACCENT}; padding: 4px 8px;
}}
QPushButton#flat:hover {{ color: {TEXT}; }}
QPushButton#flat:focus {{ border-color: {ACCENT}; background-color: {SURFACE2}; }}
QPlainTextEdit, QLineEdit {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 8px; font-size: 14px; selection-background-color: {ACCENT2};
}}
QPlainTextEdit:focus, QLineEdit:focus {{ border-color: {ACCENT}; }}
QPlainTextEdit#code, QPlainTextEdit#output {{
    font-family: {MONO_FAMILY};
    font-size: 13px;
}}
QTextBrowser {{ background-color: transparent; color: {TEXT}; border: none; font-size: 15px; }}
QLabel {{ background: transparent; }}
QLabel#heading {{ font-size: 22px; font-weight: bold; color: {TEXT}; }}
QLabel#subheading {{ font-size: 15px; color: {TEXT_MUTED}; }}
QFrame#card {{ background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
QFrame#separator {{ background-color: {BORDER}; max-height: 1px; }}
QCheckBox {{ spacing: 8px; color: {TEXT}; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {BORDER}; border-radius: 3px; background: {SURFACE2}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QCheckBox:focus, QRadioButton:focus {{ color: {ACCENT}; }}
QCheckBox::indicator:focus, QRadioButton::indicator:focus {{ border-color: {ACCENT}; }}
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


def apply(app: QApplication) -> None:
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
