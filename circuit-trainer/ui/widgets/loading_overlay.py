"""Semi-transparent loading overlay with animated ellipsis."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor
from ui import theme


class LoadingOverlay(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.hide()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label = QLabel("Loading…", self)
        self._label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._label.setStyleSheet(
            f"color: {theme.TEXT}; font-size: 18px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(self._label)
        self._dots = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

    def show_message(self, msg: str) -> None:
        self._label.setText(msg)
        self.resize(self.parentWidget().size())
        self.raise_()
        self.show()
        self._timer.start(400)

    def hide_overlay(self) -> None:
        self._timer.stop()
        self.hide()

    def resizeEvent(self, event) -> None:
        if self.parentWidget():
            self.resize(self.parentWidget().size())
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(13, 17, 23, 210))
        painter.end()

    def _tick(self) -> None:
        self._dots = (self._dots + 1) % 4
        base = self._label.text().rstrip(".")
        self._label.setText(base + "." * self._dots)
