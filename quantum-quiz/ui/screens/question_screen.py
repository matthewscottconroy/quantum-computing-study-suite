"""Question display and answer input screen."""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
    QPlainTextEdit, QPushButton, QFrame, QScrollArea, QSplitter,
)
from PyQt6.QtCore import Qt, pyqtSignal, QElapsedTimer, QTimer
from PyQt6.QtGui import QKeyEvent

from core.models import Question
from qiskit_contexts import QiskitContext
from ui import theme
from ui.widgets.pill_badge import make_subject_pill, make_difficulty_pill
from ui.widgets.circuit_viewer import CircuitViewer


class QuestionScreen(QWidget):
    # Carries (answer_text, elapsed_seconds)
    answer_submitted = pyqtSignal(str, int)
    skip_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._question: Question | None = None
        self._hints: list[str] = []
        self._hints_shown = 0
        self._is_multiple_choice = False

        # Elapsed-time tracking
        self._elapsed_timer = QElapsedTimer()
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._update_elapsed_label)

        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────────
        bar = QWidget()
        bar.setFixedHeight(48)
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-bottom: 1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 0, 16, 0)
        bar_layout.setSpacing(10)

        self._subject_pill = make_subject_pill("", self)
        self._difficulty_pill = make_difficulty_pill("", self)
        self._type_label = QLabel("")
        self._type_label.setObjectName("muted")
        self._progress_label = QLabel("")
        self._progress_label.setObjectName("muted")
        self._elapsed_label = QLabel("0s")
        self._elapsed_label.setObjectName("muted")
        self._elapsed_label.setToolTip("Time spent on this question")

        bar_layout.addWidget(self._subject_pill)
        bar_layout.addWidget(self._difficulty_pill)
        bar_layout.addWidget(self._type_label)
        bar_layout.addStretch()
        bar_layout.addWidget(self._elapsed_label)
        bar_layout.addWidget(self._progress_label)
        root.addWidget(bar)

        # ── Splitter: question pane / answer pane ─────────────────────────────
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter)

        # Question pane
        q_pane = QScrollArea()
        q_pane.setWidgetResizable(True)
        q_pane.setFrameShape(QFrame.Shape.NoFrame)
        q_inner = QWidget()
        q_layout = QVBoxLayout(q_inner)
        q_layout.setContentsMargins(40, 28, 40, 16)
        q_layout.setSpacing(16)

        self._topic_label = QLabel("")
        self._topic_label.setObjectName("muted")
        q_layout.addWidget(self._topic_label)

        self._question_browser = QTextBrowser()
        self._question_browser.setOpenExternalLinks(False)
        q_layout.addWidget(self._question_browser)

        self._circuit_viewer = CircuitViewer()
        q_layout.addWidget(self._circuit_viewer)

        self._hints_label = QLabel("")
        self._hints_label.setWordWrap(True)
        self._hints_label.setStyleSheet(
            f"color: {theme.WARNING}; font-style: italic; font-size: 13px;"
        )
        self._hints_label.hide()
        q_layout.addWidget(self._hints_label)
        q_layout.addStretch()

        q_pane.setWidget(q_inner)
        splitter.addWidget(q_pane)

        # Answer pane
        a_pane = QWidget()
        a_pane.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        a_layout = QVBoxLayout(a_pane)
        a_layout.setContentsMargins(40, 16, 40, 20)
        a_layout.setSpacing(10)

        ans_label = QLabel("Your answer")
        ans_label.setStyleSheet(
            f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};"
        )
        a_layout.addWidget(ans_label)

        self._answer_edit = _SubmitOnEnter(self)
        self._answer_edit.setPlaceholderText(
            "Write your answer here. "
            "Press Enter on a blank line to submit. "
            "For multiple-choice: press A/B/C/D then Enter."
        )
        self._answer_edit.setMinimumHeight(110)
        self._answer_edit.submit_requested.connect(self._on_submit)
        a_layout.addWidget(self._answer_edit)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._hint_btn = QPushButton("Hint (3 remaining)")
        self._hint_btn.clicked.connect(self._on_hint)
        btn_row.addWidget(self._hint_btn)

        skip_btn = QPushButton("Skip →")
        skip_btn.clicked.connect(self.skip_requested)
        btn_row.addWidget(skip_btn)

        btn_row.addStretch()

        self._submit_btn = QPushButton("Submit Answer")
        self._submit_btn.setObjectName("accent")
        self._submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(self._submit_btn)

        a_layout.addLayout(btn_row)
        splitter.addWidget(a_pane)

        splitter.setSizes([500, 220])

    # ── Public API ────────────────────────────────────────────────────────────

    def load_question(
        self,
        question: Question,
        context: QiskitContext,
        number: int,
        total: int,
    ) -> None:
        self._question = question
        self._hints = question.hints
        self._hints_shown = 0
        self._answer_edit.clear()
        self._hints_label.hide()
        self._hints_label.setText("")

        # Detect multiple-choice by looking for A) / B) / A. / B. markers
        text_lower = question.text.lower()
        self._is_multiple_choice = (
            "a)" in text_lower or "a." in text_lower
        ) and (
            "b)" in text_lower or "b." in text_lower
        )

        self._subject_pill.update_text(
            question.subject,
            theme.subject_color(question.subject),
        )
        self._difficulty_pill.update_text(
            question.difficulty.upper(),
            theme.DIFFICULTY_COLORS.get(question.difficulty, theme.ACCENT),
        )
        self._type_label.setText(question.question_type)
        self._progress_label.setText(f"Question {number} of {total}")
        self._topic_label.setText(f"Topic: {question.topic}")

        self._question_browser.setPlainText(question.text)
        self._update_hint_btn()

        if context.circuit_png:
            self._circuit_viewer.set_image(context.circuit_png)
        else:
            self._circuit_viewer.clear_image()

        # Start elapsed timer
        self._tick_timer.stop()
        self._elapsed_label.setText("0s")
        self._elapsed_timer.start()
        self._tick_timer.start()

    # ── Slots ─────────────────────────────────────────────────────────────────

    def _on_hint(self) -> None:
        if self._hints_shown >= len(self._hints):
            return
        hint = self._hints[self._hints_shown]
        self._hints_shown += 1
        existing = self._hints_label.text()
        sep = "\n" if existing else ""
        self._hints_label.setText(
            f"{existing}{sep}Hint {self._hints_shown}: {hint}"
        )
        self._hints_label.show()
        self._update_hint_btn()

    def _on_submit(self) -> None:
        text = self._answer_edit.toPlainText().strip()
        if text:
            self._tick_timer.stop()
            elapsed = int(self._elapsed_timer.elapsed() / 1000)
            self.answer_submitted.emit(text, elapsed)

    def _update_elapsed_label(self) -> None:
        secs = int(self._elapsed_timer.elapsed() / 1000)
        if secs < 60:
            self._elapsed_label.setText(f"{secs}s")
        else:
            m, s = divmod(secs, 60)
            self._elapsed_label.setText(f"{m}m {s:02d}s")

    def _update_hint_btn(self) -> None:
        remaining = max(0, len(self._hints) - self._hints_shown)
        self._hint_btn.setText(f"Hint ({remaining} remaining)")
        self._hint_btn.setEnabled(remaining > 0)


class _SubmitOnEnter(QPlainTextEdit):
    """QPlainTextEdit that emits submit_requested on blank-line Enter.

    When the host QuestionScreen is in multiple-choice mode, pressing A/B/C/D
    sets the answer text and Enter immediately submits.
    """
    submit_requested = pyqtSignal()

    def __init__(self, host: "QuestionScreen") -> None:
        super().__init__(host)
        self._host = host

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()

        # A/B/C/D shortcut for multiple-choice questions
        if self._host._is_multiple_choice and not event.modifiers():
            label = {
                Qt.Key.Key_A: "A",
                Qt.Key.Key_B: "B",
                Qt.Key.Key_C: "C",
                Qt.Key.Key_D: "D",
            }.get(key)
            if label:
                self.setPlainText(label)
                c = self.textCursor()
                c.movePosition(c.MoveOperation.End)
                self.setTextCursor(c)
                return

        # Enter on any non-empty line submits in multiple-choice mode;
        # in free-text mode, only a blank-line Enter submits.
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            if self._host._is_multiple_choice and self.toPlainText().strip():
                self.submit_requested.emit()
                return
            cursor = self.textCursor()
            cursor.select(cursor.SelectionType.LineUnderCursor)
            line = cursor.selectedText().strip()
            if not line:
                self.submit_requested.emit()
                return

        super().keyPressEvent(event)
