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
    "Pauli Matrices":       "#6e40c9",
    "Gate Unitaries":       "#1f6feb",
    "Commutators":          "#2da44e",
    "Complexity":           "#b08800",
    "Theorems":             "#cf222e",
    "Quantum Info":         "#0969da",
    "Algorithms":           "#8250df",
    "Quantum Circuits":     "#3fb950",
    "Error Correction":     "#f778ba",
    "States & Measurement": "#d29922",
    "Quantum Hardware":     "#f0883e",
    "Quantum Optics":       "#39c5cf",
    "Many-Body Physics":    "#a371f7",
    "Qiskit API":           "#58a6ff",
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
/* --- Review feedback: confidence strip + mistake-cause row ---------------
   Every control below is Tab-reachable, so each one needs a focus ring that is
   visible against the dark palette (2 px ACCENT).  State is never colour-only:
   the buttons carry a "○ / ●" glyph as well as the accent fill. */
QPushButton#conf_btn, QPushButton#cause_btn {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 13px;
    padding: 5px 12px; font-size: 12px; font-weight: normal;
}}
QPushButton#conf_btn:hover, QPushButton#cause_btn:hover {{
    background-color: {BORDER}; border-color: {ACCENT};
}}
QPushButton#conf_btn:checked, QPushButton#cause_btn:checked {{
    background-color: {ACCENT}; color: {BG};
    border-color: {ACCENT}; font-weight: bold;
}}
QPushButton#conf_opt_out, QPushButton#cause_dismiss {{
    background: transparent; color: {TEXT_MUTED};
    border: 1px solid transparent; border-radius: 6px;
    padding: 5px 10px; font-size: 12px;
}}
QPushButton#conf_opt_out:hover, QPushButton#cause_dismiss:hover {{
    color: {TEXT}; border-color: {BORDER};
}}
QPushButton#conf_btn:focus, QPushButton#cause_btn:focus,
QPushButton#conf_opt_out:focus, QPushButton#cause_dismiss:focus {{
    border: 2px solid {ACCENT}; outline: none;
}}
QLineEdit#cause_note {{ font-size: 12px; padding: 5px 8px; }}
QLineEdit#cause_note:focus {{ border: 2px solid {ACCENT}; }}
QCheckBox#conf_pref {{ border: 1px solid transparent; border-radius: 4px; padding: 2px; }}
QCheckBox#conf_pref:focus {{ border-color: {ACCENT}; }}
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
QLineEdit {{
    background-color: {SURFACE2}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; padding: 6px 10px;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QTextBrowser {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px;
    font-size: 14px; selection-background-color: {ACCENT2};
}}
QListWidget {{
    background-color: {SURFACE}; color: {TEXT};
    border: 1px solid {BORDER}; border-radius: 6px; outline: none; padding: 4px;
}}
QListWidget::item {{ padding: 6px 8px; border-radius: 4px; }}
QListWidget::item:hover {{ background: {SURFACE2}; }}
QListWidget::item:selected {{ background: {ACCENT2}; color: white; }}
QSplitter::handle {{ background: {BORDER}; }}
QSplitter::handle:horizontal {{ width: 1px; margin: 0 6px; }}
"""


def apply(app: QApplication) -> None:
    app.setStyleSheet(QSS)
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
