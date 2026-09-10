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
    reference_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._subject_cbs: dict[str, QCheckBox] = {}
        self._type_cbs: dict[str, QCheckBox] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 40)
        root.setSpacing(24)

        title = QLabel("Math for Quantum Computing")
        title.setObjectName("heading")
        subtitle = QLabel(
            "Build your mathematical foundations for quantum computing research."
        )
        subtitle.setObjectName("subheading")
        root.addWidget(title)
        root.addWidget(subtitle)

        sep = QFrame()
        sep.setObjectName("separator")
        root.addWidget(sep)

        content = QHBoxLayout()
        content.setSpacing(32)
        root.addLayout(content)

        # ── Left: subject selection ───────────────────────────────────────────
        left = QVBoxLayout()
        left.setSpacing(8)
        subj_label = QLabel("Subjects")
        subj_label.setStyleSheet(
            f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;"
        )
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
            self._subject_cbs[subj] = cb
            grid.addWidget(cb, i // 2, i % 2)

        scroll.setWidget(inner)
        scroll.setMinimumHeight(280)
        left.addWidget(scroll)

        row = QHBoxLayout()
        for label, val in [("All", True), ("None", False)]:
            btn = QPushButton(label)
            btn.setObjectName("flat")
            btn.clicked.connect(lambda _, v=val: self._set_all(v))
            row.addWidget(btn)
        row.addStretch()
        left.addLayout(row)
        content.addLayout(left, 3)

        # ── Right: options ────────────────────────────────────────────────────
        right = QVBoxLayout()
        right.setSpacing(20)

        diff_card = self._make_card("Difficulty")
        self._diff_combo = QComboBox()
        self._diff_combo.addItem("Randomise each question", None)
        for d in DIFFICULTY_LEVELS:
            self._diff_combo.addItem(d.capitalize(), d)
        diff_card.layout().addWidget(self._diff_combo)
        right.addWidget(diff_card)

        count_card = self._make_card("Number of questions")
        self._count_spin = QSpinBox()
        self._count_spin.setRange(3, 50)
        self._count_spin.setValue(DEFAULT_QUESTION_COUNT)
        count_card.layout().addWidget(self._count_spin)
        right.addWidget(count_card)

        type_card = self._make_card("Question types")
        for qt in QUESTION_TYPES:
            cb = QCheckBox(qt.replace("_", " ").capitalize())
            cb.setChecked(True)
            cb.stateChanged.connect(self._on_type_changed)
            self._type_cbs[qt] = cb
            type_card.layout().addWidget(cb)
        right.addWidget(type_card)

        right.addStretch()
        content.addLayout(right, 2)

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
        reference_btn.setToolTip("Browse the shared docs/ chapters inside the app")
        reference_btn.clicked.connect(self.reference_requested)
        btn_row.addWidget(reference_btn)
        btn_row.addStretch()
        self._begin_btn = QPushButton("Begin Session")
        self._begin_btn.setObjectName("accent")
        self._begin_btn.clicked.connect(self._on_begin)
        btn_row.addWidget(self._begin_btn)
        root.addLayout(btn_row)

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
        for cb in self._subject_cbs.values():
            cb.setChecked(val)

    def _on_subject_changed(self) -> None:
        self._update_begin_btn()

    def _on_type_changed(self) -> None:
        self._update_begin_btn()

    def _update_begin_btn(self) -> None:
        any_subj = any(cb.isChecked() for cb in self._subject_cbs.values())
        any_type = any(cb.isChecked() for cb in self._type_cbs.values())
        self._begin_btn.setEnabled(any_subj and any_type)

    def _on_begin(self) -> None:
        subjects = [s for s, cb in self._subject_cbs.items() if cb.isChecked()]
        types    = [t for t, cb in self._type_cbs.items()    if cb.isChecked()]
        if not subjects or not types:
            return
        config = QuizConfig(
            subjects=subjects,
            difficulty=self._diff_combo.currentData(),
            question_types=types,
            question_count=self._count_spin.value(),
        )
        self.quiz_started.emit(config)
