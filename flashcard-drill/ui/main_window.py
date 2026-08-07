"""Main application window for flashcard-drill."""
from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from config import WINDOW_TITLE, WINDOW_MIN_SIZE
from ui.screens.setup_screen import SetupScreen
from ui.screens.card_screen import CardScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.browse_screen import BrowseScreen
from persistence.storage import save_session

PAGE_SETUP   = 0
PAGE_CARDS   = 1
PAGE_SUMMARY = 2
PAGE_HISTORY = 3
PAGE_BROWSE  = 4


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumSize(*WINDOW_MIN_SIZE)
        self.resize(960, 700)

        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        self._setup   = SetupScreen()
        self._cards   = CardScreen()
        self._summary = SummaryScreen()
        self._history = HistoryScreen()
        self._browse  = BrowseScreen()

        for w in (self._setup, self._cards, self._summary, self._history, self._browse):
            self._stack.addWidget(w)

        self._setup.drill_started.connect(self._on_drill_started)
        self._setup.history_requested.connect(self._on_history)
        self._setup.browse_requested.connect(self._on_browse)
        self._cards.session_complete.connect(self._on_session_complete)
        self._cards.back_requested.connect(self._go_setup)
        self._cards.flag_toggled.connect(self._on_flag_toggled)
        self._summary.drill_again.connect(self._on_drill_again)
        self._summary.back_requested.connect(self._go_setup)
        self._summary.review_missed.connect(self._on_review_missed)
        self._history.back_requested.connect(self._go_setup)
        self._browse.back_requested.connect(self._go_setup)

        self._last_config = None
        self._last_stats = None

    def _on_drill_started(self, config) -> None:
        self._last_config = config
        self._cards.start(config)
        self._stack.setCurrentIndex(PAGE_CARDS)

    def _on_session_complete(self, stats) -> None:
        self._last_stats = stats
        save_session(stats)
        self._summary.show_stats(stats)
        self._stack.setCurrentIndex(PAGE_SUMMARY)

    def _on_drill_again(self) -> None:
        if self._last_config:
            self._cards.start(self._last_config)
            self._stack.setCurrentIndex(PAGE_CARDS)
        else:
            self._go_setup()

    def _on_flag_toggled(self, card_id: str, flagged: bool) -> None:
        pass  # card_screen already called toggle_flag; nothing else needed here

    def _on_review_missed(self) -> None:
        if self._last_config is None:
            self._go_setup()
            return
        if not hasattr(self, '_last_stats') or self._last_stats is None:
            self._go_setup()
            return
        from core.deck import all_cards
        missed_ids = {r.card_id for r in self._last_stats.results if r.rating == "missed"}
        if not missed_ids:
            self._go_setup()
            return
        pool = [c for c in all_cards() if c.id in missed_ids]
        if not pool:
            self._go_setup()
            return
        from core.models import SessionStats
        self._cards._deck = pool
        self._cards._idx = 0
        self._cards._stats = SessionStats()
        self._cards._timer_secs = self._last_config.timer_secs
        self._cards._show_card()
        self._stack.setCurrentIndex(PAGE_CARDS)

    def _on_history(self) -> None:
        self._history.refresh()
        self._stack.setCurrentIndex(PAGE_HISTORY)

    def _on_browse(self) -> None:
        self._browse.load_all()
        self._stack.setCurrentIndex(PAGE_BROWSE)

    def _go_setup(self) -> None:
        self._stack.setCurrentIndex(PAGE_SETUP)
