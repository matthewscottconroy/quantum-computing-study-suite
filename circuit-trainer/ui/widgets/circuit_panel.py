"""Auto-scaling circuit image panel with optional label."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from ui import theme


class CircuitPanel(QWidget):
    def __init__(self, label: str = "", parent=None) -> None:
        super().__init__(parent)
        self._raw_px: QPixmap | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if label:
            lbl = QLabel(label)
            lbl.setObjectName("muted")
            layout.addWidget(lbl)

        self._img = QLabel()
        self._img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._img.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        layout.addWidget(self._img)
        self.hide()

    def set_image(self, png_bytes: bytes) -> None:
        if not png_bytes:
            self.hide()
            return
        px = QPixmap()
        px.loadFromData(png_bytes, "PNG")
        self._raw_px = px
        self._refresh()
        self.show()

    def clear(self) -> None:
        self._raw_px = None
        self._img.clear()
        self.hide()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self) -> None:
        if self._raw_px is None:
            return
        w = self.width() or self._raw_px.width()
        scaled = self._raw_px.scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
        self._img.setPixmap(scaled)
        self._img.setFixedHeight(scaled.height())
