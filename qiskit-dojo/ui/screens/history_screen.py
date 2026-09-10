"""History screen for qiskit-dojo."""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg

import time

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui import theme


class HistoryScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._flag_rows: list[str] = []
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

        title = QLabel("Dojo Training History")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        cards_row = QHBoxLayout(); cards_row.setSpacing(16)
        self._sessions_card = _StatCard("Sessions", "0")
        self._katas_card    = _StatCard("Katas Attempted", "0")
        self._rate_card     = _StatCard("Lifetime Pass Rate", "—")
        for c in (self._sessions_card, self._katas_card, self._rate_card):
            cards_row.addWidget(c)
        root.addLayout(cards_row)

        trend_lbl = QLabel("Pass rate trend (last 30 sessions)")
        trend_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(trend_lbl)

        self._trend_frame = QFrame()
        self._trend_frame.setObjectName("card")
        self._trend_frame.setFixedHeight(200)
        ti = QVBoxLayout(self._trend_frame)
        ti.setContentsMargins(0, 0, 0, 0)
        self._trend_slot = ti
        root.addWidget(self._trend_frame)

        sec_lbl = QLabel("Pass rate by section (all time)")
        sec_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(sec_lbl)

        self._sec_frame = QFrame()
        self._sec_frame.setObjectName("card")
        self._sec_frame.setMinimumHeight(120)
        ci = QVBoxLayout(self._sec_frame)
        ci.setContentsMargins(0, 0, 0, 0)
        self._sec_slot = ci
        root.addWidget(self._sec_frame)

        self._empty_lbl = QLabel("No history yet. Complete a session to see stats here.")
        self._empty_lbl.setObjectName("subheading")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._empty_lbl)

        self._flag_lbl = QLabel("Flagged for review")
        self._flag_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(self._flag_lbl)

        self._flag_frame = QFrame()
        self._flag_frame.setObjectName("card")
        fl = QVBoxLayout(self._flag_frame)
        fl.setContentsMargins(16, 12, 16, 12)
        fl.setSpacing(6)
        self._flag_slot = fl
        root.addWidget(self._flag_frame)

        root.addStretch()

        bar = QWidget()
        bar.setObjectName("footer")
        # Scoped to the bar itself: an unscoped rule cascades onto the accent
        # Back button and paints it dark-on-dark with a stray top rule.
        bar.setStyleSheet(
            f"QWidget#footer {{ background: {theme.SURFACE}; "
            f"border-top: 1px solid {theme.BORDER}; }}"
        )
        self._footer = bar
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(48, 12, 48, 12)
        bl.addStretch()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("accent")
        back_btn.clicked.connect(self.back_requested)
        bl.addWidget(back_btn)
        outer.addWidget(bar)

    def refresh(self) -> None:
        from persistence import _load_raw, load_flagged
        self._render(_load_raw())
        try:
            flagged = load_flagged()
        except Exception:
            flagged = []
        self._render_flagged(flagged)

    def flagged_rows(self) -> list[str]:
        """Kata ids currently listed in the flagged card (UI state)."""
        return list(self._flag_rows)

    def _render_flagged(self, entries: list[dict]) -> None:
        _clear_slot(self._flag_slot)
        self._flag_rows = []
        self._flag_lbl.setText(f"Flagged for review ({len(entries)})")
        if not entries:
            empty = QLabel("No katas flagged. Use “⚑ Flag for review” on a kata to add it here.")
            empty.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
            empty.setWordWrap(True)
            self._flag_slot.addWidget(empty)
            return
        for e in sorted(entries, key=lambda x: _to_float(x.get("timestamp")),
                        reverse=True):
            kid = str(e.get("id", ""))
            self._flag_rows.append(kid)
            self._flag_slot.addWidget(_FlagRow(e, self._on_unflag))

    def _on_unflag(self, kata_id: str) -> None:
        from persistence import unflag, load_flagged
        try:
            unflag(kata_id)
            entries = load_flagged()
        except Exception:
            entries = []
        self._render_flagged(entries)

    def _render(self, sessions: list[dict]) -> None:
        if not sessions:
            self._empty_lbl.show()
            self._trend_frame.hide()
            self._sec_frame.hide()
            self._sessions_card.set_value("0")
            self._katas_card.set_value("0")
            self._rate_card.set_value("—")
            return

        self._empty_lbl.hide()
        self._trend_frame.show()
        self._sec_frame.show()

        total_k = sum(s.get("total", 0) for s in sessions)
        total_p = sum(s.get("passed", 0) for s in sessions)
        rate = total_p / total_k * 100 if total_k else 0

        self._sessions_card.set_value(str(len(sessions)))
        self._katas_card.set_value(str(total_k))
        self._rate_card.set_value(f"{rate:.0f}%" if total_k else "—")

        window = sessions[-30:]
        rates = [
            (s.get("passed", 0) / s.get("total", 1) * 100) if s.get("total") else 0
            for s in window
        ]
        xs = list(range(1, len(rates) + 1))

        _clear_slot(self._trend_slot)
        fig, ax = plt.subplots(figsize=(8, 1.8), dpi=96)
        fig.patch.set_facecolor(theme.SURFACE)
        ax.set_facecolor(theme.SURFACE)
        ax.plot(xs, rates, color=theme.ACCENT, linewidth=2, marker="o",
                markersize=4, markerfacecolor=theme.ACCENT2)
        ax.fill_between(xs, rates, alpha=0.15, color=theme.ACCENT)
        ax.set_xlim(0.5, max(len(rates) + 0.5, 5))
        ax.set_ylim(0, 105)
        ax.set_ylabel("Pass rate %", color=theme.TEXT_MUTED, fontsize=9)
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

        buckets: dict[str, list] = {}
        for s in sessions:
            for a in s.get("attempts", []):
                sec = a.get("section", "")
                if sec:
                    buckets.setdefault(sec, []).append(1 if a.get("passed") else 0)

        if buckets:
            secs   = list(buckets.keys())
            avgs   = [sum(v) / len(v) * 100 for v in buckets.values()]
            colors = [theme.SECTION_COLORS.get(s, theme.ACCENT) for s in secs]

            frame_h = max(120, len(secs) * 38 + 50)
            self._sec_frame.setFixedHeight(frame_h)

            _clear_slot(self._sec_slot)
            fig2, ax2 = plt.subplots(figsize=(8, frame_h / 96), dpi=96)
            fig2.patch.set_facecolor(theme.SURFACE)
            ax2.set_facecolor(theme.SURFACE)
            bars = ax2.barh(secs, avgs, color=colors, height=0.55, edgecolor="none")
            ax2.set_xlim(0, 105)
            ax2.set_xlabel("Pass rate %", color=theme.TEXT_MUTED, fontsize=9)
            ax2.tick_params(colors=theme.TEXT_MUTED, labelsize=9)
            for spine in ax2.spines.values():
                spine.set_edgecolor(theme.BORDER)
            for bar, avg in zip(bars, avgs):
                ax2.text(avg + 1, bar.get_y() + bar.get_height() / 2,
                         f"{avg:.0f}%", va="center", color=theme.TEXT, fontsize=9)
            fig2.tight_layout(pad=0.5)
            canvas2 = FigureCanvasQTAgg(fig2)
            canvas2.setStyleSheet(f"background: {theme.SURFACE};")
            self._sec_slot.addWidget(canvas2)
            plt.close(fig2)


class _FlagRow(QWidget):
    """One flagged kata: section badge, title, when flagged, Unflag button."""

    def __init__(self, entry: dict, on_unflag, parent=None) -> None:
        super().__init__(parent)
        kid      = str(entry.get("id", ""))
        label    = str(entry.get("label") or kid)
        section  = str(entry.get("category", ""))
        ts       = entry.get("timestamp") or 0
        color    = theme.SECTION_COLORS.get(section, theme.ACCENT)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        badge = QLabel(section or "—")
        badge.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {color}; "
            f"border: 1px solid {color}; border-radius: 9px; padding: 1px 10px;"
        )
        row.addWidget(badge)

        title = QLabel(label)
        title.setStyleSheet(f"font-size: 13px; color: {theme.TEXT};")
        title.setToolTip(kid)
        row.addWidget(title, 1)

        try:
            when = time.strftime("%Y-%m-%d", time.localtime(float(ts))) if ts else ""
        except (TypeError, ValueError, OverflowError, OSError):
            when = ""
        meta = QLabel(f"{kid}  ·  {when}" if when else kid)
        meta.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        row.addWidget(meta)

        btn = QPushButton("Unflag")
        btn.setObjectName("flat")
        btn.clicked.connect(lambda _=False, k=kid: on_unflag(k))
        row.addWidget(btn)


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


def _to_float(value) -> float:
    """Epoch timestamp as float; a hand-edited or foreign value sorts as 0.0
    instead of raising TypeError halfway through refresh()."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _clear_slot(layout) -> None:
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()
