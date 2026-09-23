"""Confidence strip — rated BEFORE the answer is revealed, so it cannot be hindsight.

Optional and skippable: the session runs exactly the same whether or not a
level is picked, and "Don't ask again" stores an opt-out in the app's own
settings file so the strip is never shown again.
"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QButtonGroup,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui import theme

# 1 = guessing … 4 = certain. The digit is part of the visible label so the
# ordering never depends on colour or position alone.
LEVELS: tuple[tuple[int, str, str], ...] = (
    (1, "Guessing",    "Pure guess — no idea which answer is right"),
    (2, "Unsure",      "Leaning one way but far from sure"),
    (3, "Fairly sure", "Fairly sure this is right"),
    (4, "Certain",     "Certain this is right"),
)


class ConfidenceStrip(QWidget):
    """A 4-button confidence strip plus an opt-out link."""

    rating_changed = pyqtSignal(int)
    opt_out_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._value: int | None = None
        self._buttons: dict[int, QPushButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self._prompt = QLabel("How sure are you?")
        self._prompt.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        row.addWidget(self._prompt)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for level, label, tip in LEVELS:
            btn = QPushButton(f"{level} · {label}")
            btn.setObjectName("chip")
            btn.setCheckable(True)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(tip)
            btn.setAccessibleName(f"Confidence {level} of 4: {label}")
            btn.setAccessibleDescription(tip)
            self._group.addButton(btn, level)
            self._buttons[level] = btn
            row.addWidget(btn)

        self._skip_lbl = QLabel("optional")
        self._skip_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        self._skip_lbl.setAccessibleName("Confidence rating is optional")
        row.addWidget(self._skip_lbl)

        row.addStretch()

        self._opt_out_btn = QPushButton("Don't ask again")
        self._opt_out_btn.setObjectName("linkbtn")
        self._opt_out_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._opt_out_btn.setAccessibleName("Stop asking for a confidence rating")
        self._opt_out_btn.setToolTip(
            "Hide the confidence strip for good (re-enable it by deleting "
            "confidence_prompt from vqa_settings.json)."
        )
        self._opt_out_btn.clicked.connect(self.opt_out_requested)
        row.addWidget(self._opt_out_btn)

        self._group.idClicked.connect(self._on_clicked)

    # -- API ---------------------------------------------------------------
    def _on_clicked(self, level: int) -> None:
        self._value = level
        self.rating_changed.emit(level)

    def value(self) -> int | None:
        """The chosen level, or None if the user skipped the strip."""
        return self._value

    def reset(self) -> None:
        """Clear the selection for a new problem."""
        self._value = None
        self._group.setExclusive(False)
        for btn in self._buttons.values():
            btn.setChecked(False)
        self._group.setExclusive(True)

    def button_for(self, level: int) -> QPushButton | None:
        return self._buttons.get(level)
