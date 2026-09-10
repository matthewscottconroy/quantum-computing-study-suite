"""Per-question feedback screen — shows score, feedback, model answer, and a
flag-for-review toggle."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import QuestionAttempt, Verdict
from ui import theme


class FeedbackScreen(QWidget):
    next_requested = pyqtSignal()
    done_requested = pyqtSignal()    # emitted on last question
    flag_requested = pyqtSignal()    # toggle "flag for review" on the shown question

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._is_last = False
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 24)
        root.setSpacing(16)

        # Score row
        score_row = QHBoxLayout()
        self._score_lbl = QLabel("")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold;")
        score_row.addWidget(self._score_lbl)
        score_row.addStretch()
        self._verdict_lbl = QLabel("")
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold;")
        score_row.addWidget(self._verdict_lbl)
        root.addLayout(score_row)

        # Question recap
        self._q_lbl = QLabel("")
        self._q_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_MUTED};")
        self._q_lbl.setWordWrap(True)
        root.addWidget(self._q_lbl)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        # Feedback card
        fb_card = QFrame(); fb_card.setObjectName("card")
        fb_layout = QVBoxLayout(fb_card)
        fb_layout.setContentsMargins(20, 16, 20, 16)
        fb_lbl_hdr = QLabel("Feedback")
        fb_lbl_hdr.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        fb_layout.addWidget(fb_lbl_hdr)
        self._feedback_browser = QTextBrowser()
        self._feedback_browser.setFixedHeight(90)
        fb_layout.addWidget(self._feedback_browser)
        root.addWidget(fb_card)

        # Model answer card
        ma_card = QFrame(); ma_card.setObjectName("card")
        ma_layout = QVBoxLayout(ma_card)
        ma_layout.setContentsMargins(20, 16, 20, 16)
        ma_hdr = QLabel("Model Answer")
        ma_hdr.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        ma_layout.addWidget(ma_hdr)
        self._model_browser = QTextBrowser()
        self._model_browser.setFixedHeight(120)
        ma_layout.addWidget(self._model_browser)
        root.addWidget(ma_card)

        root.addStretch()

        btn_row = QHBoxLayout()
        self._flag_btn = QPushButton("⚑ Flag for Review")
        self._flag_btn.setObjectName("flat")
        self._flag_btn.setToolTip("Toggle this question in your review list")
        self._flag_btn.clicked.connect(self.flag_requested)
        btn_row.addWidget(self._flag_btn)
        btn_row.addStretch()
        self._next_btn = QPushButton("Next Question")
        self._next_btn.setObjectName("accent")
        self._next_btn.clicked.connect(self._on_next)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    def show_attempt(self, attempt: QuestionAttempt, is_last: bool) -> None:
        self._is_last = is_last
        ev = attempt.evaluation
        score = ev.score if ev else 0
        verdict = ev.verdict if ev else Verdict.INCORRECT

        color = theme.SUCCESS if verdict == Verdict.CORRECT else (
            theme.PARTIAL if verdict == Verdict.PARTIAL else theme.ERROR
        )
        self._score_lbl.setText(f"{score}/10")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        self._verdict_lbl.setText(verdict.value)
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color};")

        self._q_lbl.setText(f"Q: {attempt.question.text}")
        self._feedback_browser.setPlainText(ev.feedback if ev else "")
        self._model_browser.setPlainText(ev.model_answer if ev else "")
        self._next_btn.setText("View Summary" if is_last else "Next Question")
        self.set_flagged(False)   # caller refreshes from persistence after this

    def set_flagged(self, flagged: bool) -> None:
        """Reflect the question's flagged state on the toggle button."""
        self._flag_btn.setText(
            "⚑ Flagged — click to unflag" if flagged else "⚑ Flag for Review"
        )
        self._flag_btn.setStyleSheet(
            f"color: {theme.WARNING};" if flagged else ""
        )

    def is_flagged_shown(self) -> bool:
        return self._flag_btn.text().startswith("⚑ Flagged")

    def _on_next(self) -> None:
        if self._is_last:
            self.done_requested.emit()
        else:
            self.next_requested.emit()
