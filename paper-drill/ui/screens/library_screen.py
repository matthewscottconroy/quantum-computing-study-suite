"""Library screen — browse and re-drill saved papers."""
from __future__ import annotations
from datetime import datetime, timezone

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import DrillConfig
from ui import theme


class LibraryScreen(QWidget):
    drill_requested = pyqtSignal(object)   # DrillConfig
    back_requested  = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Scrollable body
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        self._root = QVBoxLayout(content)
        self._root.setContentsMargins(48, 36, 48, 24)
        self._root.setSpacing(16)
        scroll.setWidget(content)

        heading = QLabel("Paper Library")
        heading.setObjectName("heading")
        self._root.addWidget(heading)

        sep = QFrame(); sep.setObjectName("separator")
        self._root.addWidget(sep)

        self._empty_lbl = QLabel(
            'No papers saved yet. Check "Save to Library" when drilling a paper.'
        )
        self._empty_lbl.setObjectName("subheading")
        self._empty_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._root.addWidget(self._empty_lbl)

        # Container for paper cards; populated on refresh()
        self._cards_widget = QWidget()
        self._cards_layout = QVBoxLayout(self._cards_widget)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(10)
        self._root.addWidget(self._cards_widget)

        self._root.addStretch()

        # Bottom bar
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

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        from persistence import load_library
        self._render(load_library())

    def _render(self, papers: list[dict]) -> None:
        # Clear existing cards
        while self._cards_layout.count():
            child = self._cards_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not papers:
            self._empty_lbl.show()
            self._cards_widget.hide()
            return

        self._empty_lbl.hide()
        self._cards_widget.show()

        for paper in papers:
            card = _PaperCard(paper)
            card.drill_requested.connect(self._on_drill)
            card.delete_requested.connect(self._on_delete)
            self._cards_layout.addWidget(card)

    def _on_drill(self, paper: dict) -> None:
        config = DrillConfig(
            paper_text=paper["text"],
            paper_title=paper["title"],
            question_count=paper.get("q_count", 5),
        )
        self.drill_requested.emit(config)

    def _on_delete(self, paper_id: str) -> None:
        from persistence import delete_paper
        delete_paper(paper_id)
        self.refresh()


# ---------------------------------------------------------------------------
# Card widget for a single paper
# ---------------------------------------------------------------------------

class _PaperCard(QFrame):
    drill_requested  = pyqtSignal(object)   # paper dict
    delete_requested = pyqtSignal(str)      # paper_id

    def __init__(self, paper: dict, parent=None) -> None:
        super().__init__(parent)
        self._paper = paper
        self.setObjectName("card")
        self._build()

    def _build(self) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(18, 14, 18, 14)
        row.setSpacing(16)

        # Text column
        info = QVBoxLayout()
        info.setSpacing(4)

        title_lbl = QLabel(self._paper.get("title", "Untitled Paper"))
        title_lbl.setStyleSheet("font-size: 14px; font-weight: bold;")
        info.addWidget(title_lbl)

        saved_at_raw = self._paper.get("saved_at", "")
        date_str = _format_date(saved_at_raw)
        q_count  = self._paper.get("q_count", 5)
        meta_lbl = QLabel(f"Saved {date_str}  ·  {q_count} questions")
        meta_lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        info.addWidget(meta_lbl)

        row.addLayout(info, 1)

        # Buttons
        drill_btn = QPushButton("Drill Again")
        drill_btn.setObjectName("accent")
        drill_btn.clicked.connect(lambda: self.drill_requested.emit(self._paper))
        row.addWidget(drill_btn)

        del_btn = QPushButton("Delete")
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._paper["id"]))
        row.addWidget(del_btn)


def _format_date(iso: str) -> str:
    """Convert an ISO-8601 UTC string to a short local date, e.g. 'May 5, 2026'."""
    if not iso:
        return "unknown date"
    try:
        dt = datetime.fromisoformat(iso)
        # Convert to local time for display
        dt = dt.astimezone()
        return dt.strftime("%b %-d, %Y")
    except Exception:
        return iso[:10]
