"""Dark theme for exam-sim (mirrors the vqa-trainer theme)."""
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
FLAG       = "#e3b341"

MONO = '"JetBrains Mono", "Fira Code", "DejaVu Sans Mono", monospace'

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
QPushButton#accent {{
    background-color: {ACCENT}; color: {BG};
    border: none; font-weight: bold; font-size: 14px; padding: 10px 28px;
}}
QPushButton#accent:hover {{ background-color: {ACCENT2}; }}
QPushButton#accent:disabled {{ background-color: {SURFACE2}; color: {TEXT_MUTED}; }}
QPushButton#flat {{ background: transparent; border: none; color: {ACCENT}; padding: 4px 8px; }}
QPushButton#flat:hover {{ color: {TEXT}; }}
QPushButton#nav {{
    padding: 0; min-width: 34px; max-width: 34px; min-height: 30px; max-height: 30px;
    font-size: 12px; border-radius: 4px;
}}
QTextBrowser {{ background-color: transparent; color: {TEXT}; border: none; font-size: 15px; }}
QLabel {{ background: transparent; }}
QLabel#heading {{ font-size: 22px; font-weight: bold; color: {TEXT}; }}
QLabel#subheading {{ font-size: 15px; color: {TEXT_MUTED}; }}
QFrame#card {{ background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
QFrame#separator {{ background-color: {BORDER}; max-height: 1px; }}
QComboBox {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; selection-background-color: {ACCENT2};
}}
QRadioButton {{ spacing: 10px; color: {TEXT}; font-size: 14px; }}
QRadioButton::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {BORDER}; border-radius: 8px; background: {SURFACE2};
}}
QRadioButton::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
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
QLineEdit {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QSplitter::handle {{ background-color: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 1px; }}
"""


def apply(app: QApplication) -> None:
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
