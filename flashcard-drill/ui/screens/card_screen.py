"""Main flashcard screen — shows front, flips on reveal, takes rating.

Keyboard: Space / Return / Enter reveal the current card; 1 / 2 / 3 rate it
(Got it / Unsure / Missed).  The screen itself owns keyboard focus — every
button is ``NoFocus`` — so Space can never "click" a stray button such as
End Session (which used to end the session on the first keypress).
"""
from __future__ import annotations
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import Flashcard, DrillConfig, Rating, CardResult, SessionStats
from core.deck import build_deck
from ui import theme
from ui.widgets.timer_widget import TimerWidget

_FLAG_ON  = "⚑ Flagged — click to unflag"
_FLAG_OFF = "⚑ Flag for Review"


class CardScreen(QWidget):
    session_complete  = pyqtSignal(object)   # SessionStats
    back_requested    = pyqtSignal()
    flag_toggled      = pyqtSignal(str, bool)  # card_id, new_state

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._deck: list[Flashcard] = []
        self._idx  = 0
        self._stats = SessionStats()
        self._timer_secs = 0
        self._shown_at: float | None = None
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(48, 32, 48, 24)
        root.setSpacing(16)

        # Progress row
        prog_row = QHBoxLayout()
        self._progress_lbl = QLabel("")
        self._progress_lbl.setStyleSheet(f"color: {theme.TEXT_MUTED}; font-size: 13px;")
        prog_row.addWidget(self._progress_lbl)
        prog_row.addStretch()
        self._timer_widget = TimerWidget(0)
        prog_row.addWidget(self._timer_widget)
        self._end_btn = QPushButton("End Session")
        self._end_btn.setObjectName("flat")
        self._end_btn.clicked.connect(self._on_end_session)
        prog_row.addWidget(self._end_btn)
        root.addLayout(prog_row)

        # Category badge
        self._cat_lbl = QLabel("")
        self._cat_lbl.setStyleSheet(
            f"font-size: 11px; font-weight: bold; color: {theme.TEXT_MUTED};"
        )
        root.addWidget(self._cat_lbl)

        # Card frame
        self._card_frame = QFrame()
        self._card_frame.setObjectName("card")
        card_layout = QVBoxLayout(self._card_frame)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(24)

        self._front_lbl = QLabel("")
        self._front_lbl.setObjectName("card_front")
        self._front_lbl.setWordWrap(True)
        self._front_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self._front_lbl)

        self._divider = QFrame()
        self._divider.setObjectName("separator")
        self._divider.hide()
        card_layout.addWidget(self._divider)

        self._back_lbl = QLabel("")
        self._back_lbl.setObjectName("card_back")
        self._back_lbl.setWordWrap(True)
        self._back_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._back_lbl.hide()
        card_layout.addWidget(self._back_lbl)

        root.addWidget(self._card_frame, 1)

        # Reveal button
        self._reveal_btn = QPushButton("Reveal Answer")
        self._reveal_btn.setObjectName("accent")
        self._reveal_btn.setToolTip("Space / Enter")
        self._reveal_btn.clicked.connect(self._reveal)

        reveal_row = QHBoxLayout()
        reveal_row.addStretch()
        reveal_row.addWidget(self._reveal_btn)
        reveal_row.addStretch()
        self._reveal_container = QWidget()
        self._reveal_container.setLayout(reveal_row)
        root.addWidget(self._reveal_container)

        # Rating buttons
        self._rating_widget = QWidget()
        rating_row = QHBoxLayout(self._rating_widget)
        rating_row.setSpacing(16)
        rating_row.addStretch()
        self._got_btn  = QPushButton("✓  Got it")
        self._got_btn.setObjectName("got_it")
        self._got_btn.setToolTip("Key 1")
        self._got_btn.clicked.connect(lambda: self._rate(Rating.GOT_IT))
        self._unsure_btn = QPushButton("~  Unsure")
        self._unsure_btn.setObjectName("unsure")
        self._unsure_btn.setToolTip("Key 2")
        self._unsure_btn.clicked.connect(lambda: self._rate(Rating.UNSURE))
        self._missed_btn = QPushButton("✗  Missed")
        self._missed_btn.setObjectName("missed")
        self._missed_btn.setToolTip("Key 3")
        self._missed_btn.clicked.connect(lambda: self._rate(Rating.MISSED))
        for b in (self._got_btn, self._unsure_btn, self._missed_btn):
            rating_row.addWidget(b)
        rating_row.addStretch()
        self._rating_widget.hide()
        root.addWidget(self._rating_widget)

        # Flag button row
        self._flag_row = QHBoxLayout()
        self._flag_btn = QPushButton(_FLAG_OFF)
        self._flag_btn.setObjectName("flat")
        self._flag_btn.clicked.connect(self._on_flag)
        self._flag_row.addStretch()
        self._flag_row.addWidget(self._flag_btn)
        self._flag_row.addStretch()
        self._flag_container = QWidget()
        self._flag_container.setLayout(self._flag_row)
        self._flag_container.hide()
        root.addWidget(self._flag_container)

        # Keyboard focus stays on the screen: no button may take it, so Space /
        # Return always reach keyPressEvent instead of activating a button.
        for b in (self._end_btn, self._reveal_btn, self._got_btn,
                  self._unsure_btn, self._missed_btn, self._flag_btn):
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    # ------------------------------------------------------------------
    # Session control
    # ------------------------------------------------------------------

    def start(self, config: DrillConfig) -> bool:
        """Build a deck for *config* and show its first card.

        Returns False — and leaves the screen untouched, emitting nothing —
        when the deck is empty (e.g. "Show Flagged Only" with no flags), so an
        empty session is never completed or saved.
        """
        return self.start_deck(build_deck(config), config.timer_secs)

    def start_deck(self, deck: list[Flashcard], timer_secs: int = 0) -> bool:
        """Drill an explicit *deck* (used by Review Missed).  False if empty."""
        if not deck:
            return False
        self._deck = list(deck)
        self._idx  = 0
        self._timer_secs = timer_secs
        self._stats = SessionStats()
        self._show_card()
        return True

    @property
    def deck(self) -> list[Flashcard]:
        return list(self._deck)

    @property
    def current_card(self) -> Flashcard | None:
        return self._deck[self._idx] if self._idx < len(self._deck) else None

    @property
    def is_revealed(self) -> bool:
        return not self._rating_widget.isHidden()

    def _show_card(self) -> None:
        if self._idx >= len(self._deck):
            self.session_complete.emit(self._stats)
            return

        card = self._deck[self._idx]
        self._progress_lbl.setText(f"Card {self._idx + 1} of {len(self._deck)}")
        self._cat_lbl.setText(card.category.upper())
        color = theme.CATEGORY_COLORS.get(card.category, theme.ACCENT)
        self._cat_lbl.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color};")

        self._front_lbl.setText(card.front)
        self._back_lbl.setText(card.back)
        self._back_lbl.hide()
        self._divider.hide()
        self._reveal_container.show()
        self._rating_widget.hide()
        self._flag_container.hide()
        self._flag_btn.setToolTip("")

        self._timer_widget.reset(self._timer_secs)
        try:
            self._timer_widget.time_up.disconnect()
        except (TypeError, RuntimeError):
            # PyQt6 raises TypeError when the signal has no connections yet
            # (first card of the first session); older bindings raised RuntimeError.
            pass
        self._timer_widget.time_up.connect(self._on_time_up)
        self._timer_widget.start()
        self._shown_at = time.monotonic()
        self.setFocus()

    def _reveal(self) -> None:
        if self._idx >= len(self._deck) or self.is_revealed:
            return
        self._timer_widget.stop()
        self._back_lbl.show()
        self._divider.show()
        self._reveal_container.hide()
        self._rating_widget.show()
        self._flag_container.show()
        self._flag_btn.setText(_FLAG_ON if self._is_flagged() else _FLAG_OFF)
        self.setFocus()

    def _is_flagged(self) -> bool:
        try:
            from persistence.storage import load_flagged
            return self._deck[self._idx].id in load_flagged()
        except Exception:
            return False

    def _on_time_up(self) -> None:
        self._reveal()

    def _on_end_session(self) -> None:
        self._timer_widget.stop()
        if self._stats.total > 0:
            self.session_complete.emit(self._stats)
        else:
            self.back_requested.emit()

    def _on_flag(self) -> None:
        if self._idx >= len(self._deck):
            return
        card = self._deck[self._idx]
        try:
            from persistence.storage import toggle_flag
            new_state = toggle_flag(card.id)
        except Exception as exc:
            # Nothing was persisted: keep the button truthful (re-read the real
            # state) and surface the error instead of pretending it worked.
            self._flag_btn.setText(_FLAG_ON if self._is_flagged() else _FLAG_OFF)
            self._flag_btn.setToolTip(f"Could not save flag: {exc}")
            return
        self._flag_btn.setToolTip("")
        self._flag_btn.setText(_FLAG_ON if new_state else _FLAG_OFF)
        self.flag_toggled.emit(card.id, new_state)

    # ------------------------------------------------------------------
    # Keyboard / focus
    # ------------------------------------------------------------------

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        self.setFocus()

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if self._idx < len(self._deck):
            if not self.is_revealed:
                if key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self._reveal()
                    return
            else:
                if key == Qt.Key.Key_1:
                    self._rate(Rating.GOT_IT)
                    return
                elif key == Qt.Key.Key_2:
                    self._rate(Rating.UNSURE)
                    return
                elif key == Qt.Key.Key_3:
                    self._rate(Rating.MISSED)
                    return
        super().keyPressEvent(event)

    def _rate(self, rating: Rating) -> None:
        if self._idx >= len(self._deck):
            return
        card = self._deck[self._idx]
        elapsed = (time.monotonic() - self._shown_at) if self._shown_at is not None else None
        self._stats.total += 1
        if rating == Rating.GOT_IT:
            self._stats.got_it += 1
        elif rating == Rating.UNSURE:
            self._stats.unsure += 1
        else:
            self._stats.missed += 1
        self._stats.results.append(CardResult(
            card_id=card.id, category=card.category, rating=rating.value,
            elapsed_secs=elapsed,
        ))
        self._idx += 1
        self._show_card()
