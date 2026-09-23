"""Review mode — re-answer previously missed questions from exam_missed.json."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QRadioButton, QButtonGroup, QTextBrowser,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import Question
import persistence
from persistence import load_missed, resolve_missed, record_miss
from bank import all_questions
from ui import theme
from ui.feedback import CauseRow, ConfidenceStrip
from ui.format import question_html


class ReviewScreen(QWidget):
    home_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._queue: list[Question] = []
        self._idx = 0
        self._answered = False
        self._confidence_value: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 28, 48, 20)
        root.setSpacing(12)

        top = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        top.addWidget(self._progress_lbl)
        top.addStretch()
        self._section_lbl = QLabel("")
        top.addWidget(self._section_lbl)
        root.addLayout(top)

        q_frame = QFrame(); q_frame.setObjectName("card")
        q_layout = QVBoxLayout(q_frame)
        q_layout.setContentsMargins(20, 14, 20, 14)
        self._question_browser = QTextBrowser()
        q_layout.addWidget(self._question_browser)
        root.addWidget(q_frame, 2)

        self._btn_group = QButtonGroup(self)
        self._btn_group.buttonClicked.connect(
            lambda _: self._submit_btn.setEnabled(not self._answered))
        self._radio_btns: list[QRadioButton] = []
        for i in range(4):
            rb = QRadioButton("")
            self._btn_group.addButton(rb, i)
            self._radio_btns.append(rb)
            root.addWidget(rb)

        # Confidence is asked before "Check Answer" reveals anything.
        self._confidence = ConfidenceStrip(prompt="How sure?")
        self._confidence.rated.connect(self._on_confidence)
        self._confidence.cleared.connect(lambda: self._on_confidence(None))
        self._confidence.opt_out.connect(self._on_confidence_opt_out)
        self._confidence.install_shortcuts(self)
        root.addWidget(self._confidence)

        self._feedback_lbl = QLabel("")
        self._feedback_lbl.setWordWrap(True)
        self._feedback_lbl.setTextFormat(Qt.TextFormat.RichText)
        root.addWidget(self._feedback_lbl)

        self._cause_row = CauseRow()
        self._cause_row.setVisible(False)
        self._cause_row.chosen.connect(self._on_cause)
        root.addWidget(self._cause_row)
        root.addStretch()

        btn_row = QHBoxLayout()
        back_btn = QPushButton("Back to Home")
        back_btn.setObjectName("flat")
        back_btn.setAccessibleName("Back to home screen")
        back_btn.clicked.connect(self.home_requested)
        btn_row.addWidget(back_btn)
        btn_row.addStretch()
        self._submit_btn = QPushButton("Check Answer")
        self._submit_btn.setObjectName("accent")
        self._submit_btn.setAccessibleName("Check this answer")
        self._submit_btn.setEnabled(False)
        self._submit_btn.clicked.connect(self._on_submit)
        btn_row.addWidget(self._submit_btn)
        self._next_btn = QPushButton("Next →")
        self._next_btn.setAccessibleName("Next missed question")
        self._next_btn.setEnabled(False)
        self._next_btn.clicked.connect(self._on_next)
        btn_row.addWidget(self._next_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------- session
    def start(self) -> bool:
        """Load missed questions; returns False if there is nothing to review."""
        missed_ids = [e.get("question_id") for e in load_missed()]
        by_id = {q.id: q for q in all_questions()}
        self._queue = [by_id[i] for i in missed_ids if i in by_id]
        # Stale ids (question no longer in the bank) are dropped from the file.
        for qid in missed_ids:
            if qid not in by_id and qid:
                resolve_missed(qid)
        if not self._queue:
            return False
        self._idx = 0
        self._show_current()
        return True

    def _show_current(self) -> None:
        q = self._queue[self._idx]
        self._answered = False
        self._progress_lbl.setText(
            f"Missed question {self._idx + 1} of {len(self._queue)}")
        color = theme.SECTION_COLORS.get(q.section, theme.ACCENT)
        self._section_lbl.setText(q.section.upper())
        self._section_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {color};")
        self._question_browser.setHtml(question_html(q.question))
        self._btn_group.setExclusive(False)
        for i, rb in enumerate(self._radio_btns):
            rb.setChecked(False)
            rb.setEnabled(True)
            rb.setText(f"{chr(65 + i)}.  {q.options[i]}" if i < len(q.options) else "")
            rb.setAccessibleName(
                f"Option {chr(65 + i)}: {q.options[i]}" if i < len(q.options) else "")
            rb.setVisible(i < len(q.options))
        self._btn_group.setExclusive(True)
        self._feedback_lbl.setText("")
        self._confidence_value = None
        self._confidence.set_value(None)
        try:
            self._confidence.setVisible(persistence.confidence_enabled())
        except Exception:
            self._confidence.setVisible(True)
        self._cause_row.reset()
        self._cause_row.setVisible(False)
        self._submit_btn.setEnabled(False)
        self._next_btn.setEnabled(False)

    def _on_submit(self) -> None:
        chosen = self._btn_group.checkedId()
        if chosen < 0 or self._answered:
            return
        self._answered = True
        q = self._queue[self._idx]
        for rb in self._radio_btns:
            rb.setEnabled(False)
        if chosen == q.correct_index:
            resolve_missed(q.id)
            self._journal_resolved(q)
            self._feedback_lbl.setText(
                f'<span style="color:{theme.SUCCESS};font-weight:bold;">✓ Correct'
                f"</span> — removed from the missed list.<br>"
                f'<span style="color:{theme.TEXT_MUTED};">{q.explanation}</span>'
            )
        else:
            record_miss(q, chosen)
            self._journal_miss(q, chosen)
            correct = q.options[q.correct_index]
            self._feedback_lbl.setText(
                f'<span style="color:{theme.ERROR};font-weight:bold;">✗ Incorrect'
                f"</span> — correct answer: {correct}<br>"
                f'<span style="color:{theme.TEXT_MUTED};">{q.explanation}</span>'
            )
            self._cause_row.setVisible(True)
        self._log_confidence(q, chosen == q.correct_index)
        self._submit_btn.setEnabled(False)
        is_last = self._idx + 1 >= len(self._queue)
        self._next_btn.setText("Finish" if is_last else "Next →")
        self._next_btn.setEnabled(True)

    # ------------------------------------------- mistake journal / confidence
    def _journal_miss(self, q: Question, chosen: int) -> None:
        """Add a cause-analysis row (alongside exam_missed.json, not instead)."""
        try:
            persistence.log_mistake(persistence.mistake_entry_for(q, chosen))
        except Exception:
            pass

    def _journal_resolved(self, q: Question) -> None:
        try:
            persistence.resolve_mistake(q.id)
        except Exception:
            pass

    def _on_cause(self, cause: str, note: str) -> None:
        q = self._queue[self._idx]
        try:
            if not persistence.update_mistake_cause(q.id, cause, note):
                persistence.log_mistake(persistence.mistake_entry_for(
                    q, self._btn_group.checkedId(), cause=cause, note=note))
        except Exception:
            pass

    def _on_confidence(self, value: int | None) -> None:
        self._confidence_value = value

    def _on_confidence_opt_out(self) -> None:
        self._confidence.setVisible(False)
        try:
            persistence.set_confidence_enabled(False)
        except Exception:
            pass

    def _log_confidence(self, q: Question, correct: bool) -> None:
        if self._confidence_value is None:
            return
        try:
            persistence.log_confidence(q.id, q.section,
                                       self._confidence_value, correct)
        except Exception:
            pass

    def _on_next(self) -> None:
        if self._idx + 1 >= len(self._queue):
            self.home_requested.emit()
        else:
            self._idx += 1
            self._show_current()
