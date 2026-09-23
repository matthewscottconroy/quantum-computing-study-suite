"""Compact, skippable study-journal controls shared by the problem and
derivation screens.

* :class:`ConfidenceStrip` — a 1–4 rating offered *before* an answer is graded,
  so the rating can never be hindsight.  Pairing it with the outcome is what
  exposes confidently-wrong topics.
* :class:`MistakeRow`      — a one-line "What went wrong?" cause picker shown
  on the feedback view after a bad result.  Choosing a cause turns a flagged
  item into analysis; skipping it costs nothing (the mistake is already logged
  with ``cause=null``).

Both are inline, never modal, never block the flow, are fully keyboard
reachable (Tab moves between the buttons, Space/Enter activates), carry
accessible names, show a visible focus ring, and encode state with a glyph and
text as well as colour.  Colours are taken from the app's dark palette; every
text/background pair used here clears 4.5:1 (TEXT 12.9:1, TEXT_MUTED 5.0:1,
ACCENT 6.0:1, PARTIAL 7.8:1 on SURFACE2).
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QButtonGroup,
    QLineEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal

from ui import theme

# Shown left of each control so meaning never rests on colour alone.
CONFIDENCE_GLYPH = "◔"
MISTAKE_GLYPH    = "✗"
CHECK_GLYPH      = "✓"

CONFIDENCE_LEVELS: list[tuple[int, str]] = [
    (1, "Guessing"),
    (2, "Unsure"),
    (3, "Fairly sure"),
    (4, "Certain"),
]

# (cause key stored in mistakes.json, button label)
MISTAKE_CAUSE_LABELS: list[tuple[str, str]] = [
    ("misread",          "Misread it"),
    ("didnt_know",       "Didn't know"),
    ("knew_but_slipped", "Knew it — slipped"),
    ("confused",         "Confused"),
    ("out_of_time",      "Out of time"),
    ("other",            "Other"),
]


def safe(fn, *args, **kwargs):
    """Call a persistence helper; never let a bad data dir break the UI flow."""
    try:
        return fn(*args, **kwargs)
    except Exception:
        return None


def _chip_qss(accent: str) -> str:
    """Small toggle-button styling with an unmistakable focus ring."""
    return (
        f"QPushButton {{ background: {theme.SURFACE2}; color: {theme.TEXT};"
        f"  border: 1px solid {theme.BORDER}; border-radius: 6px;"
        f"  padding: 4px 10px; font-size: 12px; }}"
        f"QPushButton:hover {{ border-color: {accent}; }}"
        f"QPushButton:checked {{ border: 1px solid {accent}; color: {accent};"
        f"  font-weight: bold; }}"
        f"QPushButton:focus {{ border: 2px solid {theme.ACCENT}; }}"
    )


class _Chip(QPushButton):
    """A checkable chip whose checked state is shown by a glyph, not just colour."""

    def __init__(self, label: str, parent=None) -> None:
        super().__init__(parent)
        self._label = label
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.toggled.connect(self._sync_text)
        self._sync_text(False)

    def _sync_text(self, checked: bool) -> None:
        self.setText(f"{CHECK_GLYPH} {self._label}" if checked else self._label)

    def plain_label(self) -> str:
        return self._label


class ConfidenceStrip(QWidget):
    """“How sure are you?” — 1–4, asked before the answer is graded.

    Optional and skippable: leaving it untouched records nothing.  The
    “Don't ask” button emits :attr:`opt_out_requested` so the screen can
    persist the opt-out and hide every strip.
    """

    rated             = pyqtSignal(int)
    opt_out_requested = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAccessibleName("Confidence rating")
        self.setAccessibleDescription(
            "Optional: how sure are you, before you see the result?")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(6)

        lbl = QLabel(f"{CONFIDENCE_GLYPH} How sure?")
        lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        lbl.setToolTip("Rate your confidence before submitting — optional")
        row.addWidget(lbl)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[int, _Chip] = {}
        for level, text in CONFIDENCE_LEVELS:
            btn = _Chip(f"{level} {text}")
            btn.setAccessibleName(f"Confidence {level} of 4: {text}")
            btn.setToolTip(f"Confidence {level}/4 — {text}")
            btn.setStyleSheet(_chip_qss(theme.ACCENT))
            btn.clicked.connect(lambda _c, lv=level: self.rated.emit(lv))
            self._group.addButton(btn, level)
            self._buttons[level] = btn
            row.addWidget(btn)

        self._opt_out = QPushButton("Don't ask")
        self._opt_out.setObjectName("flat")
        self._opt_out.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._opt_out.setAccessibleName("Stop asking for confidence ratings")
        self._opt_out.setToolTip(
            "Hide the confidence question from now on "
            "(re-enable it on the Setup screen)")
        self._opt_out.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none;"
            f"  color: {theme.TEXT_MUTED}; padding: 4px 8px; font-size: 11px; }}"
            f"QPushButton:hover {{ color: {theme.TEXT}; }}"
            f"QPushButton:focus {{ border: 2px solid {theme.ACCENT}; border-radius: 6px; }}"
        )
        self._opt_out.clicked.connect(self.opt_out_requested)
        row.addWidget(self._opt_out)
        row.addStretch()

    # ------------------------------------------------------------------

    def value(self) -> int | None:
        """The selected level (1–4), or None when the user skipped it."""
        checked = self._group.checkedId()
        return checked if checked in self._buttons else None

    def set_value(self, level: int | None) -> None:
        for lv, btn in self._buttons.items():
            btn.setChecked(lv == level)

    def clear(self) -> None:
        """Forget the rating (exclusive groups need the ceremony below)."""
        self._group.setExclusive(False)
        for btn in self._buttons.values():
            btn.setChecked(False)
        self._group.setExclusive(True)

    def button(self, level: int) -> QPushButton | None:
        return self._buttons.get(level)


class MistakeRow(QWidget):
    """“What went wrong?” — one chip per cause, plus an optional note.

    The mistake itself is logged the moment the answer is wrong (with
    ``cause=null``); this row only categorises it, so ignoring it loses
    nothing.  :attr:`cause_chosen` and :attr:`note_changed` carry the edits.
    """

    cause_chosen = pyqtSignal(str)
    note_changed = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAccessibleName("What went wrong")
        self.setAccessibleDescription(
            "Optional: categorise this mistake so the pattern can be spotted later")

        # QWidget subclasses only paint a stylesheet background with this set.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 8, 10, 8)
        root.setSpacing(6)
        self.setStyleSheet(
            f"MistakeRow {{ background: {theme.SURFACE2};"
            f"  border: 1px solid {theme.BORDER}; border-radius: 6px; }}")

        top = QHBoxLayout()
        top.setSpacing(6)
        self._title = QLabel(f"{MISTAKE_GLYPH} What went wrong?")
        self._title.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {theme.PARTIAL};")
        self._title.setToolTip("Optional — skip it and the mistake is still logged")
        top.addWidget(self._title)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, _Chip] = {}
        for cause, label in MISTAKE_CAUSE_LABELS:
            btn = _Chip(label)
            btn.setAccessibleName(f"Cause: {label}")
            btn.setToolTip(f"Log the cause of this mistake as “{label}”")
            btn.setStyleSheet(_chip_qss(theme.PARTIAL))
            btn.clicked.connect(lambda _c, key=cause: self._on_cause(key))
            self._group.addButton(btn)
            self._buttons[cause] = btn
            top.addWidget(btn)
        top.addStretch()
        root.addLayout(top)

        self._note = QLineEdit()
        self._note.setPlaceholderText("Optional one-line note — what to remember next time…")
        self._note.setAccessibleName("Optional note about this mistake")
        self._note.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._note.setMaxLength(200)
        self._note.setStyleSheet(
            f"QLineEdit {{ background: {theme.SURFACE}; color: {theme.TEXT};"
            f"  border: 1px solid {theme.BORDER}; border-radius: 6px;"
            f"  padding: 5px 8px; font-size: 12px; }}"
            f"QLineEdit:focus {{ border: 2px solid {theme.ACCENT}; }}")
        self._note.editingFinished.connect(
            lambda: self.note_changed.emit(self._note.text().strip()))
        root.addWidget(self._note)

        self._hint = QLabel("Skippable — the mistake is already saved to your journal.")
        self._hint.setStyleSheet(f"font-size: 11px; color: {theme.TEXT_MUTED};")
        root.addWidget(self._hint)

    # ------------------------------------------------------------------

    def _on_cause(self, cause: str) -> None:
        # cause_chosen carries the note with it, so one click is one write.
        self.cause_chosen.emit(cause)

    def set_context(self, title: str) -> None:
        self._title.setText(f"{MISTAKE_GLYPH} {title}")

    def value(self) -> str | None:
        for cause, btn in self._buttons.items():
            if btn.isChecked():
                return cause
        return None

    def note(self) -> str:
        return self._note.text().strip()

    def reset(self, cause: str | None = None, note: str = "") -> None:
        self._group.setExclusive(False)
        for key, btn in self._buttons.items():
            btn.setChecked(key == cause)
        self._group.setExclusive(True)
        self._note.setText(note)

    def button(self, cause: str) -> QPushButton | None:
        return self._buttons.get(cause)
