"""Mistake journal + confidence calibration.

Two shared suite files, both honouring QUANTUM_STUDY_DATA_DIR and redirected
here into a temp dir:

* ``mistakes.json``   — {"id", "app", "category", "question", "your_answer",
  "correct_answer", "cause", "note", "timestamp", "resolved"}
* ``confidence.json`` — {"id", "app", "category", "confidence", "correct",
  "timestamp"}

The pure-helper half exercises the schemas, the cause vocabulary, corruption
tolerance, atomic writes and the growth caps.  The UI half drives the offscreen
MainWindow end to end through the real grading worker (stubbed Claude): rate
confidence, answer badly, categorise the mistake, then answer well and watch
the entry resolve itself.  A derivation's model-step reveal is driven too.
"""
import json
import time

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

import persistence
from core.models import GradeResult, StepCheck
from ui.widgets.study_journal import (
    CONFIDENCE_LEVELS, MISTAKE_CAUSE_LABELS, ConfidenceStrip, MistakeRow,
)

MISTAKE_KEYS = {"id", "app", "category", "question", "your_answer",
                "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_KEYS = {"id", "app", "category", "confidence", "correct", "timestamp"}
APP = "problem-trainer"


def _clipped(text: str, limit: int = 200) -> str:
    """The contract's <=200-char form of a one-line text field.

    Whitespace is collapsed first: ``question`` / ``your_answer`` /
    ``correct_answer`` are shown in a one-line list row on the History screen
    and in ``coach --mistakes``, and a model solution with a newline in it
    breaks the row.  (This is ``common.journal.clip_text``; the app's own copy
    used to truncate without collapsing, which is the divergence common/
    reconciled.  The *note* is the exception — it keeps its line breaks.)
    """
    flat = " ".join(text.split())
    return flat if len(flat) <= limit else flat[: limit - 1].rstrip() + "…"


def _raw(data_dir, name):
    path = data_dir / name
    return json.loads(path.read_text()) if path.exists() else None


def _mistakes(data_dir):
    return _raw(data_dir, "mistakes.json")


def _confidence(data_dir):
    return _raw(data_dir, "confidence.json")


def _drain(win, qapp, timeout: float = 10.0) -> None:
    """Let every running grading/step worker finish and its signals arrive."""
    deadline = time.time() + timeout
    while win._workers and time.time() < deadline:
        for w in list(win._workers):
            w.wait(50)
        qapp.processEvents()
    qapp.processEvents()
    assert not win._workers, "a worker never finished"


# ---------------------------------------------------------------------------
# File locations / the data-dir override
# ---------------------------------------------------------------------------

def test_journal_files_live_beside_the_other_suite_files():
    from config import CONFIDENCE_FILE, HISTORY_FILE, MISTAKES_FILE, SETTINGS_FILE

    assert MISTAKES_FILE.name == "mistakes.json"
    assert CONFIDENCE_FILE.name == "confidence.json"
    assert SETTINGS_FILE.name == "problems_settings.json"
    for f in (MISTAKES_FILE, CONFIDENCE_FILE, SETTINGS_FILE):
        assert f.parent == HISTORY_FILE.parent


def test_data_dir_env_override_relocates_the_journal(tmp_path, monkeypatch):
    import importlib

    import config
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(tmp_path / "elsewhere"))
    reloaded = importlib.reload(config)
    try:
        assert reloaded.MISTAKES_FILE == tmp_path / "elsewhere" / "mistakes.json"
        assert reloaded.CONFIDENCE_FILE == tmp_path / "elsewhere" / "confidence.json"
    finally:
        monkeypatch.undo()
        importlib.reload(config)


# ---------------------------------------------------------------------------
# Mistake journal — pure helpers
# ---------------------------------------------------------------------------

def test_make_mistake_entry_matches_the_contract_field_for_field():
    entry = persistence.make_mistake_entry(
        "la_schmidt:a", "Linear Algebra & QM Math", "Question?", "my answer",
        "the right answer", cause="misread", note="read it twice",
        timestamp=1700000000.0)

    assert set(entry) == MISTAKE_KEYS
    assert entry == {
        "id": "la_schmidt:a",
        "app": APP,
        "category": "Linear Algebra & QM Math",
        "question": "Question?",
        "your_answer": "my answer",
        "correct_answer": "the right answer",
        "cause": "misread",
        "note": "read it twice",
        "timestamp": 1700000000.0,
        "resolved": False,
    }
    assert isinstance(entry["timestamp"], float)
    assert isinstance(entry["resolved"], bool)


def test_cause_vocabulary_is_the_contract_and_the_ui_agrees():
    assert persistence.MISTAKE_CAUSES == (
        "misread", "didnt_know", "knew_but_slipped", "confused",
        "out_of_time", "other")
    assert [c for c, _ in MISTAKE_CAUSE_LABELS] == list(persistence.MISTAKE_CAUSES)
    for bad in (None, "", "nope", 3, True):
        assert persistence.normalize_cause(bad) is None
    for good in persistence.MISTAKE_CAUSES:
        assert persistence.normalize_cause(good) == good


def test_long_text_fields_are_clipped_to_200_chars():
    entry = persistence.make_mistake_entry(
        "x", "c", "q" * 500, "a" * 500, "s" * 500, note="n" * 500)
    for key in ("question", "your_answer", "correct_answer", "note"):
        assert len(entry[key]) == 200
        assert entry[key].endswith("…")


def test_log_mistake_writes_the_file_and_updates_in_place(data_dir):
    before = time.time()
    persistence.log_mistake("p:a", "VQA", "Q", "wrong", "right")

    raw = _mistakes(data_dir)
    assert isinstance(raw, list) and len(raw) == 1
    (entry,) = raw
    assert set(entry) == MISTAKE_KEYS
    assert entry["id"] == "p:a" and entry["app"] == APP
    assert entry["category"] == "VQA" and entry["question"] == "Q"
    assert entry["your_answer"] == "wrong" and entry["correct_answer"] == "right"
    assert entry["cause"] is None and entry["note"] == ""
    assert entry["resolved"] is False
    assert before - 1 <= entry["timestamp"] <= time.time() + 1

    # A second bad attempt at the same item refreshes rather than duplicates.
    persistence.log_mistake("p:a", "VQA", "Q", "wrong again", "right")
    raw = _mistakes(data_dir)
    assert len(raw) == 1 and raw[0]["your_answer"] == "wrong again"

    persistence.log_mistake("p:b", "VQA", "Q2", "no", "yes")
    assert [e["id"] for e in _mistakes(data_dir)] == ["p:a", "p:b"]


def test_cause_and_note_survive_a_later_relog(data_dir):
    persistence.log_mistake("p:a", "VQA", "Q", "wrong", "right")
    persistence.set_mistake_cause("p:a", "knew_but_slipped", "endianness again")
    persistence.log_mistake("p:a", "VQA", "Q", "wrong twice", "right")

    (entry,) = _mistakes(data_dir)
    assert entry["cause"] == "knew_but_slipped"
    assert entry["note"] == "endianness again"
    assert entry["your_answer"] == "wrong twice"


def test_a_resolved_item_reopens_when_it_is_missed_again(data_dir):
    persistence.log_mistake("p:a", "VQA", "Q", "wrong", "right")
    persistence.set_mistake_cause("p:a", "confused")
    persistence.resolve_mistake("p:a")
    assert _mistakes(data_dir)[0]["resolved"] is True

    persistence.log_mistake("p:a", "VQA", "Q", "wrong again", "right")
    (entry,) = _mistakes(data_dir)
    assert entry["resolved"] is False and entry["cause"] == "confused"


def test_a_note_without_a_cause_is_kept(data_dir):
    persistence.log_mistake("p:a", "VQA", "Q", "wrong", "right")
    persistence.set_mistake_cause("p:a", None, "come back to Schmidt rank")
    (entry,) = _mistakes(data_dir)
    assert entry["cause"] is None
    assert entry["note"] == "come back to Schmidt rank"


def test_set_mistake_cause_rejects_unknown_causes_and_missing_items(data_dir):
    persistence.log_mistake("p:a", "VQA", "Q", "wrong", "right")
    assert persistence.set_mistake_cause("p:a", "not-a-cause")["cause"] is None
    assert persistence.set_mistake_cause("nope", "misread") is None


def test_resolve_mistake_sets_the_flag_and_is_idempotent(data_dir):
    persistence.log_mistake("p:a", "VQA", "Q", "wrong", "right")
    assert persistence.resolve_mistake("p:a") is True
    (entry,) = _mistakes(data_dir)
    assert entry["resolved"] is True
    assert persistence.resolve_mistake("p:a") is False
    assert persistence.resolve_mistake("never-seen") is False


def test_entries_from_other_apps_are_preserved_and_never_resolved(data_dir):
    data_dir.mkdir(parents=True)
    other = persistence.make_mistake_entry("q1", "Gates", "Q", "a", "b",
                                           app="quantum-quiz")
    persistence.MISTAKES_FILE.write_text(json.dumps([other]))

    persistence.log_mistake("p:a", "VQA", "Q", "wrong", "right")
    persistence.resolve_mistake("q1")                   # different app: no-op
    raw = _mistakes(data_dir)
    assert [e["app"] for e in raw] == ["quantum-quiz", APP]
    assert raw[0]["resolved"] is False
    assert [e["id"] for e in persistence.app_mistakes()] == ["p:a"]


def test_corrupt_or_non_list_mistake_file_starts_fresh(data_dir):
    data_dir.mkdir(parents=True)
    for bad in ("{not json", json.dumps({"not": "a list"}), ""):
        persistence.MISTAKES_FILE.write_text(bad)
        assert persistence.load_mistakes() == []
    persistence.MISTAKES_FILE.write_text(json.dumps(
        ["a string", 42, None, {"no": "id"}, {"id": ""},
         {"id": "ok", "timestamp": "yesterday", "cause": "bogus"}]))
    entries = persistence.load_mistakes()
    assert [e["id"] for e in entries] == ["ok"]
    assert entries[0]["timestamp"] == 0.0 and entries[0]["cause"] is None
    assert set(entries[0]) == MISTAKE_KEYS


def test_mistake_journal_is_capped(data_dir, monkeypatch):
    monkeypatch.setattr(persistence, "MAX_MISTAKES", 3)
    for i in range(6):
        persistence.log_mistake(f"p:{i}", "VQA", "Q", "w", "r")
    assert [e["id"] for e in _mistakes(data_dir)] == ["p:3", "p:4", "p:5"]


# ---------------------------------------------------------------------------
# Confidence calibration — pure helpers
# ---------------------------------------------------------------------------

def test_log_confidence_writes_the_contract_row(data_dir):
    before = time.time()
    persistence.log_confidence("p:a", "Algorithms", 4, False)

    raw = _confidence(data_dir)
    assert isinstance(raw, list) and len(raw) == 1
    (row,) = raw
    assert set(row) == CONFIDENCE_KEYS
    assert row["id"] == "p:a" and row["app"] == APP
    assert row["category"] == "Algorithms"
    assert row["confidence"] == 4 and isinstance(row["confidence"], int)
    assert row["correct"] is False and isinstance(row["correct"], bool)
    assert before - 1 <= row["timestamp"] <= time.time() + 1

    persistence.log_confidence("p:a", "Algorithms", 2, True)
    assert [r["confidence"] for r in _confidence(data_dir)] == [4, 2]


def test_confidence_levels_are_clamped_and_labelled():
    assert [lv for lv, _ in CONFIDENCE_LEVELS] == [1, 2, 3, 4]
    assert persistence.CONFIDENCE_LABELS == {
        1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}
    assert persistence.make_confidence_entry("x", "c", 9, True)["confidence"] == 4
    assert persistence.make_confidence_entry("x", "c", -1, True)["confidence"] == 1
    assert persistence.make_confidence_entry("x", "c", "oops", True)["confidence"] == 1


def test_confidence_summary_finds_the_confidently_wrong(data_dir):
    persistence.log_confidence("a", "QEC", 4, False)
    persistence.log_confidence("b", "QEC", 4, False)
    persistence.log_confidence("c", "QEC", 4, True)
    persistence.log_confidence("d", "QEC", 1, True)
    assert persistence.confidence_summary() == {4: (1, 3), 1: (1, 1)}
    assert persistence.confidence_summary(app="other-app") == {}


def test_corrupt_confidence_file_starts_fresh(data_dir):
    data_dir.mkdir(parents=True)
    for bad in ("{broken", json.dumps({"a": 1})):
        persistence.CONFIDENCE_FILE.write_text(bad)
        assert persistence.load_confidence() == []
    persistence.CONFIDENCE_FILE.write_text(json.dumps(
        [{"id": "x"}, {"confidence": 3}, "junk",
         {"id": "y", "confidence": 3, "timestamp": None}]))
    rows = persistence.load_confidence()
    assert [r["id"] for r in rows] == ["y"]
    assert rows[0]["timestamp"] == 0.0 and rows[0]["correct"] is False


def test_confidence_log_is_capped(data_dir, monkeypatch):
    monkeypatch.setattr(persistence, "MAX_CONFIDENCE", 2)
    for i in range(5):
        persistence.log_confidence(f"p:{i}", "VQA", 3, True)
    assert [r["id"] for r in _confidence(data_dir)] == ["p:3", "p:4"]


# ---------------------------------------------------------------------------
# Atomic writes / settings
# ---------------------------------------------------------------------------

def test_writes_are_atomic_and_leave_no_temp_files(data_dir):
    persistence.log_mistake("p:a", "VQA", "Q", "w", "r")
    persistence.log_confidence("p:a", "VQA", 3, True)
    persistence.set_confidence_prompt_enabled(False)
    persistence.toggle_flag("p", "P", "VQA")
    leftovers = sorted(p.name for p in data_dir.iterdir() if p.suffix == ".tmp")
    assert leftovers == []
    # Three sidecars per data file, and nothing else:
    #   .lock         an empty file flock()ed for the length of a
    #                 read-modify-write, so a second window or a second app
    #                 cannot clobber rows we just appended (common.locking);
    #   .schema.json  the version marker (common.schema).  It is a sidecar and
    #                 not a key in the data because coach.py / dashboard.py
    #                 require the top level of these files to be a plain list.
    # No .bak yet: nothing here existed before this session's first write.
    assert sorted(p.name for p in data_dir.iterdir()) == [
        "confidence.json", "confidence.json.lock", "confidence.json.schema.json",
        "mistakes.json", "mistakes.json.lock", "mistakes.json.schema.json",
        "problems_flagged.json", "problems_flagged.json.lock",
        "problems_flagged.json.schema.json",
        "problems_settings.json", "problems_settings.json.lock",
        "problems_settings.json.schema.json"]
    assert (data_dir / "mistakes.json.lock").read_bytes() == b""
    assert not list(data_dir.glob("*.bak*"))
    # The names coach.py globs for still match exactly one file each.
    assert [p.name for p in data_dir.glob("*_flagged.json")] == ["problems_flagged.json"]


def test_confidence_prompt_setting_round_trips(data_dir):
    assert persistence.confidence_prompt_enabled() is True      # default on
    assert not (data_dir / "problems_settings.json").exists()   # reading never writes

    persistence.set_confidence_prompt_enabled(False)
    assert json.loads((data_dir / "problems_settings.json").read_text()) == {
        "confidence_prompt": False}
    assert persistence.confidence_prompt_enabled() is False

    persistence.set_confidence_prompt_enabled(True)
    assert persistence.confidence_prompt_enabled() is True


def test_corrupt_settings_fall_back_to_defaults(data_dir):
    data_dir.mkdir(parents=True)
    for bad in ("{broken", json.dumps([1, 2])):
        persistence.SETTINGS_FILE.write_text(bad)
        assert persistence.load_settings() == {"confidence_prompt": True}
        assert persistence.confidence_prompt_enabled() is True


def test_existing_history_and_flag_schemas_are_untouched(data_dir):
    """The new files must not disturb what coach.py parses."""
    from core.models import AttemptRecord, SessionStats

    persistence.save_session(SessionStats(
        attempts=[AttemptRecord("la_schmidt", "problem", 8.0, title="t")]))
    persistence.log_mistake("la_schmidt:a", "VQA", "Q", "w", "r")
    (session,) = json.loads((data_dir / "problems_history.json").read_text())
    assert set(session) == {"timestamp", "total", "avg_score", "attempts"}
    assert session["attempts"] == [
        {"problem_id": "la_schmidt", "kind": "problem", "score": 8.0}]


# ---------------------------------------------------------------------------
# Accessibility of the new controls
# ---------------------------------------------------------------------------

def test_new_controls_are_keyboard_reachable_and_named(qapp):
    strip = ConfidenceStrip()
    row = MistakeRow()
    try:
        assert strip.accessibleName() and row.accessibleName()
        for level, label in CONFIDENCE_LEVELS:
            btn = strip.button(level)
            assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
            assert btn.accessibleName() == f"Confidence {level} of 4: {label}"
            assert str(level) in btn.text() and label in btn.text()
            assert ":focus" in btn.styleSheet()
        for cause, label in MISTAKE_CAUSE_LABELS:
            btn = row.button(cause)
            assert btn.focusPolicy() == Qt.FocusPolicy.StrongFocus
            assert btn.accessibleName() == f"Cause: {label}"
            assert btn.text() == label
            assert ":focus" in btn.styleSheet()
        assert row._note.accessibleName()
        assert ":focus" in row._note.styleSheet()
        opt_out = [b for b in strip.findChildren(QPushButton)
                   if b.text() == "Don't ask"]
        assert len(opt_out) == 1 and opt_out[0].accessibleName()
    finally:
        strip.deleteLater()
        row.deleteLater()
        qapp.processEvents()


def test_selection_is_shown_by_a_glyph_not_only_colour(qapp):
    strip = ConfidenceStrip()
    row = MistakeRow()
    try:
        btn = strip.button(3)
        assert not btn.text().startswith("✓")
        btn.click()
        assert btn.text().startswith("✓") and strip.value() == 3
        strip.clear()
        assert strip.value() is None and not btn.text().startswith("✓")

        cause_btn = row.button("confused")
        cause_btn.click()
        assert cause_btn.text().startswith("✓") and row.value() == "confused"
        assert row._title.text().startswith("✗")     # ✗ glyph, not just red
    finally:
        strip.deleteLater()
        row.deleteLater()
        qapp.processEvents()


def test_new_widget_colours_clear_45_to_1_on_the_dark_palette():
    from ui import theme

    def luminance(hexcolor: str) -> float:
        h = hexcolor.lstrip("#")
        chan = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        chan = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
                for c in chan]
        return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]

    def ratio(fg: str, bg: str) -> float:
        a, b = luminance(fg), luminance(bg)
        hi, lo = max(a, b), min(a, b)
        return (hi + 0.05) / (lo + 0.05)

    pairs = [
        (theme.TEXT, theme.SURFACE2),        # chip label
        (theme.TEXT_MUTED, theme.SURFACE2),  # "How sure?" / hint / Don't ask
        (theme.ACCENT, theme.SURFACE2),      # selected confidence chip
        (theme.PARTIAL, theme.SURFACE2),     # "What went wrong?" + selected cause
        (theme.TEXT, theme.SURFACE),         # note field text
        (theme.TEXT_MUTED, theme.SURFACE),
    ]
    for fg, bg in pairs:
        assert ratio(fg, bg) >= 4.5, f"{fg} on {bg} is {ratio(fg, bg):.2f}:1"


# ---------------------------------------------------------------------------
# UI drive — problem parts, end to end through the real worker
# ---------------------------------------------------------------------------

BAD_GRADE = json.dumps({"score": 2, "feedback": "Missed the point.",
                        "missed_points": ["normalisation"]})
GOOD_GRADE = json.dumps({"score": 9, "feedback": "Right.", "missed_points": []})


def test_wrong_part_logs_a_mistake_that_a_cause_then_a_good_answer_closes(
        main_window, data_dir, problems, qapp, fake_claude, find_button):
    from ui.main_window import PAGE_PROBLEM
    from ui.screens.problem_screen import part_item_id
    from ui.screens.setup_screen import MODE_PROBLEMS

    fake_claude(BAD_GRADE, GOOD_GRADE)
    win = main_window
    problem = problems[0]
    part = problem.parts[0]
    item_id = part_item_id(problem, part)

    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    assert win._stack.currentIndex() == PAGE_PROBLEM
    widget = win._problem._part_widgets[part.part_id]
    assert _mistakes(data_dir) is None, "opening a problem must not write the journal"
    assert not widget._mistake_row.isVisibleTo(widget)

    # (3) rate confidence BEFORE submitting, then answer badly
    assert widget._conf_strip.isVisibleTo(widget)
    widget._conf_strip.button(4).click()
    widget._answer_edit.setPlainText("the answer is obviously 42")
    find_button(widget, "Submit for grading").click()
    _drain(win, qapp)

    # (1)+(2) a mistake entry, field for field
    raw = _mistakes(data_dir)
    assert isinstance(raw, list) and len(raw) == 1
    (entry,) = raw
    assert set(entry) == MISTAKE_KEYS
    assert entry["id"] == item_id == f"{problem.id}:{part.part_id}"
    assert entry["app"] == APP
    assert entry["category"] == problem.topic
    assert entry["question"] == _clipped(part.prompt)
    assert entry["your_answer"] == "the answer is obviously 42"
    assert entry["correct_answer"] == _clipped(part.model_solution)
    assert len(entry["correct_answer"]) <= 200
    assert entry["cause"] is None                     # logged, not yet categorised
    assert entry["note"] == ""
    assert isinstance(entry["timestamp"], float) and entry["timestamp"] > 0
    assert entry["resolved"] is False

    # (3) the confidence pairing row: certain, and wrong
    (row,) = _confidence(data_dir)
    assert set(row) == CONFIDENCE_KEYS
    assert row == {"id": item_id, "app": APP, "category": problem.topic,
                   "confidence": 4, "correct": False,
                   "timestamp": row["timestamp"]}
    assert isinstance(row["timestamp"], float) and row["timestamp"] > 0

    # the "What went wrong?" row is on the feedback view, and skippable
    assert widget._mistake_row.isVisibleTo(widget)
    assert widget._mistake_row.value() is None
    widget._mistake_row._note.setText("read the ket backwards")
    widget._mistake_row.button("misread").click()
    qapp.processEvents()
    (entry,) = _mistakes(data_dir)
    assert entry["cause"] == "misread"
    assert entry["note"] == "read the ket backwards"
    assert entry["resolved"] is False

    # the rating is cleared so a resubmission cannot reuse a stale one
    assert widget._conf_strip.value() is None

    # (4) answer it properly: the entry resolves, a second pairing is logged
    widget._conf_strip.button(2).click()
    widget._answer_edit.setPlainText("a properly worked answer")
    find_button(widget, "Resubmit revision").click()
    _drain(win, qapp)

    (entry,) = _mistakes(data_dir)
    assert entry["resolved"] is True
    assert entry["cause"] == "misread"                # analysis is not lost
    assert not widget._mistake_row.isVisibleTo(widget)
    rows = _confidence(data_dir)
    assert [(r["confidence"], r["correct"]) for r in rows] == [(4, False), (2, True)]


def test_skipping_the_cause_still_keeps_the_mistake(main_window, data_dir, problems,
                                                    qapp, fake_claude, find_button):
    from ui.screens.setup_screen import MODE_PROBLEMS

    fake_claude(BAD_GRADE)
    win = main_window
    problem = problems[0]
    part = problem.parts[0]
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    widget = win._problem._part_widgets[part.part_id]
    widget._answer_edit.setPlainText("nope")
    find_button(widget, "Submit for grading").click()
    _drain(win, qapp)

    (entry,) = _mistakes(data_dir)
    assert entry["cause"] is None and entry["resolved"] is False
    assert _confidence(data_dir) is None, "an unrated answer logs no calibration row"


def test_a_note_typed_without_a_cause_reaches_the_journal(
        main_window, data_dir, problems, qapp, fake_claude, find_button):
    from ui.screens.setup_screen import MODE_PROBLEMS

    fake_claude(BAD_GRADE)
    win = main_window
    problem = problems[0]
    part = problem.parts[0]
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    widget = win._problem._part_widgets[part.part_id]
    widget._answer_edit.setPlainText("nope")
    find_button(widget, "Submit for grading").click()
    _drain(win, qapp)

    widget._mistake_row._note.setText("revisit the amplitude bookkeeping")
    widget._mistake_row._note.editingFinished.emit()
    qapp.processEvents()
    (entry,) = _mistakes(data_dir)
    assert entry["cause"] is None
    assert entry["note"] == "revisit the amplitude bookkeeping"


def test_half_credit_is_not_a_mistake(main_window, data_dir, problems, qapp,
                                      fake_claude, find_button):
    from ui.screens.setup_screen import MODE_PROBLEMS

    fake_claude(json.dumps({"score": 5, "feedback": "half", "missed_points": []}))
    win = main_window
    problem = problems[0]
    part = problem.parts[0]
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    widget = win._problem._part_widgets[part.part_id]
    widget._conf_strip.button(3).click()
    widget._answer_edit.setPlainText("halfway there")
    find_button(widget, "Submit for grading").click()
    _drain(win, qapp)

    assert _mistakes(data_dir) is None
    assert _confidence(data_dir)[0]["correct"] is True


def test_grading_failure_logs_nothing(main_window, data_dir, problems, qapp,
                                      no_api_key, find_button):
    from ui.screens.setup_screen import MODE_PROBLEMS

    win = main_window
    problem = problems[0]
    part = problem.parts[0]
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    widget = win._problem._part_widgets[part.part_id]
    widget._conf_strip.button(4).click()
    widget._answer_edit.setPlainText("no key configured")
    find_button(widget, "Submit for grading").click()
    _drain(win, qapp)

    assert _mistakes(data_dir) is None
    assert _confidence(data_dir) is None


def test_confidence_opt_out_persists_and_is_re_enabled_from_setup(
        main_window, data_dir, problems, qapp):
    from ui.screens.setup_screen import MODE_PROBLEMS

    win = main_window
    problem = problems[0]
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    widget = win._problem._part_widgets[problem.parts[0].part_id]
    assert widget._conf_strip.isVisibleTo(widget)

    widget._conf_strip._opt_out.click()
    qapp.processEvents()
    assert persistence.confidence_prompt_enabled() is False
    for w in win._problem._part_widgets.values():
        assert not w._conf_strip.isVisibleTo(w)

    # a new problem honours the opt-out, and Setup mirrors + reverses it
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    widget = win._problem._part_widgets[problem.parts[0].part_id]
    assert not widget._conf_strip.isVisibleTo(widget)

    win._go_setup()
    qapp.processEvents()
    assert win._setup._confidence_cb.isChecked() is False
    win._setup._confidence_cb.setChecked(True)
    qapp.processEvents()
    assert persistence.confidence_prompt_enabled() is True
    win._setup.session_started.emit(MODE_PROBLEMS, [problem])
    qapp.processEvents()
    widget = win._problem._part_widgets[problem.parts[0].part_id]
    assert widget._conf_strip.isVisibleTo(widget)


# ---------------------------------------------------------------------------
# UI drive — derivation steps
# ---------------------------------------------------------------------------

def test_model_step_reveal_logs_a_mistake_and_a_clean_step_resolves_it(
        main_window, data_dir, derivations, qapp):
    from ui.screens.derivation_screen import DERIVATION_CATEGORY, step_item_id
    from ui.screens.setup_screen import MODE_DERIVATIONS

    win = main_window
    deriv = derivations[0]
    step = deriv.steps[0]
    item_id = step_item_id(deriv, step)

    win._setup.session_started.emit(MODE_DERIVATIONS, [deriv])
    qapp.processEvents()
    screen = win._derivation
    assert _mistakes(data_dir) is None
    assert not screen._mistake_row.isVisibleTo(screen)

    screen._answer_edit.setPlainText("I am stuck")
    screen._reveal_btn.click()
    qapp.processEvents()

    (entry,) = _mistakes(data_dir)
    assert set(entry) == MISTAKE_KEYS
    assert entry["id"] == item_id == f"{deriv.id}:{step.step_id}"
    assert entry["app"] == APP and entry["category"] == DERIVATION_CATEGORY
    assert entry["your_answer"] == "I am stuck"
    assert entry["correct_answer"] == _clipped(step.model_step)
    assert entry["question"] == _clipped(step.prompt)
    assert entry["cause"] is None and entry["resolved"] is False
    assert screen._mistake_row.isVisibleTo(screen)

    screen._mistake_row.button("didnt_know").click()
    qapp.processEvents()
    assert _mistakes(data_dir)[0]["cause"] == "didnt_know"

    # Later, the same step answered cleanly resolves the entry.
    win._setup.session_started.emit(MODE_DERIVATIONS, [deriv])
    qapp.processEvents()
    screen._answer_edit.setPlainText("the right move")
    screen._conf_strip.button(3).click()
    screen._on_check()
    screen.on_step_checked(step.step_id, StepCheck(verdict="accept", nudge="Yes"))
    qapp.processEvents()

    (entry,) = _mistakes(data_dir)
    assert entry["resolved"] is True and entry["cause"] == "didnt_know"
    (row,) = _confidence(data_dir)
    assert row == {"id": item_id, "app": APP, "category": DERIVATION_CATEGORY,
                   "confidence": 3, "correct": True, "timestamp": row["timestamp"]}


def test_rejected_step_pairs_confidence_with_a_miss(main_window, data_dir,
                                                    derivations, qapp):
    from ui.screens.setup_screen import MODE_DERIVATIONS

    win = main_window
    deriv = derivations[0]
    win._setup.session_started.emit(MODE_DERIVATIONS, [deriv])
    qapp.processEvents()
    screen = win._derivation
    screen._answer_edit.setPlainText("probably wrong")
    screen._conf_strip.button(4).click()
    screen._on_check()
    screen.on_step_checked(deriv.steps[0].step_id,
                           StepCheck(verdict="needs_work", nudge="Try again"))
    qapp.processEvents()

    (row,) = _confidence(data_dir)
    assert row["confidence"] == 4 and row["correct"] is False
    assert _mistakes(data_dir) is None, "a nudge is not yet a journal entry"
    # the rating is consumed: a failed API call afterwards logs nothing more
    screen.on_step_failed(deriv.steps[0].step_id, "no key")
    qapp.processEvents()
    assert len(_confidence(data_dir)) == 1


# ---------------------------------------------------------------------------
# History screen surfaces the journal
# ---------------------------------------------------------------------------

def test_history_lists_open_mistakes_and_calibration(main_window, data_dir, qapp,
                                                     find_button):
    from ui.main_window import PAGE_HISTORY

    persistence.log_mistake("p:a", "VQA", "Ansatz question", "wrong", "right")
    persistence.set_mistake_cause("p:a", "knew_but_slipped", "sign error")
    persistence.log_mistake("p:b", "Algorithms", "Grover question", "wrong", "right")
    persistence.log_confidence("p:a", "VQA", 4, False)
    persistence.log_confidence("p:b", "Algorithms", 4, True)

    win = main_window
    find_button(win._setup, "View History").click()
    qapp.processEvents()
    hist = win._history
    assert win._stack.currentIndex() == PAGE_HISTORY
    assert hist.open_mistake_count() == 2
    assert hist._mistakes_card._value.text() == "2"
    assert not hist._journal_empty_lbl.isVisibleTo(hist)
    text = hist._calibration_lbl.text()
    assert "4 Certain: 1/2 right (50%)" in text

    find_button(hist._journal_box.itemAt(0).widget(), "Mark resolved").click()
    qapp.processEvents()
    assert hist.open_mistake_count() == 1
    assert [e["resolved"] for e in persistence.load_mistakes()] == [False, True]

    find_button(hist._journal_box.itemAt(0).widget(), "Mark resolved").click()
    qapp.processEvents()
    assert hist.open_mistake_count() == 0
    assert hist._journal_empty_lbl.isVisibleTo(hist)
    assert hist._mistakes_card._value.text() == "0"


def test_history_survives_an_empty_journal(main_window, data_dir, qapp):
    hist = main_window._history
    hist.refresh()
    assert hist.open_mistake_count() == 0
    assert "No confidence ratings yet" in hist._calibration_lbl.text()


# ---------------------------------------------------------------------------
# Shared-file contract: another app's rows are never ours to rewrite
# ---------------------------------------------------------------------------

FOREIGN_MISTAKE_ROW = {
    "id": "tutor-7", "app": "quantum-tutor", "category": "Gates",
    "question": "q", "your_answer": "a", "correct_answer": "b",
    "cause": "confused", "note": "n", "timestamp": 1.0, "resolved": False,
    "revision": 3,                       # keys this app's schema knows nothing
    "tags": ["endianness", {"deep": True}],   # about: they must survive anyway
}
FOREIGN_CONFIDENCE_ROW = {
    "id": "tutor-7", "app": "quantum-tutor", "category": "Gates",
    "confidence": 2, "correct": True, "timestamp": 1.0,
    "source": "tutor-v2", "latency_ms": 940,
}


def test_a_foreign_row_keeps_its_unknown_keys_through_our_writes(data_dir):
    """Another app's rows come back byte for byte — extra keys included.

    Both files are shared, so a rewrite here must put every row this app does
    not own back exactly as it was read.  Normalising a foreign row through
    this app's schema would silently drop whatever the owning app added to it.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "mistakes.json").write_text(json.dumps([FOREIGN_MISTAKE_ROW]))
    (data_dir / "confidence.json").write_text(json.dumps([FOREIGN_CONFIDENCE_ROW]))

    persistence.log_mistake("ours", "VQA", "Q", "w", "r")
    persistence.set_mistake_cause("ours", "misread")
    persistence.resolve_mistake("ours")
    persistence.log_confidence("ours", "VQA", 3, False)

    mistakes = json.loads((data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {APP}
    confidence = json.loads((data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {APP}
