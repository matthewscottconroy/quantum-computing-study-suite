"""Lifetime history screen for flashcard-drill."""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui import theme


class HistoryScreen(QWidget):
    back_requested = pyqtSignal()
    flag_toggled   = pyqtSignal(str, bool)   # card_id, new_state (False after an unflag)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._flag_rows: dict[str, QWidget] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 36, 48, 24)
        root.setSpacing(24)

        title = QLabel("Drill History")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        cards_row = QHBoxLayout(); cards_row.setSpacing(16)
        self._sessions_card = _StatCard("Sessions", "0")
        self._cards_card    = _StatCard("Cards Seen", "0")
        self._known_card    = _StatCard("% Known", "—")
        for c in (self._sessions_card, self._cards_card, self._known_card):
            cards_row.addWidget(c)
        root.addLayout(cards_row)

        trend_lbl = QLabel("% Known trend (last 30 sessions)")
        trend_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(trend_lbl)

        self._trend_frame = QFrame()
        self._trend_frame.setObjectName("card")
        self._trend_frame.setFixedHeight(200)
        trend_inner = QVBoxLayout(self._trend_frame)
        trend_inner.setContentsMargins(0, 0, 0, 0)
        self._trend_slot = trend_inner
        root.addWidget(self._trend_frame)

        self._empty_lbl = QLabel("No history yet. Complete a drill session to see stats here.")
        self._empty_lbl.setObjectName("subheading")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._empty_lbl)

        # ── Flagged cards ──────────────────────────────────────────────
        flag_hdr = QHBoxLayout()
        flag_lbl = QLabel("Flagged for review")
        flag_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        flag_hdr.addWidget(flag_lbl)
        self._flag_count_lbl = QLabel("")
        self._flag_count_lbl.setStyleSheet(f"font-size: 11px; color: {theme.WARNING};")
        flag_hdr.addWidget(self._flag_count_lbl)
        flag_hdr.addStretch()
        hint = QLabel("Tick “Show Flagged Only” on the setup screen to drill just these cards.")
        hint.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        flag_hdr.addWidget(hint)
        root.addLayout(flag_hdr)

        self._flag_frame = QFrame()
        self._flag_frame.setObjectName("card")
        self._flag_frame.setMinimumHeight(72)
        self._flag_frame.setMaximumHeight(260)
        self._flag_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        flag_outer = QVBoxLayout(self._flag_frame)
        flag_outer.setContentsMargins(4, 4, 4, 4)
        self._flag_scroll = QScrollArea()
        self._flag_scroll.setWidgetResizable(True)
        self._flag_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._flag_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._flag_scroll.setStyleSheet(f"QScrollArea, QScrollArea > QWidget > QWidget {{ background: {theme.SURFACE}; }}")
        self._flag_content = QWidget()
        self._flag_layout = QVBoxLayout(self._flag_content)
        self._flag_layout.setContentsMargins(8, 6, 8, 6)
        self._flag_layout.setSpacing(2)
        self._flag_layout.addStretch()
        self._flag_scroll.setWidget(self._flag_content)
        flag_outer.addWidget(self._flag_scroll)
        self._flag_empty_lbl = QLabel("No flagged cards. Reveal a card during a drill and click “⚑ Flag for Review”.")
        self._flag_empty_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px; background: transparent;")
        self._flag_empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._flag_empty_lbl.setWordWrap(True)
        flag_outer.addWidget(self._flag_empty_lbl)
        root.addWidget(self._flag_frame, 1)

        root.addStretch()

        bar = QWidget()
        bar.setObjectName("bottom_bar")
        # Scoped to the bar itself so the rule does not cascade onto the Back button.
        bar.setStyleSheet(f"QWidget#bottom_bar {{ background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER}; }}")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(48, 12, 48, 12)
        bar_layout.addStretch()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("accent")
        back_btn.clicked.connect(self.back_requested)
        bar_layout.addWidget(back_btn)
        root.addWidget(bar)

    def refresh(self) -> None:
        from persistence.storage import _load_raw
        sessions = _load_raw()
        self._render(sessions)
        self.refresh_flagged()

    # ------------------------------------------------------------------
    # Flagged cards
    # ------------------------------------------------------------------

    def flagged_ids(self) -> list[str]:
        """Card IDs currently listed in the flagged section (sorted)."""
        return sorted(self._flag_rows)

    def refresh_flagged(self) -> None:
        """Rebuild the flagged-cards list from flagged_cards.json (newest first)."""
        try:
            from persistence.storage import load_flagged_entries
            entries = load_flagged_entries()
        except Exception:
            entries = []
        entries.sort(key=lambda e: e.get("timestamp", 0.0), reverse=True)
        ids = [e["id"] for e in entries]
        try:
            from core.deck import all_cards
            by_id = {c.id: c for c in all_cards()}
        except Exception:
            by_id = {}

        _clear_slot(self._flag_layout)
        self._flag_rows.clear()
        self._flag_layout.addStretch()

        self._flag_count_lbl.setText(f"({len(ids)})" if ids else "")
        self._flag_empty_lbl.setVisible(not ids)
        self._flag_scroll.setVisible(bool(ids))
        for cid in ids:
            row = self._make_flag_row(cid, by_id.get(cid))
            self._flag_layout.insertWidget(self._flag_layout.count() - 1, row)
            self._flag_rows[cid] = row

    def _make_flag_row(self, card_id: str, card) -> QWidget:
        row = QWidget()
        row.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(10)

        category = card.category if card is not None else "—"
        color = theme.CATEGORY_COLORS.get(category, theme.TEXT_MUTED)
        badge = QLabel(category.upper())
        badge.setFixedWidth(150)
        badge.setStyleSheet(f"font-size: 10px; font-weight: bold; color: {color}; background: transparent;")
        layout.addWidget(badge)

        if card is not None:
            text = card.front
        else:
            text = f"{card_id}  (card no longer exists — unflag to tidy up)"
        front = QLabel(text)
        front.setWordWrap(True)
        front.setToolTip(card.back if card is not None else card_id)
        front.setStyleSheet(f"font-size: 13px; color: {theme.TEXT}; background: transparent;")
        layout.addWidget(front, 1)

        unflag = QPushButton("Unflag")
        unflag.setObjectName("flat")
        unflag.setToolTip(card_id)
        unflag.clicked.connect(lambda _checked=False, cid=card_id: self._on_unflag(cid))
        layout.addWidget(unflag)
        return row

    def _on_unflag(self, card_id: str) -> None:
        try:
            from persistence.storage import toggle_flag
            new_state = toggle_flag(card_id)
        except Exception:
            return
        self.flag_toggled.emit(card_id, new_state)
        self.refresh_flagged()

    def _render(self, sessions: list[dict]) -> None:
        # A session with no rated cards carries no information (and used to
        # divide by zero in the trend); ignore any such entry in the file.
        sessions = [s for s in sessions if isinstance(s, dict) and (s.get("total") or 0) > 0]
        if not sessions:
            self._empty_lbl.show()
            self._trend_frame.hide()
            self._sessions_card.set_value("0")
            self._cards_card.set_value("0")
            self._known_card.set_value("—")
            return

        self._empty_lbl.hide()
        self._trend_frame.show()

        total_cards = sum(s.get("total", 0) for s in sessions)
        total_got   = sum(s.get("got_it", 0) for s in sessions)
        pct = total_got / total_cards * 100 if total_cards else 0

        self._sessions_card.set_value(str(len(sessions)))
        self._cards_card.set_value(str(total_cards))
        self._known_card.set_value(f"{pct:.0f}%" if total_cards else "—")

        window = sessions[-30:]
        pcts = [(s.get("got_it") or 0) / (s.get("total") or 1) * 100 for s in window]
        xs   = list(range(1, len(pcts) + 1))

        _clear_slot(self._trend_slot)
        fig, ax = plt.subplots(figsize=(8, 1.8), dpi=96)
        fig.patch.set_facecolor(theme.SURFACE)
        ax.set_facecolor(theme.SURFACE)
        ax.plot(xs, pcts, color=theme.ACCENT, linewidth=2, marker="o",
                markersize=4, markerfacecolor=theme.ACCENT2)
        ax.fill_between(xs, pcts, alpha=0.15, color=theme.ACCENT)
        ax.set_xlim(0.5, max(len(pcts) + 0.5, 5))
        ax.set_ylim(0, 105)
        ax.set_ylabel("% Known", color=theme.TEXT_MUTED, fontsize=9)
        ax.set_xlabel("Session", color=theme.TEXT_MUTED, fontsize=9)
        ax.tick_params(colors=theme.TEXT_MUTED, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(theme.BORDER)
        ax.axhline(70, color=theme.SUCCESS, linewidth=0.8, linestyle="--", alpha=0.5)
        fig.tight_layout(pad=0.4)
        canvas = FigureCanvasQTAgg(fig)
        canvas.setStyleSheet(f"background: {theme.SURFACE};")
        self._trend_slot.addWidget(canvas)
        plt.close(fig)


class _StatCard(QFrame):
    def __init__(self, label: str, value: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED}; font-weight: bold;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)
        self._val = QLabel(value)
        self._val.setStyleSheet("font-size: 26px; font-weight: bold;")
        self._val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._val)

    def set_value(self, v: str) -> None:
        self._val.setText(v)


def _clear_slot(layout) -> None:
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
