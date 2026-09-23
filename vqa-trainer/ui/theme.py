"""Dark theme for vqa-trainer."""
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
# Keyboard-focus ring. FOCUS reads 14:1 on SURFACE2 and 17:1 on BG; on a
# filled ACCENT chip the ring flips to FOCUS_ON_ACCENT (7.5:1 on ACCENT).
FOCUS           = "#f0f6fc"
FOCUS_ON_ACCENT = "#0d1117"

CATEGORY_COLORS = {
    "VQE Fundamentals":  "#6e40c9",
    "QAOA":              "#1f6feb",
    "Parameter Shift":   "#2da44e",
    "Ansatz Design":     "#b08800",
    "Barren Plateaus":   "#cf222e",
    "Noise & Mitigation":"#0969da",
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
QPlainTextEdit, QLineEdit {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 8px; font-size: 14px; selection-background-color: {ACCENT2};
}}
QPlainTextEdit:focus, QLineEdit:focus {{ border-color: {ACCENT}; }}
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
QRadioButton {{ spacing: 8px; color: {TEXT}; }}
QRadioButton::indicator {{
    width: 16px; height: 16px;
    border: 1px solid {BORDER}; border-radius: 8px; background: {SURFACE2};
}}
QRadioButton::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}

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


def apply(app: QApplication) -> None:
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
