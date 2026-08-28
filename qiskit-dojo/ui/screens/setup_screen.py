"""Setup screen for qiskit-dojo."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QComboBox, QSpinBox, QFrame, QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import DojoConfig
from katas import all_sections, all_katas
from config import DEFAULT_KATA_COUNT
from ui import theme

_ORDERS = [("Shuffled", True), ("Curriculum order (by section)", False)]


class SetupScreen(QWidget):
    session_started   = pyqtSignal(object)
    history_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cbs: dict[str, QCheckBox] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 36)
        root.setSpacing(20)

        title = QLabel("Qiskit Dojo")
        title.setObjectName("heading")
        sub = QLabel(
            "Write real Qiskit 2.x code, run it, get graded — circuits, primitives, "
            "OpenQASM, plus bug-hunt and legacy-code modernization katas for the "
            "IBM Quantum Developer exam."
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
        sec_lbl = QLabel("Sections")
        sec_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        left.addWidget(sec_lbl)

        try:
            from persistence import pass_rates_by_section
            rates = pass_rates_by_section()
        except Exception:
            rates = {}
        kata_counts: dict[str, int] = {}
        for k in all_katas():
            kata_counts[k.section] = kata_counts.get(k.section, 0) + 1

        for sec in all_sections():
            row = QHBoxLayout()
            row.setSpacing(8)

            cb = QCheckBox(f"{sec}  ({kata_counts.get(sec, 0)})")
            cb.setChecked(True)
            cb.stateChanged.connect(self._validate)
            color = theme.SECTION_COLORS.get(sec, theme.ACCENT)
            cb.setStyleSheet(
                f"QCheckBox::indicator:checked {{ background: {color}; border-color: {color}; }}"
            )
            self._cbs[sec] = cb
            row.addWidget(cb, 1)

            rate = rates.get(sec)
            pct = int(rate * 100) if rate is not None else None
            pct_lbl = QLabel(f"{pct}%" if pct is not None else "—")
            pct_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED}; min-width: 32px;")
            pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            row.addWidget(pct_lbl)
            left.addLayout(row)

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
            left.addWidget(bar)

        shortcuts = QHBoxLayout()
        for label, val in [("All", True), ("None", False)]:
            btn = QPushButton(label); btn.setObjectName("flat")
            btn.clicked.connect(lambda _, v=val: self._set_all(v))
            shortcuts.addWidget(btn)
        shortcuts.addStretch()
        left.addLayout(shortcuts)
        left.addStretch()
        content.addLayout(left, 3)

        right = QVBoxLayout(); right.setSpacing(16)

        count_card = self._card("Number of katas")
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 36)
        self._count_spin.setValue(DEFAULT_KATA_COUNT)
        count_card.layout().addWidget(self._count_spin)
        right.addWidget(count_card)

        order_card = self._card("Order")
        self._order_combo = QComboBox()
        for label, val in _ORDERS:
            self._order_combo.addItem(label, val)
        order_card.layout().addWidget(self._order_combo)
        right.addWidget(order_card)

        tip_card = self._card("How it works")
        tip = QLabel(
            "You write real Qiskit code in the editor; the dojo executes it in an "
            "isolated Python subprocess and grades it with assertions — fully "
            "offline.\n\n"
            "Debugging katas hand you code with a planted bug; Modernization "
            "katas hand you retired-API code to rewrite for Qiskit 2.x.\n\n"
            "The optional Claude review button needs an Anthropic API key."
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
        btn_row.addStretch()
        self._start_btn = QPushButton("Start Session")
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
        sections = [s for s, cb in self._cbs.items() if cb.isChecked()]
        if not sections:
            return
        config = DojoConfig(
            sections=sections,
            kata_count=self._count_spin.value(),
            shuffle=self._order_combo.currentData(),
        )
        self.session_started.emit(config)
