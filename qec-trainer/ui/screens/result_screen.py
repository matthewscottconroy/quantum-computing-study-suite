"""Per-problem result screen for qec-trainer."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QPushButton, QFrame,
)
from PyQt6.QtCore import pyqtSignal
from core.models import Attempt, Verdict
from ui import theme


class ResultScreen(QWidget):
    next_requested = pyqtSignal()
    flag_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 20)
        root.setSpacing(16)

        score_row = QHBoxLayout()
        self._score_lbl = QLabel("")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold;")
        score_row.addWidget(self._score_lbl)
        score_row.addStretch()
        self._verdict_lbl = QLabel("")
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold;")
        score_row.addWidget(self._verdict_lbl)
        root.addLayout(score_row)

        self._q_lbl = QLabel("")
        self._q_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_MUTED};")
        self._q_lbl.setWordWrap(True)
        root.addWidget(self._q_lbl)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        fb_card = QFrame(); fb_card.setObjectName("card")
        fb_l = QVBoxLayout(fb_card)
        fb_l.setContentsMargins(20, 16, 20, 16)
        fb_l.addWidget(self._muted_label("Explanation"))
        self._explanation_browser = QTextBrowser()
        self._explanation_browser.setMinimumHeight(100)
        fb_l.addWidget(self._explanation_browser)
        root.addWidget(fb_card)

        root.addStretch()

        btn_row = QHBoxLayout()
        self._flag_btn = QPushButton("⚑ Flag for Review")
        self._flag_btn.setObjectName("flat")
        self._flag_btn.clicked.connect(self.flag_requested)
        btn_row.addWidget(self._flag_btn)
        btn_row.addStretch()
        self._next_btn = QPushButton("Next Problem")
        self._next_btn.setObjectName("accent")
        self._next_btn.clicked.connect(self.next_requested)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    def _muted_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        return lbl

    def show_attempt(self, attempt: Attempt, is_last: bool) -> None:
        color = (
            theme.SUCCESS if attempt.verdict == Verdict.CORRECT else
            theme.PARTIAL if attempt.verdict == Verdict.PARTIAL else
            theme.ERROR
        )
        self._score_lbl.setText(f"{attempt.score}/10")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        self._verdict_lbl.setText(attempt.verdict.value)
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color};")
        self._q_lbl.setText(attempt.problem.question)

        explanation = attempt.feedback or attempt.problem.explanation
        if attempt.model_answer and attempt.model_answer != attempt.problem.explanation:
            explanation += f"\n\nModel answer: {attempt.model_answer}"
        self._explanation_browser.setPlainText(explanation)
        self._next_btn.setText("View Summary" if is_last else "Next Problem")

    def set_flagged(self, flagged: bool) -> None:
        """Update flag button to reflect flagged state. Button always enabled."""
        if flagged:
            self._flag_btn.setText("⚑ Flagged — click to unflag")
        else:
            self._flag_btn.setText("⚑ Flag for Review")
        self._flag_btn.setEnabled(True)
