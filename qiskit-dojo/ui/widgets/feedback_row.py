"""Compact, skippable feedback controls shown on the kata screen.

`ConfidenceStrip` asks "how sure are you this passes?" **before** the first
Run, so the rating can never be hindsight.  `MistakeRow` asks "what went
wrong?" once a kata has been given up on, turning a failure into a diagnosis
instead of a bookmark.  Both are optional: neither blocks the flow, neither
opens a dialog, and skipping either loses nothing (the mistake is already
journalled with ``cause=None``).

Accessibility notes for both widgets:
  * every control is a real focusable QPushButton / QLineEdit with
    StrongFocus, an accessible name and an accessible description, so the
    whole row is reachable and announceable from the keyboard alone;
  * the selected state carries a glyph (``○``/``●`` and a ``✓`` tick) as well
    as a colour, so nothing is encoded in colour alone;
  * the focus ring is an explicit accent border on a pre-reserved 1px border,
    so focus is visible without the widget shifting by a pixel;
  * text is TEXT/TEXT_MUTED/ACCENT on SURFACE/SURFACE2, all >= 4.5:1.
"""
from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import (
    QButtonGroup, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QWidget,
)

from persistence import CAUSE_LABELS, CONFIDENCE_LABELS, MISTAKE_CAUSES
from ui import theme

# A 1px transparent border in the resting state means the focus ring can
# simply recolour it — no reflow when a button takes focus.
_CHIP_QSS = f"""
QPushButton {{
    background: {theme.SURFACE2}; color: {theme.TEXT};
    border: 1px solid {theme.BORDER}; border-radius: 6px;
    padding: 4px 10px; font-size: 12px; text-align: center;
}}
QPushButton:hover {{ background: {theme.BORDER}; border-color: {theme.ACCENT}; }}
QPushButton:checked {{
    background: {theme.BORDER}; color: {theme.TEXT};
    border: 1px solid {theme.ACCENT}; font-weight: bold;
}}
QPushButton:focus {{ border: 1px solid {theme.ACCENT}; background: {theme.BORDER}; }}
"""

#: horizontal padding + border reserved by _CHIP_QSS (10px * 2 + 1px * 2),
#: plus a couple of pixels of slack for style-dependent rounding.
_CHIP_H_PADDING = 26

_LINK_QSS = f"""
QPushButton {{
    background: transparent; color: {theme.ACCENT};
    border: 1px solid transparent; border-radius: 6px;
    padding: 4px 8px; font-size: 12px;
}}
QPushButton:hover {{ color: {theme.TEXT}; }}
QPushButton:focus {{ border-color: {theme.ACCENT}; background: {theme.SURFACE2}; }}
"""


class _NoteEdit(QLineEdit):
    """A QLineEdit whose placeholder keeps an AA-contrast colour.

    Qt derives PlaceholderText from the text colour at 50% alpha every time a
    stylesheet-aware style re-polishes the widget — merely adding it to a
    layout is enough — and on SURFACE2 that lands at 4.36:1, under AA.  Every
    palette recomputation re-asserts TEXT_MUTED (4.95:1) instead.
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._fixing = False
        self._fix_placeholder()

    def changeEvent(self, event) -> None:
        super().changeEvent(event)
        if event.type() == QEvent.Type.PaletteChange:
            self._fix_placeholder()

    def _fix_placeholder(self) -> None:
        if self._fixing:
            return
        want = QColor(theme.TEXT_MUTED)
        pal = self.palette()
        if pal.color(QPalette.ColorRole.PlaceholderText) == want:
            return
        pal.setColor(QPalette.ColorRole.PlaceholderText, want)
        self._fixing = True
        try:
            self.setPalette(pal)
        finally:
            self._fixing = False


def _chip(text: str, accessible_name: str, description: str,
          widest: str = "") -> QPushButton:
    btn = QPushButton(text)
    btn.setCheckable(True)
    btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    btn.setStyleSheet(_CHIP_QSS)
    btn.setAccessibleName(accessible_name)
    btn.setAccessibleDescription(description)
    btn.setToolTip(description)
    # The selection glyph makes the label longer than the resting one, and a
    # laid-out button does not always grow to match — reserve the wider width
    # up front so the tick can never clip the text.
    if widest:
        btn.setMinimumWidth(btn.fontMetrics().horizontalAdvance(widest)
                            + _CHIP_H_PADDING)
    return btn


def _link(text: str, accessible_name: str, description: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
    btn.setStyleSheet(_LINK_QSS)
    btn.setAccessibleName(accessible_name)
    btn.setAccessibleDescription(description)
    btn.setToolTip(description)
    return btn


class ConfidenceStrip(QWidget):
    """1-4 confidence rating, asked before the first Run of a kata."""

    rated     = pyqtSignal(int)     # 1..4
    opted_out = pyqtSignal()        # "Don't ask again"

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAccessibleName("Confidence rating")
        self.setAccessibleDescription(
            "Optional: rate how sure you are that your code passes, before "
            "you run it."
        )
        self._value: int | None = None
        self._buttons: dict[int, QPushButton] = {}

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        self._prompt = QLabel("How sure are you this passes?")
        self._prompt.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        row.addWidget(self._prompt)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for level in (1, 2, 3, 4):
            label = CONFIDENCE_LABELS[level]
            btn = _chip(
                f"○ {level}  {label}",
                f"Confidence {level} of 4: {label}",
                f"Rate your confidence {level} of 4 ({label}) before running.",
                widest=f"● {level}  {label}",
            )
            btn.clicked.connect(lambda _=False, lv=level: self._on_pick(lv))
            self._group.addButton(btn, level)
            self._buttons[level] = btn
            row.addWidget(btn)

        self._dismiss = _link(
            "Don't ask again",
            "Turn off confidence ratings",
            "Stop asking for a confidence rating in this app. "
            "Re-enable it in dojo_settings.json.",
        )
        self._dismiss.clicked.connect(self.opted_out)
        row.addWidget(self._dismiss)
        row.addStretch()

    # ------------------------------------------------------------- state

    def value(self) -> int | None:
        """The chosen level, or None when the strip was skipped."""
        return self._value

    def reset(self) -> None:
        """Back to unrated and interactive (called for every new kata)."""
        self._value = None
        self._group.setExclusive(False)
        for level, btn in self._buttons.items():
            btn.setChecked(False)
            btn.setText(f"○ {level}  {CONFIDENCE_LABELS[level]}")
            btn.setEnabled(True)
        self._group.setExclusive(True)
        self._dismiss.setEnabled(True)
        self._prompt.setText("How sure are you this passes?")
        self._prompt.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: 12px; background: transparent;"
        )

    def set_rating(self, level: int) -> None:
        """Choose a level programmatically (same path as a click)."""
        if level in self._buttons:
            self._buttons[level].setChecked(True)
            self._on_pick(level)

    def freeze(self) -> None:
        """Lock the rating once the kata has been run — no hindsight edits."""
        for btn in self._buttons.values():
            btn.setEnabled(False)
        self._dismiss.setEnabled(False)
        if self._value is None:
            self._prompt.setText("Confidence: not rated")
        else:
            self._prompt.setText(
                f"Confidence: {self._value}/4 {CONFIDENCE_LABELS[self._value]}"
            )

    def _on_pick(self, level: int) -> None:
        self._value = level
        for lv, btn in self._buttons.items():
            glyph = "●" if lv == level else "○"
            btn.setText(f"{glyph} {lv}  {CONFIDENCE_LABELS[lv]}")
        self._prompt.setText("How sure are you this passes?")
        self.rated.emit(level)


class MistakeRow(QWidget):
    """"What went wrong?" — one chip per cause, plus an optional note."""

    #: (cause or None, note) — emitted whenever the diagnosis changes.
    logged    = pyqtSignal(object, str)
    dismissed = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAccessibleName("Mistake journal")
        self.setAccessibleDescription(
            "Optional: say what went wrong on this kata. Skipping still "
            "records the mistake, just without a cause."
        )
        self._cause: str | None = None
        self._buttons: dict[str, QPushButton] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 6, 0, 0)
        root.setSpacing(6)

        header = QHBoxLayout()
        header.setSpacing(8)
        title = QLabel("✎ What went wrong?")
        title.setStyleSheet(
            f"color: {theme.WARNING}; font-size: 12px; font-weight: bold; "
            "background: transparent;"
        )
        header.addWidget(title)
        hint = QLabel("(optional — it is already journalled)")
        hint.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: 11px; background: transparent;"
        )
        header.addWidget(hint)
        header.addStretch()
        self._skip_btn = _link(
            "Skip",
            "Skip the mistake diagnosis",
            "Hide this row. The mistake stays journalled without a cause.",
        )
        self._skip_btn.clicked.connect(self._on_skip)
        header.addWidget(self._skip_btn)
        root.addLayout(header)

        chips = QHBoxLayout()
        chips.setSpacing(6)
        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        for cause in MISTAKE_CAUSES:
            label = CAUSE_LABELS[cause]
            btn = _chip(
                label,
                f"Cause: {label}",
                f"Record “{label}” as the cause of this mistake.",
                widest=f"✓ {label}",
            )
            btn.clicked.connect(lambda _=False, c=cause: self._on_pick(c))
            self._group.addButton(btn)
            self._buttons[cause] = btn
            chips.addWidget(btn)
        chips.addStretch()
        root.addLayout(chips)

        self._note = _NoteEdit()
        self._note.setPlaceholderText("One-line note (optional) — press Enter to save")
        self._note.setMaxLength(200)
        self._note.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._note.setAccessibleName("Mistake note")
        self._note.setAccessibleDescription(
            "Optional one-line note saved with this mistake."
        )
        self._note.setStyleSheet(
            f"QLineEdit {{ background: {theme.SURFACE2}; color: {theme.TEXT}; "
            f"border: 1px solid {theme.BORDER}; border-radius: 6px; "
            f"padding: 4px 8px; font-size: 12px; }}"
            f"QLineEdit:focus {{ border-color: {theme.ACCENT}; }}"
        )
        self._note.returnPressed.connect(self._emit)
        self._note.editingFinished.connect(self._emit)
        root.addWidget(self._note)

    # ------------------------------------------------------------- state

    def selected_cause(self) -> str | None:
        return self._cause

    def note_text(self) -> str:
        return self._note.text()

    def reset(self) -> None:
        self._cause = None
        self._group.setExclusive(False)
        for cause, btn in self._buttons.items():
            btn.setChecked(False)
            btn.setText(CAUSE_LABELS[cause])
        self._group.setExclusive(True)
        self._note.clear()

    def choose(self, cause: str) -> None:
        """Pick a cause programmatically (same path as a click)."""
        if cause in self._buttons:
            self._buttons[cause].setChecked(True)
            self._on_pick(cause)

    def set_note(self, text: str) -> None:
        self._note.setText(text)
        self._emit()

    def _on_pick(self, cause: str) -> None:
        self._cause = cause
        for c, btn in self._buttons.items():
            btn.setText(f"✓ {CAUSE_LABELS[c]}" if c == cause else CAUSE_LABELS[c])
        self._emit()

    def _emit(self) -> None:
        self.logged.emit(self._cause, self._note.text())

    def _on_skip(self) -> None:
        self.hide()
        self.dismissed.emit()
