"""Confidence-calibration strip — asked BEFORE the answer is revealed.

Four pills (1 guessing → 4 certain) plus a "Don't ask again" opt-out. Entirely
optional: the user can submit without touching it and nothing is recorded.
The pairing with the graded outcome is written by the caller once the answer
has been marked, via ``persistence.log_confidence``.

Accessibility: every pill is a tab-reachable QPushButton with an accessible
name and a visible focus ring (see ``ui/theme.py``); the chosen pill is marked
with a "✓" glyph and a text readout as well as the accent fill, so the state is
never carried by colour alone.
"""
from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QButtonGroup, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal

from persistence import (
    CONFIDENCE_LABELS, confidence_prompt_enabled, set_confidence_prompt_enabled,
)
from ui import theme

_PROMPT = "How sure are you?"


class ConfidenceStrip(QWidget):
    """A skippable 1–4 confidence picker. ``rating()`` is None until used."""

    rating_changed = pyqtSignal(int)      # 1–4
    opted_out      = pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rating: int | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        self._prompt_lbl = QLabel(_PROMPT)
        self._prompt_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {theme.TEXT_MUTED};")
        row.addWidget(self._prompt_lbl)

        self._group = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[int, QPushButton] = {}
        for level in (1, 2, 3, 4):
            label = CONFIDENCE_LABELS[level]
            btn = QPushButton(f"{level} · {label}")
            btn.setObjectName("pill")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setAccessibleName(f"Confidence {level} of 4: {label}")
            btn.setAccessibleDescription(
                "Optional. Record how sure you are before submitting.")
            btn.setToolTip(f"Confidence {level}/4 — {label}")
            btn.clicked.connect(lambda _=False, lv=level: self._on_pick(lv))
            self._group.addButton(btn, level)
            self._buttons[level] = btn
            row.addWidget(btn)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(f"font-size: 12px; color: {theme.ACCENT};")
        self._status_lbl.setAccessibleName("Selected confidence")
        row.addWidget(self._status_lbl)

        row.addStretch()

        self._optout_btn = QPushButton("Don't ask again")
        self._optout_btn.setObjectName("flat")
        self._optout_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._optout_btn.setAccessibleName("Stop asking for confidence ratings")
        self._optout_btn.setToolTip(
            "Hide the confidence strip in this app from now on.")
        self._optout_btn.clicked.connect(self._on_opt_out)
        row.addWidget(self._optout_btn)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    # ── API ───────────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear the pick and re-read the opt-out; call per question."""
        self._rating = None
        self._group.setExclusive(False)
        for level, btn in self._buttons.items():
            btn.setChecked(False)
            btn.setEnabled(True)
            btn.setText(f"{level} · {CONFIDENCE_LABELS[level]}")
        self._group.setExclusive(True)
        self._status_lbl.setText("")
        try:
            enabled = confidence_prompt_enabled()
        except Exception:
            enabled = True
        self.setVisible(enabled)

    def rating(self) -> int | None:
        return self._rating

    def set_rating(self, level: int) -> None:
        """Programmatic equivalent of clicking a pill (used by tests)."""
        if level in self._buttons:
            self._buttons[level].setChecked(True)
            self._on_pick(level)

    def lock(self) -> None:
        """Disable the pills once the answer is in, so the rating can't be
        edited with hindsight. The opt-out stays live — a user who dislikes the
        strip must be able to dismiss it at any moment."""
        for btn in self._buttons.values():
            btn.setEnabled(False)

    def unlock(self) -> None:
        for btn in self._buttons.values():
            btn.setEnabled(True)

    # ── Internals ─────────────────────────────────────────────────────────────

    def _on_pick(self, level: int) -> None:
        self._rating = level
        for lv, btn in self._buttons.items():
            btn.setText(
                (f"✓ {lv} · {CONFIDENCE_LABELS[lv]}" if lv == level
                 else f"{lv} · {CONFIDENCE_LABELS[lv]}"))
        self._status_lbl.setText(f"✓ {CONFIDENCE_LABELS[level]}")
        self.rating_changed.emit(level)

    def _on_opt_out(self) -> None:
        try:
            set_confidence_prompt_enabled(False)
        except Exception:
            pass
        self._rating = None
        self.hide()
        self.opted_out.emit()
