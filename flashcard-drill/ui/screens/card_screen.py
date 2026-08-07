"""Main flashcard screen — shows front, flips on reveal, takes rating."""
from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from core.models import Flashcard, DrillConfig, Rating, CardResult, SessionStats
from core.deck import build_deck
from ui import theme
from ui.widgets.timer_widget import TimerWidget


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
        end_btn = QPushButton("End Session")
        end_btn.setObjectName("flat")
        end_btn.clicked.connect(self._on_end_session)
        prog_row.addWidget(end_btn)
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
        self._got_btn.clicked.connect(lambda: self._rate(Rating.GOT_IT))
        self._unsure_btn = QPushButton("~  Unsure")
        self._unsure_btn.setObjectName("unsure")
        self._unsure_btn.clicked.connect(lambda: self._rate(Rating.UNSURE))
        self._missed_btn = QPushButton("✗  Missed")
        self._missed_btn.setObjectName("missed")
        self._missed_btn.clicked.connect(lambda: self._rate(Rating.MISSED))
        for b in (self._got_btn, self._unsure_btn, self._missed_btn):
            rating_row.addWidget(b)
        rating_row.addStretch()
        self._rating_widget.hide()
        root.addWidget(self._rating_widget)

        # Flag button row
        self._flag_row = QHBoxLayout()
        self._flag_btn = QPushButton("⚑ Flag for Review")
        self._flag_btn.setObjectName("flat")
        self._flag_btn.clicked.connect(self._on_flag)
        self._flag_row.addStretch()
        self._flag_row.addWidget(self._flag_btn)
        self._flag_row.addStretch()
        self._flag_container = QWidget()
        self._flag_container.setLayout(self._flag_row)
        self._flag_container.hide()
        root.addWidget(self._flag_container)

    def start(self, config: DrillConfig) -> None:
        self._deck = build_deck(config)
        self._idx  = 0
        self._timer_secs = config.timer_secs
        self._stats = SessionStats()
        self._show_card()

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

        self._timer_widget.reset(self._timer_secs)
        try:
            self._timer_widget.time_up.disconnect()
        except RuntimeError:
            pass
        self._timer_widget.time_up.connect(self._on_time_up)
        self._timer_widget.start()

    def _reveal(self) -> None:
        self._timer_widget.stop()
        self._back_lbl.show()
        self._divider.show()
        self._reveal_container.hide()
        self._rating_widget.show()
        self._flag_container.show()
        try:
            from persistence.storage import load_flagged
            flagged_ids = load_flagged()
            card = self._deck[self._idx]
            if card.id in flagged_ids:
                self._flag_btn.setText("⚑ Flagged — click to unflag")
            else:
                self._flag_btn.setText("⚑ Flag for Review")
        except Exception:
            self._flag_btn.setText("⚑ Flag for Review")

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
        except Exception:
            new_state = True
        if new_state:
            self._flag_btn.setText("⚑ Flagged — click to unflag")
        else:
            self._flag_btn.setText("⚑ Flag for Review")
        self.flag_toggled.emit(card.id, new_state)

    def keyPressEvent(self, event) -> None:
        from PyQt6.QtCore import Qt as _Qt
        key = event.key()
        if self._reveal_container.isVisible():
            if key in (_Qt.Key.Key_Space, _Qt.Key.Key_Return, _Qt.Key.Key_Enter):
                self._reveal()
                return
        elif self._rating_widget.isVisible():
            if key == _Qt.Key.Key_1:
                self._rate(Rating.GOT_IT)
                return
            elif key == _Qt.Key.Key_2:
                self._rate(Rating.UNSURE)
                return
            elif key == _Qt.Key.Key_3:
                self._rate(Rating.MISSED)
                return
        super().keyPressEvent(event)

    def _rate(self, rating: Rating) -> None:
        card = self._deck[self._idx]
        self._stats.total += 1
        if rating == Rating.GOT_IT:
            self._stats.got_it += 1
        elif rating == Rating.UNSURE:
            self._stats.unsure += 1
        else:
            self._stats.missed += 1
        self._stats.results.append(CardResult(
            card_id=card.id, category=card.category, rating=rating.value
        ))
        self._idx += 1
        self._show_card()
