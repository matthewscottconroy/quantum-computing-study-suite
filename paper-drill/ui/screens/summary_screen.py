"""Summary screen for paper-drill session."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import SessionStats
from ui import theme


class SummaryScreen(QWidget):
    drill_again    = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 48, 48, 36)
        root.setSpacing(24)

        title = QLabel("Session Complete")
        title.setObjectName("heading")
        root.addWidget(title)

        sep = QFrame(); sep.setObjectName("separator")
        root.addWidget(sep)

        self._avg_lbl = QLabel("")
        self._avg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._avg_lbl.setStyleSheet(
            f"font-size: 52px; font-weight: bold; color: {theme.ACCENT};"
        )
        root.addWidget(self._avg_lbl)

        self._paper_lbl = QLabel("")
        self._paper_lbl.setObjectName("subheading")
        self._paper_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._paper_lbl)

        self._scores_lbl = QLabel("")
        self._scores_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scores_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        root.addWidget(self._scores_lbl)

        root.addStretch()

        btn_row = QHBoxLayout()
        back_btn = QPushButton("← New Paper")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        btn_row.addWidget(back_btn)
        btn_row.addStretch()
        again_btn = QPushButton("Drill Same Paper Again")
        again_btn.setObjectName("accent")
        again_btn.clicked.connect(self.drill_again)
        btn_row.addWidget(again_btn)
        root.addLayout(btn_row)

    def show_stats(self, stats: SessionStats) -> None:
        avg = stats.average
        color = theme.SUCCESS if avg >= 7 else (theme.WARNING if avg >= 4 else theme.ERROR)
        self._avg_lbl.setText(f"{avg:.1f}/10")
        self._avg_lbl.setStyleSheet(f"font-size: 52px; font-weight: bold; color: {color};")
        self._paper_lbl.setText(stats.title)
        score_str = "  ".join(str(s) for s in stats.scores)
        self._scores_lbl.setText(f"Scores: {score_str}")
