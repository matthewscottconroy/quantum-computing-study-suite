"""Problem screen — handles both MC and free-form QEC problems."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QPlainTextEdit, QButtonGroup, QRadioButton,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QElapsedTimer
from core.models import Problem, GradeMode
from ui import theme
from ui.widgets.loading_overlay import LoadingOverlay


class ProblemScreen(QWidget):
    answer_submitted = pyqtSignal(object, str, int, int)   # problem, answer_str, hints_used, elapsed_secs
    session_ended    = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._problem: Problem | None = None
        self._overlay = LoadingOverlay(self)
        self._hints_shown = 0
        self._elapsed_timer = QElapsedTimer()
        self._tick_timer = QTimer(self)
        self._tick_timer.setInterval(1000)
        self._tick_timer.timeout.connect(self._update_elapsed)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 20)
        root.setSpacing(14)

        # Progress + streak + hint
        top_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        top_row.addWidget(self._progress_lbl)
        self._streak_lbl = QLabel("")
        self._streak_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {theme.WARNING};")
        self._streak_lbl.hide()
        top_row.addWidget(self._streak_lbl)
        top_row.addStretch()
        self._elapsed_lbl = QLabel("0:00")
        self._elapsed_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT_MUTED};")
        top_row.addWidget(self._elapsed_lbl)
        self._hint_btn = QPushButton("Hint")
        self._hint_btn.setObjectName("flat")
        self._hint_btn.clicked.connect(self._on_hint)
        top_row.addWidget(self._hint_btn)
        root.addLayout(top_row)

        # Category + difficulty
        meta_row = QHBoxLayout()
        self._cat_lbl = QLabel("")
        self._cat_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold;")
        meta_row.addWidget(self._cat_lbl)
        meta_row.addStretch()
        self._diff_lbl = QLabel("")
        self._diff_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        meta_row.addWidget(self._diff_lbl)
        root.addLayout(meta_row)

        # Question
        q_frame = QFrame(); q_frame.setObjectName("card")
        q_layout = QVBoxLayout(q_frame)
        q_layout.setContentsMargins(24, 18, 24, 18)
        self._question_lbl = QLabel("")
        self._question_lbl.setWordWrap(True)
        self._question_lbl.setStyleSheet(f"font-size: 15px; color: {theme.TEXT};")
        q_layout.addWidget(self._question_lbl)
        self._hint_lbl = QLabel("")
        self._hint_lbl.setWordWrap(True)
        self._hint_lbl.setStyleSheet(f"font-size: 13px; color: {theme.WARNING};")
        self._hint_lbl.hide()
        q_layout.addWidget(self._hint_lbl)
        root.addWidget(q_frame)

        # MC choices
        self._mc_widget = QWidget()
        mc_layout = QVBoxLayout(self._mc_widget)
        mc_layout.setSpacing(8)
        mc_layout.setContentsMargins(0, 0, 0, 0)
        self._btn_group = QButtonGroup(self)
        self._btn_group.buttonClicked.connect(self._validate_mc)
        self._radio_btns: list[QRadioButton] = []
        for i, letter in enumerate("ABCD"):
            rb = QRadioButton("")
            rb.setStyleSheet(f"font-size: 14px; color: {theme.TEXT};")
            self._btn_group.addButton(rb, i)
            self._radio_btns.append(rb)
            mc_layout.addWidget(rb)
        root.addWidget(self._mc_widget)

        # Free-form text
        self._freeform_widget = QWidget()
        ff_layout = QVBoxLayout(self._freeform_widget)
        ff_layout.setContentsMargins(0, 0, 0, 0)
        ff_lbl = QLabel("Your answer:")
        ff_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        ff_layout.addWidget(ff_lbl)
        self._text_edit = QPlainTextEdit()
        self._text_edit.setPlaceholderText("Write your explanation here…")
        self._text_edit.textChanged.connect(self._validate_ff)
        ff_layout.addWidget(self._text_edit)
        self._freeform_widget.hide()
        root.addWidget(self._freeform_widget, 1)

        root.addStretch()

        btn_row = QHBoxLayout()
        self._quit_btn = QPushButton("End Session")
        self._quit_btn.setObjectName("flat")
        self._quit_btn.clicked.connect(self.session_ended)
        btn_row.addWidget(self._quit_btn)
        btn_row.addStretch()
        self._submit_btn = QPushButton("Submit")
        self._submit_btn.setObjectName("accent")
        self._submit_btn.setEnabled(False)
        self._submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(self._submit_btn)
        root.addLayout(btn_row)

    def show_problem(self, problem: Problem, idx: int, total: int, streak: int = 0) -> None:
        self._problem = problem
        self._hints_shown = 0
        self._elapsed_timer.start()
        self._elapsed_lbl.setText("0:00")
        self._tick_timer.start()
        self._progress_lbl.setText(f"Problem {idx} of {total}")

        if streak >= 2:
            self._streak_lbl.setText(f"  🔥 {streak}")
            self._streak_lbl.show()
        else:
            self._streak_lbl.hide()

        color = theme.CATEGORY_COLORS.get(problem.category, theme.ACCENT)
        self._cat_lbl.setText(problem.category.upper())
        self._cat_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color};")
        self._diff_lbl.setText(problem.difficulty.capitalize())

        self._question_lbl.setText(problem.question)
        self._hint_lbl.hide()
        self._hint_btn.setVisible(bool(problem.hints))
        if problem.hints:
            self._hint_btn.setText(f"Hint ({len(problem.hints)})")

        if problem.grade_mode == GradeMode.AUTO and problem.choices:
            self._mc_widget.show()
            self._freeform_widget.hide()
            for i, rb in enumerate(self._radio_btns):
                rb.setChecked(False)
                if i < len(problem.choices):
                    rb.setText(f"{chr(65+i)}.  {problem.choices[i]}")
                    rb.show()
                else:
                    rb.hide()
            self._submit_btn.setEnabled(False)
        else:
            self._mc_widget.hide()
            self._freeform_widget.show()
            self._text_edit.clear()
            self._submit_btn.setEnabled(False)

    def _on_hint(self) -> None:
        if not self._problem or self._hints_shown >= len(self._problem.hints):
            return
        self._hint_lbl.setText(f"Hint: {self._problem.hints[self._hints_shown]}")
        self._hint_lbl.show()
        self._hints_shown += 1
        remaining = len(self._problem.hints) - self._hints_shown
        self._hint_btn.setVisible(remaining > 0)
        if remaining > 0:
            self._hint_btn.setText(f"Hint ({remaining} left)")

    def _validate_mc(self) -> None:
        self._submit_btn.setEnabled(self._btn_group.checkedId() >= 0)

    def _validate_ff(self) -> None:
        self._submit_btn.setEnabled(bool(self._text_edit.toPlainText().strip()))

    def _on_submit(self) -> None:
        if not self._problem:
            return
        self._tick_timer.stop()
        elapsed = int(self._elapsed_timer.elapsed() // 1000)
        if self._problem.grade_mode == GradeMode.AUTO and self._problem.choices:
            answer = chr(65 + self._btn_group.checkedId())
        else:
            answer = self._text_edit.toPlainText().strip()
        self.answer_submitted.emit(self._problem, answer, self._hints_shown, elapsed)

    def _update_elapsed(self) -> None:
        secs = self._elapsed_timer.elapsed() // 1000
        self._elapsed_lbl.setText(f"{secs // 60}:{secs % 60:02d}")

    def keyPressEvent(self, event) -> None:
        key = event.key()
        from PyQt6.QtCore import Qt as _Qt
        if self._problem and self._problem.grade_mode == GradeMode.AUTO and self._problem.choices:
            key_to_idx = {
                _Qt.Key.Key_A: 0, _Qt.Key.Key_1: 0,
                _Qt.Key.Key_B: 1, _Qt.Key.Key_2: 1,
                _Qt.Key.Key_C: 2, _Qt.Key.Key_3: 2,
                _Qt.Key.Key_D: 3, _Qt.Key.Key_4: 3,
            }
            if key in key_to_idx:
                idx = key_to_idx[key]
                if idx < len(self._radio_btns) and self._radio_btns[idx].isVisible():
                    self._radio_btns[idx].setChecked(True)
                    self._validate_mc()
                    return
        if key in (_Qt.Key.Key_Return, _Qt.Key.Key_Enter):
            if self._submit_btn.isEnabled():
                self._on_submit()
                return
        super().keyPressEvent(event)

    def show_grading(self) -> None:
        self._overlay.show_message("Grading with Claude…")

    def hide_grading(self) -> None:
        self._overlay.hide()

    def resizeEvent(self, event) -> None:
        self._overlay.resize(self.size())
        super().resizeEvent(event)
