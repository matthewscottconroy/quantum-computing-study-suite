"""Session setup screen — subject selection, difficulty, count, question type."""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QComboBox, QSpinBox, QScrollArea, QFrame, QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal

from core.models import QuizConfig
from core.topics import TOPICS, DIFFICULTY_LEVELS, QUESTION_TYPES
from config import DEFAULT_QUESTION_COUNT
from ui import theme


class SetupScreen(QWidget):
    quiz_started        = pyqtSignal(object)   # QuizConfig
    history_requested   = pyqtSignal()
    reference_requested = pyqtSignal()         # open the in-app docs browser

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._checkboxes: dict[str, QCheckBox] = {}
        self._type_checkboxes: dict[str, QCheckBox] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(24)

        # ── Header ────────────────────────────────────────────────────────────
        header = QVBoxLayout()
        title = QLabel("Quantum Computing Quiz")
        title.setObjectName("heading")
        subtitle = QLabel("Configure your session, then begin.")
        subtitle.setObjectName("subheading")
        header.addWidget(title)
        header.addWidget(subtitle)
        root.addLayout(header)

        sep = QFrame()
        sep.setObjectName("separator")
        root.addWidget(sep)

        # ── Main content row ──────────────────────────────────────────────────
        content = QHBoxLayout()
        content.setSpacing(32)
        root.addLayout(content)

        # Left: subject selection
        left = QVBoxLayout()
        left.setSpacing(8)
        subj_label = QLabel("Subjects")
        subj_label.setStyleSheet(f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
        left.addWidget(subj_label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        grid = QGridLayout(inner)
        grid.setSpacing(6)
        grid.setContentsMargins(0, 0, 8, 0)

        subjects = list(TOPICS.keys())
        for i, subj in enumerate(subjects):
            cb = QCheckBox(subj)
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_subject_changed)
            color = theme.subject_color(subj)
            cb.setStyleSheet(
                f"QCheckBox::indicator:checked {{ background: {color}; border-color: {color}; }}"
            )
            self._checkboxes[subj] = cb
            grid.addWidget(cb, i // 2, i % 2)

        scroll.setWidget(inner)
        scroll.setMinimumHeight(240)
        left.addWidget(scroll)

        # Select all / none shortcuts
        row = QHBoxLayout()
        for label, val in [("All", True), ("None", False)]:
            btn = QPushButton(label)
            btn.setObjectName("flat")
            btn.clicked.connect(lambda _, v=val: self._set_all(v))
            row.addWidget(btn)
        row.addStretch()
        left.addLayout(row)
        content.addLayout(left, 3)

        # Right: options
        right = QVBoxLayout()
        right.setSpacing(20)

        # Difficulty
        diff_card = self._make_card("Difficulty")
        diff_inner = diff_card.layout()
        self._diff_combo = QComboBox()
        self._diff_combo.addItem("Randomise each question", None)
        for d in DIFFICULTY_LEVELS:
            self._diff_combo.addItem(d.capitalize(), d)
        diff_inner.addWidget(self._diff_combo)
        right.addWidget(diff_card)

        # Question count
        count_card = self._make_card("Number of questions")
        count_inner = count_card.layout()
        self._count_spin = QSpinBox()
        self._count_spin.setRange(3, 50)
        self._count_spin.setValue(DEFAULT_QUESTION_COUNT)
        count_inner.addWidget(self._count_spin)
        right.addWidget(count_card)

        # Question types
        type_card = self._make_card("Question types")
        type_inner = type_card.layout()
        for qt in QUESTION_TYPES:
            cb = QCheckBox(qt.replace("_", " ").capitalize())
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_type_changed)
            self._type_checkboxes[qt] = cb
            type_inner.addWidget(cb)
        right.addWidget(type_card)

        # Study modes
        mode_card = self._make_card("Study modes")
        mode_inner = mode_card.layout()
        self._viva_check = QCheckBox("Viva mode: follow-up probing")
        self._viva_check.setChecked(False)
        self._viva_check.setToolTip(
            "After a well-answered question (score ≥ 4), Claude asks one probing\n"
            "follow-up derived from your actual answer. Follow-ups are extra\n"
            "questions beyond the configured count."
        )
        mode_inner.addWidget(self._viva_check)
        right.addWidget(mode_card)

        right.addStretch()
        content.addLayout(right, 2)

        # ── Begin button ──────────────────────────────────────────────────────
        sep2 = QFrame()
        sep2.setObjectName("separator")
        root.addWidget(sep2)

        btn_row = QHBoxLayout()
        history_btn = QPushButton("View History")
        history_btn.setObjectName("flat")
        history_btn.clicked.connect(self.history_requested)
        btn_row.addWidget(history_btn)
        reference_btn = QPushButton("Reference")
        reference_btn.setObjectName("flat")
        reference_btn.setToolTip("Browse the study-suite docs (docs/**/*.md) inside the app")
        reference_btn.clicked.connect(self.reference_requested)
        btn_row.addWidget(reference_btn)
        btn_row.addStretch()
        self._begin_btn = QPushButton("Begin Session")
        self._begin_btn.setObjectName("accent")
        self._begin_btn.clicked.connect(self._on_begin)
        btn_row.addWidget(self._begin_btn)
        root.addLayout(btn_row)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _make_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(lbl)
        return card

    def _set_all(self, val: bool) -> None:
        for cb in self._checkboxes.values():
            cb.setChecked(val)

    def _on_subject_changed(self) -> None:
        any_checked = any(cb.isChecked() for cb in self._checkboxes.values())
        self._begin_btn.setEnabled(any_checked)

    def _on_type_changed(self) -> None:
        any_checked = any(cb.isChecked() for cb in self._type_checkboxes.values())
        self._begin_btn.setEnabled(any_checked)

    def _on_begin(self) -> None:
        subjects = [s for s, cb in self._checkboxes.items() if cb.isChecked()]
        types = [t for t, cb in self._type_checkboxes.items() if cb.isChecked()]
        if not subjects or not types:
            return
        difficulty = self._diff_combo.currentData()
        config = QuizConfig(
            subjects=subjects,
            difficulty=difficulty,
            question_types=types,
            question_count=self._count_spin.value(),
            viva_mode=self._viva_check.isChecked(),
        )
        self.quiz_started.emit(config)
