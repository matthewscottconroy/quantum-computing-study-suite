"""Pure model logic."""
from __future__ import annotations

import json

from core.models import CardResult, DrillConfig, Rating, SessionStats


def test_pct_known():
    assert SessionStats().pct_known == 0.0
    assert SessionStats(total=4, got_it=3).pct_known == 0.75


def test_rating_values_serialise_as_plain_strings():
    assert {r.value for r in Rating} == {"got_it", "unsure", "missed"}
    assert json.dumps({"rating": Rating.MISSED}) == '{"rating": "missed"}'
    assert Rating("unsure") is Rating.UNSURE


def test_drill_config_defaults():
    cfg = DrillConfig(categories=["Algorithms"])
    assert (cfg.card_count, cfg.timer_secs, cfg.flagged_only) == (20, 0, False)
    r = CardResult(card_id="x", category="Algorithms", rating=Rating.GOT_IT)
    assert r.rating == "got_it"
