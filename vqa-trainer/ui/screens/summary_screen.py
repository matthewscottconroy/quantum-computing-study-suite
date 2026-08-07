"""Summary screen for vqa-trainer."""
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
    review_mistakes = pyqtSignal()

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

        self._acc_lbl = QLabel("")
        self._acc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._acc_lbl.setStyleSheet(f"font-size: 52px; font-weight: bold; color: {theme.ACCENT};")
        root.addWidget(self._acc_lbl)

        self._sub_lbl = QLabel("")
        self._sub_lbl.setObjectName("subheading")
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._sub_lbl)

        self._breakdown_row = QHBoxLayout(); self._breakdown_row.setSpacing(16)
        root.addLayout(self._breakdown_row)

        root.addStretch()

        btn_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        btn_row.addWidget(back_btn)
        self._mistakes_btn = QPushButton("Review Mistakes")
        self._mistakes_btn.setObjectName("flat")
        self._mistakes_btn.clicked.connect(self.review_mistakes)
        btn_row.addWidget(self._mistakes_btn)
        btn_row.addStretch()
        again_btn = QPushButton("Another Session")
        again_btn.setObjectName("accent")
        again_btn.clicked.connect(self.session_again)
        btn_row.addWidget(again_btn)
        root.addLayout(btn_row)

    def show_stats(self, stats: SessionStats) -> None:
        acc = stats.accuracy * 100
        color = theme.SUCCESS if acc >= 70 else (theme.WARNING if acc >= 40 else theme.ERROR)
        self._acc_lbl.setText(f"{acc:.0f}%")
        self._acc_lbl.setStyleSheet(f"font-size: 52px; font-weight: bold; color: {color};")
        self._sub_lbl.setText(f"{stats.correct} of {stats.total} correct")

        while self._breakdown_row.count():
            item = self._breakdown_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cat_stats: dict[str, dict] = {}
        for a in stats.attempts:
            d = cat_stats.setdefault(a.problem.category, {"correct": 0, "total": 0})
            d["total"] += 1
            if a.score >= 7:
                d["correct"] += 1

        has_mistakes = any(a.score < 7 for a in stats.attempts)
        self._mistakes_btn.setVisible(has_mistakes)

        self._breakdown_row.addStretch()
        for cat, d in cat_stats.items():
            cat_attempts = [a for a in stats.attempts if a.problem.category == cat]
            avg_s = sum(a.score for a in cat_attempts) / len(cat_attempts) if cat_attempts else None
            card = _MiniCard(cat, d["correct"], d["total"], avg_score=avg_s)
            self._breakdown_row.addWidget(card)
        self._breakdown_row.addStretch()


class _MiniCard(QFrame):
    def __init__(self, category: str, correct: int, total: int, avg_score=None, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        color = theme.CATEGORY_COLORS.get(category, theme.ACCENT)
        name = QLabel(category)
        name.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color};")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name)

        pct = correct / total * 100 if total else 0
        score = QLabel(f"{pct:.0f}%")
        score.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {theme.TEXT};")
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(score)

        sub = QLabel(f"{correct}/{total}")
        sub.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        if avg_score is not None:
            avg_lbl = QLabel(f"avg {avg_score:.1f}")
            avg_lbl.setStyleSheet(f"font-size: 10px; color: {theme.TEXT_MUTED};")
            avg_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(avg_lbl)
