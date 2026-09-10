"""Setup screen — choose categories, card count, optional timer."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QSpinBox, QComboBox, QFrame, QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import DrillConfig
from core.deck import all_categories, all_cards
from config import DEFAULT_CARD_COUNT, DEFAULT_TIMER_SECS
from ui import theme

_TIMER_OPTIONS = [
    ("No timer", 0),
    ("10 seconds", 10),
    ("20 seconds", 20),
    ("30 seconds", 30),
    ("60 seconds", 60),
]


def _avg_secs_per_card() -> float | None:
    """Typical seconds per card across saved sessions (median), or None.

    ``elapsed_secs`` is recorded per rated card by the card screen (show →
    rate).  The median is used so one card left open while the user walked
    away does not inflate the estimate.
    """
    try:
        from persistence.storage import _load_raw
        sessions = _load_raw()
    except Exception:
        return None
    elapsed = sorted(
        float(r["elapsed_secs"])
        for s in sessions
        for r in s.get("results", [])
        if isinstance(r, dict) and isinstance(r.get("elapsed_secs"), (int, float))
        and r["elapsed_secs"] >= 0
    )
    if not elapsed:
        return None
    n = len(elapsed)
    mid = n // 2
    return elapsed[mid] if n % 2 else (elapsed[mid - 1] + elapsed[mid]) / 2


class SetupScreen(QWidget):
    drill_started       = pyqtSignal(object)   # DrillConfig
    history_requested   = pyqtSignal()
    browse_requested    = pyqtSignal()
    reference_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cbs: dict[str, QCheckBox] = {}
        self._mastery_bars:   dict[str, QProgressBar] = {}
        self._mastery_labels: dict[str, QLabel]       = {}
        self._flagged_cb: QCheckBox | None = None
        self._avg_secs: float | None = _avg_secs_per_card()
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 36)
        root.setSpacing(20)

        title = QLabel("Flashcard Drill")
        title.setObjectName("heading")
        sub = QLabel("Rapid-fire quantum computing facts — SRS-weighted for what you need most.")
        sub.setObjectName("subheading")
        root.addWidget(title)
        root.addWidget(sub)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        content = QHBoxLayout(); content.setSpacing(32)
        root.addLayout(content)

        # Left: category checkboxes
        left = QVBoxLayout(); left.setSpacing(8)
        cat_lbl = QLabel("Categories")
        cat_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        left.addWidget(cat_lbl)

        for cat in all_categories():
            # Checkbox + mastery label on same row
            row = QHBoxLayout()
            row.setSpacing(8)
            row.setContentsMargins(0, 0, 0, 0)

            cb = QCheckBox(cat)
            cb.setChecked(True)
            cb.stateChanged.connect(self._validate)
            color = theme.CATEGORY_COLORS.get(cat, theme.ACCENT)
            cb.setStyleSheet(
                f"QCheckBox::indicator:checked {{ background: {color}; border-color: {color}; }}"
            )
            self._cbs[cat] = cb
            row.addWidget(cb, 1)

            pct_lbl = QLabel("–")
            pct_lbl.setFixedWidth(36)
            pct_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            pct_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
            self._mastery_labels[cat] = pct_lbl
            row.addWidget(pct_lbl)

            row_widget = QWidget()
            row_widget.setLayout(row)
            left.addWidget(row_widget)

            # Progress bar below each checkbox row
            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            bar.setTextVisible(False)
            bar.setFixedHeight(4)
            bar.setStyleSheet(
                f"QProgressBar {{ background: {theme.SURFACE2}; border: none; border-radius: 2px; }}"
                f"QProgressBar::chunk {{ background: {theme.BORDER}; border-radius: 2px; }}"
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

        self._flagged_cb = QCheckBox("Show Flagged Only")
        self._flagged_cb.setStyleSheet(f"color: {theme.WARNING};")
        self._flagged_cb.stateChanged.connect(self._on_flagged_toggled)
        left.addWidget(self._flagged_cb)

        left.addStretch()
        content.addLayout(left, 3)

        # Right: options
        right = QVBoxLayout(); right.setSpacing(16)

        count_card = self._card("Cards per session")
        self._count_spin = QSpinBox()
        self._count_spin.setRange(5, 80)
        self._count_spin.setValue(DEFAULT_CARD_COUNT)
        count_card.layout().addWidget(self._count_spin)
        self._estimate_lbl = QLabel("")
        self._estimate_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        count_card.layout().addWidget(self._estimate_lbl)
        self._count_spin.valueChanged.connect(self._update_estimate)
        self._update_estimate(self._count_spin.value())
        right.addWidget(count_card)

        timer_card = self._card("Time limit per card")
        self._timer_combo = QComboBox()
        for label, val in _TIMER_OPTIONS:
            self._timer_combo.addItem(label, val)
        idx = next((i for i, (_, v) in enumerate(_TIMER_OPTIONS) if v == DEFAULT_TIMER_SECS), 0)
        self._timer_combo.setCurrentIndex(idx)
        timer_card.layout().addWidget(self._timer_combo)
        right.addWidget(timer_card)

        tip_card = self._card("How it works")
        tip = QLabel(
            "Each card shows a question.  Click Reveal to see the answer, then rate yourself:\n\n"
            "  Got it — knew it cold\n"
            "  Unsure — partial recall\n"
            "  Missed — didn't know\n\n"
            "Cards you miss appear more frequently (spaced repetition)."
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
        browse_btn = QPushButton("Browse Cards")
        browse_btn.setObjectName("flat")
        browse_btn.clicked.connect(self.browse_requested)
        btn_row.addWidget(browse_btn)
        reference_btn = QPushButton("Reference")
        reference_btn.setObjectName("flat")
        reference_btn.setToolTip("Browse the study docs (docs/**/*.md) without leaving the app")
        reference_btn.clicked.connect(self.reference_requested)
        btn_row.addWidget(reference_btn)
        btn_row.addStretch()
        self._start_btn = QPushButton("Start Drill")
        self._start_btn.setObjectName("accent")
        self._start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(self._start_btn)
        root.addLayout(btn_row)

        # One-line notice (e.g. "no flagged cards yet"); hidden until needed.
        self._notice_lbl = QLabel("")
        self._notice_lbl.setObjectName("notice")
        self._notice_lbl.setWordWrap(True)
        self._notice_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._notice_lbl.setStyleSheet(f"font-size: 12px; color: {theme.WARNING};")
        self._notice_lbl.hide()
        root.addWidget(self._notice_lbl)

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self._load_mastery()
        self._avg_secs = _avg_secs_per_card()
        self._update_estimate(self._count_spin.value())
        self._validate()            # flags may have changed on the History screen

    # ------------------------------------------------------------------
    # Notice line
    # ------------------------------------------------------------------

    def show_notice(self, text: str) -> None:
        self._notice_lbl.setText(text)
        self._notice_lbl.setVisible(bool(text))

    def clear_notice(self) -> None:
        self.show_notice("")

    def notice_text(self) -> str:
        return self._notice_lbl.text() if not self._notice_lbl.isHidden() else ""

    @staticmethod
    def _flag_count() -> int:
        try:
            from persistence.storage import load_flagged
            return len(load_flagged())
        except Exception:
            return 0

    def _load_mastery(self) -> None:
        """Compute per-category mastery from card_weights() and update UI."""
        try:
            from persistence.storage import card_weights
            weights = card_weights()
        except Exception:
            weights = {}

        # Build category → list of card ids
        cat_cards: dict[str, list[str]] = {}
        for card in all_cards():
            cat_cards.setdefault(card.category, []).append(card.id)

        for cat, bar in self._mastery_bars.items():
            ids = cat_cards.get(cat, [])
            if not ids or not weights:
                # No history — neutral styling
                bar.setValue(0)
                bar.setStyleSheet(
                    f"QProgressBar {{ background: {theme.SURFACE2}; border: none; border-radius: 2px; }}"
                    f"QProgressBar::chunk {{ background: {theme.BORDER}; border-radius: 2px; }}"
                )
                self._mastery_labels[cat].setText("–")
                continue

            card_ws = [weights.get(cid) for cid in ids if cid in weights]
            if not card_ws:
                bar.setValue(0)
                bar.setStyleSheet(
                    f"QProgressBar {{ background: {theme.SURFACE2}; border: none; border-radius: 2px; }}"
                    f"QProgressBar::chunk {{ background: {theme.BORDER}; border-radius: 2px; }}"
                )
                self._mastery_labels[cat].setText("–")
                continue

            avg_w = sum(card_ws) / len(card_ws)
            mastery = int((1.0 - avg_w) * 100)
            mastery = max(0, min(100, mastery))

            if mastery >= 70:
                chunk_color = theme.SUCCESS
            elif mastery >= 40:
                chunk_color = theme.WARNING
            else:
                chunk_color = theme.ERROR

            bar.setStyleSheet(
                f"QProgressBar {{ background: {theme.SURFACE2}; border: none; border-radius: 2px; }}"
                f"QProgressBar::chunk {{ background: {chunk_color}; border-radius: 2px; }}"
            )
            bar.setValue(mastery)
            self._mastery_labels[cat].setText(f"{mastery}%")
            self._mastery_labels[cat].setStyleSheet(
                f"font-size: 11px; color: {chunk_color};"
            )

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
        if self._flagged_cb and self._flagged_cb.isChecked():
            n = self._flag_count()
            self._start_btn.setEnabled(n > 0)
            self._start_btn.setToolTip(
                "" if n else "No flagged cards yet — reveal a card during a drill "
                             "and click “⚑ Flag for Review”."
            )
        else:
            self._start_btn.setToolTip("")
            self._start_btn.setEnabled(any(cb.isChecked() for cb in self._cbs.values()))

    def _update_estimate(self, count: int) -> None:
        if self._avg_secs is None:
            self._estimate_lbl.setText("")
            return
        total = self._avg_secs * count
        minutes = round(total / 60)
        self._estimate_lbl.setText(f"≈ {minutes} min" if minutes >= 1 else "< 1 min")

    def _on_start(self) -> None:
        self.clear_notice()
        flagged_only = self._flagged_cb.isChecked() if self._flagged_cb else False
        if flagged_only:
            if self._flag_count() == 0:
                self.show_notice("No flagged cards yet — nothing to drill.")
                self._validate()
                return
            cats = list(self._cbs.keys())
        else:
            cats = [c for c, cb in self._cbs.items() if cb.isChecked()]
            if not cats:
                return
        config = DrillConfig(
            categories=cats,
            card_count=self._count_spin.value(),
            timer_secs=self._timer_combo.currentData(),
            flagged_only=flagged_only,
        )
        self.drill_started.emit(config)
