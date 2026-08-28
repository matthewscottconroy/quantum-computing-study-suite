"""Summary screen — session results."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import SessionStats
from ui import theme


class SummaryScreen(QWidget):
    session_again  = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 48, 48, 36)
        root.setSpacing(20)

        title = QLabel("Session Complete")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        self._avg_lbl = QLabel("")
        self._avg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._avg_lbl)

        self._sub_lbl = QLabel("")
        self._sub_lbl.setObjectName("subheading")
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._sub_lbl)

        self._rows = QVBoxLayout()
        self._rows.setSpacing(8)
        root.addLayout(self._rows)

        root.addStretch()

        btn_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        btn_row.addWidget(back_btn)
        btn_row.addStretch()
        again_btn = QPushButton("Another Session")
        again_btn.setObjectName("accent")
        again_btn.clicked.connect(self.session_again)
        btn_row.addWidget(again_btn)
        root.addLayout(btn_row)

    def show_stats(self, stats: SessionStats) -> None:
        avg = stats.avg_score
        color = (theme.SUCCESS if avg >= 7 else
                 theme.PARTIAL if avg >= 4 else theme.ERROR)
        self._avg_lbl.setText(f"{avg:.1f}/10")
        self._avg_lbl.setStyleSheet(
            f"font-size: 52px; font-weight: bold; color: {color};")
        self._sub_lbl.setText(
            f"average score across {stats.total} "
            f"{'item' if stats.total == 1 else 'items'}")

        while self._rows.count():
            item = self._rows.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for a in stats.attempts:
            row = QFrame(); row.setObjectName("card")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(16, 10, 16, 10)
            kind = QLabel(a.kind.upper())
            kind_color = (theme.TOPIC_COLORS.get("Derivation", theme.WARNING)
                          if a.kind == "derivation" else theme.ACCENT)
            kind.setStyleSheet(
                f"font-size: 10px; font-weight: bold; color: {kind_color}; min-width: 76px;")
            rl.addWidget(kind)
            name = QLabel(a.title or a.problem_id)
            name.setStyleSheet(f"font-size: 13px; color: {theme.TEXT};")
            rl.addWidget(name, 1)
            sc_color = (theme.SUCCESS if a.score >= 7 else
                        theme.PARTIAL if a.score >= 4 else theme.ERROR)
            sc = QLabel(f"{a.score:.1f}/10")
            sc.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {sc_color};")
            rl.addWidget(sc)
            self._rows.addWidget(row)
