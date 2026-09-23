"""Setup screen — the daily pull, session mode, categories, card count, timer."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QPushButton, QSpinBox, QComboBox, QFrame, QProgressBar, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import DrillConfig
from core.deck import all_categories, all_cards
from core.scheduler import DueSummary, describe_due, summarise
from config import DEFAULT_CARD_COUNT, DEFAULT_TIMER_SECS
from ui import theme

MODE_DUE  = "due"
MODE_FREE = "free"

_MODE_OPTIONS = [
    ("Due today — spaced repetition", MODE_DUE),
    ("Free drill — weighted mix",     MODE_FREE),
]

_TIMER_OPTIONS = [
    ("No timer", 0),
    ("10 seconds", 10),
    ("20 seconds", 20),
    ("30 seconds", 30),
    ("60 seconds", 60),
]


def _confidence_pref() -> bool:
    """Is the card screen's confidence strip switched on?  Defaults to yes."""
    try:
        from persistence.review_store import confidence_enabled
        return confidence_enabled()
    except Exception:
        return True


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
        self._mode_combo: QComboBox | None = None
        self._avg_secs: float | None = _avg_secs_per_card()
        self._all_cards = all_cards()          # card bank is static for the session
        self._due = DueSummary(total=len(self._all_cards), new=len(self._all_cards))
        self._mode_touched = False             # user picked a mode: stop auto-selecting
        self._suspend_refresh = True           # no schedule reads while building the UI
        self._build_ui()
        self._suspend_refresh = False
        self._refresh_due()
        self._auto_select_mode()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 40, 48, 36)
        root.setSpacing(20)

        title = QLabel("Flashcard Drill")
        title.setObjectName("heading")
        sub = QLabel("Rapid-fire quantum computing facts — SM-2 scheduled, "
                     "so each card comes back exactly when you are about to forget it.")
        sub.setObjectName("subheading")
        root.addWidget(title)
        root.addWidget(sub)

        root.addWidget(self._build_due_banner())

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        # The two option columns scroll: 14 categories, the daily pull and the
        # session cards do not fit the 800x600 minimum window, and a squeezed
        # column used to overlap its own rows.
        content_host = QWidget()
        content = QHBoxLayout(content_host)
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(32)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(content_host)
        root.addWidget(scroll, 1)

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

        mode_card = self._card("Session mode")
        self._mode_combo = QComboBox()
        for label, val in _MODE_OPTIONS:
            self._mode_combo.addItem(label, val)
        self._mode_combo.setCurrentIndex(1)                  # free drill until a schedule exists
        self._mode_combo.activated.connect(self._on_mode_picked)
        self._mode_combo.currentIndexChanged.connect(lambda _: self._validate())
        mode_card.layout().addWidget(self._mode_combo)
        self._mode_hint = QLabel("")
        self._mode_hint.setWordWrap(True)
        self._mode_hint.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        mode_card.layout().addWidget(self._mode_hint)
        right.addWidget(mode_card)

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

        feedback_card = self._card("Self-assessment")
        self._confidence_cb = QCheckBox("Ask my confidence before each reveal")
        self._confidence_cb.setObjectName("conf_pref")
        self._confidence_cb.setChecked(_confidence_pref())
        self._confidence_cb.setAccessibleName("Ask my confidence before each reveal")
        self._confidence_cb.setToolTip(
            "A 1-4 strip on the card front, before the answer can be seen — it is "
            "what separates “right” from “right and knew it”.")
        self._confidence_cb.stateChanged.connect(self._on_confidence_pref_toggled)
        feedback_card.layout().addWidget(self._confidence_cb)
        conf_hint = QLabel(
            "Missed cards are also journalled: a skippable “what went wrong?” row "
            "records the cause (misread / didn’t know / knew but slipped / …) so the "
            "pattern shows up, not just the card.  Your SM-2 schedule is unaffected."
        )
        conf_hint.setWordWrap(True)
        conf_hint.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        feedback_card.layout().addWidget(conf_hint)
        right.addWidget(feedback_card)

        tip_card = self._card("How it works")
        tip = QLabel(
            "Reveal the answer (Space), then rate yourself:\n\n"
            "  1  Got it — knew it cold\n"
            "  2  Unsure — partial recall\n"
            "  3  Missed — didn't know\n\n"
            "Every rating reschedules the card with SM-2: Got it pushes it out "
            "(1 → 6 → 15 → 37 → 92 days), Unsure stretches it a little, "
            "Missed brings it back tomorrow."
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
        if getattr(self, "_confidence_cb", None) is not None:
            # "Don't ask" on the card screen writes the same setting.
            self._confidence_cb.blockSignals(True)
            self._confidence_cb.setChecked(_confidence_pref())
            self._confidence_cb.blockSignals(False)
        self._load_mastery()
        self._avg_secs = _avg_secs_per_card()
        self._update_estimate(self._count_spin.value())
        self._refresh_due()         # a finished session moves due dates
        self._auto_select_mode()
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

    # ------------------------------------------------------------------
    # Daily pull (SM-2)
    # ------------------------------------------------------------------

    def _build_due_banner(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        row = QHBoxLayout(frame)
        row.setContentsMargins(16, 10, 16, 10)
        row.setSpacing(16)

        col = QVBoxLayout()
        col.setSpacing(2)
        self._due_lbl = QLabel("")
        self._due_lbl.setStyleSheet(
            f"font-size: 18px; font-weight: bold; color: {theme.ACCENT};")
        col.addWidget(self._due_lbl)
        self._due_sub_lbl = QLabel("")
        self._due_sub_lbl.setWordWrap(True)
        self._due_sub_lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        col.addWidget(self._due_sub_lbl)
        row.addLayout(col, 1)

        self._due_btn = QPushButton("Review Due Cards")
        self._due_btn.setObjectName("accent")
        self._due_btn.setToolTip("Draw today's due cards, oldest first")
        self._due_btn.clicked.connect(self._on_start_due)
        self._due_btn.hide()
        row.addWidget(self._due_btn)
        return frame

    @property
    def mode(self) -> str:
        """``MODE_DUE`` or ``MODE_FREE`` — the selected session mode."""
        if self._mode_combo is None:
            return MODE_FREE
        return self._mode_combo.currentData() or MODE_FREE

    @property
    def due_summary(self) -> DueSummary:
        """Last computed due/new counts for the selected categories."""
        return self._due

    def _set_mode(self, mode: str) -> None:
        if self._mode_combo is None:
            return
        idx = self._mode_combo.findData(mode)
        if idx >= 0 and idx != self._mode_combo.currentIndex():
            self._mode_combo.setCurrentIndex(idx)

    def _on_mode_picked(self, _index: int) -> None:
        self._mode_touched = True       # respect the choice from here on
        self._validate()

    def _selected_card_ids(self) -> list[str]:
        cats = {c for c, cb in self._cbs.items() if cb.isChecked()}
        return [c.id for c in self._all_cards if c.category in cats]

    def _refresh_due(self) -> None:
        """Recompute the daily pull and repaint the banner.

        Reentrancy-guarded: changing the mode combo re-enters ``_validate``.
        """
        if self._suspend_refresh:
            return
        self._suspend_refresh = True
        try:
            try:
                from persistence.schedule_store import ensure_states
                states = ensure_states()
            except Exception:
                states = {}
            self._due = summarise(states, self._selected_card_ids())
            self._paint_due_banner()
        finally:
            self._suspend_refresh = False

    def _auto_select_mode(self) -> None:
        """Offer today's pull when there is one; otherwise the classic free drill.

        Only ever runs while the user has not picked a mode by hand, and never
        from inside ``_validate`` — selecting "Due today" with nothing due must
        not bounce straight back to "Free drill".
        """
        if self._mode_touched:
            return
        self._set_mode(MODE_DUE if self._due.due > 0 else MODE_FREE)

    def _paint_due_banner(self) -> None:
        d = self._due
        flagged = bool(self._flagged_cb and self._flagged_cb.isChecked())
        bits = [f"{d.scheduled} scheduled", f"{d.new} new", f"{d.total} in scope"]
        if not d.total:
            self._due_lbl.setText("No categories selected")
            self._due_lbl.setStyleSheet(
                f"font-size: 18px; font-weight: bold; color: {theme.TEXT_MUTED};")
            self._due_sub_lbl.setText("Tick a category to see what is due.")
            self._due_btn.hide()
            return
        if d.due:
            self._due_lbl.setText(f"{d.due} card{'' if d.due == 1 else 's'} due today")
            self._due_lbl.setStyleSheet(
                f"font-size: 18px; font-weight: bold; color: {theme.ACCENT};")
            if d.overdue:
                bits.insert(0, f"{d.overdue} overdue")
        elif d.scheduled:
            self._due_lbl.setText("Nothing due today")
            self._due_lbl.setStyleSheet(
                f"font-size: 18px; font-weight: bold; color: {theme.SUCCESS};")
            bits.insert(0, f"next review {describe_due(d.next_due)}")
        else:
            self._due_lbl.setText("No review schedule yet")
            self._due_lbl.setStyleSheet(
                f"font-size: 18px; font-weight: bold; color: {theme.TEXT_MUTED};")
            bits = ["rate a few cards and SM-2 starts scheduling them"] + bits[1:]
        self._due_sub_lbl.setText("  ·  ".join(bits))
        self._due_btn.setVisible(bool(d.due) and not flagged)

    def _on_start_due(self) -> None:
        self._mode_touched = True
        self._set_mode(MODE_DUE)
        self._on_start()

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
        self._suspend_refresh = True
        try:
            for cb in self._cbs.values():
                cb.setChecked(val)
        finally:
            self._suspend_refresh = False
        self._validate()

    def _on_confidence_pref_toggled(self) -> None:
        """Persist the opt-out the card screen's “Don't ask” button also writes."""
        try:
            from persistence.review_store import set_confidence_enabled
            set_confidence_enabled(self._confidence_cb.isChecked())
        except Exception:
            pass        # the preference simply stays as it was on disk

    def _on_flagged_toggled(self) -> None:
        flagged = self._flagged_cb.isChecked()
        for cb in self._cbs.values():
            cb.setEnabled(not flagged)
        if self._mode_combo is not None:
            self._mode_combo.setEnabled(not flagged)   # flagged-only ignores the schedule
        self._validate()

    def _validate(self) -> None:
        self._refresh_due()
        if self._flagged_cb and self._flagged_cb.isChecked():
            n = self._flag_count()
            self._start_btn.setEnabled(n > 0)
            self._start_btn.setToolTip(
                "" if n else "No flagged cards yet — reveal a card during a drill "
                             "and click “⚑ Flag for Review”."
            )
            self._set_mode_hint("Flagged-only ignores the schedule and drills every flag.")
            return

        any_cat = any(cb.isChecked() for cb in self._cbs.values())
        if self.mode == MODE_DUE:
            d = self._due
            self._start_btn.setEnabled(any_cat and d.available > 0)
            self._start_btn.setToolTip(
                "" if d.available else
                f"Nothing due and no new cards left — next review {describe_due(d.next_due)}."
            )
            if d.due and d.new:
                hint = (f"Draws the {d.due} due card(s) oldest-first, then fills up "
                        f"with new cards.")
            elif d.due:
                hint = f"Draws the {d.due} due card(s), oldest first."
            elif d.new:
                hint = (f"Nothing due — draws new cards only "
                        f"(next review {describe_due(d.next_due)}).")
            else:
                hint = f"Nothing due and nothing new — next review {describe_due(d.next_due)}."
            self._set_mode_hint(hint)
        else:
            self._start_btn.setToolTip("")
            self._start_btn.setEnabled(any_cat)
            self._set_mode_hint("Weighted sampling — recently missed cards come up more "
                                "often.  Ratings still update the SM-2 schedule.")

    def _set_mode_hint(self, text: str) -> None:
        if getattr(self, "_mode_hint", None) is not None:
            self._mode_hint.setText(text)

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
            due_only=(not flagged_only) and self.mode == MODE_DUE,
        )
        self.drill_started.emit(config)
