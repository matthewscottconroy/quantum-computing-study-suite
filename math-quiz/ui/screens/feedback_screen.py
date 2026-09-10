"""Evaluation / feedback screen shown after each answer is graded."""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser,
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

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._flagged = False
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

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
        self._model_answer_widget.setStyleSheet(
            "font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', 'Courier New', monospace;"
            "font-size: 13px; line-height: 1.5;"
        )
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

        root.addStretch()

        # ── Bottom bar ────────────────────────────────────────────────────────
        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(48, 12, 48, 12)
        self._flag_btn = QPushButton("⚑ Flag for review")
        self._flag_btn.setObjectName("flat")
        self._flag_btn.setToolTip(
            "Bookmark this question for later review (click again to remove)"
        )
        self._flag_btn.clicked.connect(self.flag_requested)
        bar_layout.addWidget(self._flag_btn)
        bar_layout.addStretch()
        next_btn = QPushButton("Next Question →")
        next_btn.setObjectName("accent")
        next_btn.clicked.connect(self.next_question_requested)
        bar_layout.addWidget(next_btn)
        outer.addWidget(bar)

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

    def set_flagged(self, flagged: bool) -> None:
        """Reflect the question's flagged state on the toggle button."""
        self._flagged = flagged
        if flagged:
            self._flag_btn.setText("⚑ Flagged — click to unflag")
            self._flag_btn.setStyleSheet(f"color: {theme.WARNING}; font-weight: bold;")
        else:
            self._flag_btn.setText("⚑ Flag for review")
            self._flag_btn.setStyleSheet("")
        self._flag_btn.setEnabled(True)

    def is_flagged(self) -> bool:
        return self._flagged


def _verdict_color(verdict: str) -> str:
    if verdict == "Correct":
        return theme.SUCCESS
    if verdict == "Partially correct":
        return theme.PARTIAL
    return theme.ERROR
