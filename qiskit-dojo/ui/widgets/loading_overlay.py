"""Loading overlay widget."""
from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui import theme


class LoadingOverlay(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background: rgba(13,17,23,200);")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl = QLabel("Working…")
        self._lbl.setStyleSheet(
            f"font-size: 16px; color: {theme.TEXT}; background: transparent;"
        )
        self._lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._lbl)
        self.hide()

    def show_message(self, msg: str) -> None:
        self._lbl.setText(msg)
        self.resize(self.parent().size())
        self.raise_()
        self.show()

    def resizeEvent(self, event) -> None:
        if self.parent():
            self.resize(self.parent().size())
        super().resizeEvent(event)
