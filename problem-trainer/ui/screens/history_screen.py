"""History screen — past sessions from problems_history.json."""
from __future__ import annotations
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui import theme


class _StatCard(QFrame):
    def __init__(self, title: str, value: str, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        t = QLabel(title)
        t.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(t)
        self._value = QLabel(value)
        self._value.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {theme.TEXT};")
        self._value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._value)

    def set_value(self, v: str) -> None:
        self._value.setText(v)


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
        root.setSpacing(20)
        scroll.setWidget(content)

        title = QLabel("Problem Trainer History")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        cards = QHBoxLayout(); cards.setSpacing(16)
        self._sessions_card = _StatCard("Sessions", "0")
        self._items_card    = _StatCard("Problems + Derivations", "0")
        self._avg_card      = _StatCard("Lifetime Avg Score", "—")
        for c in (self._sessions_card, self._items_card, self._avg_card):
            cards.addWidget(c)
        root.addLayout(cards)

        list_lbl = QLabel("Recent sessions")
        list_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(list_lbl)

        self._sessions_box = QVBoxLayout()
        self._sessions_box.setSpacing(8)
        root.addLayout(self._sessions_box)

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
        from persistence import load_history
        self._render(load_history())

    def _render(self, sessions: list[dict]) -> None:
        while self._sessions_box.count():
            item = self._sessions_box.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not sessions:
            self._empty_lbl.show()
            self._sessions_card.set_value("0")
            self._items_card.set_value("0")
            self._avg_card.set_value("—")
            return

        self._empty_lbl.hide()
        total_items = sum(s.get("total", 0) for s in sessions)
        weighted = sum(s.get("avg_score", 0.0) * s.get("total", 0) for s in sessions)
        lifetime_avg = weighted / total_items if total_items else 0.0

        self._sessions_card.set_value(str(len(sessions)))
        self._items_card.set_value(str(total_items))
        self._avg_card.set_value(f"{lifetime_avg:.1f}/10")

        for s in reversed(sessions[-20:]):
            row = QFrame(); row.setObjectName("card")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(16, 10, 16, 10)

            ts = s.get("timestamp")
            when = (time.strftime("%Y-%m-%d %H:%M", time.localtime(ts))
                    if isinstance(ts, (int, float)) else "—")
            when_lbl = QLabel(when)
            when_lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
            rl.addWidget(when_lbl)

            attempts = s.get("attempts", [])
            n_prob  = sum(1 for a in attempts if a.get("kind") == "problem")
            n_deriv = sum(1 for a in attempts if a.get("kind") == "derivation")
            desc = []
            if n_prob:
                desc.append(f"{n_prob} problem{'s' if n_prob != 1 else ''}")
            if n_deriv:
                desc.append(f"{n_deriv} derivation{'s' if n_deriv != 1 else ''}")
            desc_lbl = QLabel(", ".join(desc) or f"{s.get('total', 0)} items")
            desc_lbl.setStyleSheet(f"font-size: 13px; color: {theme.TEXT};")
            rl.addWidget(desc_lbl, 1)

            avg = s.get("avg_score", 0.0)
            color = (theme.SUCCESS if avg >= 7 else
                     theme.PARTIAL if avg >= 4 else theme.ERROR)
            avg_lbl = QLabel(f"{avg:.1f}/10")
            avg_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {color};")
            rl.addWidget(avg_lbl)
            self._sessions_box.addWidget(row)
