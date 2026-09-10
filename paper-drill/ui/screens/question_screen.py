"""Question screen — shows one question at a time, takes free-text answer."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import Question, DrillConfig, QuestionAttempt
from ui import theme
from ui.widgets.loading_overlay import LoadingOverlay


class QuestionScreen(QWidget):
    answer_submitted  = pyqtSignal(object)   # QuestionAttempt (no evaluation yet)
    session_cancelled = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._questions: list[Question] = []
        self._idx = 0
        self._paper_text = ""
        self._overlay = LoadingOverlay(self)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 24)
        root.setSpacing(16)

        prog_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        prog_row.addWidget(self._progress_lbl)
        prog_row.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("flat")
        cancel_btn.clicked.connect(self.session_cancelled)
        prog_row.addWidget(cancel_btn)
        root.addLayout(prog_row)

        self._qtype_lbl = QLabel("")
        self._qtype_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        root.addWidget(self._qtype_lbl)

        q_frame = QFrame(); q_frame.setObjectName("card")
        q_layout = QVBoxLayout(q_frame)
        q_layout.setContentsMargins(24, 20, 24, 20)
        self._question_lbl = QLabel("")
        self._question_lbl.setWordWrap(True)
        self._question_lbl.setStyleSheet(f"font-size: 16px; color: {theme.TEXT};")
        q_layout.addWidget(self._question_lbl)
        root.addWidget(q_frame)

        ans_lbl = QLabel("Your answer:")
        ans_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        root.addWidget(ans_lbl)

        self._answer_edit = QPlainTextEdit()
        self._answer_edit.setPlaceholderText("Write your answer here…")
        self._answer_edit.textChanged.connect(self._validate)
        root.addWidget(self._answer_edit, 1)

        btn_row = QHBoxLayout(); btn_row.addStretch()
        self._submit_btn = QPushButton("Submit Answer")
        self._submit_btn.setObjectName("accent")
        self._submit_btn.setEnabled(False)
        self._submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(self._submit_btn)
        root.addLayout(btn_row)

    def start(self, questions: list[Question], paper_text: str) -> None:
        self._questions  = questions
        self._idx        = 0
        self._paper_text = paper_text
        self._show_question()

    def show_current(self) -> None:
        self._show_question()

    def advance(self) -> None:
        """Move on to the next question.

        Called by the controller only after the current question has been
        graded (or explicitly skipped).  Submitting does *not* advance, so a
        failed grade leaves the same question — and the typed answer — in
        place for a retry.
        """
        if self._idx < len(self._questions):
            self._idx += 1

    def current_index(self) -> int:
        """Zero-based index of the question currently shown."""
        return self._idx

    def has_current(self) -> bool:
        """False once every question has been graded (nothing left to show)."""
        return self._idx < len(self._questions)

    def _show_question(self) -> None:
        if not self.has_current():
            self._submit_btn.setEnabled(False)
            return
        q = self._questions[self._idx]
        self._progress_lbl.setText(f"Question {self._idx + 1} of {len(self._questions)}")
        color = theme.QTYPE_COLORS.get(q.q_type, theme.ACCENT)
        self._qtype_lbl.setText(q.q_type.upper())
        self._qtype_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color};")
        self._question_lbl.setText(q.text)
        self._answer_edit.clear()
        self._submit_btn.setEnabled(False)

    def _validate(self) -> None:
        self._submit_btn.setEnabled(bool(self._answer_edit.toPlainText().strip()))

    def _on_submit(self) -> None:
        if not self.has_current():
            self._submit_btn.setEnabled(False)
            return
        q = self._questions[self._idx]
        attempt = QuestionAttempt(
            question=q,
            answer_text=self._answer_edit.toPlainText().strip(),
        )
        # The index is advanced by the controller (advance()) only once this
        # attempt has been graded or skipped — see MainWindow._on_grade_failed.
        self.answer_submitted.emit(attempt)

    def show_grading(self) -> None:
        self._overlay.show_with_message("Grading…")

    def hide_grading(self) -> None:
        self._overlay.hide()

    def resizeEvent(self, event) -> None:
        self._overlay.resize(self.size())
        super().resizeEvent(event)
