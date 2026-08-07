"""Animated score bar widget."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtProperty, QEasingCurve
from PyQt6.QtGui import QPainter, QColor
from ui import theme
from config import SCORE_BAR_ANIMATION_MS


class ScoreBar(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._score: float = 0.0
        self.setFixedHeight(32)
        self.setMinimumWidth(200)

    def _get_score(self) -> float:
        return self._score

    def _set_score(self, v: float) -> None:
        self._score = v
        self.update()

    score = pyqtProperty(float, _get_score, _set_score)

    def animate_to(self, target: int) -> None:
        anim = QPropertyAnimation(self, b"score", self)
        anim.setDuration(SCORE_BAR_ANIMATION_MS)
        anim.setStartValue(0.0)
        anim.setEndValue(float(target))
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._anim = anim

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        blocks = 10
        block_w = (self.width() - (blocks - 1) * 4) / blocks
        block_h = self.height()
        filled = int(self._score)
        frac = self._score - filled
        for i in range(blocks):
            x = i * (block_w + 4)
            if i < filled:
                color = _block_color(i)
            elif i == filled and frac > 0.01:
                base = _block_color(i)
                color = QColor(base)
                color.setAlphaF(frac)
            else:
                color = QColor(theme.SURFACE2)
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(int(x), 0, int(block_w), block_h, 4, 4)
        painter.end()


def _block_color(idx: int) -> QColor:
    t = idx / 9.0
    if t < 0.5:
        r, g = 248, int(83 + t * 2 * (185 - 83))
        b = 73
    else:
        r = int(248 - (t - 0.5) * 2 * (248 - 63))
        g, b = 185, 80
    return QColor(r, g, b)
