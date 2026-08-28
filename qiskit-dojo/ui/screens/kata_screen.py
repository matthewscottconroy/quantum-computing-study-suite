"""Kata screen for qiskit-dojo — task pane, code editor, run/grade loop."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QPlainTextEdit, QSplitter, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QFontMetricsF
from core.models import Kata, KataAttempt, RunResult
from ui import theme
from ui.widgets.code_editor import CodeEditor
from workers.run_worker import RunWorker
from workers.review_worker import ReviewWorker


class KataScreen(QWidget):
    kata_completed = pyqtSignal(object)     # KataAttempt
    session_ended  = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._kata: Kata | None = None
        self._attempt: KataAttempt | None = None
        self._run_worker: RunWorker | None = None
        self._review_worker: ReviewWorker | None = None
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(28, 20, 28, 16)
        root.setSpacing(10)

        top_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        top_row.addWidget(self._progress_lbl)
        self._section_lbl = QLabel("")
        top_row.addWidget(self._section_lbl)
        self._diff_lbl = QLabel("")
        self._diff_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        top_row.addWidget(self._diff_lbl)
        top_row.addStretch()
        end_btn = QPushButton("End Session")
        end_btn.setObjectName("flat")
        end_btn.clicked.connect(self._on_end_session)
        top_row.addWidget(end_btn)
        root.addLayout(top_row)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # ---- left: task pane -------------------------------------------
        left = QFrame(); left.setObjectName("card")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 14, 16, 14)
        left_layout.setSpacing(10)

        self._title_lbl = QLabel("")
        self._title_lbl.setWordWrap(True)
        self._title_lbl.setStyleSheet(f"font-size: 17px; font-weight: bold; color: {theme.TEXT};")
        left_layout.addWidget(self._title_lbl)

        self._prompt_view = QPlainTextEdit()
        self._prompt_view.setReadOnly(True)
        self._prompt_view.setObjectName("output")
        self._prompt_view.setStyleSheet(
            f"QPlainTextEdit {{ background: transparent; border: none; "
            f"color: {theme.TEXT}; font-size: 13px; }}"
        )
        self._prompt_view.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        left_layout.addWidget(self._prompt_view, 3)

        self._hint_lbl = QLabel("")
        self._hint_lbl.setWordWrap(True)
        self._hint_lbl.setStyleSheet(f"font-size: 13px; color: {theme.WARNING};")
        self._hint_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._hint_lbl.hide()
        left_layout.addWidget(self._hint_lbl)

        self._review_view = QPlainTextEdit()
        self._review_view.setReadOnly(True)
        self._review_view.setPlaceholderText("Claude review feedback appears here…")
        self._review_view.setStyleSheet(
            f"QPlainTextEdit {{ background: {theme.SURFACE2}; border: 1px solid {theme.BORDER}; "
            f"border-radius: 6px; color: {theme.TEXT}; font-size: 12px; }}"
        )
        self._review_view.hide()
        left_layout.addWidget(self._review_view, 2)
        splitter.addWidget(left)

        # ---- right: editor over output ---------------------------------
        right_split = QSplitter(Qt.Orientation.Vertical)

        editor_frame = QFrame(); editor_frame.setObjectName("card")
        editor_layout = QVBoxLayout(editor_frame)
        editor_layout.setContentsMargins(8, 8, 8, 8)
        editor_layout.setSpacing(6)
        editor_lbl = QLabel("Your code")
        editor_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        editor_layout.addWidget(editor_lbl)
        self._editor = CodeEditor()
        editor_layout.addWidget(self._editor)
        right_split.addWidget(editor_frame)

        output_frame = QFrame(); output_frame.setObjectName("card")
        output_layout = QVBoxLayout(output_frame)
        output_layout.setContentsMargins(8, 8, 8, 8)
        output_layout.setSpacing(6)
        out_header = QHBoxLayout()
        out_lbl = QLabel("Output")
        out_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        out_header.addWidget(out_lbl)
        out_header.addStretch()
        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {theme.TEXT_MUTED};")
        out_header.addWidget(self._status_lbl)
        output_layout.addLayout(out_header)
        self._output_view = QPlainTextEdit()
        self._output_view.setReadOnly(True)
        self._output_view.setObjectName("output")
        mono = QFont("JetBrains Mono", 10)
        mono.setStyleHint(QFont.StyleHint.Monospace)
        self._output_view.setFont(mono)
        self._output_view.setTabStopDistance(
            QFontMetricsF(mono).horizontalAdvance(" ") * 4
        )
        self._output_view.setPlaceholderText("Run your code to see results here.")
        output_layout.addWidget(self._output_view)
        right_split.addWidget(output_frame)
        right_split.setSizes([420, 220])
        splitter.addWidget(right_split)
        splitter.setSizes([380, 640])

        # ---- bottom buttons --------------------------------------------
        btn_row = QHBoxLayout()
        self._hint_btn = QPushButton("Hint")
        self._hint_btn.setObjectName("flat")
        self._hint_btn.clicked.connect(self._on_hint)
        btn_row.addWidget(self._hint_btn)

        self._reveal_btn = QPushButton("Reveal Solution")
        self._reveal_btn.setObjectName("flat")
        self._reveal_btn.clicked.connect(self._on_reveal)
        btn_row.addWidget(self._reveal_btn)

        self._review_btn = QPushButton("Claude Review")
        self._review_btn.setObjectName("flat")
        self._review_btn.clicked.connect(self._on_review)
        btn_row.addWidget(self._review_btn)

        btn_row.addStretch()

        self._run_btn = QPushButton("Run  ▶")
        self._run_btn.setObjectName("accent")
        self._run_btn.clicked.connect(self._on_run)
        btn_row.addWidget(self._run_btn)

        self._next_btn = QPushButton("Skip →")
        self._next_btn.clicked.connect(self._on_next)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------- public

    def show_kata(self, kata: Kata, index: int, total: int) -> None:
        self._kata = kata
        self._attempt = KataAttempt(kata=kata)
        self._progress_lbl.setText(f"Kata {index} of {total}")
        color = theme.SECTION_COLORS.get(kata.section, theme.ACCENT)
        self._section_lbl.setText(kata.section)
        self._section_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {color}; "
            f"border: 1px solid {color}; border-radius: 9px; padding: 1px 10px;"
        )
        self._diff_lbl.setText(kata.difficulty)
        self._title_lbl.setText(kata.title)
        self._prompt_view.setPlainText(kata.prompt)
        self._editor.setPlainText(kata.starter_code)
        self._output_view.clear()
        self._status_lbl.setText("")
        self._hint_lbl.hide()
        self._hint_lbl.setText("")
        self._review_view.hide()
        self._review_view.clear()
        self._hint_btn.setEnabled(bool(kata.hints))
        self._hint_btn.setText(f"Hint (0/{len(kata.hints)})" if kata.hints else "Hint")
        self._reveal_btn.setEnabled(True)
        self._run_btn.setEnabled(True)
        self._next_btn.setText("Skip →")

    # ------------------------------------------------------------ actions

    def _on_run(self) -> None:
        if self._kata is None or self._run_worker is not None:
            return
        self._attempt.tries += 1
        self._run_btn.setEnabled(False)
        self._status_lbl.setText("Running…")
        self._status_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 13px; color: {theme.TEXT_MUTED};"
        )
        self._run_worker = RunWorker(self._editor.toPlainText(), self._kata.test_code, self)
        self._run_worker.finished_run.connect(self._on_run_finished)
        self._run_worker.failed.connect(self._on_run_failed)
        self._run_worker.finished.connect(self._clear_run_worker)
        self._run_worker.start()

    def _clear_run_worker(self) -> None:
        self._run_worker = None
        self._run_btn.setEnabled(True)

    def _on_run_finished(self, result: RunResult) -> None:
        self._output_view.setPlainText(result.output)
        if result.passed:
            self._attempt.passed = True
            self._status_lbl.setText(f"✓ PASSED  ({result.duration_secs:.1f}s)")
            self._status_lbl.setStyleSheet(
                f"font-weight: bold; font-size: 13px; color: {theme.SUCCESS};"
            )
            self._next_btn.setText("Next →")
            self._next_btn.setObjectName("accent")
            self._next_btn.setStyle(self._next_btn.style())
        else:
            label = {
                "user_error":  "✗ ERROR IN YOUR CODE",
                "test_failed": "✗ TESTS FAILED",
                "timeout":     "✗ TIMED OUT",
            }.get(result.phase, "✗ FAILED")
            self._status_lbl.setText(f"{label}  ({result.duration_secs:.1f}s)")
            self._status_lbl.setStyleSheet(
                f"font-weight: bold; font-size: 13px; color: {theme.ERROR};"
            )

    def _on_run_failed(self, err: str) -> None:
        self._output_view.setPlainText(f"Harness error:\n{err}")
        self._status_lbl.setText("✗ HARNESS ERROR")
        self._status_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 13px; color: {theme.ERROR};"
        )

    def _on_hint(self) -> None:
        if self._kata is None or not self._kata.hints:
            return
        shown = min(self._attempt.hints_used + 1, len(self._kata.hints))
        self._attempt.hints_used = shown
        text = "\n".join(
            f"Hint {i + 1}: {h}" for i, h in enumerate(self._kata.hints[:shown])
        )
        self._hint_lbl.setText(text)
        self._hint_lbl.show()
        self._hint_btn.setText(f"Hint ({shown}/{len(self._kata.hints)})")
        if shown >= len(self._kata.hints):
            self._hint_btn.setEnabled(False)

    def _on_reveal(self) -> None:
        if self._kata is None:
            return
        btn = QMessageBox.question(
            self, "Reveal Solution",
            "Show the reference solution in the output pane?\n"
            "(You can still edit, run, and pass the kata afterwards.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if btn != QMessageBox.StandardButton.Yes:
            return
        self._attempt.revealed_solution = True
        self._output_view.setPlainText(
            "=== Reference solution ===\n\n" + self._kata.solution_code
        )
        self._status_lbl.setText("Solution revealed")
        self._status_lbl.setStyleSheet(
            f"font-weight: bold; font-size: 13px; color: {theme.WARNING};"
        )

    def _on_review(self) -> None:
        if self._kata is None or self._review_worker is not None:
            return
        self._review_btn.setEnabled(False)
        self._review_view.show()
        self._review_view.setPlainText("Asking Claude for a code review…")
        self._review_worker = ReviewWorker(self._kata, self._editor.toPlainText(), self)
        self._review_worker.reviewed.connect(self._on_reviewed)
        self._review_worker.failed.connect(self._on_review_failed)
        self._review_worker.finished.connect(self._clear_review_worker)
        self._review_worker.start()

    def _clear_review_worker(self) -> None:
        self._review_worker = None
        self._review_btn.setEnabled(True)

    def _on_reviewed(self, feedback: str) -> None:
        self._review_view.setPlainText(feedback)

    def _on_review_failed(self, err: str) -> None:
        self._review_view.hide()
        QMessageBox.warning(self, "Claude Review Unavailable", err)

    def _on_next(self) -> None:
        if self._attempt is None:
            return
        if self._attempt.tries == 0 and not self._attempt.passed:
            # Skipping without ever running still counts as one failed try.
            self._attempt.tries = 1
        self.kata_completed.emit(self._attempt)

    def _on_end_session(self) -> None:
        btn = QMessageBox.question(
            self, "End Session",
            "End the session now? Completed katas will be saved.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if btn == QMessageBox.StandardButton.Yes:
            self.session_ended.emit()
