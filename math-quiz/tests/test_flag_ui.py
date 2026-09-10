"""Flag-for-review UI: feedback toggle button, MainWindow wiring (including
error surfacing), and the history screen's flagged list with unflag."""
from __future__ import annotations

import json
import time

import pytest

import persistence
from core.models import Evaluation, Question


def _question(text="Compute the eigenvalues of the Pauli-Z operator.",
              subject="Linear Algebra", topic="eigenvalues") -> Question:
    return Question(subject=subject, topic=topic, difficulty="beginner",
                    question_type="calculation", text=text, hints=["h1"])


def _entry(flag_id: str, label: str, category: str, age_seconds: float) -> dict:
    return {"id": flag_id, "label": label, "category": category,
            "app": "math-quiz", "timestamp": time.time() - age_seconds}


# ── FeedbackScreen ────────────────────────────────────────────────────────────

def test_feedback_screen_flag_button_reflects_state(qapp):
    from ui.screens.feedback_screen import FeedbackScreen

    fb = FeedbackScreen()
    assert fb.is_flagged() is False                      # initialised, not a getattr default
    assert fb._flag_btn.text() == "⚑ Flag for review"
    fb.set_flagged(True)
    assert fb.is_flagged() is True
    assert "unflag" in fb._flag_btn.text().lower()
    assert fb._flag_btn.isEnabled()
    fb.set_flagged(False)
    assert fb.is_flagged() is False
    assert fb._flag_btn.text() == "⚑ Flag for review"

    fired = []
    fb.flag_requested.connect(lambda: fired.append(True))
    fb._flag_btn.click()
    assert fired == [True]
    # load_evaluation never touches the flag state (MainWindow sets it explicitly).
    fb.set_flagged(True)
    fb.load_evaluation(Evaluation(score=9, verdict="Correct", feedback="f", model_answer="m"))
    assert fb.is_flagged() is True


# ── MainWindow wiring ─────────────────────────────────────────────────────────

@pytest.fixture
def window(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    win = MainWindow()
    try:
        yield win
    finally:
        win.close()
        win.deleteLater()


def test_flag_button_click_round_trips_through_persistence(window, qapp):
    q = _question()
    window._current_question = q
    window._feedback.set_flagged(window._question_is_flagged(q))
    assert window._feedback.is_flagged() is False

    window._feedback._flag_btn.click()
    qapp.processEvents()
    assert window._feedback.is_flagged() is True
    raw = json.loads(persistence._FLAGGED_FILE.read_text(encoding="utf-8"))
    assert [e["id"] for e in raw] == [persistence.flag_id_for(q)]
    assert raw[0]["app"] == "math-quiz" and raw[0]["category"] == "Linear Algebra"

    window._feedback._flag_btn.click()
    qapp.processEvents()
    assert window._feedback.is_flagged() is False
    assert json.loads(persistence._FLAGGED_FILE.read_text(encoding="utf-8")) == []

    # A different question on the same topic has independent state.
    other = _question(text="A different question on the same topic.")
    persistence.toggle_flag(q)
    assert window._question_is_flagged(q) is True
    assert window._question_is_flagged(other) is False
    assert window._question_is_flagged(None) is False


def test_flag_failure_is_surfaced_not_swallowed(window, qapp, monkeypatch):
    q = _question()
    window._current_question = q
    window._feedback.set_flagged(True)

    def boom(_q):
        raise OSError("read-only data dir")
    monkeypatch.setattr(persistence, "toggle_flag", boom)

    window._feedback._flag_btn.click()
    qapp.processEvents()
    assert window._feedback.is_flagged() is True                 # state kept, not flipped
    assert window.statusBar().currentMessage() == "Could not update flag: read-only data dir"
    assert not persistence._FLAGGED_FILE.exists()

    window._current_question = None
    window._on_flag()                                            # no question: no-op, no raise


# ── HistoryScreen flagged list ────────────────────────────────────────────────

def test_history_flagged_list_orders_skips_malformed_and_unflags(qapp):
    from ui.screens.history_screen import HistoryScreen

    newest = _entry("Linear Algebra::SVD#aaaaaaaa", "Newest question", "Linear Algebra", 10)
    middle = _entry("Number Theory::primes#bbbbbbbb", "Middle question", "Number Theory", 3600)
    oldest = _entry("Topology & Geometry::π₁#cccccccc", "Oldest question", "Topology & Geometry", 86400 * 3)
    persistence.save_flagged([middle, {"garbage": True}, oldest, {"id": ""}, newest])

    h = HistoryScreen()
    h.refresh()                                                  # also renders (empty) history
    assert h.flagged_ids() == [newest["id"], middle["id"], oldest["id"]]
    assert not h._flag_list.isHidden() and h._flag_empty_lbl.isHidden()
    assert h._flag_count_lbl.text() == "3 flagged"
    item0 = h._flag_list.item(0)
    assert item0.text().startswith("Newest question")
    assert "Linear Algebra" in item0.text()
    assert time.strftime("%Y-%m-%d", time.localtime(newest["timestamp"])) in item0.text()
    assert item0.toolTip() == newest["id"]

    assert not h._unflag_btn.isEnabled()
    h._on_unflag_selected()                                      # nothing selected: no-op
    assert len(persistence.load_flagged()) == 3

    h._flag_list.setCurrentRow(1)                                # the middle one
    qapp.processEvents()
    assert h._unflag_btn.isEnabled()
    h._unflag_btn.click()
    qapp.processEvents()
    assert h.flagged_ids() == [newest["id"], oldest["id"]]
    on_disk = json.loads(persistence._FLAGGED_FILE.read_text(encoding="utf-8"))
    assert [e["id"] for e in on_disk] == [oldest["id"], newest["id"]]   # file keeps insertion order
    assert h._flag_count_lbl.text() == "2 flagged"

    for _ in range(2):
        h._flag_list.setCurrentRow(0)
        qapp.processEvents()
        h._unflag_btn.click()
        qapp.processEvents()
    assert h.flagged_ids() == []
    assert h._flag_list.isHidden() and not h._flag_empty_lbl.isHidden()
    assert h._flag_count_lbl.text() == ""
    assert not h._unflag_btn.isEnabled()
    assert json.loads(persistence._FLAGGED_FILE.read_text(encoding="utf-8")) == []


def test_history_flagged_list_tolerates_bad_timestamps_and_missing_labels(qapp):
    from ui.screens.history_screen import HistoryScreen

    persistence.save_flagged([
        {"id": "A::b#1", "label": "", "category": "A", "app": "math-quiz", "timestamp": "not-a-number"},
        {"id": "A::c#2", "category": "A", "app": "math-quiz", "timestamp": 1e300},
        {"id": "A::d#3", "label": "fine", "category": "", "app": "math-quiz", "timestamp": time.time()},
    ])
    h = HistoryScreen()
    h.refresh_flagged()
    # 1e300 is a valid (absurdly future) float, so it sorts newest; the
    # unparseable timestamp sorts as 0 (oldest). Neither may crash rendering.
    assert h.flagged_ids() == ["A::c#2", "A::d#3", "A::b#1"]
    texts = [h._flag_list.item(i).text() for i in range(h._flag_list.count())]
    assert texts[0] == "A::c#2\nA"                              # id used when label missing; no date (overflow)
    assert texts[1].startswith("fine\n") and time.strftime("%Y-%m-%d") in texts[1]
    assert texts[2] == "A::b#1\nA"                              # id used when label empty; no date (bad ts)
    assert h._flag_count_lbl.text() == "3 flagged"
