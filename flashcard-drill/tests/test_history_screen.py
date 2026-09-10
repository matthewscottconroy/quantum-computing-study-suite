"""HistoryScreen: stats/trend rendering, zero-total sessions, flagged list + Unflag."""
from __future__ import annotations

import json

import pytest

import persistence.storage as storage
from cards import all_cards
from core.models import CardResult, Rating, SessionStats


@pytest.fixture
def history(qapp):
    from ui.screens.history_screen import HistoryScreen

    screen = HistoryScreen()
    screen.show()
    qapp.processEvents()
    yield screen
    screen.close()
    screen.deleteLater()
    qapp.processEvents()


def _session(*ratings: Rating) -> SessionStats:
    stats = SessionStats(total=len(ratings))
    for i, r in enumerate(ratings):
        stats.results.append(CardResult(card_id=f"c{i}", category="Algorithms", rating=r))
        setattr(stats, r.value, getattr(stats, r.value) + 1)
    return stats


def test_empty_history_shows_placeholder(history):
    history.refresh()
    assert not history._empty_lbl.isHidden()
    assert history._sessions_card._val.text() == "0"
    assert history._known_card._val.text() == "—"
    assert history.flagged_ids() == []
    assert not history._flag_empty_lbl.isHidden()


def test_zero_total_session_does_not_crash_refresh(history, data_dir):
    """Regression: a persisted {'total': 0, ...} session raised ZeroDivisionError
    inside a slot -> qFatal -> SIGABRT on every later launch."""
    data_dir.mkdir(parents=True, exist_ok=True)
    storage.HISTORY_FILE.write_text(json.dumps([
        {"total": 0, "got_it": 0, "unsure": 0, "missed": 0, "timestamp": 1.0, "results": []},
    ]))
    history.refresh()                                      # must not raise
    assert not history._empty_lbl.isHidden()               # treated as no data
    assert history._sessions_card._val.text() == "0"

    storage.save_session(_session(Rating.GOT_IT, Rating.MISSED))
    history.refresh()
    assert history._empty_lbl.isHidden()
    assert history._sessions_card._val.text() == "1"       # zero-total entry not counted
    assert history._cards_card._val.text() == "2"
    assert history._known_card._val.text() == "50%"


def test_stats_and_trend_render(history):
    storage.save_session(_session(Rating.GOT_IT, Rating.GOT_IT, Rating.MISSED))
    storage.save_session(_session(Rating.GOT_IT, Rating.UNSURE))
    history.refresh()
    assert history._sessions_card._val.text() == "2"
    assert history._cards_card._val.text() == "5"
    assert history._known_card._val.text() == "60%"
    assert history._trend_slot.count() == 1                # one matplotlib canvas


def test_flagged_list_and_unflag(history, data_dir):
    cards = all_cards()
    a, b = cards[0], cards[1]
    storage.toggle_flag(a.id)
    storage.toggle_flag(b.id)
    storage.toggle_flag("stale_id_xyz")
    history.refresh()

    assert history.flagged_ids() == sorted([a.id, b.id, "stale_id_xyz"])
    assert history._flag_count_lbl.text() == "(3)"
    assert history._flag_empty_lbl.isHidden()

    toggled = []
    history.flag_toggled.connect(lambda c, s: toggled.append((c, s)))
    history._on_unflag(b.id)
    assert toggled == [(b.id, False)]
    assert storage.load_flagged() == {a.id, "stale_id_xyz"}
    assert history.flagged_ids() == sorted([a.id, "stale_id_xyz"])

    history._on_unflag("stale_id_xyz")
    history._on_unflag(a.id)
    assert storage.load_flagged() == set()
    assert history.flagged_ids() == []
    assert not history._flag_empty_lbl.isHidden()
    assert history._flag_count_lbl.text() == ""


def test_legacy_bare_id_flag_file_is_listed(history, data_dir):
    data_dir.mkdir(parents=True, exist_ok=True)
    storage._FLAGGED_FILE.write_text(json.dumps([all_cards()[0].id]))
    history.refresh()
    assert history.flagged_ids() == [all_cards()[0].id]
