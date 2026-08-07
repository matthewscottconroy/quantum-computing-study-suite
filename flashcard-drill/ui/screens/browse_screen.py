"""Browse / Study Mode screen — read-only view of all flashcards by category."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QComboBox, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.deck import all_cards
from ui import theme


class BrowseScreen(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._card_entries: list[tuple[str, QFrame]] = []  # (category, widget)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Top bar
        top_bar = QWidget()
        top_bar.setStyleSheet(f"background-color: {theme.SURFACE}; border-bottom: 1px solid {theme.BORDER};")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(24, 12, 24, 12)
        top_layout.setSpacing(16)

        title_lbl = QLabel("Browse Cards")
        title_lbl.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {theme.TEXT};")

        self._cat_filter = QComboBox()
        self._cat_filter.addItem("All Categories", None)
        self._cat_filter.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        self._cat_filter.currentIndexChanged.connect(self._on_filter_changed)

        back_btn = QPushButton("← Back")
        back_btn.setObjectName("flat")
        back_btn.clicked.connect(self.back_requested)

        top_layout.addWidget(title_lbl)
        top_layout.addStretch()
        top_layout.addWidget(self._cat_filter)
        top_layout.addStretch()
        top_layout.addWidget(back_btn)

        root.addWidget(top_bar)

        # Scroll area
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._content = QWidget()
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(32, 24, 32, 24)
        self._content_layout.setSpacing(10)
        self._content_layout.addStretch()

        self._scroll.setWidget(self._content)
        root.addWidget(self._scroll)

    def load_all(self) -> None:
        """Populate scroll area from all_cards(). Call before showing."""
        # Clear existing card widgets (keep the trailing stretch)
        while self._content_layout.count() > 1:
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._card_entries.clear()

        # Repopulate category filter
        self._cat_filter.blockSignals(True)
        current_text = self._cat_filter.currentText()
        self._cat_filter.clear()
        self._cat_filter.addItem("All Categories", None)

        seen_cats: list[str] = []
        cards = all_cards()
        for card in cards:
            if card.category not in seen_cats:
                seen_cats.append(card.category)
                self._cat_filter.addItem(card.category, card.category)

        # Restore selection if possible
        idx = self._cat_filter.findText(current_text)
        self._cat_filter.setCurrentIndex(max(0, idx))
        self._cat_filter.blockSignals(False)

        # Build card widgets
        for card in cards:
            widget = self._make_card_widget(card)
            # Insert before the trailing stretch
            self._content_layout.insertWidget(self._content_layout.count() - 1, widget)
            self._card_entries.append((card.category, widget))

        self._on_filter_changed()

    def _make_card_widget(self, card) -> QFrame:
        frame = QFrame()
        frame.setObjectName("card")
        frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(10)

        # Header: category badge (left) + card id (right)
        header = QHBoxLayout()
        header.setSpacing(8)

        cat_color = theme.CATEGORY_COLORS.get(card.category, theme.ACCENT)
        badge = QLabel(card.category.upper())
        badge.setStyleSheet(
            f"font-size: 10px; font-weight: bold; color: {cat_color}; "
            f"background: transparent; letter-spacing: 0.5px;"
        )

        id_lbl = QLabel(card.id)
        id_lbl.setStyleSheet(f"font-size: 10px; color: {theme.TEXT_MUTED}; background: transparent;")
        id_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        header.addWidget(badge)
        header.addStretch()
        header.addWidget(id_lbl)
        layout.addLayout(header)

        # Front text
        front_lbl = QLabel(card.front)
        front_lbl.setWordWrap(True)
        front_lbl.setStyleSheet(
            f"font-size: 14px; font-weight: bold; color: {theme.TEXT}; background: transparent;"
        )
        layout.addWidget(front_lbl)

        # Thin separator
        sep = QFrame()
        sep.setObjectName("separator")
        layout.addWidget(sep)

        # Back text
        back_lbl = QLabel(card.back)
        back_lbl.setWordWrap(True)
        back_lbl.setStyleSheet(
            f"font-size: 13px; color: {theme.TEXT_MUTED}; background: transparent;"
        )
        layout.addWidget(back_lbl)

        return frame

    def _on_filter_changed(self) -> None:
        selected = self._cat_filter.currentData()
        for category, widget in self._card_entries:
            if selected is None or category == selected:
                widget.show()
            else:
                widget.hide()
