"""History screen for qiskit-dojo."""
from __future__ import annotations
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

        root.addStretch()

        bar = QWidget()
        bar.setStyleSheet(f"background: {theme.SURFACE}; border-top: 1px solid {theme.BORDER};")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(48, 12, 48, 12)
        bl.addStretch()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("accent")
        back_btn.clicked.connect(self.back_requested)
        bl.addWidget(back_btn)
        outer.addWidget(bar)

    def refresh(self) -> None:
        from persistence import _load_raw
        self._render(_load_raw())

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
