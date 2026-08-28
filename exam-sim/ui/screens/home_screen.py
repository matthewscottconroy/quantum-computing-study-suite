"""Home screen for exam-sim — pick a mode."""
from __future__ import annotations
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame,
)
from PyQt6.QtCore import pyqtSignal
from config import (
    SECTIONS, EXAM_QUESTION_COUNT, EXAM_MINUTES, PASS_MARK,
    SPRINT_QUESTION_COUNT, SPRINT_MINUTES,
)
from persistence import load_history, load_missed
from ui import theme


class HomeScreen(QWidget):
    full_exam_requested = pyqtSignal()
    sprint_requested    = pyqtSignal(str)   # section name
    review_requested    = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 36)
        root.setSpacing(20)

        title = QLabel("Exam Sim")
        title.setObjectName("heading")
        sub = QLabel(
            "Timed mock exams for IBM C1000-179 — Fundamentals of Quantum "
            f"Computing Using Qiskit v2.X Developer. {EXAM_QUESTION_COUNT} questions, "
            f"{EXAM_MINUTES} minutes, {PASS_MARK} correct to pass."
        )
        sub.setObjectName("subheading")
        sub.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(sub)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        cards = QHBoxLayout(); cards.setSpacing(20)
        root.addLayout(cards)

        # --- Full exam ---
        full_card = self._card("Full exam")
        full_lbl = QLabel(
            f"{EXAM_QUESTION_COUNT} questions drawn proportionally to the exam "
            f"section weights.\n\n{EXAM_MINUTES}-minute countdown, question "
            "navigator with flag/skip, no feedback until you submit."
        )
        full_lbl.setWordWrap(True)
        full_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        full_card.layout().addWidget(full_lbl)
        full_card.layout().addStretch()
        full_btn = QPushButton("Start Full Exam")
        full_btn.setObjectName("accent")
        full_btn.clicked.connect(self.full_exam_requested)
        full_card.layout().addWidget(full_btn)
        cards.addWidget(full_card, 1)

        # --- Sprint ---
        sprint_card = self._card("Sprint")
        sprint_lbl = QLabel(
            f"{SPRINT_QUESTION_COUNT} questions from one section, "
            f"{SPRINT_MINUTES}-minute timer. Drill your weakest objective."
        )
        sprint_lbl.setWordWrap(True)
        sprint_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        sprint_card.layout().addWidget(sprint_lbl)
        self._section_combo = QComboBox()
        for section, count in SECTIONS.items():
            self._section_combo.addItem(f"{section}  ({count} in bank)", section)
        sprint_card.layout().addWidget(self._section_combo)
        sprint_card.layout().addStretch()
        sprint_btn = QPushButton("Start Sprint")
        sprint_btn.clicked.connect(self._on_sprint)
        sprint_card.layout().addWidget(sprint_btn)
        cards.addWidget(sprint_card, 1)

        # --- Review ---
        review_card = self._card("Review missed")
        self._missed_lbl = QLabel("")
        self._missed_lbl.setWordWrap(True)
        self._missed_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        review_card.layout().addWidget(self._missed_lbl)
        review_card.layout().addStretch()
        self._review_btn = QPushButton("Review Missed Questions")
        self._review_btn.clicked.connect(self.review_requested)
        review_card.layout().addWidget(self._review_btn)
        cards.addWidget(review_card, 1)

        root.addStretch()

        self._history_lbl = QLabel("")
        self._history_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        self._history_lbl.setWordWrap(True)
        root.addWidget(self._history_lbl)
        self.refresh()

    def _card(self, title: str) -> QFrame:
        card = QFrame(); card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        lbl = QLabel(title.upper())
        lbl.setStyleSheet(f"font-weight: bold; color: {theme.ACCENT}; font-size: 12px;")
        layout.addWidget(lbl)
        return card

    def refresh(self) -> None:
        missed = load_missed()
        if missed:
            self._missed_lbl.setText(
                f"{len(missed)} previously missed question"
                f"{'s' if len(missed) != 1 else ''} waiting. Answer one correctly "
                "and it leaves the list."
            )
            self._review_btn.setEnabled(True)
        else:
            self._missed_lbl.setText("No missed questions on file — take an exam first.")
            self._review_btn.setEnabled(False)

        history = load_history()
        if history:
            last = history[-1]
            when = time.strftime("%Y-%m-%d %H:%M", time.localtime(last.get("timestamp", 0)))
            self._history_lbl.setText(
                f"{len(history)} session(s) recorded — last: {last.get('mode', '?')} "
                f"{last.get('correct', 0)}/{last.get('total', 0)} on {when}"
            )
        else:
            self._history_lbl.setText("No sessions recorded yet.")

    def _on_sprint(self) -> None:
        self.sprint_requested.emit(self._section_combo.currentData())
