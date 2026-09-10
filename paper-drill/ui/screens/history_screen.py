"""History screen for paper-drill — session stats, score trend, and the
flagged-for-review list (with unflag)."""
from __future__ import annotations
from datetime import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui import theme


class HistoryScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
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
        root.setSpacing(24)
        scroll.setWidget(content)

        title = QLabel("Paper Drill History")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        cards_row = QHBoxLayout(); cards_row.setSpacing(16)
        self._sessions_card = _StatCard("Sessions", "0")
        self._papers_card   = _StatCard("Papers", "0")
        self._avg_card      = _StatCard("Lifetime Avg", "—")
        for c in (self._sessions_card, self._papers_card, self._avg_card):
            cards_row.addWidget(c)
        root.addLayout(cards_row)

        trend_lbl = QLabel("Average score trend (last 30 sessions)")
        trend_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(trend_lbl)

        self._trend_frame = QFrame()
        self._trend_frame.setObjectName("card")
        self._trend_frame.setFixedHeight(200)
        trend_inner = QVBoxLayout(self._trend_frame)
        trend_inner.setContentsMargins(0, 0, 0, 0)
        self._trend_slot = trend_inner
        root.addWidget(self._trend_frame)

        self._empty_lbl = QLabel("No history yet. Complete a session to see stats here.")
        self._empty_lbl.setObjectName("subheading")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._empty_lbl)

        # Flagged-for-review section — populated by refresh(); hidden when empty
        self._flag_section = QWidget()
        flag_layout = QVBoxLayout(self._flag_section)
        flag_layout.setContentsMargins(0, 0, 0, 0)
        flag_layout.setSpacing(10)
        flag_hdr = QLabel("Flagged for review")
        flag_hdr.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        flag_layout.addWidget(flag_hdr)
        self._flag_list = QVBoxLayout()
        self._flag_list.setSpacing(8)
        flag_layout.addLayout(self._flag_list)
        root.addWidget(self._flag_section)
        self._flag_section.hide()

        root.addStretch()

        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bar_layout = QHBoxLayout(bar)
        bar_layout.setContentsMargins(48, 12, 48, 12)
        bar_layout.addStretch()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("accent")
        back_btn.clicked.connect(self.back_requested)
        bar_layout.addWidget(back_btn)
        outer.addWidget(bar)

    def refresh(self) -> None:
        from persistence import _load_raw, load_flagged
        self._render(_load_raw())
        self._render_flagged(load_flagged())

    # ------------------------------------------------------------------
    # Flagged-for-review list
    # ------------------------------------------------------------------

    def flagged_count(self) -> int:
        """Number of flagged rows currently shown."""
        return self._flag_list.count()

    def _render_flagged(self, entries: list[dict]) -> None:
        _clear_slot(self._flag_list)
        if not entries:
            self._flag_section.hide()
            return
        self._flag_section.show()
        newest_first = sorted(entries, key=_flag_timestamp, reverse=True)
        for entry in newest_first:
            row = _FlaggedRow(entry)
            row.unflag_requested.connect(self._on_unflag)
            self._flag_list.addWidget(row)

    def _on_unflag(self, flag_id: str) -> None:
        from persistence import unflag, load_flagged
        unflag(flag_id)
        self._render_flagged(load_flagged())

    def _render(self, sessions: list[dict]) -> None:
        if not sessions:
            self._empty_lbl.show()
            self._trend_frame.hide()
            for c in (self._sessions_card, self._papers_card, self._avg_card):
                c.set_value("0" if c is not self._avg_card else "—")
            return

        self._empty_lbl.hide()
        self._trend_frame.show()

        papers = len({s.get("title", "") for s in sessions})
        all_avgs = [s["average"] for s in sessions if s.get("total", 0) > 0]
        lifetime = sum(all_avgs) / len(all_avgs) if all_avgs else 0.0

        self._sessions_card.set_value(str(len(sessions)))
        self._papers_card.set_value(str(papers))
        self._avg_card.set_value(f"{lifetime:.1f}/10" if all_avgs else "—")

        window = sessions[-30:]
        avgs = [s.get("average", 0) for s in window]
        xs   = list(range(1, len(avgs) + 1))

        _clear_slot(self._trend_slot)
        fig, ax = plt.subplots(figsize=(8, 1.8), dpi=96)
        fig.patch.set_facecolor(theme.SURFACE)
        ax.set_facecolor(theme.SURFACE)
        ax.plot(xs, avgs, color=theme.ACCENT, linewidth=2, marker="o",
                markersize=4, markerfacecolor=theme.ACCENT2)
        ax.fill_between(xs, avgs, alpha=0.15, color=theme.ACCENT)
        ax.set_xlim(0.5, max(len(avgs) + 0.5, 5))
        ax.set_ylim(0, 10.5)
        ax.set_ylabel("Avg score", color=theme.TEXT_MUTED, fontsize=9)
        ax.set_xlabel("Session", color=theme.TEXT_MUTED, fontsize=9)
        ax.tick_params(colors=theme.TEXT_MUTED, labelsize=8)
        for spine in ax.spines.values():
            spine.set_edgecolor(theme.BORDER)
        ax.axhline(7, color=theme.SUCCESS, linewidth=0.8, linestyle="--", alpha=0.5)
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


class _FlaggedRow(QFrame):
    """One flagged question: label, paper title, and an Unflag button."""
    unflag_requested = pyqtSignal(str)   # flag id

    def __init__(self, entry: dict, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self._id = str(entry.get("id", ""))
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 12, 18, 12)
        row.setSpacing(16)

        info = QVBoxLayout()
        info.setSpacing(3)
        label = QLabel(str(entry.get("label", "")) or self._id)
        label.setWordWrap(True)
        label.setStyleSheet("font-size: 13px; font-weight: bold;")
        info.addWidget(label)
        category = str(entry.get("category", "")).strip()
        meta = QLabel(f"Paper: {category}" if category else "Paper: —")
        meta.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        info.addWidget(meta)
        row.addLayout(info, 1)

        self._unflag_btn = QPushButton("Unflag")
        self._unflag_btn.clicked.connect(lambda: self.unflag_requested.emit(self._id))
        row.addWidget(self._unflag_btn)

    @property
    def flag_id(self) -> str:
        return self._id


def _flag_timestamp(entry: dict) -> float:
    """Sort key for flagged entries: coerce the contract ``timestamp`` to epoch
    seconds, tolerating numeric strings and ISO-8601 (other tools may write
    those); anything unusable sorts as 0.0 rather than raising mid-render."""
    value = entry.get("timestamp", 0)
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        text = value.strip()
        try:
            return float(text)
        except ValueError:
            pass
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00")).timestamp()
        except ValueError:
            pass
    return 0.0


def _clear_slot(layout) -> None:
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
