"""Collapsible section widget with animated height transition."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from ui import theme

_ANIMATION_MS = 250


class CollapsiblePanel(QWidget):
    def __init__(self, title: str, content_widget: QWidget, parent=None) -> None:
        super().__init__(parent)
        self._expanded = False
        self._content = content_widget

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._toggle = QPushButton(f"▶  {title}")
        self._toggle.setObjectName("flat")
        self._toggle.setCheckable(True)
        self._toggle.clicked.connect(self._on_toggle)
        self._toggle.setStyleSheet(
            f"text-align: left; padding: 6px 4px; color: {theme.ACCENT}; "
            "font-size: 13px; font-weight: bold;"
        )
        layout.addWidget(self._toggle)

        self._area = QScrollArea()
        self._area.setWidgetResizable(True)
        self._area.setWidget(content_widget)
        self._area.setStyleSheet(f"background: {theme.SURFACE}; border-radius: 6px;")
        self._area.setMaximumHeight(0)
        self._area.setMinimumHeight(0)
        layout.addWidget(self._area)

    def _on_toggle(self, checked: bool) -> None:
        self._expanded = checked
        arrow = "▼" if checked else "▶"
        title = self._toggle.text()[2:]
        self._toggle.setText(f"{arrow}  {title}")

        target_h = self._content.sizeHint().height() + 20 if checked else 0

        anim = QPropertyAnimation(self._area, b"maximumHeight", self)
        anim.setDuration(_ANIMATION_MS)
        anim.setStartValue(self._area.maximumHeight())
        anim.setEndValue(target_h)
        anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        anim.start()
        self._anim = anim
