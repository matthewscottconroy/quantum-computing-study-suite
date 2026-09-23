"""Two small reusable rows shared by the exam, results and review screens.

* ``ConfidenceStrip`` — 1-4 self-rating shown *before* the answer is revealed
  (so it can never be hindsight). Optional, skippable, keyboard-driven.
* ``CauseRow`` — the "What went wrong?" categoriser shown next to a wrong
  answer on a feedback/result view. Skipping it is fine: the miss is already
  in mistakes.json with cause=null, choosing a cause only fills that in.

Accessibility rules both rows follow: every control is keyboard reachable
(strong focus policy), carries an accessible name, and draws a visible focus
ring (see the ``#chip`` rules in ui/theme.py). Selection is never signalled by
colour alone — the selected chip also gains a "✓" glyph, and the confirmation
line is text.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QButtonGroup, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget,
)

from persistence import CAUSE_LABELS, CONFIDENCE_LABELS, MISTAKE_CAUSES
from ui import theme

_CHECK = "✓"       # ✓ — pairs with colour so selection is never colour-only


def _chip(text: str, accessible_name: str, tooltip: str = "") -> QPushButton:
    btn = QPushButton(text)
    btn.setObjectName("chip")
    btn.setCheckable(True)
    btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    btn.setAccessibleName(accessible_name)
    btn.setToolTip(tooltip or accessible_name)
    btn.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return btn


def _set_chip_text(btn: QPushButton, label: str, checked: bool) -> None:
    btn.setText(f"{_CHECK} {label}" if checked else label)


class ConfidenceStrip(QWidget):
    """Compact 'How sure are you?' row: four chips plus a Hide button.

    Emits ``rated(int)`` (1-4), ``cleared()`` when the rating is taken back
    (key 0) and ``opt_out()`` when the user hides the strip for good.
    """

    rated = pyqtSignal(int)
    cleared = pyqtSignal()
    opt_out = pyqtSignal()

    def __init__(self, parent=None, *, prompt: str = "How sure?") -> None:
        super().__init__(parent)
        self._buttons: dict[int, QPushButton] = {}

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        label = QLabel(prompt)
        label.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        label.setToolTip("Optional — rate your confidence before you move on. "
                         "Keys 1-4; 0 clears.")
        row.addWidget(label)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for value in sorted(CONFIDENCE_LABELS):
            words = CONFIDENCE_LABELS[value]
            btn = _chip(
                f"{value} {words}",
                f"Confidence {value} of 4: {words.lower()}",
                f"Confidence {value}/4 — {words.lower()} (key {value})",
            )
            self._group.addButton(btn, value)
            self._buttons[value] = btn
            row.addWidget(btn)
        self._group.idClicked.connect(self._on_clicked)

        row.addStretch()

        self._hide_btn = QPushButton("Hide")
        self._hide_btn.setObjectName("flat")
        self._hide_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._hide_btn.setAccessibleName("Hide the confidence prompt and stop asking")
        self._hide_btn.setToolTip(
            "Stop asking for a confidence rating. Turn it back on from the "
            "home screen.")
        self._hide_btn.clicked.connect(self.opt_out)
        row.addWidget(self._hide_btn)

    # ------------------------------------------------------------------ api
    def install_shortcuts(self, host: QWidget) -> list[QShortcut]:
        """Bind 1-4 (rate) and 0 (clear) while focus is inside `host`."""
        shortcuts: list[QShortcut] = []
        for value in list(CONFIDENCE_LABELS) + [0]:
            sc = QShortcut(QKeySequence(str(value)), host)
            sc.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            sc.activated.connect(lambda v=value: self._on_shortcut(v))
            shortcuts.append(sc)
        return shortcuts

    def value(self) -> int | None:
        checked = self._group.checkedId()
        return checked if checked in CONFIDENCE_LABELS else None

    def set_value(self, value: int | None) -> None:
        """Reflect a stored rating without emitting ``rated``."""
        self._group.setExclusive(False)
        for val, btn in self._buttons.items():
            btn.setChecked(val == value)
            _set_chip_text(btn, f"{val} {CONFIDENCE_LABELS[val]}", val == value)
        self._group.setExclusive(True)

    # -------------------------------------------------------------- internal
    def _on_shortcut(self, value: int) -> None:
        if not self.isVisible():
            return
        if value == 0:
            self.set_value(None)
            self.cleared.emit()
            return
        self.set_value(value)
        self.rated.emit(value)

    def _on_clicked(self, value: int) -> None:
        self.set_value(value)
        self.rated.emit(value)


class CauseRow(QWidget):
    """'What went wrong?' — one chip per cause plus an optional one-line note.

    Emits ``chosen(cause, note)``. Never blocks the flow: it is one more row on
    the feedback view, no modal, and skipping it leaves the already-logged
    mistake with cause=null.
    """

    chosen = pyqtSignal(str, str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cause: str | None = None
        self._buttons: dict[str, QPushButton] = {}

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 6, 0, 0)
        outer.setSpacing(4)

        head = QLabel("What went wrong?  <span style='font-size:11px;'>"
                      "(optional — the miss is already logged)</span>")
        head.setTextFormat(Qt.TextFormat.RichText)
        head.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 12px;")
        outer.addWidget(head)

        chips = QHBoxLayout()
        chips.setContentsMargins(0, 0, 0, 0)
        chips.setSpacing(6)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for cause in MISTAKE_CAUSES:
            label = CAUSE_LABELS[cause]
            btn = _chip(label, f"Cause: {label}",
                        f"Log this miss as: {label.lower()}")
            self._group.addButton(btn)
            self._buttons[cause] = btn
            btn.clicked.connect(lambda _=False, c=cause: self._on_cause(c))
            chips.addWidget(btn)
        chips.addStretch()
        outer.addLayout(chips)

        note_row = QHBoxLayout()
        note_row.setContentsMargins(0, 0, 0, 0)
        note_row.setSpacing(6)
        self._note = QLineEdit()
        self._note.setPlaceholderText("Optional note (press Enter to save)")
        self._note.setAccessibleName("Note about this mistake")
        self._note.setToolTip("One line on why you missed it. Enter saves it.")
        self._note.setMaxLength(200)
        self._note.returnPressed.connect(self._on_note_entered)
        note_row.addWidget(self._note, 1)
        outer.addLayout(note_row)

        self._status = QLabel("")
        self._status.setStyleSheet(f"color: {theme.SUCCESS}; font-size: 12px;")
        self._status.setVisible(False)
        outer.addWidget(self._status)

    # ------------------------------------------------------------------ api
    def reset(self) -> None:
        self._cause = None
        self._group.setExclusive(False)
        for cause, btn in self._buttons.items():
            btn.setChecked(False)
            _set_chip_text(btn, CAUSE_LABELS[cause], False)
        self._group.setExclusive(True)
        self._note.clear()
        self._status.clear()
        self._status.setVisible(False)

    def cause(self) -> str | None:
        return self._cause

    def note(self) -> str:
        return self._note.text().strip()

    # -------------------------------------------------------------- internal
    def _on_cause(self, cause: str) -> None:
        self._cause = cause
        for name, btn in self._buttons.items():
            _set_chip_text(btn, CAUSE_LABELS[name], name == cause)
        self._emit()

    def _on_note_entered(self) -> None:
        if self._cause is None:      # a note needs a cause to hang off
            self._on_cause("other")
        else:
            self._emit()

    def _emit(self) -> None:
        assert self._cause is not None
        self.chosen.emit(self._cause, self.note())
        note = self.note()
        self._status.setText(
            f"{_CHECK} Logged as “{CAUSE_LABELS[self._cause]}”"
            + (" with a note." if note else ".")
        )
        self._status.setVisible(True)
