"""Main flashcard screen — shows front, flips on reveal, takes rating.

Keyboard: Space / Return / Enter reveal the current card; 1 / 2 / 3 rate it
(Got it / Unsure / Missed); 1 / 2 / 3 / 4 *before* the reveal set the confidence
strip instead; ``W`` jumps to the "what went wrong?" row after a miss and Escape
dismisses it.  The screen itself owns keyboard focus — every button in the drill
flow (End Session, Reveal, the three ratings, Flag) is ``NoFocus`` — so Space can
never "click" a stray button such as End Session (which used to end the session
on the first keypress).  The review-feedback controls added on top of that flow
*are* Tab-reachable (accessibility), and hand focus straight back to the screen
when activated, so the drill shortcuts keep working.

Two optional review features hang off the same flow, both persisted through
:mod:`persistence.review_store` and neither able to disturb the drill:

* **Confidence strip** — shown with the card *front*, before the answer can be
  seen, so the rating cannot be hindsight.  Skippable, and "Don't ask" stores an
  opt-out the setup screen can undo.
* **Mistake journal** — a "Missed" rating logs the card (``cause=null``) and pops
  a compact, skippable cause row carrying the question and the answer.  Rating
  the next card, Escape or Dismiss closes it; nothing is ever blocked and no
  modal appears.  Rating the card "Got it" later resolves the entry.

The SM-2 schedule update is untouched by all of this: a journalled mistake is
analysis, never a second lapse.
"""
from __future__ import annotations
import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit,
    QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import Flashcard, DrillConfig, Rating, CardResult, SessionStats
from core.deck import build_deck
from ui import theme
from ui.widgets.timer_widget import TimerWidget

_FLAG_ON  = "⚑ Flagged — click to unflag"
_FLAG_OFF = "⚑ Flag for Review"

_OFF_GLYPH = "○"      # ○ — state is never encoded in colour alone
_ON_GLYPH  = "●"      # ●

# Confidence levels, in strip order: (value, label, what it means).
_CONFIDENCE_CHOICES = (
    (1, "Guessing",    "a pure guess"),
    (2, "Unsure",      "leaning one way, not sure"),
    (3, "Fairly sure", "fairly sure"),
    (4, "Certain",     "certain"),
)
_CAUSES_PER_ROW = 3


class CardScreen(QWidget):
    session_complete  = pyqtSignal(object)   # SessionStats
    back_requested    = pyqtSignal()
    flag_toggled      = pyqtSignal(str, bool)  # card_id, new_state
    mistake_logged    = pyqtSignal(str, object)  # card_id, cause (str | None)
    confidence_set    = pyqtSignal(str, int)     # card_id, 1-4

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._deck: list[Flashcard] = []
        self._idx  = 0
        self._stats = SessionStats()
        self._timer_secs = 0
        self._shown_at: float | None = None
        # Review feedback (both optional, neither on the drill's critical path).
        self._confidence: int | None = None       # this card, before the reveal
        self._confidence_on = self._confidence_pref()
        self._pending_mistake: dict | None = None  # journal entry awaiting a cause
        self._pending_cause: str | None = None
        self._cause_written = False                # a cause/note reached the file
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

        # Confidence strip — with the FRONT, before anything can be revealed.
        root.addWidget(self._build_confidence_strip())

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

        # Mistake journal — "what went wrong?" after a Missed rating.
        root.addWidget(self._build_cause_row())

        # Keyboard focus stays on the screen: no button in the drill flow may take
        # it, so Space / Return always reach keyPressEvent instead of activating a
        # button.  (The review-feedback controls built above are deliberately
        # Tab-reachable and hand focus back when used — see _build_cause_row.)
        for b in (self._end_btn, self._reveal_btn, self._got_btn,
                  self._unsure_btn, self._missed_btn, self._flag_btn):
            b.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    # ------------------------------------------------------------------
    # Confidence strip (shown with the card front)
    # ------------------------------------------------------------------

    def _build_confidence_strip(self) -> QWidget:
        self._confidence_container = QWidget()
        row = QHBoxLayout(self._confidence_container)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addStretch()

        prompt = QLabel("How sure are you?")
        prompt.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        row.addWidget(prompt)

        self._confidence_btns: dict[int, QPushButton] = {}
        for value, label, meaning in _CONFIDENCE_CHOICES:
            btn = QPushButton(f"{_OFF_GLYPH} {value} {label}")
            btn.setObjectName("conf_btn")
            btn.setCheckable(True)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setAccessibleName(f"Confidence {value} of 4: {label}")
            btn.setAccessibleDescription(f"Record that you are {meaning} before revealing")
            btn.setToolTip(f"Key {value} — {meaning}")
            btn.clicked.connect(lambda _=False, v=value: self._set_confidence(v))
            self._confidence_btns[value] = btn
            row.addWidget(btn)

        self._confidence_off_btn = QPushButton("Don't ask")
        self._confidence_off_btn.setObjectName("conf_opt_out")
        self._confidence_off_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._confidence_off_btn.setAccessibleName("Stop asking for my confidence")
        self._confidence_off_btn.setToolTip(
            "Hide the confidence strip for good — re-enable it on the setup screen")
        self._confidence_off_btn.clicked.connect(self._on_confidence_opt_out)
        row.addWidget(self._confidence_off_btn)
        row.addStretch()

        self._confidence_container.hide()
        return self._confidence_container

    @staticmethod
    def _confidence_pref() -> bool:
        try:
            from persistence.review_store import confidence_enabled
            return confidence_enabled()
        except Exception:
            return True

    def _paint_confidence(self) -> None:
        for value, btn in self._confidence_btns.items():
            chosen = (value == self._confidence)
            btn.setChecked(chosen)
            label = dict((v, l) for v, l, _ in _CONFIDENCE_CHOICES)[value]
            btn.setText(f"{_ON_GLYPH if chosen else _OFF_GLYPH} {value} {label}")

    def _set_confidence(self, value: int) -> None:
        """Remember this card's pre-reveal confidence (toggles off when re-picked)."""
        if self._idx >= len(self._deck) or not self._confidence_on or self.is_revealed:
            return
        self._confidence = None if self._confidence == value else value
        self._paint_confidence()
        if self._confidence is not None:
            self.confidence_set.emit(self._deck[self._idx].id, self._confidence)
        self.setFocus()             # keep Space / digits working after a click

    def _on_confidence_opt_out(self) -> None:
        self._confidence = None
        self._confidence_on = False
        self._confidence_container.hide()
        try:
            from persistence.review_store import set_confidence_enabled
            set_confidence_enabled(False)
        except Exception:
            pass                    # the strip is still hidden for this session
        self.setFocus()

    def _log_confidence(self, card: Flashcard, rating: Rating) -> None:
        """Pair this card's confidence with the grade, once the answer is graded."""
        if self._confidence is None:
            return
        try:
            from persistence.review_store import log_confidence
            log_confidence(card.id, card.category, self._confidence,
                           correct=(rating == Rating.GOT_IT))
        except Exception:
            pass                    # calibration is never worth losing a rating over

    # ------------------------------------------------------------------
    # Mistake journal ("what went wrong?")
    # ------------------------------------------------------------------

    def _build_cause_row(self) -> QWidget:
        from persistence.review_store import CAUSES, CAUSE_LABELS

        self._cause_container = QFrame()
        self._cause_container.setObjectName("card")
        box = QVBoxLayout(self._cause_container)
        box.setContentsMargins(16, 10, 16, 12)
        box.setSpacing(6)

        self._cause_question_lbl = QLabel("")
        self._cause_question_lbl.setWordWrap(True)
        self._cause_question_lbl.setStyleSheet(
            f"font-size: 12px; font-weight: bold; color: {theme.ERROR};")
        box.addWidget(self._cause_question_lbl)

        self._cause_answer_lbl = QLabel("")
        self._cause_answer_lbl.setWordWrap(True)
        self._cause_answer_lbl.setStyleSheet(f"font-size: 12px; color: {theme.TEXT_MUTED};")
        box.addWidget(self._cause_answer_lbl)

        head = QHBoxLayout()
        head.setContentsMargins(0, 0, 0, 0)
        prompt = QLabel("What went wrong?")
        prompt.setStyleSheet(f"font-size: 12px; color: {theme.TEXT};")
        head.addWidget(prompt)
        head.addStretch()
        self._cause_dismiss_btn = QPushButton("✕ Dismiss")
        self._cause_dismiss_btn.setObjectName("cause_dismiss")
        self._cause_dismiss_btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._cause_dismiss_btn.setAccessibleName("Dismiss the what-went-wrong row")
        self._cause_dismiss_btn.setToolTip("Escape — the mistake stays logged, uncategorised")
        self._cause_dismiss_btn.clicked.connect(self._hide_cause_row)
        head.addWidget(self._cause_dismiss_btn)
        box.addLayout(head)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)
        self._cause_btns: dict[str, QPushButton] = {}
        for i, cause in enumerate(CAUSES):
            btn = QPushButton(f"{_OFF_GLYPH} {CAUSE_LABELS[cause]}")
            btn.setObjectName("cause_btn")
            btn.setCheckable(True)
            btn.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            btn.setAccessibleName(f"Cause: {CAUSE_LABELS[cause]}")
            btn.setAccessibleDescription("Categorise why this card was missed")
            btn.clicked.connect(lambda _=False, c=cause: self._on_cause(c))
            self._cause_btns[cause] = btn
            grid.addWidget(btn, i // _CAUSES_PER_ROW, i % _CAUSES_PER_ROW)
        box.addLayout(grid)

        self._cause_note = QLineEdit()
        self._cause_note.setObjectName("cause_note")
        self._cause_note.setPlaceholderText("Optional one-line note…")
        self._cause_note.setMaxLength(200)
        self._cause_note.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self._cause_note.setAccessibleName("Note about this mistake")
        self._cause_note.editingFinished.connect(self._commit_note)
        box.addWidget(self._cause_note)

        self._cause_container.hide()
        return self._cause_container

    @property
    def cause_row_visible(self) -> bool:
        return not self._cause_container.isHidden()

    def _log_mistake(self, card: Flashcard) -> None:
        """Journal a missed card immediately, cause unset — nothing is ever lost."""
        self._pending_mistake = None
        self._pending_cause = None
        self._cause_written = False
        try:
            from persistence.review_store import log_mistake
            self._pending_mistake = log_mistake(
                card.id,
                category=card.category,
                question=card.front,
                your_answer="Self-rated: Missed (no recall)",
                correct_answer=card.back,
            )
        except Exception:
            self._pending_mistake = None
        self.mistake_logged.emit(card.id, None)

    def _show_cause_row(self, card: Flashcard) -> None:
        from persistence.review_store import clip_text

        self._paint_causes()
        self._cause_note.clear()
        self._cause_question_lbl.setText(f"✗ Missed · {clip_text(card.front, 120)}")
        self._cause_answer_lbl.setText(f"Answer: {clip_text(card.back, 160)}")
        self._cause_container.setVisible(self._pending_mistake is not None)

    def _paint_causes(self) -> None:
        from persistence.review_store import CAUSE_LABELS

        for cause, btn in self._cause_btns.items():
            chosen = (cause == self._pending_cause)
            btn.setChecked(chosen)
            btn.setText(f"{_ON_GLYPH if chosen else _OFF_GLYPH} {CAUSE_LABELS[cause]}")

    def _on_cause(self, cause: str) -> None:
        """Categorise the pending mistake (clicking the same cause clears it)."""
        if self._pending_mistake is None:
            return
        self._pending_cause = None if self._pending_cause == cause else cause
        self._paint_causes()
        self._save_cause()
        self.mistake_logged.emit(self._pending_mistake["id"], self._pending_cause)
        self.setFocus()

    def _commit_note(self) -> None:
        if self._pending_mistake is None:
            return
        self._save_cause()

    def _save_cause(self) -> None:
        """Push the current cause/note onto the logged entry (no-op until there is one)."""
        entry = self._pending_mistake
        if entry is None:
            return
        if self._pending_cause is None and not self._cause_note.text().strip() \
                and not self._cause_written:
            return                  # nothing to say yet: leave the entry as logged
        try:
            from persistence.review_store import set_mistake_cause
            self._cause_written = set_mistake_cause(
                entry["id"], self._pending_cause,
                note=self._cause_note.text(),
                timestamp=entry["timestamp"]) or self._cause_written
        except Exception:
            pass                    # journalling must never interrupt the drill

    def _hide_cause_row(self) -> None:
        """Close the row; the entry keeps whatever cause/note it already has."""
        if self._pending_mistake is not None:
            self._save_cause()
        self._pending_mistake = None
        self._pending_cause = None
        self._cause_written = False
        self._cause_container.hide()
        self.setFocus()

    def _focus_cause_row(self) -> None:
        if self.cause_row_visible:
            next(iter(self._cause_btns.values())).setFocus()

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
        self._hide_cause_row()                    # nothing carries over between sessions
        self._confidence_on = self._confidence_pref()
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
            # Leaving the screen: close the cause row so it cannot reappear stale
            # on the next session (the entry itself is already journalled).
            self._hide_cause_row()
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

        # Confidence is asked per card, before anything can be revealed.
        self._confidence = None
        self._paint_confidence()
        self._confidence_container.setVisible(self._confidence_on)

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
        self._confidence_container.hide()   # the rating must not be hindsight
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
        self._hide_cause_row()
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
        # Review-feedback shortcuts first; neither collides with the drill keys.
        if key == Qt.Key.Key_W and self.cause_row_visible:
            self._focus_cause_row()
            return
        if key == Qt.Key.Key_Escape and self.cause_row_visible:
            self._hide_cause_row()
            return
        if self._idx < len(self._deck):
            if not self.is_revealed:
                if key in (Qt.Key.Key_Space, Qt.Key.Key_Return, Qt.Key.Key_Enter):
                    self._reveal()
                    return
                # Digits before the reveal set the confidence strip, not a rating.
                if self._confidence_on:
                    level = {Qt.Key.Key_1: 1, Qt.Key.Key_2: 2,
                             Qt.Key.Key_3: 3, Qt.Key.Key_4: 4}.get(key)
                    if level is not None:
                        self._set_confidence(level)
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
        # Rating the next card ends the window for the previous card's cause row
        # (its note, if any, is written before the row closes).
        self._hide_cause_row()
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
        # SM-2 first and unchanged: the journal below never feeds the scheduler,
        # so a logged mistake can never double-count as a lapse.
        self._record_schedule(card.id, rating)
        self._log_confidence(card, rating)
        if rating == Rating.MISSED:
            self._log_mistake(card)         # cause unset — nothing is ever lost
        elif rating == Rating.GOT_IT:
            self._resolve_mistakes(card.id)
        self._idx += 1
        self._show_card()
        if rating == Rating.MISSED and self._idx < len(self._deck):
            # The skippable cause row is raised over the *next* card, so the
            # drill itself is never held up and no modal ever appears.
            self._show_cause_row(card)

    @staticmethod
    def _schedule_outcome(card_id: str, rating: Rating):
        """Persist one SM-2 review; ``None`` if the schedule could not be written.

        Isolated (and swallowing every error) so a read-only data directory or a
        corrupt schedule file can never interrupt a drill in progress.
        """
        try:
            from persistence.schedule_store import record_rating
            return record_rating(card_id, rating.value)
        except Exception:
            return None

    def _record_schedule(self, card_id: str, rating: Rating) -> None:
        outcome = self._schedule_outcome(card_id, rating)
        if outcome is not None:
            self._stats.schedule.append(outcome)

    @staticmethod
    def _resolve_mistakes(card_id: str) -> None:
        """A later "Got it" closes every open journal entry for the card."""
        try:
            from persistence.review_store import resolve_mistakes
            resolve_mistakes(card_id)
        except Exception:
            pass
