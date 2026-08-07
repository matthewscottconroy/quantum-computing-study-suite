"""Countdown timer widget displayed on the card screen."""
from __future__ import annotations
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, pyqtSignal
from ui import theme


class TimerWidget(QLabel):
    time_up = pyqtSignal()

    def __init__(self, seconds: int, parent=None) -> None:
        super().__init__(parent)
        self._total   = seconds
        self._remain  = seconds
        self._timer   = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)
        self._update_label()

    def start(self) -> None:
        if self._total > 0:
            self._timer.start()

    def stop(self) -> None:
        self._timer.stop()

    def reset(self, total_secs: int | None = None) -> None:
        self._timer.stop()
        if total_secs is not None:
            self._total = total_secs
        self._remain = self._total
        self._update_label()

    def _tick(self) -> None:
        self._remain -= 1
        self._update_label()
        if self._remain <= 0:
            self._timer.stop()
            self.time_up.emit()

    def _update_label(self) -> None:
        if self._total <= 0:
            self.hide()
            return
        color = theme.ERROR if self._remain <= 5 else theme.TEXT_MUTED
        self.setStyleSheet(f"font-size: 13px; color: {color}; font-weight: bold;")
        self.setText(f"⏱ {self._remain}s")
        self.show()
