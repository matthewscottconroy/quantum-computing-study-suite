"""Review-flag contract.

File: <data dir>/problems_flagged.json holding a list of
{"id", "label", "category", "app", "timestamp"}; flagging is a toggle; legacy
bare-string / {"problem_id": …} entries are normalised on read.  The UI half
drives the offscreen MainWindow: the flag button on the problem and derivation
screens, the per-row toggles on the summary, the History list with Unflag, and
the Setup "flagged only" filter.  Persistence is redirected to a temp dir.
"""
import fnmatch
import json
import time

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel

import persistence
from core.models import AttemptRecord, SessionStats
from ui.theme import FLAG_OFF_TEXT, FLAG_ON_TEXT

CONTRACT_KEYS = {"id", "label", "category", "app", "timestamp"}
APP = "problem-trainer"


def _raw(data_dir):
    """The flagged file exactly as written (None if it does not exist)."""
    path = data_dir / "problems_flagged.json"
    return json.loads(path.read_text()) if path.exists() else None


# ---------------------------------------------------------------------------
# File name / labels
# ---------------------------------------------------------------------------

def test_flagged_file_follows_the_suite_prefix_contract():
    from config import FLAGGED_FILE, HISTORY_FILE

    assert FLAGGED_FILE.name == "problems_flagged.json"
    assert HISTORY_FILE.name == "problems_history.json"
    assert FLAGGED_FILE.parent == HISTORY_FILE.parent
    assert fnmatch.fnmatch(FLAGGED_FILE.name, "*_flagged.json")   # coach.py --review glob
    assert persistence.APP_NAME_KEY == APP


def test_flag_labels_are_shared_by_every_screen():
    from ui.screens import derivation_screen, problem_screen, summary_screen

    for mod in (problem_screen, derivation_screen, summary_screen):
        assert mod.FLAG_ON_TEXT == FLAG_ON_TEXT
        assert mod.FLAG_OFF_TEXT == FLAG_OFF_TEXT
    assert FLAG_ON_TEXT != FLAG_OFF_TEXT
    assert FLAG_ON_TEXT.startswith("⚑") and FLAG_OFF_TEXT.startswith("⚑")


# ---------------------------------------------------------------------------
# persistence layer
# ---------------------------------------------------------------------------

def test_toggle_flag_writes_contract_entry(data_dir):
    before = time.time()
    assert persistence.toggle_flag("la_schmidt", "Schmidt", "Linear Algebra & QM Math") is True

    assert persistence.FLAGGED_FILE == data_dir / "problems_flagged.json"
    raw = _raw(data_dir)
    assert isinstance(raw, list) and len(raw) == 1
    entry = raw[0]
    assert set(entry) == CONTRACT_KEYS
    assert entry["id"] == "la_schmidt"
    assert entry["label"] == "Schmidt"
    assert entry["category"] == "Linear Algebra & QM Math"
    assert entry["app"] == APP
    assert isinstance(entry["timestamp"], float)
    assert before - 1 <= entry["timestamp"] <= time.time() + 1
    assert persistence.is_flagged("la_schmidt")
    assert persistence.flagged_ids() == {"la_schmidt"}
    assert not persistence.is_flagged("other")


def test_toggle_twice_removes_and_unflag_is_idempotent(data_dir):
    persistence.toggle_flag("a", "A", "c")
    persistence.toggle_flag("b", "B", "c")
    assert persistence.toggle_flag("a", "A", "c") is False
    assert [e["id"] for e in _raw(data_dir)] == ["b"]
    persistence.unflag("b")
    assert _raw(data_dir) == []
    persistence.unflag("b")                       # nothing left: must not raise
    assert _raw(data_dir) == []
    assert persistence.load_flagged() == []
    assert persistence.toggle_flag("a") is True   # re-flag after removal
    assert [e["id"] for e in _raw(data_dir)] == ["a"]


def test_label_defaults_to_id_and_category_to_empty(data_dir):
    persistence.toggle_flag("x")
    (entry,) = _raw(data_dir)
    assert entry["label"] == "x" and entry["category"] == "" and entry["app"] == APP


def test_legacy_entries_are_normalised_and_garbage_dropped(data_dir):
    data_dir.mkdir(parents=True)
    persistence.FLAGGED_FILE.write_text(json.dumps(
        ["la_schmidt", {"problem_id": "deriv_qpe"}, {"nope": 1}, 42, "", None, {"id": ""}]))

    entries = persistence.load_flagged()
    assert [e["id"] for e in entries] == ["la_schmidt", "deriv_qpe"]
    for e in entries:
        assert set(e) == CONTRACT_KEYS
        assert e["label"] == e["id"] and e["category"] == ""
        assert e["app"] == APP and e["timestamp"] == 0.0
    assert persistence.is_flagged("la_schmidt") and persistence.is_flagged("deriv_qpe")

    # The first write rewrites the file in the contract shape, dropping garbage.
    assert persistence.toggle_flag("la_schmidt") is False
    assert _raw(data_dir) == [{"id": "deriv_qpe", "label": "deriv_qpe", "category": "",
                               "app": APP, "timestamp": 0.0}]


def test_dict_entries_keep_fields_and_coerce_bad_timestamp(data_dir):
    data_dir.mkdir(parents=True)
    persistence.FLAGGED_FILE.write_text(json.dumps([{
        "id": "q1", "label": "Q", "category": "Algorithms",
        "app": "other-app", "timestamp": "yesterday", "extra": True}]))
    (e,) = persistence.load_flagged()
    assert e == {"id": "q1", "label": "Q", "category": "Algorithms",
                 "app": "other-app", "timestamp": 0.0}


def test_corrupt_or_non_list_file_reads_empty_and_recovers(data_dir):
    data_dir.mkdir(parents=True)
    for bad in ("{corrupt", json.dumps({"not": "a list"})):
        persistence.FLAGGED_FILE.write_text(bad)
        assert persistence.load_flagged() == []
        assert persistence.flagged_ids() == set()
    assert persistence.toggle_flag("x", "X", "c") is True
    assert [e["id"] for e in _raw(data_dir)] == ["x"]


# ---------------------------------------------------------------------------
# UI: problem / derivation screens
# ---------------------------------------------------------------------------

def test_problem_flag_button_round_trips_through_the_file(main_window, data_dir, problems,
                                                          qapp, find_button):
    from ui.main_window import PAGE_PROBLEM, PAGE_SUMMARY
    from ui.screens.setup_screen import MODE_PROBLEMS

    win = main_window
    p0, p1 = problems[0], problems[1]
    win._setup.session_started.emit(MODE_PROBLEMS, [p0, p1])
    qapp.processEvents()
    ps = win._problem
    assert win._stack.currentIndex() == PAGE_PROBLEM and ps._problem is p0
    assert not ps.is_flagged_shown() and ps._flag_btn.text() == FLAG_OFF_TEXT
    assert _raw(data_dir) is None, "showing a problem must not create the flagged file"

    ps._flag_btn.click()
    qapp.processEvents()
    raw = _raw(data_dir)
    assert len(raw) == 1 and set(raw[0]) == CONTRACT_KEYS
    assert raw[0]["id"] == p0.id and raw[0]["label"] == p0.title
    assert raw[0]["category"] == p0.topic and raw[0]["app"] == APP
    assert isinstance(raw[0]["timestamp"], float) and raw[0]["timestamp"] > 0
    assert ps.is_flagged_shown() and ps._flag_btn.text() == FLAG_ON_TEXT

    ps._flag_btn.click()
    qapp.processEvents()
    assert _raw(data_dir) == []
    assert not ps.is_flagged_shown() and ps._flag_btn.text() == FLAG_OFF_TEXT

    # Flag again, advance: the next problem starts unflagged.
    ps._flag_btn.click()
    find_button(ps, "Finish Problem →").click()
    qapp.processEvents()
    assert ps._problem is p1 and not ps.is_flagged_shown()
    assert [e["id"] for e in _raw(data_dir)] == [p0.id]

    # End Session -> summary (one attempt); its row reflects the persisted flag.
    find_button(ps, "End Session").click()
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_SUMMARY
    assert set(win._summary._flag_buttons) == {p0.id}
    assert win._summary.is_flagged_shown(p0.id) is True


def test_restarted_session_reshows_persisted_flag(main_window, data_dir, problems, qapp):
    from ui.screens.setup_screen import MODE_PROBLEMS

    win = main_window
    p0, p1 = problems[0], problems[1]
    persistence.toggle_flag(p0.id, p0.title, p0.topic)

    win._setup.session_started.emit(MODE_PROBLEMS, [p0])
    qapp.processEvents()
    assert win._problem.is_flagged_shown() and win._problem._flag_btn.text() == FLAG_ON_TEXT

    win._setup.session_started.emit(MODE_PROBLEMS, [p1])
    qapp.processEvents()
    assert not win._problem.is_flagged_shown()


def test_derivation_flag_uses_derivation_category(main_window, data_dir, derivations, qapp):
    from ui.main_window import PAGE_DERIVATION
    from ui.screens.setup_screen import MODE_DERIVATIONS

    win = main_window
    d0 = derivations[0]
    win._setup.session_started.emit(MODE_DERIVATIONS, [d0])
    qapp.processEvents()
    ds = win._derivation
    assert win._stack.currentIndex() == PAGE_DERIVATION
    assert not ds.is_flagged_shown() and ds._flag_btn.text() == FLAG_OFF_TEXT

    ds._flag_btn.click()
    qapp.processEvents()
    (e,) = _raw(data_dir)
    assert set(e) == CONTRACT_KEYS
    assert e["id"] == d0.id and e["label"] == d0.title
    assert e["category"] == "derivation" and e["app"] == APP
    assert ds.is_flagged_shown() and ds._flag_btn.text() == FLAG_ON_TEXT

    ds._flag_btn.click()
    qapp.processEvents()
    assert _raw(data_dir) == [] and not ds.is_flagged_shown()


# ---------------------------------------------------------------------------
# UI: summary rows
# ---------------------------------------------------------------------------

def test_summary_rows_toggle_flags_with_contract_schema(main_window, data_dir, problems,
                                                        derivations, qapp):
    win = main_window
    p0, d0 = problems[0], derivations[0]
    stats = SessionStats(attempts=[
        AttemptRecord(p0.id, "problem", 7.0, title=p0.title, category=p0.topic),
        AttemptRecord(d0.id, "derivation", 5.0, title=d0.title, category="derivation"),
    ])
    persistence.toggle_flag(d0.id, d0.title, "derivation")

    win._summary.show_stats(stats)
    assert set(win._summary._flag_buttons) == {p0.id, d0.id}
    assert win._summary.is_flagged_shown(d0.id) is True
    assert win._summary.is_flagged_shown(p0.id) is False
    assert win._summary._flag_buttons[d0.id].text() == FLAG_ON_TEXT
    p_btn = win._summary._flag_buttons[p0.id]
    assert p_btn.text() == FLAG_OFF_TEXT

    p_btn.click()
    qapp.processEvents()
    raw = _raw(data_dir)
    assert [e["id"] for e in raw] == [d0.id, p0.id]
    assert set(raw[1]) == CONTRACT_KEYS
    assert raw[1]["label"] == p0.title and raw[1]["category"] == p0.topic and raw[1]["app"] == APP
    assert p_btn.isChecked() and p_btn.text() == FLAG_ON_TEXT

    win._summary._flag_buttons[d0.id].click()
    qapp.processEvents()
    assert [e["id"] for e in _raw(data_dir)] == [p0.id]
    assert not win._summary.is_flagged_shown(d0.id)
    assert win._summary.is_flagged_shown("never-shown") is False


def test_summary_category_falls_back_to_kind():
    from ui.screens.summary_screen import _flag_category

    assert _flag_category(AttemptRecord("d", "derivation", 1.0)) == "derivation"
    assert _flag_category(AttemptRecord("p", "problem", 1.0)) == ""
    assert _flag_category(AttemptRecord("p", "problem", 1.0, category="VQA")) == "VQA"


# ---------------------------------------------------------------------------
# UI: History list with Unflag
# ---------------------------------------------------------------------------

def _row_texts(history, i: int) -> list[str]:
    row = history._flagged_box.itemAt(i).widget()
    return [lbl.text() for lbl in row.findChildren(QLabel)]


def test_history_lists_flags_newest_first_and_unflag_rewrites_file(main_window, data_dir,
                                                                    problems, derivations,
                                                                    qapp, find_button):
    from ui.main_window import PAGE_HISTORY

    win = main_window
    p0, d0 = problems[0], derivations[0]
    persistence.toggle_flag(p0.id, p0.title, p0.topic)
    persistence.toggle_flag(d0.id, d0.title, "derivation")

    find_button(win._setup, "View History").click()
    qapp.processEvents()
    hist = win._history
    assert win._stack.currentIndex() == PAGE_HISTORY
    assert hist.flagged_count() == 2
    assert hist._flagged_card._value.text() == "2"
    assert not hist._flagged_empty_lbl.isVisibleTo(hist)

    newest, older = _row_texts(hist, 0), _row_texts(hist, 1)
    assert d0.title in newest and "DERIVATION" in newest
    assert p0.title in older and p0.topic.upper() in older
    assert any(t == time.strftime("%Y-%m-%d") for t in newest)

    find_button(hist._flagged_box.itemAt(0).widget(), "Unflag").click()
    qapp.processEvents()
    assert [e["id"] for e in _raw(data_dir)] == [p0.id]
    assert hist.flagged_count() == 1 and hist._flagged_card._value.text() == "1"
    assert p0.title in _row_texts(hist, 0)

    find_button(hist._flagged_box.itemAt(0).widget(), "Unflag").click()
    qapp.processEvents()
    assert _raw(data_dir) == []
    assert hist.flagged_count() == 0 and hist._flagged_card._value.text() == "0"
    assert hist._flagged_empty_lbl.isVisibleTo(hist)


def test_history_renders_legacy_entries(main_window, data_dir, qapp):
    data_dir.mkdir(parents=True)
    persistence.FLAGGED_FILE.write_text(json.dumps(["la_schmidt", {"problem_id": "deriv_qpe"}]))
    hist = main_window._history
    hist.refresh()
    assert hist.flagged_count() == 2
    texts = _row_texts(hist, 0)
    assert "deriv_qpe" in texts and "ITEM" in texts and "—" in texts   # no category, no date


# ---------------------------------------------------------------------------
# UI: Setup "flagged only" filter
# ---------------------------------------------------------------------------

def _listed_ids(setup) -> list[str]:
    return [setup._list.item(i).data(Qt.ItemDataRole.UserRole).id
            for i in range(setup._list.count())]


def test_setup_flagged_only_filter_narrows_list(main_window, data_dir, problems,
                                                derivations, qapp):
    win = main_window
    setup = win._setup
    assert setup._list.count() == len(problems)
    assert not setup.flagged_only()

    setup.set_flagged_only(True)
    qapp.processEvents()
    assert setup.flagged_only()
    assert setup._list.count() == 0 and not setup._start_btn.isEnabled()
    assert setup._list_lbl.text() == "Problems (0 flagged)"

    p1 = problems[1]
    persistence.toggle_flag(p1.id, p1.title, p1.topic)
    win._go_setup()                       # what Back / Another Session do
    qapp.processEvents()
    assert _listed_ids(setup) == [p1.id]
    assert setup._list_lbl.text() == "Problems (1 flagged)"
    assert setup._start_btn.isEnabled()

    # Derivations mode shares the filter.
    setup._rb_derivs.setChecked(True)
    qapp.processEvents()
    assert setup._list.count() == 0
    d0 = derivations[0]
    persistence.toggle_flag(d0.id, d0.title, "derivation")
    setup.refresh_flag_filter()
    assert _listed_ids(setup) == [d0.id]
    assert setup._list_lbl.text() == "Derivations (1 flagged)"

    setup.set_flagged_only(False)
    qapp.processEvents()
    assert setup._list.count() == len(derivations)
    assert setup._list_lbl.text() == f"Derivations ({len(derivations)})"
