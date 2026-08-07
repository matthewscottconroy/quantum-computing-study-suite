"""Widget that displays a PNG circuit image, scaling to fit available width."""

from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from ui import theme


class CircuitViewer(QLabel):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._raw_pixmap: QPixmap | None = None
        self._show_placeholder()

    def set_image(self, png_bytes: bytes) -> None:
        """Load PNG bytes and display, scaling to fit width."""
        px = QPixmap()
        px.loadFromData(png_bytes, "PNG")
        self._raw_pixmap = px
        self._refresh()
        self.show()

    def clear_image(self) -> None:
        self._raw_pixmap = None
        self._show_placeholder()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self._raw_pixmap:
            self._refresh()

    def _refresh(self) -> None:
        if self._raw_pixmap is None:
            return
        w = self.width() or self._raw_pixmap.width()
        scaled = self._raw_pixmap.scaledToWidth(
            w, Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
        self.setFixedHeight(scaled.height())

    def _show_placeholder(self) -> None:
        self.setText("")
        self.setFixedHeight(0)
        self.hide()
