"""Coloured capsule label for subject name and difficulty level."""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from ui import theme


class PillBadge(QLabel):
    def __init__(self, text: str, color: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_color(color)

    def _set_color(self, color: str) -> None:
        self.setStyleSheet(
            f"background-color: {color}22;"
            f"color: {color};"
            f"border: 1px solid {color}55;"
            "border-radius: 10px;"
            "padding: 2px 10px;"
            "font-size: 11px;"
            "font-weight: bold;"
        )

    def update_text(self, text: str, color: str) -> None:
        self.setText(text)
        self._set_color(color)


def make_subject_pill(subject: str, parent=None) -> PillBadge:
    return PillBadge(subject, theme.subject_color(subject), parent)


def make_difficulty_pill(difficulty: str, parent=None) -> PillBadge:
    color = theme.DIFFICULTY_COLORS.get(difficulty, theme.ACCENT)
    return PillBadge(difficulty.upper(), color, parent)
