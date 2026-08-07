"""Setup screen for vqa-trainer."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QComboBox, QSpinBox, QFrame,
    QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import TrainerConfig
from problems import all_categories
from config import DEFAULT_PROBLEM_COUNT
from ui import theme

_DIFFICULTIES = [("Mixed (all levels)", None), ("Beginner", "beginner"),
                 ("Intermediate", "intermediate"), ("Advanced", "advanced")]


def _avg_secs_per_problem() -> float | None:
    """Return mean elapsed_secs per attempt across all saved sessions, or None."""
    try:
        from persistence import _load_raw
        sessions = _load_raw()
    except Exception:
        return None
    elapsed = [
        a["elapsed_secs"]
        for s in sessions
        for a in s.get("attempts", [])
        if a.get("elapsed_secs", 0) > 0
    ]
    return sum(elapsed) / len(elapsed) if elapsed else None


class SetupScreen(QWidget):
    session_started     = pyqtSignal(object)
    history_requested   = pyqtSignal()
    reference_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cbs: dict[str, QCheckBox] = {}
        self._mastery_bars: dict[str, QProgressBar] = {}
        self._mastery_lbls: dict[str, QLabel] = {}
        self._avg_secs: float | None = _avg_secs_per_problem()
        self._problem_weights: dict[str, float] = {}
        self._problem_categories: dict[str, str] = {}
        self._build_ui()
        self._update_badge()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 36)
        root.setSpacing(20)

        title = QLabel("VQA Trainer")
        title.setObjectName("heading")
        sub = QLabel(
            "Master variational quantum algorithms — VQE, QAOA, parameter shift rule, "
            "ansatz design, barren plateaus, and error mitigation."
        )
        sub.setObjectName("subheading")
        sub.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(sub)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        content = QHBoxLayout(); content.setSpacing(32)
        root.addLayout(content)

        left = QVBoxLayout(); left.setSpacing(8)
        cat_lbl = QLabel("Topics")
        cat_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        left.addWidget(cat_lbl)

        # Try to load mastery scores
        try:
            from persistence import avg_scores_by_category
            avg_scores = avg_scores_by_category()
        except Exception:
            avg_scores = {}

        # Pre-load problem weights and category map for difficulty badge
        try:
            from persistence import problem_score_weights
            from problems import all_problems
            self._problem_weights = problem_score_weights()
            self._problem_categories = {p.id: p.category for p in all_problems()}
        except Exception:
            self._problem_weights = {}
            self._problem_categories = {}

        for cat in all_categories():
            # Row: checkbox + pct label
            row = QHBoxLayout()
            row.setSpacing(8)

            cb = QCheckBox(cat)
            cb.setChecked(True)
            cb.stateChanged.connect(self._validate)
            cb.stateChanged.connect(self._update_badge)
            color = theme.CATEGORY_COLORS.get(cat, theme.ACCENT)
            cb.setStyleSheet(
                f"QCheckBox::indicator:checked {{ background: {color}; border-color: {color}; }}"
            )
            self._cbs[cat] = cb
            row.addWidget(cb, 1)

            # Mastery percentage label
            raw_score = avg_scores.get(cat)
            pct = int((raw_score / 10) * 100) if raw_score is not None else None
            pct_lbl = QLabel(f"{pct}%" if pct is not None else "—")
            pct_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED}; min-width: 32px;")
            pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._mastery_lbls[cat] = pct_lbl
            row.addWidget(pct_lbl)

            left.addLayout(row)

            # Mastery progress bar
            bar = QProgressBar()
            bar.setFixedHeight(4)
            bar.setTextVisible(False)
            bar.setRange(0, 100)
            if pct is not None:
                bar.setValue(pct)
                bar_color = (
                    theme.SUCCESS if pct >= 70 else
                    theme.WARNING if pct >= 40 else
                    theme.ERROR
                )
            else:
                bar.setValue(0)
                bar_color = theme.BORDER
            bar.setStyleSheet(
                f"QProgressBar {{ background: {theme.SURFACE2}; border: none; border-radius: 2px; }}"
                f"QProgressBar::chunk {{ background: {bar_color}; border-radius: 2px; }}"
            )
            self._mastery_bars[cat] = bar
            left.addWidget(bar)

        shortcuts = QHBoxLayout()
        for label, val in [("All", True), ("None", False)]:
            btn = QPushButton(label); btn.setObjectName("flat")
            btn.clicked.connect(lambda _, v=val: self._set_all(v))
            shortcuts.addWidget(btn)
        shortcuts.addStretch()
        left.addLayout(shortcuts)

        # Flagged only checkbox
        self._flagged_cb = QCheckBox("Show Flagged Only")
        self._flagged_cb.setStyleSheet(f"color: {theme.WARNING};")
        self._flagged_cb.stateChanged.connect(self._on_flagged_toggled)
        left.addWidget(self._flagged_cb)

        # Adaptive difficulty badge
        self._badge_lbl = QLabel("")
        self._badge_lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        self._badge_lbl.setWordWrap(True)
        left.addWidget(self._badge_lbl)

        left.addStretch()
        content.addLayout(left, 3)

        right = QVBoxLayout(); right.setSpacing(16)

        diff_card = self._card("Difficulty")
        self._diff_combo = QComboBox()
        for label, val in _DIFFICULTIES:
            self._diff_combo.addItem(label, val)
        diff_card.layout().addWidget(self._diff_combo)
        right.addWidget(diff_card)

        count_card = self._card("Number of problems")
        self._count_spin = QSpinBox()
        self._count_spin.setRange(3, 40)
        self._count_spin.setValue(DEFAULT_PROBLEM_COUNT)
        count_card.layout().addWidget(self._count_spin)
        self._estimate_lbl = QLabel("")
        self._estimate_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        count_card.layout().addWidget(self._estimate_lbl)
        self._count_spin.valueChanged.connect(self._update_estimate)
        self._update_estimate(self._count_spin.value())
        right.addWidget(count_card)

        tip_card = self._card("Problem types")
        tip = QLabel(
            "Multiple-choice and numeric (parameter shift) problems are auto-graded.\n\n"
            "Open-ended design and explanation questions are graded by Claude "
            "(Anthropic API key required)."
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        tip_card.layout().addWidget(tip)
        right.addWidget(tip_card)
        right.addStretch()
        content.addLayout(right, 2)

        sep2 = QFrame(); sep2.setObjectName("separator")
        root.addWidget(sep2)

        btn_row = QHBoxLayout()
        history_btn = QPushButton("View History")
        history_btn.setObjectName("flat")
        history_btn.clicked.connect(self.history_requested)
        btn_row.addWidget(history_btn)

        reference_btn = QPushButton("Browse Reference")
        reference_btn.setObjectName("flat")
        reference_btn.clicked.connect(self.reference_requested)
        btn_row.addWidget(reference_btn)

        btn_row.addStretch()
        self._start_btn = QPushButton("Start Session")
        self._start_btn.setObjectName("accent")
        self._start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(self._start_btn)
        root.addLayout(btn_row)

    def _card(self, title: str) -> QFrame:
        card = QFrame(); card.setObjectName("card")
        from PyQt6.QtWidgets import QVBoxLayout as VBL
        layout = VBL(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)
        lbl = QLabel(title)
        lbl.setStyleSheet(f"font-weight: bold; color: {theme.TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(lbl)
        return card

    def _set_all(self, val: bool) -> None:
        for cb in self._cbs.values():
            cb.setChecked(val)

    def _on_flagged_toggled(self) -> None:
        flagged = self._flagged_cb.isChecked()
        for cb in self._cbs.values():
            cb.setEnabled(not flagged)
        self._validate()

    def _validate(self) -> None:
        if self._flagged_cb.isChecked():
            self._start_btn.setEnabled(True)
        else:
            self._start_btn.setEnabled(any(cb.isChecked() for cb in self._cbs.values()))

    def _update_estimate(self, count: int) -> None:
        if self._avg_secs is None:
            self._estimate_lbl.setText("")
            return
        total = self._avg_secs * count
        minutes = round(total / 60)
        self._estimate_lbl.setText(f"≈ {minutes} min" if minutes >= 1 else "< 1 min")

    def _update_badge(self) -> None:
        if not hasattr(self, "_badge_lbl"):
            return
        if not self._problem_weights:
            self._badge_lbl.setText("")
            return
        selected_cats = {cat for cat, cb in self._cbs.items() if cb.isChecked()}
        if not selected_cats:
            self._badge_lbl.setText("")
            return
        relevant = [
            w for pid, w in self._problem_weights.items()
            if self._problem_categories.get(pid) in selected_cats
        ]
        if not relevant:
            self._badge_lbl.setText("")
            return
        avg_weight = sum(relevant) / len(relevant)
        if avg_weight < 0.95:
            self._badge_lbl.setText("✓ Strong here — try Hard difficulty!")
        else:
            self._badge_lbl.setText("")

    def _on_start(self) -> None:
        flagged_only = self._flagged_cb.isChecked()
        if flagged_only:
            cats = list(self._cbs.keys())
        else:
            cats = [c for c, cb in self._cbs.items() if cb.isChecked()]
            if not cats:
                return
        config = TrainerConfig(
            categories=cats,
            difficulty=self._diff_combo.currentData(),
            problem_count=self._count_spin.value(),
            flagged_only=flagged_only,
        )
        self.session_started.emit(config)
