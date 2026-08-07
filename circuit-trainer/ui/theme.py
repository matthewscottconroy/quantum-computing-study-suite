"""Dark theme — same palette as quantum-quiz for visual consistency."""

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

BG        = "#0d1117"
SURFACE   = "#161b22"
SURFACE2  = "#21262d"
BORDER    = "#30363d"
ACCENT    = "#58a6ff"
ACCENT2   = "#388bfd"
TEXT      = "#e6edf3"
TEXT_MUTED = "#8b949e"
SUCCESS   = "#3fb950"
WARNING   = "#d29922"
ERROR     = "#f85149"
PARTIAL   = "#e3b341"
PURPLE    = "#bc8cff"
TEAL      = "#39d0d8"

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

QSS = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "Inter", "Segoe UI", "Helvetica Neue", sans-serif;
    font-size: 14px;
}}
QScrollArea, QScrollArea > QWidget > QWidget {{ background-color: {BG}; border: none; }}
QScrollBar:vertical {{ background: {SURFACE}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{ background: {BORDER}; border-radius: 4px; min-height: 24px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QPushButton {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 8px 18px; font-size: 13px;
}}
QPushButton:hover {{ background-color: {BORDER}; border-color: {ACCENT}; }}
QPushButton:pressed {{ background-color: {ACCENT2}; color: white; }}
QPushButton:disabled {{ color: {TEXT_MUTED}; border-color: {SURFACE2}; }}
QPushButton#accent {{
    background-color: {ACCENT}; color: {BG}; border: none;
    font-weight: bold; font-size: 14px; padding: 10px 28px;
}}
QPushButton#accent:hover {{ background-color: {ACCENT2}; }}
QPushButton#accent:disabled {{ background-color: {SURFACE2}; color: {TEXT_MUTED}; }}
QPushButton#flat {{ background: transparent; border: none; color: {ACCENT}; padding: 4px 8px; }}
QPushButton#flat:hover {{ color: {TEXT}; }}
QPushButton#choice {{
    background-color: {SURFACE}; color: {TEXT};
    border: 2px solid {BORDER}; border-radius: 8px;
    padding: 12px 16px; font-size: 14px; text-align: left;
}}
QPushButton#choice:hover {{ border-color: {ACCENT}; background-color: {SURFACE2}; }}
QPushButton#choice_correct {{
    background-color: {SUCCESS}22; color: {SUCCESS};
    border: 2px solid {SUCCESS}; border-radius: 8px; padding: 12px 16px; font-size: 14px; text-align: left;
}}
QPushButton#choice_wrong {{
    background-color: {ERROR}22; color: {ERROR};
    border: 2px solid {ERROR}; border-radius: 8px; padding: 12px 16px; font-size: 14px; text-align: left;
}}
QPushButton#choice_missed {{
    background-color: {WARNING}22; color: {WARNING};
    border: 2px solid {WARNING}; border-radius: 8px; padding: 12px 16px; font-size: 14px; text-align: left;
}}
QPlainTextEdit, QTextEdit {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 8px; font-size: 14px;
}}
QTextBrowser {{ background-color: transparent; color: {TEXT}; border: none; font-size: 15px; }}
QLabel {{ background: transparent; }}
QLabel#heading {{ font-size: 22px; font-weight: bold; }}
QLabel#subheading {{ font-size: 15px; color: {TEXT_MUTED}; }}
QLabel#muted {{ color: {TEXT_MUTED}; font-size: 12px; }}
QLabel#mono {{ font-family: "JetBrains Mono","Fira Code","Consolas",monospace; font-size: 13px; }}
QFrame#card {{ background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
QFrame#separator {{ background-color: {BORDER}; max-height: 1px; }}
QComboBox {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QComboBox QAbstractItemView {{
    background-color: {SURFACE2}; color: {TEXT}; border: 1px solid {BORDER};
    selection-background-color: {ACCENT2};
}}
QSpinBox {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QCheckBox {{ spacing: 8px; color: {TEXT}; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border: 1px solid {BORDER};
    border-radius: 3px; background: {SURFACE2};
}}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
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


def apply(app: QApplication) -> None:
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
