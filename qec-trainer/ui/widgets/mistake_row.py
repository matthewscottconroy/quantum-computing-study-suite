"""Mistake-journal "What went wrong?" row, shown inline on a wrong answer.

A wrong answer is already logged by the caller with ``cause=None`` before this
row appears, so skipping it loses nothing. Picking a cause (or typing a note)
updates that record. One compact row, no modal, never blocking: the Next button
stays live the whole time.

Accessibility: every pill is a tab-reachable QPushButton with an accessible
name and a visible focus ring; the chosen cause is marked with a "✓" glyph and
echoed in a text status line, so nothing is carried by colour alone.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QButtonGroup,
    QLineEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal

from persistence import CAUSE_LABELS, MISTAKE_CAUSES
from ui import theme

_PROMPT = "What went wrong?"
_HINT   = "Optional — one tap turns this mistake into data you can act on."


class MistakeRow(QWidget):
    """Cause pills + an optional one-line note for the current mistake."""

    cause_chosen = pyqtSignal(str)        # one of persistence.MISTAKE_CAUSES
    note_edited  = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cause: str | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        top = QHBoxLayout()
        top.setSpacing(8)
        self._prompt_lbl = QLabel(_PROMPT)
        self._prompt_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {theme.TEXT_MUTED};")
        self._prompt_lbl.setToolTip(_HINT)
        top.addWidget(self._prompt_lbl)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}
        for cause in MISTAKE_CAUSES:
            label = CAUSE_LABELS[cause]
            btn = QPushButton(label)
            btn.setObjectName("pill")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setAccessibleName(f"Cause of mistake: {label}")
            btn.setAccessibleDescription(
                "Optional. Files this mistake under a cause in your journal.")
            btn.setToolTip(_HINT)
            btn.clicked.connect(lambda _=False, c=cause: self._on_pick(c))
            self._group.addButton(btn)
            self._buttons[cause] = btn
            top.addWidget(btn)

        top.addStretch()
        root.addLayout(top)

        bottom = QHBoxLayout()
        bottom.setSpacing(8)
        self._note_edit = QLineEdit()
        self._note_edit.setPlaceholderText("Optional note — what will you do differently?")
        self._note_edit.setAccessibleName("Note about this mistake")
        self._note_edit.setClearButtonEnabled(True)
        self._note_edit.setMaxLength(200)
        self._note_edit.editingFinished.connect(self._on_note)
        self._note_edit.returnPressed.connect(self._on_note)
        bottom.addWidget(self._note_edit, 1)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(f"font-size: 12px; color: {theme.ACCENT};")
        self._status_lbl.setAccessibleName("Mistake journal status")
        bottom.addWidget(self._status_lbl)
        root.addLayout(bottom)

    # ── API ───────────────────────────────────────────────────────────────────

    def reset(self, logged: bool = True) -> None:
        """Clear the row for a new mistake. *logged* False means the journal
        write failed, so the row says so instead of claiming a save."""
        self._cause = None
        self._group.setExclusive(False)
        for cause, btn in self._buttons.items():
            btn.setChecked(False)
            btn.setText(CAUSE_LABELS[cause])
        self._group.setExclusive(True)
        self._note_edit.blockSignals(True)
        self._note_edit.clear()
        self._note_edit.blockSignals(False)
        self._status_lbl.setText(
            "Logged — uncategorised" if logged else "Journal unavailable")

    def cause(self) -> str | None:
        return self._cause

    def note(self) -> str:
        return self._note_edit.text().strip()

    def choose(self, cause: str) -> None:
        """Programmatic equivalent of clicking a cause pill (used by tests)."""
        if cause in self._buttons:
            self._buttons[cause].setChecked(True)
            self._on_pick(cause)

    def set_note(self, text: str) -> None:
        self._note_edit.setText(text)
        self._on_note()

    # ── Internals ─────────────────────────────────────────────────────────────

    def _on_pick(self, cause: str) -> None:
        self._cause = cause
        for c, btn in self._buttons.items():
            btn.setText(f"✓ {CAUSE_LABELS[c]}" if c == cause else CAUSE_LABELS[c])
        self._status_lbl.setText(f"✓ Filed under “{CAUSE_LABELS[cause]}”")
        self.cause_chosen.emit(cause)

    def _on_note(self) -> None:
        self.note_edited.emit(self._note_edit.text().strip())
