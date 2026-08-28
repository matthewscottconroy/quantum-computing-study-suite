"""Collapsible section widget — header button toggles a content area."""
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt
from ui import theme


class CollapsibleSection(QWidget):
    """A titled section whose body can be expanded/collapsed."""

    def __init__(self, title: str, content: QWidget,
                 expanded: bool = False, accent: str | None = None,
                 parent=None) -> None:
        super().__init__(parent)
        self._content = content
        color = accent or theme.ACCENT

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._toggle = QPushButton()
        self._toggle.setCheckable(True)
        self._toggle.setChecked(expanded)
        self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle.setStyleSheet(
            f"QPushButton {{ background: {theme.SURFACE2}; color: {color};"
            f"  border: 1px solid {theme.BORDER}; border-radius: 6px;"
            f"  padding: 6px 12px; text-align: left; font-weight: bold; font-size: 13px; }}"
            f"QPushButton:hover {{ border-color: {color}; }}"
        )
        self._title = title
        self._toggle.toggled.connect(self._on_toggled)
        root.addWidget(self._toggle)

        self._body = QFrame()
        self._body.setStyleSheet(
            f"QFrame {{ background: {theme.SURFACE}; border: 1px solid {theme.BORDER};"
            f"  border-top: none; border-radius: 0 0 6px 6px; }}"
        )
        body_layout = QVBoxLayout(self._body)
        body_layout.setContentsMargins(12, 10, 12, 10)
        body_layout.addWidget(content)
        root.addWidget(self._body)

        self._on_toggled(expanded)

    def _arrow(self, expanded: bool) -> str:
        return "▾" if expanded else "▸"

    def _on_toggled(self, expanded: bool) -> None:
        self._toggle.setText(f"{self._arrow(expanded)}  {self._title}")
        self._body.setVisible(expanded)

    def set_title(self, title: str) -> None:
        self._title = title
        self._on_toggled(self._toggle.isChecked())

    def set_expanded(self, expanded: bool) -> None:
        self._toggle.setChecked(expanded)
