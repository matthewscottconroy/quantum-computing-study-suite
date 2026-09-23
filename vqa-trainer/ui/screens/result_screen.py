"""Per-problem result screen for vqa-trainer."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QPushButton, QFrame,
)
from PyQt6.QtCore import pyqtSignal
from core.models import Attempt, Verdict
from ui import theme
from ui.widgets.mistake_row import MistakeRow

# Verdict glyphs: the result must never be carried by colour alone.
_VERDICT_GLYPH = {
    Verdict.CORRECT:   "\u2713",   # check
    Verdict.PARTIAL:   "\u25d0",   # half-filled circle
    Verdict.INCORRECT: "\u2717",   # cross
}


class ResultScreen(QWidget):
    next_requested = pyqtSignal()
    flag_requested = pyqtSignal()
    mistake_cause_selected = pyqtSignal(str)
    mistake_note_committed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._is_last = False
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 20)
        root.setSpacing(16)

        score_row = QHBoxLayout()
        self._score_lbl = QLabel("")
        self._score_lbl.setStyleSheet("font-size: 36px; font-weight: bold;")
        score_row.addWidget(self._score_lbl)
        score_row.addStretch()
        self._verdict_lbl = QLabel("")
        self._verdict_lbl.setStyleSheet("font-size: 15px; font-weight: bold;")
        score_row.addWidget(self._verdict_lbl)
        root.addLayout(score_row)

        self._q_lbl = QLabel("")
        self._q_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_MUTED};")
        self._q_lbl.setWordWrap(True)
        root.addWidget(self._q_lbl)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        exp_card = QFrame(); exp_card.setObjectName("card")
        exp_layout = QVBoxLayout(exp_card)
        exp_layout.setContentsMargins(20, 16, 20, 16)
        hdr = QLabel("Explanation")
        hdr.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        exp_layout.addWidget(hdr)
        self._explanation_browser = QTextBrowser()
        self._explanation_browser.setMinimumHeight(120)
        exp_layout.addWidget(self._explanation_browser)
        root.addWidget(exp_card)

        # Mistake journal — inline, compact, skippable. Shown only when the
        # answer scored below the app's "correct" bar (7/10).
        self._journal_card = QFrame(); self._journal_card.setObjectName("card")
        jl = QVBoxLayout(self._journal_card)
        jl.setContentsMargins(20, 12, 20, 12)
        jl.setSpacing(6)
        jhdr = QLabel("Mistake journal")
        jhdr.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        jl.addWidget(jhdr)
        self._mistake_row = MistakeRow()
        self._mistake_row.cause_selected.connect(self.mistake_cause_selected)
        self._mistake_row.note_committed.connect(self.mistake_note_committed)
        jl.addWidget(self._mistake_row)
        self._journal_card.hide()
        root.addWidget(self._journal_card)

        root.addStretch()

        btn_row = QHBoxLayout()
        self._flag_btn = QPushButton("⚑ Flag for Review")
        self._flag_btn.setObjectName("linkbtn")
        self._flag_btn.setAccessibleName("Flag this problem for review")
        self._flag_btn.clicked.connect(self.flag_requested)
        btn_row.addWidget(self._flag_btn)
        btn_row.addStretch()
        self._next_btn = QPushButton("Next Problem")
        self._next_btn.setObjectName("accent")
        self._next_btn.setAccessibleName("Next problem")
        self._next_btn.clicked.connect(self._on_next)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    def show_attempt(self, attempt: Attempt, is_last: bool) -> None:
        self._is_last = is_last
        color = (
            theme.SUCCESS if attempt.verdict == Verdict.CORRECT else
            theme.PARTIAL if attempt.verdict == Verdict.PARTIAL else
            theme.ERROR
        )
        glyph = _VERDICT_GLYPH.get(attempt.verdict, "")
        self._score_lbl.setText(f"{attempt.score}/10")
        self._score_lbl.setStyleSheet(f"font-size: 36px; font-weight: bold; color: {color};")
        self._score_lbl.setAccessibleName(f"Score {attempt.score} out of 10")
        self._verdict_lbl.setText(f"{glyph} {attempt.verdict.value}".strip())
        self._verdict_lbl.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {color};")
        self._verdict_lbl.setAccessibleName(f"Verdict: {attempt.verdict.value}")
        self._q_lbl.setText(attempt.problem.question)

        self._mistake_row.reset()
        self._journal_card.setVisible(attempt.score < 7)

        text = attempt.feedback or attempt.problem.explanation
        if attempt.model_answer and attempt.model_answer not in text:
            text += f"\n\nModel answer: {attempt.model_answer}"
        self._explanation_browser.setPlainText(text)
        self._next_btn.setText("View Summary" if is_last else "Next Problem")

    def _on_next(self) -> None:
        self._mistake_row.flush_note()
        self.next_requested.emit()

    def mistake_cause(self) -> str | None:
        return self._mistake_row.cause()

    def mistake_note(self) -> str:
        return self._mistake_row.note()

    def journal_visible(self) -> bool:
        return not self._journal_card.isHidden()

    def set_flagged(self, flagged: bool) -> None:
        if flagged:
            self._flag_btn.setText("⚑ Flagged — click to unflag")
        else:
            self._flag_btn.setText("⚑ Flag for Review")
        self._flag_btn.setEnabled(True)
