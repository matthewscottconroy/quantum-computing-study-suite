"""Post-session summary screen."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGridLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import SessionStats, Rating
from ui import theme


class SummaryScreen(QWidget):
    drill_again    = pyqtSignal()
    back_requested = pyqtSignal()
    review_missed  = pyqtSignal()

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

        self._score_lbl = QLabel("")
        self._score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._score_lbl.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {theme.ACCENT};")
        root.addWidget(self._score_lbl)

        self._sub_lbl = QLabel("")
        self._sub_lbl.setObjectName("subheading")
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self._sub_lbl)

        # Breakdown row (mini-cards)
        self._breakdown = QHBoxLayout(); self._breakdown.setSpacing(16)
        root.addLayout(self._breakdown)

        # Per-category detail table
        self._cat_frame = QFrame()
        self._cat_frame.setObjectName("card")
        self._cat_layout = QVBoxLayout(self._cat_frame)
        self._cat_layout.setContentsMargins(16, 12, 16, 12)
        self._cat_layout.setSpacing(0)
        root.addWidget(self._cat_frame)

        root.addStretch()

        btn_row = QHBoxLayout()
        back_btn = QPushButton("← Back to Setup")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)
        btn_row.addWidget(back_btn)
        self._missed_review_btn = QPushButton("Review Missed")
        self._missed_review_btn.setObjectName("flat")
        self._missed_review_btn.clicked.connect(self.review_missed)
        btn_row.addWidget(self._missed_review_btn)
        btn_row.addStretch()
        again_btn = QPushButton("Drill Again")
        again_btn.setObjectName("accent")
        again_btn.clicked.connect(self.drill_again)
        btn_row.addWidget(again_btn)
        root.addLayout(btn_row)

    def show_stats(self, stats: SessionStats) -> None:
        has_missed = stats.missed > 0
        self._missed_review_btn.setVisible(has_missed)

        pct = stats.pct_known * 100
        self._score_lbl.setText(f"{pct:.0f}%")
        color = theme.SUCCESS if pct >= 70 else (theme.WARNING if pct >= 40 else theme.ERROR)
        self._score_lbl.setStyleSheet(f"font-size: 48px; font-weight: bold; color: {color};")
        self._sub_lbl.setText(
            f"{stats.got_it} of {stats.total} cards known cold  |  "
            f"{stats.unsure} unsure  |  {stats.missed} missed"
        )

        # Clear and rebuild breakdown
        while self._breakdown.count():
            item = self._breakdown.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Per-category aggregation
        cat_counts: dict[str, dict] = {}
        for r in stats.results:
            d = cat_counts.setdefault(r.category, {"got": 0, "unsure": 0, "missed": 0, "total": 0})
            d["total"] += 1
            if r.rating == Rating.GOT_IT:
                d["got"] += 1
            elif r.rating == Rating.UNSURE:
                d["unsure"] += 1
            elif r.rating == Rating.MISSED:
                d["missed"] += 1

        # Mini-card row
        self._breakdown.addStretch()
        for cat, d in cat_counts.items():
            card = _MiniCard(cat, d["got"], d["total"])
            self._breakdown.addWidget(card)
        self._breakdown.addStretch()

        # Category detail table — clear and rebuild
        while self._cat_layout.count():
            item = self._cat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if cat_counts:
            # Header row
            header_grid = QGridLayout()
            header_grid.setContentsMargins(0, 0, 0, 6)
            header_grid.setSpacing(8)
            for col, (text, align) in enumerate([
                ("Category", Qt.AlignmentFlag.AlignLeft),
                ("Got It",   Qt.AlignmentFlag.AlignCenter),
                ("Unsure",   Qt.AlignmentFlag.AlignCenter),
                ("Missed",   Qt.AlignmentFlag.AlignCenter),
            ]):
                lbl = QLabel(text)
                lbl.setAlignment(align | Qt.AlignmentFlag.AlignVCenter)
                lbl.setStyleSheet(
                    f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
                )
                header_grid.addWidget(lbl, 0, col)
            header_grid.setColumnStretch(0, 3)
            header_grid.setColumnStretch(1, 1)
            header_grid.setColumnStretch(2, 1)
            header_grid.setColumnStretch(3, 1)

            header_widget = QWidget()
            header_widget.setLayout(header_grid)
            self._cat_layout.addWidget(header_widget)

            sep = QFrame(); sep.setObjectName("separator")
            self._cat_layout.addWidget(sep)

            for cat, d in cat_counts.items():
                row_grid = QGridLayout()
                row_grid.setContentsMargins(0, 6, 0, 6)
                row_grid.setSpacing(8)
                row_grid.setColumnStretch(0, 3)
                row_grid.setColumnStretch(1, 1)
                row_grid.setColumnStretch(2, 1)
                row_grid.setColumnStretch(3, 1)

                cat_color = theme.CATEGORY_COLORS.get(cat, theme.ACCENT)
                cat_lbl = QLabel(cat)
                cat_lbl.setStyleSheet(
                    f"font-size: 13px; font-weight: bold; color: {cat_color};"
                )
                row_grid.addWidget(cat_lbl, 0, 0)

                for col, (val, color) in enumerate([
                    (d["got"],    theme.SUCCESS),
                    (d["unsure"], theme.WARNING),
                    (d["missed"], theme.ERROR),
                ], start=1):
                    num_lbl = QLabel(str(val))
                    num_lbl.setAlignment(
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                    )
                    num_lbl.setStyleSheet(
                        f"font-size: 13px; font-weight: bold; color: {color};"
                    )
                    row_grid.addWidget(num_lbl, 0, col)

                row_widget = QWidget()
                row_widget.setLayout(row_grid)
                self._cat_layout.addWidget(row_widget)

        self._cat_frame.setVisible(bool(cat_counts))


class _MiniCard(QFrame):
    def __init__(self, category: str, got: int, total: int, parent=None) -> None:
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

        pct = got / total * 100 if total else 0
        score = QLabel(f"{pct:.0f}%")
        score.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {theme.TEXT};")
        score.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(score)

        sub = QLabel(f"{got}/{total}")
        sub.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)
