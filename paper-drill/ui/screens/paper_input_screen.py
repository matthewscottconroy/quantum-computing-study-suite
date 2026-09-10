"""Paper input screen — paste text, set title and question count."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QSpinBox, QFrame, QLineEdit, QCheckBox,
)
from PyQt6.QtCore import pyqtSignal
from core.models import DrillConfig
from config import DEFAULT_Q_COUNT
from ui import theme


class PaperInputScreen(QWidget):
    drill_requested     = pyqtSignal(object)   # DrillConfig
    history_requested   = pyqtSignal()
    library_requested   = pyqtSignal()
    reference_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 36)
        root.setSpacing(16)

        # Heading row with Reference / Library buttons in top-right
        heading_row = QHBoxLayout()
        heading_row.setSpacing(12)
        title = QLabel("Paper Drill")
        title.setObjectName("heading")
        heading_row.addWidget(title, 1)
        reference_btn = QPushButton("Reference")
        reference_btn.setObjectName("flat")
        reference_btn.setToolTip("Browse the shared docs corpus")
        reference_btn.clicked.connect(self.reference_requested)
        heading_row.addWidget(reference_btn)
        library_btn = QPushButton("Library")
        library_btn.setObjectName("flat")
        library_btn.clicked.connect(self.library_requested)
        heading_row.addWidget(library_btn)
        root.addLayout(heading_row)

        sub = QLabel(
            "Paste text from a research paper — Claude generates comprehension questions "
            "tailored to the content."
        )
        sub.setObjectName("subheading")
        sub.setWordWrap(True)
        root.addWidget(sub)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        # Title field
        title_lbl = QLabel("Paper title (optional)")
        title_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        root.addWidget(title_lbl)
        self._title_edit = QLineEdit()
        self._title_edit.setPlaceholderText("e.g. Quantum Approximate Optimization Algorithm")
        self._title_edit.setStyleSheet(
            f"background: {theme.SURFACE}; border: 1px solid {theme.BORDER}; "
            f"border-radius: 6px; padding: 6px 10px; color: {theme.TEXT};"
        )
        root.addWidget(self._title_edit)

        # Text area
        text_lbl = QLabel("Paper text")
        text_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        root.addWidget(text_lbl)
        self._text_edit = QPlainTextEdit()
        self._text_edit.setPlaceholderText(
            "Paste the abstract, introduction, or any section of the paper here…"
        )
        self._text_edit.textChanged.connect(self._validate)
        root.addWidget(self._text_edit, 1)

        # Bottom row
        bot = QHBoxLayout(); bot.setSpacing(16)
        count_lbl = QLabel("Questions:")
        count_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED};")
        bot.addWidget(count_lbl)
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 15)
        self._count_spin.setValue(DEFAULT_Q_COUNT)
        bot.addWidget(self._count_spin)

        self._save_chk = QCheckBox("Save to Library")
        self._save_chk.setChecked(True)
        self._save_chk.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        bot.addWidget(self._save_chk)

        bot.addStretch()

        history_btn = QPushButton("View History")
        history_btn.setObjectName("flat")
        history_btn.clicked.connect(self.history_requested)
        bot.addWidget(history_btn)

        self._start_btn = QPushButton("Generate Questions")
        self._start_btn.setObjectName("accent")
        self._start_btn.setEnabled(False)
        self._start_btn.clicked.connect(self._on_start)
        bot.addWidget(self._start_btn)
        root.addLayout(bot)

    def _validate(self) -> None:
        self._start_btn.setEnabled(bool(self._text_edit.toPlainText().strip()))

    def _on_start(self) -> None:
        text = self._text_edit.toPlainText().strip()
        if not text:
            return
        config = DrillConfig(
            paper_text=text,
            paper_title=self._title_edit.text().strip() or "Untitled Paper",
            question_count=self._count_spin.value(),
        )
        if self._save_chk.isChecked():
            from persistence import save_paper
            save_paper(config.paper_title, config.paper_text, config.question_count)
        self.drill_requested.emit(config)
