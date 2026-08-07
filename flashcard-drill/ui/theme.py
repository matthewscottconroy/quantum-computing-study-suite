"""Dark theme — shared palette with other quantum-study apps."""
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

CATEGORY_COLORS = {
    "Pauli Matrices": "#6e40c9",
    "Gate Unitaries": "#1f6feb",
    "Commutators":    "#2da44e",
    "Complexity":     "#b08800",
    "Theorems":       "#cf222e",
    "Quantum Info":   "#0969da",
    "Algorithms":     "#8250df",
}

RATING_COLORS = {
    "got_it":  SUCCESS,
    "unsure":  WARNING,
    "missed":  ERROR,
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
QPushButton#flat {{ background: transparent; border: none; color: {ACCENT}; padding: 4px 8px; }}
QPushButton#flat:hover {{ color: {TEXT}; }}
QPushButton#got_it {{
    background-color: {SUCCESS}; color: {BG};
    border: none; font-weight: bold; font-size: 14px; padding: 10px 24px; border-radius: 6px;
}}
QPushButton#got_it:hover {{ background-color: #2da44e; }}
QPushButton#unsure {{
    background-color: {WARNING}; color: {BG};
    border: none; font-weight: bold; font-size: 14px; padding: 10px 24px; border-radius: 6px;
}}
QPushButton#unsure:hover {{ background-color: #b08800; }}
QPushButton#missed {{
    background-color: {ERROR}; color: white;
    border: none; font-weight: bold; font-size: 14px; padding: 10px 24px; border-radius: 6px;
}}
QPushButton#missed:hover {{ background-color: #cf222e; }}
QLabel {{ background: transparent; }}
QLabel#heading {{ font-size: 22px; font-weight: bold; color: {TEXT}; }}
QLabel#subheading {{ font-size: 15px; color: {TEXT_MUTED}; }}
QLabel#card_front {{
    font-size: 20px; font-weight: bold; color: {TEXT};
    qproperty-alignment: AlignCenter;
}}
QLabel#card_back {{
    font-size: 16px; color: {TEXT};
    qproperty-alignment: AlignCenter;
}}
QFrame#card {{ background-color: {SURFACE}; border: 1px solid {BORDER}; border-radius: 8px; }}
QFrame#separator {{ background-color: {BORDER}; max-height: 1px; }}
QCheckBox {{ spacing: 8px; color: {TEXT}; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid {BORDER}; border-radius: 3px; background: {SURFACE2}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}
QSpinBox {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QSpinBox::up-button, QSpinBox::down-button {{ background: {SURFACE2}; border: none; width: 18px; }}
QComboBox {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; selection-background-color: {ACCENT2};
}}
"""


def apply(app: QApplication) -> None:
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
