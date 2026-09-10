"""Main application window for flashcard-drill."""
from __future__ import annotations
from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from config import WINDOW_TITLE, WINDOW_MIN_SIZE
from ui.screens.setup_screen import SetupScreen
from ui.screens.card_screen import CardScreen
from ui.screens.summary_screen import SummaryScreen
from ui.screens.history_screen import HistoryScreen
from ui.screens.browse_screen import BrowseScreen
from ui.screens.reference_screen import ReferenceScreen
from persistence.storage import save_session

PAGE_SETUP     = 0
PAGE_CARDS     = 1
PAGE_SUMMARY   = 2
PAGE_HISTORY   = 3
PAGE_BROWSE    = 4
PAGE_REFERENCE = 5


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
        self._reference = ReferenceScreen()

        for w in (self._setup, self._cards, self._summary, self._history,
                  self._browse, self._reference):
            self._stack.addWidget(w)

        self._setup.drill_started.connect(self._on_drill_started)
        self._setup.history_requested.connect(self._on_history)
        self._setup.browse_requested.connect(self._on_browse)
        self._setup.reference_requested.connect(self._on_reference)
        self._reference.back_requested.connect(self._go_setup)
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

    _EMPTY_DECK_NOTICE = ("No cards match that configuration"
                          " — flag some cards or pick other categories.")

    def _on_drill_started(self, config) -> None:
        self._last_config = config
        self._start_cards(config)

    def _start_cards(self, config) -> None:
        """Start a drill for *config*; stay on Setup (with a notice) if the deck is empty."""
        if not self._cards.start(config):
            self._setup.show_notice(self._EMPTY_DECK_NOTICE)
            self._go_setup()
            return
        self._setup.clear_notice()
        self._show_cards()

    def _show_cards(self) -> None:
        self._stack.setCurrentIndex(PAGE_CARDS)
        self._cards.setFocus()          # keyboard: Space/Enter reveal, 1/2/3 rate

    def _on_session_complete(self, stats) -> None:
        self._last_stats = stats
        if stats.total <= 0:
            # Nothing was rated — there is nothing to summarise or persist.
            self._go_setup()
            return
        save_session(stats)
        self._summary.show_stats(stats)
        self._stack.setCurrentIndex(PAGE_SUMMARY)

    def _on_drill_again(self) -> None:
        if self._last_config:
            self._start_cards(self._last_config)
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
        if not self._cards.start_deck(pool, self._last_config.timer_secs):
            self._go_setup()
            return
        self._show_cards()

    def _on_history(self) -> None:
        self._history.refresh()
        self._stack.setCurrentIndex(PAGE_HISTORY)

    def _on_browse(self) -> None:
        self._browse.load_all()
        self._stack.setCurrentIndex(PAGE_BROWSE)

    def _on_reference(self) -> None:
        self._reference.load_all()
        self._stack.setCurrentIndex(PAGE_REFERENCE)

    def _go_setup(self) -> None:
        self._stack.setCurrentIndex(PAGE_SETUP)
