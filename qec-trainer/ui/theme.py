"""Dark theme for qec-trainer."""
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
    "Repetition Code":       "#6e40c9",
    "Stabilizer Formalism":  "#1f6feb",
    "Steane Code":           "#2da44e",
    "Surface Code":          "#b08800",
    "Fault Tolerance":       "#cf222e",
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

/* Keyboard focus must always be visible. Each rule keeps the widget the same
   size as its unfocused state so tabbing never shifts the layout. */
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

/* Confidence strip and mistake-journal cause pills. Both are plain buttons so
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
QPlainTextEdit {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 8px; font-size: 14px; selection-background-color: {ACCENT2};
}}
QPlainTextEdit:focus {{ border-color: {ACCENT}; }}
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


def apply(app: QApplication) -> None:
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
