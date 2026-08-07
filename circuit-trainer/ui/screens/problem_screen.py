"""
Problem screen — displays the circuit/matrix, question, and answer input.
Supports MULTIPLE_CHOICE (instant auto-grading) and FREE_FORM (Claude grading).
"""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser, QPlainTextEdit,
    QPushButton, QFrame, QScrollArea, QSplitter,
)
from PyQt6.QtCore import Qt, pyqtSignal, QElapsedTimer, QTimer

from core.models import Problem, Attempt, AnswerFormat
from ui import theme
from ui.widgets.circuit_panel import CircuitPanel
from ui.widgets.collapsible_panel import CollapsiblePanel


class ProblemScreen(QWidget):
    answer_submitted    = pyqtSignal(int, int)   # MC: (chosen index, elapsed_secs)
    free_form_submitted = pyqtSignal(str, int)   # FREE_FORM: (text answer, elapsed_secs)
    next_requested      = pyqtSignal()
    skip_requested      = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._problem: Problem | None = None
        self._answered = False
        self._choice_btns: list[QPushButton] = []
        self._hints: list[str] = []
        self._hints_shown = 0

        # Elapsed-time tracking
        self._elapsed_timer = QElapsedTimer()
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._update_elapsed_label)

        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────────
        bar = QWidget()
        bar.setFixedHeight(44)
        bar.setStyleSheet(f"background:{theme.SURFACE}; border-bottom:1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(16, 0, 16, 0)
        self._cat_badge   = QLabel("")
        self._diff_badge  = QLabel("")
        self._progress_lbl = QLabel("")
        self._progress_lbl.setObjectName("muted")
        self._elapsed_lbl = QLabel("0:00")
        self._elapsed_lbl.setObjectName("muted")
        self._elapsed_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: 12px; font-variant-numeric: tabular-nums;"
        )
        for w in [self._cat_badge, self._diff_badge]:
            w.setAlignment(Qt.AlignmentFlag.AlignCenter)
            w.setFixedHeight(22)
        bar_layout.addWidget(self._cat_badge)
        bar_layout.addWidget(self._diff_badge)
        bar_layout.addStretch()
        bar_layout.addWidget(self._elapsed_lbl)
        bar_layout.addSpacing(16)
        bar_layout.addWidget(self._progress_lbl)
        root.addWidget(bar)

        # ── Main splitter ─────────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        root.addWidget(splitter)

        # LEFT — question text and circuit visualisations
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.Shape.NoFrame)
        left_widget = QWidget()
        left = QVBoxLayout(left_widget)
        left.setContentsMargins(32, 24, 24, 24)
        left.setSpacing(16)

        self._question_lbl = QTextBrowser()
        self._question_lbl.setMinimumHeight(80)
        left.addWidget(self._question_lbl)

        self._circuit_a = CircuitPanel("Circuit A")
        self._circuit_b = CircuitPanel("Circuit B")
        left.addWidget(self._circuit_a)
        left.addWidget(self._circuit_b)

        self._matrix_lbl = QLabel("")
        self._matrix_lbl.setObjectName("mono")
        self._matrix_lbl.setWordWrap(True)
        self._matrix_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        left.addWidget(self._matrix_lbl)

        self._state_lbl = QLabel("")
        self._state_lbl.setStyleSheet(f"color: {theme.TEAL}; font-size: 14px;")
        left.addWidget(self._state_lbl)

        # Hints
        self._hints_label = QLabel("")
        self._hints_label.setWordWrap(True)
        self._hints_label.setStyleSheet(
            f"color: {theme.WARNING}; font-style: italic; font-size: 13px;"
        )
        self._hints_label.hide()
        left.addWidget(self._hints_label)

        left.addStretch()
        left_scroll.setWidget(left_widget)
        splitter.addWidget(left_scroll)

        # RIGHT — answer section then solution
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setFrameShape(QFrame.Shape.NoFrame)
        right_widget = QWidget()
        right_widget.setStyleSheet(f"background: {theme.SURFACE};")
        right = QVBoxLayout(right_widget)
        right.setContentsMargins(24, 24, 32, 24)
        right.setSpacing(16)

        self._answer_prompt_lbl = QLabel("Select the correct answer:")
        self._answer_prompt_lbl.setStyleSheet(
            f"font-weight:bold; font-size:11px; color:{theme.TEXT_MUTED};"
        )
        right.addWidget(self._answer_prompt_lbl)

        self._choices_container = QVBoxLayout()
        self._choices_container.setSpacing(8)
        right.addLayout(self._choices_container)

        self._free_form_edit = QPlainTextEdit()
        self._free_form_edit.setPlaceholderText("Type your explanation here…")
        self._free_form_edit.setMinimumHeight(160)
        self._free_form_edit.hide()
        right.addWidget(self._free_form_edit)

        self._submit_btn = QPushButton("Submit Answer")
        self._submit_btn.setObjectName("accent")
        self._submit_btn.clicked.connect(self._on_free_form_submit)
        self._submit_btn.hide()
        right.addWidget(self._submit_btn)

        # Hint + Skip row (before answering)
        action_row = QHBoxLayout()
        action_row.setSpacing(10)
        self._hint_btn = QPushButton("Hint (0 remaining)")
        self._hint_btn.clicked.connect(self._on_hint)
        action_row.addWidget(self._hint_btn)
        self._skip_btn = QPushButton("Skip →")
        self._skip_btn.clicked.connect(self.skip_requested)
        action_row.addWidget(self._skip_btn)
        action_row.addStretch()
        right.addLayout(action_row)

        # Solution panel (hidden until answered)
        sep = QFrame()
        sep.setObjectName("separator")
        right.addWidget(sep)

        self._solution_widget = QWidget()
        self._solution_widget.hide()
        sol_layout = QVBoxLayout(self._solution_widget)
        sol_layout.setContentsMargins(0, 0, 0, 0)
        sol_layout.setSpacing(10)

        sol_hdr = QLabel("Worked Solution")
        sol_hdr.setStyleSheet(f"font-weight:bold; font-size:11px; color:{theme.TEXT_MUTED};")
        sol_layout.addWidget(sol_hdr)

        self._solution_browser = QTextBrowser()
        self._solution_browser.setMinimumHeight(100)
        sol_layout.addWidget(self._solution_browser)

        # Model answer (collapsible, shown for FREE_FORM)
        self._model_answer_widget = QTextBrowser()
        self._model_answer_widget.setMinimumHeight(80)
        self._model_answer_widget.setStyleSheet(
            "font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;"
            "font-size: 13px;"
        )
        self._model_panel = CollapsiblePanel("Model Answer", self._model_answer_widget)
        sol_layout.addWidget(self._model_panel)

        # Follow-up card (shown for FREE_FORM when available)
        self._followup_container = QFrame()
        self._followup_container.setObjectName("card")
        fu_layout = QVBoxLayout(self._followup_container)
        fu_layout.setContentsMargins(14, 10, 14, 10)
        fu_lbl = QLabel("Follow-up to consider")
        fu_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        fu_layout.addWidget(fu_lbl)
        self._followup_label = QLabel("")
        self._followup_label.setWordWrap(True)
        self._followup_label.setStyleSheet(f"font-style: italic; color: {theme.ACCENT};")
        fu_layout.addWidget(self._followup_label)
        sol_layout.addWidget(self._followup_container)

        self._concepts_lbl = QLabel("")
        self._concepts_lbl.setObjectName("muted")
        self._concepts_lbl.setWordWrap(True)
        sol_layout.addWidget(self._concepts_lbl)

        right.addWidget(self._solution_widget)
        right.addStretch()

        self._next_btn = QPushButton("Next Problem →")
        self._next_btn.setObjectName("accent")
        self._next_btn.setEnabled(False)
        self._next_btn.clicked.connect(self.next_requested)
        right.addWidget(self._next_btn)

        right_scroll.setWidget(right_widget)
        splitter.addWidget(right_scroll)
        splitter.setSizes([550, 450])

    # ── Public API ────────────────────────────────────────────────────────────

    def load_problem(self, problem: Problem, number: int, total: int) -> None:
        self._problem = problem
        self._answered = False
        self._hints = problem.hints
        self._hints_shown = 0
        self._next_btn.setEnabled(False)
        self._solution_widget.hide()
        self._followup_container.hide()
        self._model_panel.hide()
        self._skip_btn.setEnabled(True)
        self._hints_label.hide()
        self._hints_label.setText("")

        # Start elapsed timer for this problem
        self._elapsed_lbl.setText("0:00")
        self._elapsed_timer.start()
        self._tick_timer.start()

        cat_color = theme.CATEGORY_COLORS.get(problem.category.value, theme.ACCENT)
        self._cat_badge.setText(problem.category.value)
        self._cat_badge.setStyleSheet(
            f"background:{cat_color}22; color:{cat_color}; border:1px solid {cat_color}55;"
            "border-radius:10px; padding:2px 10px; font-size:11px; font-weight:bold;"
        )
        diff_color = theme.DIFFICULTY_COLORS.get(problem.difficulty, theme.ACCENT)
        self._diff_badge.setText(problem.difficulty.upper())
        self._diff_badge.setStyleSheet(
            f"background:{diff_color}22; color:{diff_color}; border:1px solid {diff_color}55;"
            "border-radius:10px; padding:2px 10px; font-size:11px; font-weight:bold;"
        )
        self._progress_lbl.setText(f"Problem {number} of {total}")
        self._question_lbl.setPlainText(problem.question_text)

        self._circuit_a.clear()
        self._circuit_b.clear()
        if problem.circuit_png:
            self._circuit_a.set_image(problem.circuit_png)
        if problem.aux_circuit_png:
            self._circuit_b.set_image(problem.aux_circuit_png)

        if problem.matrix_str:
            self._matrix_lbl.setText(problem.matrix_str)
            self._matrix_lbl.show()
        else:
            self._matrix_lbl.hide()

        if problem.state_str:
            self._state_lbl.setText(problem.state_str)
            self._state_lbl.show()
        else:
            self._state_lbl.hide()

        self._update_hint_btn()
        self._clear_choices()
        if problem.answer_format == AnswerFormat.FREE_FORM:
            self._answer_prompt_lbl.setText("Your explanation:")
            self._free_form_edit.clear()
            self._free_form_edit.setEnabled(True)
            self._free_form_edit.show()
            self._submit_btn.setEnabled(True)
            self._submit_btn.show()
        else:
            self._answer_prompt_lbl.setText("Select the correct answer:")
            self._free_form_edit.hide()
            self._submit_btn.hide()
            if problem.choices:
                for i, choice in enumerate(problem.choices):
                    btn = QPushButton(choice)
                    btn.setObjectName("choice")
                    btn.clicked.connect(lambda _, idx=i: self._on_choice(idx))
                    self._choice_btns.append(btn)
                    self._choices_container.addWidget(btn)

    def show_result(self, attempt: Attempt) -> None:
        self._answered = True
        self._tick_timer.stop()
        problem = attempt.problem
        self._skip_btn.setEnabled(False)

        if problem.answer_format == AnswerFormat.FREE_FORM:
            self._free_form_edit.setEnabled(False)
            self._submit_btn.hide()

            # Feedback line with score
            score_color = (
                theme.SUCCESS if attempt.score >= 7
                else theme.PARTIAL if attempt.score >= 4
                else theme.ERROR
            )
            score_line = f"Score: {attempt.score}/10\n\n{attempt.feedback}"
            self._solution_browser.setPlainText(score_line)
            self._solution_browser.setStyleSheet(
                f"color: {score_color}; font-size: 14px; background: transparent; border: none;"
            )

            # Collapsible model answer
            if attempt.model_answer:
                self._model_answer_widget.setPlainText(attempt.model_answer)
                self._model_panel.show()
            else:
                self._model_panel.hide()

            # Follow-up question
            if attempt.follow_up:
                self._followup_label.setText(attempt.follow_up)
                self._followup_container.show()
            else:
                self._followup_container.hide()

            # Worked steps (appended below the score/feedback)
            if problem.solution_steps:
                divider = "\n\n" + "─" * 40 + "\n\n"
                steps_body = "\n\n".join(
                    f"Step {i+1}: {step}" for i, step in enumerate(problem.solution_steps)
                )
                self._solution_browser.setPlainText(score_line + divider + steps_body)
                self._solution_browser.setStyleSheet("")

        else:
            correct_idx = int(problem.correct_answer)
            user_idx = int(attempt.user_answer) if attempt.user_answer.isdigit() else -1
            for i, btn in enumerate(self._choice_btns):
                if i == correct_idx:
                    btn.setObjectName("choice_correct")
                elif i == user_idx and not attempt.is_correct:
                    btn.setObjectName("choice_wrong")
                btn.setEnabled(False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

            steps_body = "\n\n".join(
                f"Step {i+1}: {step}" for i, step in enumerate(problem.solution_steps)
            )
            self._solution_browser.setPlainText(steps_body)
            self._solution_browser.setStyleSheet("")

        self._concepts_lbl.setText("Key concepts: " + " · ".join(problem.key_concepts))
        self._solution_widget.show()
        self._next_btn.setEnabled(True)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _elapsed_seconds(self) -> int:
        if self._elapsed_timer.isValid():
            return int(self._elapsed_timer.elapsed() / 1000)
        return 0

    def _update_elapsed_label(self) -> None:
        secs = self._elapsed_seconds()
        minutes, s = divmod(secs, 60)
        self._elapsed_lbl.setText(f"{minutes}:{s:02d}")

    def _on_choice(self, idx: int) -> None:
        if self._answered:
            return
        self.answer_submitted.emit(idx, self._elapsed_seconds())

    def _on_free_form_submit(self) -> None:
        if self._answered:
            return
        text = self._free_form_edit.toPlainText().strip()
        if not text:
            return
        self._submit_btn.setEnabled(False)
        self.free_form_submitted.emit(text, self._elapsed_seconds())

    def _on_hint(self) -> None:
        if self._hints_shown >= len(self._hints):
            return
        hint = self._hints[self._hints_shown]
        self._hints_shown += 1
        existing = self._hints_label.text()
        sep = "\n" if existing else ""
        self._hints_label.setText(f"{existing}{sep}Hint {self._hints_shown}: {hint}")
        self._hints_label.show()
        self._update_hint_btn()

    def _update_hint_btn(self) -> None:
        remaining = max(0, len(self._hints) - self._hints_shown)
        self._hint_btn.setText(f"Hint ({remaining} remaining)")
        self._hint_btn.setEnabled(remaining > 0)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        """A/B/C/D select MC answer; Enter/Return submits free-form or MC."""
        if not self._answered:
            key = event.key()
            # A/B/C/D — select corresponding multiple-choice button
            letter_map = {
                Qt.Key.Key_A: 0,
                Qt.Key.Key_B: 1,
                Qt.Key.Key_C: 2,
                Qt.Key.Key_D: 3,
            }
            if key in letter_map:
                idx = letter_map[key]
                if idx < len(self._choice_btns):
                    self._on_choice(idx)
                    return
            # Enter/Return — submit free-form answer
            if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if self._free_form_edit.isVisible():
                    self._on_free_form_submit()
                    return
        super().keyPressEvent(event)

    def _clear_choices(self) -> None:
        for btn in self._choice_btns:
            self._choices_container.removeWidget(btn)
            btn.deleteLater()
        self._choice_btns.clear()
