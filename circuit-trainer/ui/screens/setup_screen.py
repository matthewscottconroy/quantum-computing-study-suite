"""Session setup screen — category selection, difficulty, problem count."""

from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QComboBox, QSpinBox, QFrame, QGridLayout, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import TrainerConfig, ProblemCategory
from config import DEFAULT_PROBLEM_COUNT, SPRINT_QUESTION_COUNT, SPRINT_SECONDS
from ui import theme

ALL_CATEGORIES = list(ProblemCategory)

# Prediction-style categories with deterministic, auto-checkable answers —
# the only ones used by Sprint mode (no Claude grading, instant verdicts).
SPRINT_CATEGORIES = [
    ProblemCategory.MEASUREMENT_PROBS,
    ProblemCategory.SINGLE_GATE_OUTPUT,
    ProblemCategory.GATE_SEQUENCE,
    ProblemCategory.CIRCUIT_UNITARY,
    ProblemCategory.MULTI_QUBIT_OUTPUT,
]
DIFFICULTY_OPTIONS = [("Adaptive (recommended)", None), ("Beginner", "beginner"),
                      ("Intermediate", "intermediate"), ("Advanced", "advanced")]

CATEGORY_DESCRIPTIONS = {
    ProblemCategory.SINGLE_GATE_OUTPUT:   "Apply one gate to a known state — what comes out? Includes Rx/Ry/Rz.",
    ProblemCategory.GATE_SEQUENCE:        "Multiple gates in order — trace the state step by step.",
    ProblemCategory.MEASUREMENT_PROBS:    "Compute P(|0⟩) or P(|1⟩) after a circuit.",
    ProblemCategory.GATE_IDENTITY:        "Identify a gate from its matrix or description.",
    ProblemCategory.CIRCUIT_UNITARY:      "Compute the overall unitary of a gate sequence.",
    ProblemCategory.ENTANGLEMENT:         "Detect and classify entanglement in circuit outputs.",
    ProblemCategory.MULTI_QUBIT_OUTPUT:   "Trace multi-qubit circuits — CNOT, SWAP, Toffoli.",
    ProblemCategory.CIRCUIT_EQUIVALENCE:  "Are two circuits the same up to global phase?",
    ProblemCategory.NOTATION_READING:     "Parse Dirac notation, bra-ket expressions, and QEC codes.",
    ProblemCategory.CIRCUIT_COMPOSITION:  "Identify or build a circuit that achieves a given task.",
    ProblemCategory.NOISE_CHANNEL:        "Bit-flip, phase-flip, depolarizing, amplitude damping — exact calculations.",
    ProblemCategory.CIRCUIT_EXPLANATION:  "Open-ended: explain what a circuit does. Graded by Claude (API key required).",
}


class SetupScreen(QWidget):
    session_started   = pyqtSignal(object)   # TrainerConfig
    history_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cbs: dict[ProblemCategory, QCheckBox] = {}
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 36)
        root.setSpacing(20)

        # Header
        title = QLabel("Circuit Trainer")
        title.setObjectName("heading")
        sub = QLabel("Build proficiency reading and solving quantum circuit problems.")
        sub.setObjectName("subheading")
        root.addWidget(title)
        root.addWidget(sub)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        content = QHBoxLayout()
        content.setSpacing(32)
        root.addLayout(content)

        # Left: category grid
        left = QVBoxLayout()
        left.setSpacing(8)
        hdr = QLabel("Problem Categories")
        hdr.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        left.addWidget(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        inner = QWidget()
        grid = QVBoxLayout(inner)
        grid.setSpacing(6)
        grid.setContentsMargins(0, 0, 8, 0)

        for cat in ALL_CATEGORIES:
            row = QHBoxLayout()
            cb = QCheckBox(cat.value)
            cb.setChecked(True)
            cb.stateChanged.connect(self._validate)
            color = theme.CATEGORY_COLORS.get(cat.value, theme.ACCENT)
            cb.setStyleSheet(
                f"QCheckBox::indicator:checked {{ background: {color}; border-color: {color}; }}"
            )
            self._cbs[cat] = cb

            desc = QLabel(CATEGORY_DESCRIPTIONS.get(cat, ""))
            desc.setObjectName("muted")
            desc.setWordWrap(True)

            col = QVBoxLayout()
            col.setSpacing(1)
            col.addWidget(cb)
            col.addWidget(desc)
            grid.addLayout(col)

        scroll.setWidget(inner)
        left.addWidget(scroll)

        shortcuts = QHBoxLayout()
        for label, val in [("All", True), ("None", False)]:
            btn = QPushButton(label); btn.setObjectName("flat")
            btn.clicked.connect(lambda _, v=val: self._set_all(v))
            shortcuts.addWidget(btn)
        shortcuts.addStretch()
        left.addLayout(shortcuts)
        content.addLayout(left, 3)

        # Right: options
        right = QVBoxLayout()
        right.setSpacing(16)

        diff_card = self._card("Difficulty")
        self._diff_combo = QComboBox()
        for label, val in DIFFICULTY_OPTIONS:
            self._diff_combo.addItem(label, val)
        diff_card.layout().addWidget(self._diff_combo)
        right.addWidget(diff_card)

        count_card = self._card("Number of problems")
        self._count_spin = QSpinBox()
        self._count_spin.setRange(5, 60)
        self._count_spin.setValue(DEFAULT_PROBLEM_COUNT)
        count_card.layout().addWidget(self._count_spin)
        right.addWidget(count_card)

        tip_card = self._card("How it works")
        tip = QLabel(
            "Each problem is generated fresh by Qiskit with the correct answer computed "
            "mathematically. Multiple-choice answers are auto-graded instantly. After each "
            "problem you see a full worked solution with step-by-step derivations.\n\n"
            "Adaptive mode adjusts difficulty based on your running accuracy."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        tip_card.layout().addWidget(tip)
        right.addWidget(tip_card)

        sprint_card = self._card("Sprint")
        sprint_tip = QLabel(
            f"{SPRINT_QUESTION_COUNT} rapid-fire prediction questions, "
            f"{SPRINT_SECONDS} seconds each. Timeout counts as wrong and "
            "auto-advances. Auto-graded only — instant right/wrong flash, "
            "no worked solutions until the end screen. Uses the difficulty "
            "selected above."
        )
        sprint_tip.setWordWrap(True)
        sprint_tip.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        sprint_card.layout().addWidget(sprint_tip)
        sprint_btn = QPushButton("Start Sprint ⏱")
        sprint_btn.clicked.connect(self._on_sprint)
        sprint_card.layout().addWidget(sprint_btn)
        right.addWidget(sprint_card)
        right.addStretch()
        content.addLayout(right, 2)

        sep2 = QFrame(); sep2.setObjectName("separator")
        root.addWidget(sep2)

        btn_row = QHBoxLayout()
        history_btn = QPushButton("View History")
        history_btn.setObjectName("flat")
        history_btn.clicked.connect(self.history_requested)
        btn_row.addWidget(history_btn)
        btn_row.addStretch()
        self._start_btn = QPushButton("Start Training")
        self._start_btn.setObjectName("accent")
        self._start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(self._start_btn)
        root.addLayout(btn_row)

    def _card(self, title: str) -> QFrame:
        card = QFrame(); card.setObjectName("card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(lbl)
        return card

    def _set_all(self, val: bool) -> None:
        for cb in self._cbs.values():
            cb.setChecked(val)

    def _validate(self) -> None:
        self._start_btn.setEnabled(any(cb.isChecked() for cb in self._cbs.values()))

    def _on_start(self) -> None:
        cats = [cat for cat, cb in self._cbs.items() if cb.isChecked()]
        if not cats:
            return
        config = TrainerConfig(
            categories=cats,
            difficulty=self._diff_combo.currentData(),
            problem_count=self._count_spin.value(),
        )
        self.session_started.emit(config)

    def _on_sprint(self) -> None:
        config = TrainerConfig(
            categories=list(SPRINT_CATEGORIES),
            difficulty=self._diff_combo.currentData(),
            problem_count=SPRINT_QUESTION_COUNT,
            sprint=True,
        )
        self.session_started.emit(config)
