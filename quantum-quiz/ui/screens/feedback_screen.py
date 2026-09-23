"""Evaluation / feedback screen shown after each answer is graded."""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextBrowser,
    QPushButton, QListWidget, QListWidgetItem, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.models import Evaluation
from ui import theme
from ui.widgets.score_bar import ScoreBar
from ui.widgets.collapsible_panel import CollapsiblePanel
from config import SCORE_CORRECT_THRESHOLD, SCORE_PARTIAL_THRESHOLD


class FeedbackScreen(QWidget):
    next_question_requested = pyqtSignal()
    flag_requested = pyqtSignal()          # toggle "flag for review" on this question
    mistake_cause_selected = pyqtSignal(str)   # cause id from MISTAKE_CAUSES
    mistake_note_saved = pyqtSignal(str)       # one-line note for the journal entry

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._selected_cause: str | None = None
        self._committed_note: str = ""
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Scrollable content ────────────────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        root = QVBoxLayout(content)
        root.setContentsMargins(48, 36, 48, 24)
        root.setSpacing(20)
        scroll.setWidget(content)

        # ── Score row ─────────────────────────────────────────────────────────
        score_row = QHBoxLayout()
        score_row.setSpacing(20)

        score_col = QVBoxLayout()
        score_col.setSpacing(6)
        score_lbl = QLabel("Score")
        score_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        score_col.addWidget(score_lbl)
        self._score_bar = ScoreBar()
        score_col.addWidget(self._score_bar)
        score_row.addLayout(score_col, 1)

        verdict_col = QVBoxLayout()
        verdict_col.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self._verdict_badge = QLabel("—")
        self._verdict_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._verdict_badge.setFixedHeight(32)
        verdict_col.addWidget(self._verdict_badge)
        score_row.addLayout(verdict_col)

        self._score_num = QLabel("")
        self._score_num.setStyleSheet("font-size: 28px; font-weight: bold;")
        self._score_num.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        score_row.addWidget(self._score_num)

        root.addLayout(score_row)

        sep = QFrame()
        sep.setObjectName("separator")
        root.addWidget(sep)

        # ── Feedback ──────────────────────────────────────────────────────────
        fb_lbl = QLabel("Feedback")
        fb_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        root.addWidget(fb_lbl)
        self._feedback_browser = QTextBrowser()
        self._feedback_browser.setMaximumHeight(120)
        root.addWidget(self._feedback_browser)

        # ── Model answer (collapsible) ────────────────────────────────────────
        self._model_answer_widget = QTextBrowser()
        self._model_answer_widget.setMinimumHeight(80)
        self._model_panel = CollapsiblePanel("Model Answer", self._model_answer_widget)
        root.addWidget(self._model_panel)

        # ── Missed points ─────────────────────────────────────────────────────
        self._missed_container = QWidget()
        missed_layout = QVBoxLayout(self._missed_container)
        missed_layout.setContentsMargins(0, 0, 0, 0)
        missed_layout.setSpacing(6)
        missed_lbl = QLabel("Key points missed")
        missed_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        missed_layout.addWidget(missed_lbl)
        self._missed_list = QListWidget()
        self._missed_list.setMaximumHeight(120)
        missed_layout.addWidget(self._missed_list)
        root.addWidget(self._missed_container)

        # ── Follow-up ─────────────────────────────────────────────────────────
        self._followup_container = QFrame()
        self._followup_container.setObjectName("card")
        fu_layout = QVBoxLayout(self._followup_container)
        fu_layout.setContentsMargins(16, 12, 16, 12)
        fu_lbl = QLabel("Follow-up to consider")
        fu_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        fu_layout.addWidget(fu_lbl)
        self._followup_label = QLabel("")
        self._followup_label.setWordWrap(True)
        self._followup_label.setStyleSheet(f"font-style: italic; color: {theme.ACCENT};")
        fu_layout.addWidget(self._followup_label)
        root.addWidget(self._followup_container)

        # ── Mistake journal ("what went wrong?") ──────────────────────────────
        root.addWidget(self._build_mistake_journal())

        root.addStretch()

        # ── Bottom bar ────────────────────────────────────────────────────────
        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(48, 12, 48, 12)
        self._flag_btn = QPushButton("⚑ Flag for review")
        self._flag_btn.setObjectName("flat")
        self._flag_btn.setToolTip(
            "Save this question to your review list (quiz_flagged.json).\n"
            "Click again to remove it. Flagged items are listed on the History screen."
        )
        self._flag_btn.clicked.connect(self.flag_requested)
        bar_layout.addWidget(self._flag_btn)
        bar_layout.addStretch()
        next_btn = QPushButton("Next Question →")
        next_btn.setObjectName("accent")
        next_btn.clicked.connect(self.next_question_requested)
        bar_layout.addWidget(next_btn)
        outer.addWidget(bar)

    # ── Mistake journal ───────────────────────────────────────────────────────

    def _build_mistake_journal(self) -> QWidget:
        """Compact, skippable "What went wrong?" row shown for a wrong answer.

        The mistake itself is already saved (with ``cause=null``) by the time
        this appears — clicking a cause only *categorises* it, and ignoring the
        row loses nothing.  No modal, nothing blocks Next Question.
        """
        from persistence import CAUSE_LABELS, MISTAKE_CAUSES

        card = QFrame()
        card.setObjectName("card")
        card.setAccessibleName("Mistake journal")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        header = QHBoxLayout()
        title = QLabel("What went wrong?")
        title.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        header.addWidget(title)
        hint = QLabel("optional — the mistake is already saved either way")
        hint.setObjectName("muted")
        header.addWidget(hint)
        header.addStretch()
        self._mistake_status = QLabel("")
        self._mistake_status.setObjectName("muted")
        self._mistake_status.setAccessibleName("Mistake journal status")
        header.addWidget(self._mistake_status)
        layout.addLayout(header)

        chips = QHBoxLayout()
        chips.setSpacing(6)
        self._cause_btns: dict[str, QPushButton] = {}
        for cause in MISTAKE_CAUSES:
            label = CAUSE_LABELS[cause]
            btn = QPushButton(label)
            btn.setObjectName("chip")
            btn.setCheckable(True)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setAccessibleName(f"Cause of mistake: {label.lower()}")
            btn.setAccessibleDescription(
                "Categorise this mistake. Select again to clear the category."
            )
            btn.setToolTip(f"{label} — click again to clear")
            btn.clicked.connect(lambda _checked=False, c=cause: self._on_cause_clicked(c))
            chips.addWidget(btn)
            self._cause_btns[cause] = btn
        chips.addStretch()
        layout.addLayout(chips)

        self._mistake_note = QLineEdit()
        self._mistake_note.setPlaceholderText(
            "Optional one-line note — press Enter to save"
        )
        self._mistake_note.setAccessibleName("Mistake note")
        self._mistake_note.setMaxLength(280)
        self._mistake_note.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._mistake_note.returnPressed.connect(self._on_note_committed)
        self._mistake_note.editingFinished.connect(self._on_note_committed)
        layout.addWidget(self._mistake_note)

        self._mistake_card = card
        card.hide()
        return card

    def _on_cause_clicked(self, cause: str) -> None:
        self._selected_cause = None if self._selected_cause == cause else cause
        self._sync_cause_buttons()
        self.mistake_cause_selected.emit(self._selected_cause or "")

    def _sync_cause_buttons(self) -> None:
        from persistence import CAUSE_LABELS
        for cause, btn in self._cause_btns.items():
            selected = cause == self._selected_cause
            btn.setChecked(selected)
            # Never colour alone: the chosen cause also carries a check glyph.
            btn.setText(f"✓ {CAUSE_LABELS[cause]}" if selected else CAUSE_LABELS[cause])

    def _on_note_committed(self) -> None:
        if self._mistake_card.isHidden():
            return
        text = self._mistake_note.text().strip()
        if text == self._committed_note:
            return
        self._committed_note = text
        self.mistake_note_saved.emit(text)

    def show_mistake_journal(self, cause: str | None = None, note: str = "") -> None:
        """Reveal the row for a wrong answer, pre-filled from the stored entry."""
        self._selected_cause = cause or None
        self._sync_cause_buttons()
        self._committed_note = (note or "").strip()
        self._mistake_note.setText(note or "")
        self._mistake_status.setText("✓ Logged to your mistake journal")
        self._mistake_card.show()

    def hide_mistake_journal(self) -> None:
        self._selected_cause = None
        self._committed_note = ""
        self._sync_cause_buttons()
        self._mistake_note.clear()
        self._mistake_status.setText("")
        self._mistake_card.hide()

    def mistake_journal_visible(self) -> bool:
        # isHidden(), not isVisible(): this screen is hidden while another page
        # of the stack is showing, which says nothing about this card.
        return not self._mistake_card.isHidden()

    def selected_cause(self) -> str | None:
        return self._selected_cause

    def mistake_note(self) -> str:
        return self._mistake_note.text().strip()

    def set_mistake_status(self, text: str) -> None:
        """Inline, non-blocking status for the journal row (never a dialog)."""
        self._mistake_status.setText(text)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_evaluation(self, ev: Evaluation) -> None:
        self._score_bar.animate_to(ev.score)
        self._score_num.setText(f"{ev.score}/10")

        verdict_color = _verdict_color(ev.verdict)
        self._verdict_badge.setText(ev.verdict)
        self._verdict_badge.setStyleSheet(
            f"background: {verdict_color}22; color: {verdict_color};"
            "border-radius: 10px; padding: 2px 14px;"
            "font-weight: bold; font-size: 13px;"
        )

        self._feedback_browser.setPlainText(ev.feedback)
        self._model_answer_widget.setPlainText(ev.model_answer)

        self._missed_list.clear()
        if ev.key_points_missed:
            for point in ev.key_points_missed:
                self._missed_list.addItem(QListWidgetItem(f"• {point}"))
            self._missed_container.show()
        else:
            self._missed_container.hide()

        if ev.follow_up:
            self._followup_label.setText(ev.follow_up)
            self._followup_container.show()
        else:
            self._followup_container.hide()

        # Flag state and the mistake journal are set separately by the
        # controller once it has looked this question up in persistence.
        self.set_flagged(False)
        self.hide_mistake_journal()

    def set_flagged(self, flagged: bool) -> None:
        """Reflect the persisted flag state on the toggle button."""
        self._flagged = flagged
        if flagged:
            self._flag_btn.setText("⚑ Flagged — click to unflag")
            self._flag_btn.setStyleSheet(f"color: {theme.WARNING}; font-weight: bold;")
        else:
            self._flag_btn.setText("⚑ Flag for review")
            self._flag_btn.setStyleSheet("")

    def is_flagged(self) -> bool:
        return getattr(self, "_flagged", False)


def _verdict_color(verdict: str) -> str:
    if verdict == "Correct":
        return theme.SUCCESS
    if verdict == "Partially correct":
        return theme.PARTIAL
    return theme.ERROR
