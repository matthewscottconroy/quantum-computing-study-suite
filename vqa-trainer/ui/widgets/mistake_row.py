"""\"What went wrong?\" row — turns a wrong answer into analysis, not a bookmark.

Compact, inline (never a modal) and always skippable: the mistake is already
journalled with cause=null by the time this row appears, so pressing Next
loses nothing. Picking a cause categorises the row that was just written.
"""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QButtonGroup,
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui import theme
from persistence import MISTAKE_CAUSES, CAUSE_LABELS

_TIPS = {
    "misread":          "Misread the question or an answer option",
    "didnt_know":       "Never knew this — new material",
    "knew_but_slipped": "Knew it, but slipped on the execution",
    "confused":         "Mixed this up with something similar",
    "out_of_time":      "Rushed it",
    "other":            "Something else — use the note",
}


class MistakeRow(QWidget):
    """Cause chips + one-line note for the mistake journal."""

    cause_selected = pyqtSignal(str)     # a cause key from MISTAKE_CAUSES
    note_committed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cause: str | None = None
        self._buttons: dict[str, QPushButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        chips = QHBoxLayout()
        chips.setSpacing(8)

        self._prompt = QLabel("What went wrong?")
        self._prompt.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        chips.addWidget(self._prompt)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for idx, cause in enumerate(MISTAKE_CAUSES):
            btn = QPushButton(CAUSE_LABELS[cause])
            btn.setObjectName("chip")
            btn.setCheckable(True)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(_TIPS[cause])
            btn.setAccessibleName(f"Cause: {CAUSE_LABELS[cause]}")
            btn.setAccessibleDescription(_TIPS[cause])
            self._group.addButton(btn, idx)
            self._buttons[cause] = btn
            chips.addWidget(btn)

        self._skip_lbl = QLabel("optional")
        self._skip_lbl.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        self._skip_lbl.setAccessibleName("Choosing a cause is optional")
        chips.addWidget(self._skip_lbl)
        chips.addStretch()
        root.addLayout(chips)

        self._note = QLineEdit()
        self._note.setObjectName("note")
        self._note.setPlaceholderText("Optional one-line note — what to remember next time")
        self._note.setMaxLength(200)
        self._note.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._note.setAccessibleName("Note about this mistake")
        self._note.editingFinished.connect(self._on_note_done)
        root.addWidget(self._note)

        self._group.idClicked.connect(self._on_cause_clicked)

    # -- API ---------------------------------------------------------------
    def _on_cause_clicked(self, idx: int) -> None:
        self._cause = MISTAKE_CAUSES[idx]
        self.cause_selected.emit(self._cause)

    def _on_note_done(self) -> None:
        self.note_committed.emit(self._note.text().strip())

    def cause(self) -> str | None:
        return self._cause

    def note(self) -> str:
        return self._note.text().strip()

    def flush_note(self) -> None:
        """Emit the note before the screen is left, even if focus never moved."""
        if self._note.text().strip():
            self.note_committed.emit(self._note.text().strip())

    def reset(self) -> None:
        self._cause = None
        self._group.setExclusive(False)
        for btn in self._buttons.values():
            btn.setChecked(False)
        self._group.setExclusive(True)
        self._note.clear()

    def button_for(self, cause: str) -> QPushButton | None:
        return self._buttons.get(cause)
