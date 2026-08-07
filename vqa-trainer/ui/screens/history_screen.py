"""History screen for vqa-trainer."""
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

        title = QLabel("VQA Training History")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        cards_row = QHBoxLayout(); cards_row.setSpacing(16)
        self._sessions_card  = _StatCard("Sessions", "0")
        self._problems_card  = _StatCard("Problems", "0")
        self._accuracy_card  = _StatCard("Lifetime Accuracy", "—")
        for c in (self._sessions_card, self._problems_card, self._accuracy_card):
            cards_row.addWidget(c)
        root.addLayout(cards_row)

        trend_lbl = QLabel("Accuracy trend (last 30 sessions)")
        trend_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(trend_lbl)

        self._trend_frame = QFrame()
        self._trend_frame.setObjectName("card")
        self._trend_frame.setFixedHeight(200)
        ti = QVBoxLayout(self._trend_frame)
        ti.setContentsMargins(0, 0, 0, 0)
        self._trend_slot = ti
        root.addWidget(self._trend_frame)

        cat_lbl = QLabel("Accuracy by topic (all time)")
        cat_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(cat_lbl)

        self._cat_frame = QFrame()
        self._cat_frame.setObjectName("card")
        self._cat_frame.setMinimumHeight(120)
        ci = QVBoxLayout(self._cat_frame)
        ci.setContentsMargins(0, 0, 0, 0)
        self._cat_slot = ci
        root.addWidget(self._cat_frame)

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
            self._cat_frame.hide()
            self._sessions_card.set_value("0")
            self._problems_card.set_value("0")
            self._accuracy_card.set_value("—")
            return

        self._empty_lbl.hide()
        self._trend_frame.show()
        self._cat_frame.show()

        total_p = sum(s.get("total", 0) for s in sessions)
        total_c = sum(s.get("correct", 0) for s in sessions)
        acc = total_c / total_p * 100 if total_p else 0

        self._sessions_card.set_value(str(len(sessions)))
        self._problems_card.set_value(str(total_p))
        self._accuracy_card.set_value(f"{acc:.0f}%" if total_p else "—")

        window = sessions[-30:]
        accs = [s.get("accuracy", 0) * 100 for s in window]
        xs   = list(range(1, len(accs) + 1))

        _clear_slot(self._trend_slot)
        fig, ax = plt.subplots(figsize=(8, 1.8), dpi=96)
        fig.patch.set_facecolor(theme.SURFACE)
        ax.set_facecolor(theme.SURFACE)
        ax.plot(xs, accs, color=theme.ACCENT, linewidth=2, marker="o",
                markersize=4, markerfacecolor=theme.ACCENT2)
        ax.fill_between(xs, accs, alpha=0.15, color=theme.ACCENT)
        ax.set_xlim(0.5, max(len(accs) + 0.5, 5))
        ax.set_ylim(0, 105)
        ax.set_ylabel("Accuracy %", color=theme.TEXT_MUTED, fontsize=9)
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
                cat = a.get("category", "")
                if cat:
                    buckets.setdefault(cat, []).append(1 if a.get("score", 0) >= 7 else 0)

        if buckets:
            cats   = list(buckets.keys())
            avgs   = [sum(v) / len(v) * 100 for v in buckets.values()]
            colors = [theme.CATEGORY_COLORS.get(c, theme.ACCENT) for c in cats]

            frame_h = max(120, len(cats) * 38 + 50)
            self._cat_frame.setFixedHeight(frame_h)

            _clear_slot(self._cat_slot)
            fig2, ax2 = plt.subplots(figsize=(8, frame_h / 96), dpi=96)
            fig2.patch.set_facecolor(theme.SURFACE)
            ax2.set_facecolor(theme.SURFACE)
            bars = ax2.barh(cats, avgs, color=colors, height=0.55, edgecolor="none")
            ax2.set_xlim(0, 105)
            ax2.set_xlabel("Accuracy %", color=theme.TEXT_MUTED, fontsize=9)
            ax2.tick_params(colors=theme.TEXT_MUTED, labelsize=9)
            for spine in ax2.spines.values():
                spine.set_edgecolor(theme.BORDER)
            for bar, avg in zip(bars, avgs):
                ax2.text(avg + 1, bar.get_y() + bar.get_height() / 2,
                         f"{avg:.0f}%", va="center", color=theme.TEXT, fontsize=9)
            fig2.tight_layout(pad=0.5)
            canvas2 = FigureCanvasQTAgg(fig2)
            canvas2.setStyleSheet(f"background: {theme.SURFACE};")
            self._cat_slot.addWidget(canvas2)
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
