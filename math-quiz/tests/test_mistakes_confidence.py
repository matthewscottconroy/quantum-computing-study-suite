"""Mistake journal + confidence calibration: persistence helpers, the two new
UI rows, and a headless drive of the whole answer → journal → resolve loop."""
from __future__ import annotations

import json
import time

import pytest

import persistence
from core.models import Evaluation, Question, QuizConfig


def _question(text="State the spectral theorem for Hermitian operators.",
              subject="Linear Algebra", topic="spectral theorem") -> Question:
    return Question(subject=subject, topic=topic, difficulty="beginner",
                    question_type="conceptual", text=text, hints=["h1"])


def _evaluation(score: int) -> Evaluation:
    return Evaluation(score=score, verdict="Incorrect" if score < 4 else "Correct",
                      feedback="feedback text", model_answer="the model answer")


MISTAKE_FIELDS = {"id", "app", "category", "question", "your_answer",
                  "correct_answer", "cause", "note", "timestamp", "resolved"}
CONFIDENCE_FIELDS = {"id", "app", "category", "confidence", "correct", "timestamp"}


# ── Persistence: paths and empty state ────────────────────────────────────────

def test_new_files_are_redirected_and_named_per_the_suite_contract(data_dir):
    assert persistence._MISTAKES_FILE == data_dir / "mistakes.json"
    assert persistence._CONFIDENCE_FILE == data_dir / "confidence.json"
    assert persistence._SETTINGS_FILE == data_dir / "math_settings.json"
    assert not data_dir.exists()
    # Missing files are simply empty; nothing is created just by reading.
    assert persistence.load_mistakes() == []
    assert persistence.load_app_mistakes() == []
    assert persistence.load_confidence() == []
    assert persistence.mistake_cause_counts() == {}
    assert persistence.confidence_accuracy() == {}
    assert persistence.confidently_wrong_counts() == {}
    assert persistence.load_settings() == {"confidence_prompt": True}
    assert persistence.confidence_prompt_enabled() is True
    assert not data_dir.exists()


# ── Persistence: mistake journal ──────────────────────────────────────────────

def test_make_mistake_entry_matches_the_schema_field_for_field():
    q = _question()
    before = time.time()
    entry = persistence.make_mistake_entry(q, "my wrong answer", "the right answer")
    assert set(entry) == MISTAKE_FIELDS
    assert entry["id"] == persistence.mistake_id_for(q)
    assert entry["app"] == "math-quiz"
    assert entry["category"] == "Linear Algebra"
    assert entry["question"] == q.text
    assert entry["your_answer"] == "my wrong answer"
    assert entry["correct_answer"] == "the right answer"
    assert entry["cause"] is None
    assert entry["note"] == ""
    assert isinstance(entry["timestamp"], float) and before <= entry["timestamp"] <= time.time()
    assert entry["resolved"] is False
    # Every field is JSON-round-trippable exactly as written.
    assert json.loads(json.dumps(entry)) == entry


def test_mistake_id_is_a_stable_hash_of_subject_plus_question_text():
    q = _question()
    assert persistence.mistake_id_for(q) == persistence.mistake_id_for(_question())
    # Whitespace-insensitive: a re-wrapped question is the same item.
    rewrapped = _question(text="State the spectral theorem\n  for Hermitian   operators.")
    assert persistence.mistake_id_for(rewrapped) == persistence.mistake_id_for(q)
    # Subject and text both participate.
    assert persistence.mistake_id_for(_question(subject="Topology & Geometry")) != persistence.mistake_id_for(q)
    assert persistence.mistake_id_for(_question(text="Something else")) != persistence.mistake_id_for(q)
    # But the topic does not: same question, re-tagged topic, same item.
    assert persistence.mistake_id_for(_question(topic="eigenvalues")) == persistence.mistake_id_for(q)
    digest = persistence.mistake_id_for(q)
    assert len(digest) == 16 and all(c in "0123456789abcdef" for c in digest)


def test_long_text_fields_are_clipped_to_200_characters():
    q = _question(text="Prove that " + "x" * 400)
    entry = persistence.make_mistake_entry(q, "y" * 400, "z" * 400, note="n" * 400)
    for field in ("question", "your_answer", "correct_answer", "note"):
        assert len(entry[field]) == 200, field
        assert entry[field].endswith("…"), field
    assert persistence.clip_text("  a \n b  ") == "a b"
    assert persistence.clip_text(None) == ""


def test_cause_validation_accepts_the_six_codes_and_null():
    assert persistence.MISTAKE_CAUSES == (
        "misread", "didnt_know", "knew_but_slipped", "confused", "out_of_time", "other")
    for code in persistence.MISTAKE_CAUSES:
        assert persistence.coerce_cause(code) == code
    assert persistence.coerce_cause(None) is None
    assert persistence.coerce_cause("") is None
    with pytest.raises(ValueError, match="unknown mistake cause"):
        persistence.coerce_cause("lazy")
    with pytest.raises(ValueError):
        persistence.make_mistake_entry(_question(), "a", "b", cause="typo")


def test_log_mistake_writes_appends_and_updates_the_open_entry():
    q1, q2 = _question(), _question(text="Define a unitary operator.")
    first = persistence.log_mistake(q1, "wrong", "right")
    on_disk = json.loads(persistence._MISTAKES_FILE.read_text(encoding="utf-8"))
    assert isinstance(on_disk, list) and len(on_disk) == 1
    assert set(on_disk[0]) == MISTAKE_FIELDS and on_disk[0] == first

    persistence.log_mistake(q2, "also wrong", "also right")
    assert [e["id"] for e in persistence.load_mistakes()] == [
        persistence.mistake_id_for(q1), persistence.mistake_id_for(q2)]

    # Missing the same item again updates it rather than duplicating.
    again = persistence.log_mistake(q1, "wrong a second time", "right")
    assert len(persistence.load_mistakes()) == 2
    assert again["your_answer"] == "wrong a second time"
    assert again["timestamp"] >= first["timestamp"]

    # A cause survives a later re-log that does not supply one.
    persistence.update_mistake(first["id"], cause="misread", note="skim-read it")
    persistence.log_mistake(q1, "third try", "right")
    kept = persistence.load_mistakes()[0]
    assert kept["cause"] == "misread" and kept["note"] == "skim-read it"


def test_update_mistake_sets_cause_and_note_and_can_clear_the_cause():
    q = _question()
    entry_id = persistence.log_mistake(q, "wrong", "right")["id"]
    updated = persistence.update_mistake(entry_id, cause="knew_but_slipped", note="sign error")
    assert updated["cause"] == "knew_but_slipped" and updated["note"] == "sign error"
    stored = json.loads(persistence._MISTAKES_FILE.read_text(encoding="utf-8"))[0]
    assert stored["cause"] == "knew_but_slipped" and stored["note"] == "sign error"
    # Note-only update keeps the cause; cause=None clears it again.
    persistence.update_mistake(entry_id, note="a better note")
    assert persistence.load_mistakes()[0]["cause"] == "knew_but_slipped"
    assert persistence.load_mistakes()[0]["note"] == "a better note"
    persistence.update_mistake(entry_id, cause=None)
    assert persistence.load_mistakes()[0]["cause"] is None
    assert persistence.update_mistake("no-such-id", cause="other") is None
    with pytest.raises(ValueError):
        persistence.update_mistake(entry_id, cause="nope")


def test_resolve_mistake_matches_on_app_and_id_only():
    q, other = _question(), _question(text="Define a unitary operator.")
    persistence.log_mistake(q, "wrong", "right")
    persistence.log_mistake(other, "wrong", "right")
    # An identical id belonging to another app must not be touched.
    entries = persistence.load_mistakes()
    foreign = dict(entries[0], app="quantum-quiz", resolved=False)
    persistence.save_mistakes(entries + [foreign])

    assert persistence.resolve_mistake(q) is True
    by_app = {(e["id"], e["app"]): e["resolved"] for e in persistence.load_mistakes()}
    assert by_app[(persistence.mistake_id_for(q), "math-quiz")] is True
    assert by_app[(persistence.mistake_id_for(q), "quantum-quiz")] is False
    assert by_app[(persistence.mistake_id_for(other), "math-quiz")] is False
    assert persistence.resolve_mistake(q) is False                 # already resolved
    assert persistence.resolve_mistake("unknown-id") is False
    assert persistence.resolve_mistake(persistence.mistake_id_for(other)) is True

    # Missing a resolved item again opens a fresh entry instead of reopening it.
    persistence.log_mistake(q, "wrong again", "right")
    rows = [e for e in persistence.load_mistakes()
            if e["id"] == persistence.mistake_id_for(q) and e["app"] == "math-quiz"]
    assert [e["resolved"] for e in rows] == [True, False]


def test_cause_counts_summarise_the_open_journal():
    q1 = _question()
    q2 = _question(text="Define a unitary operator.")
    q3 = _question(text="Compute the trace of a projector.")
    persistence.log_mistake(q1, "w", "r", cause="misread")
    persistence.log_mistake(q2, "w", "r", cause="misread")
    persistence.log_mistake(q3, "w", "r")
    assert persistence.mistake_cause_counts() == {"misread": 2, "uncategorised": 1}
    persistence.resolve_mistake(q1)
    assert persistence.mistake_cause_counts() == {"misread": 1, "uncategorised": 1}
    assert persistence.mistake_cause_counts(include_resolved=True) == {
        "misread": 2, "uncategorised": 1}


def test_corrupt_missing_and_foreign_rows_never_crash_the_journal(data_dir):
    data_dir.mkdir(parents=True)
    persistence._MISTAKES_FILE.write_text("{not json", encoding="utf-8")
    assert persistence.load_mistakes() == []
    persistence._MISTAKES_FILE.write_text('{"a": 1}', encoding="utf-8")
    assert persistence.load_mistakes() == []
    persistence.log_mistake(_question(), "w", "r")                 # recreates the file
    assert len(persistence.load_mistakes()) == 1
    persistence.save_mistakes([{"nope": 1}, "string", {"id": ""},
                               {"id": "keep", "app": "other-app"}])
    assert [e["id"] for e in persistence.load_mistakes()] == ["keep"]
    assert persistence.load_app_mistakes() == []


def test_journal_is_utf8_atomic_and_capped(data_dir, monkeypatch):
    q = _question(subject="Calculus & Real Analysis", topic="ε-δ definitions",
                  text="Let f: ℝ → ℝ be continuous. Show …")
    persistence.log_mistake(q, "ε was wrong", "δ depends on ε")
    written = persistence._MISTAKES_FILE.read_bytes().decode("utf-8")
    assert "Let f: ℝ → ℝ" in written and "δ depends on ε" in written   # UTF-8, not escaped
    assert not list(data_dir.glob("*.tmp"))

    good = persistence._MISTAKES_FILE.read_bytes()

    def boom(*_a, **_k):
        raise OSError("disk full")
    monkeypatch.setattr(persistence.os, "replace", boom)
    with pytest.raises(OSError):
        persistence.log_mistake(_question(text="another"), "w", "r")
    assert persistence._MISTAKES_FILE.read_bytes() == good
    assert not list(data_dir.glob("*.tmp"))
    monkeypatch.undo()

    # Growth cap: only the newest _MISTAKES_MAX rows are kept.
    monkeypatch.setattr(persistence, "_MISTAKES_MAX", 3)
    persistence.save_mistakes([{"id": str(i), "app": "math-quiz"} for i in range(10)])
    assert [e["id"] for e in persistence.load_mistakes()] == ["7", "8", "9"]


# ── Persistence: confidence calibration ───────────────────────────────────────

def test_make_confidence_entry_matches_the_schema_field_for_field():
    before = time.time()
    entry = persistence.make_confidence_entry("abc123", "Linear Algebra", 3, True)
    assert set(entry) == CONFIDENCE_FIELDS
    assert entry["id"] == "abc123"
    assert entry["app"] == "math-quiz"
    assert entry["category"] == "Linear Algebra"
    assert entry["confidence"] == 3
    assert entry["correct"] is True
    assert isinstance(entry["timestamp"], float) and before <= entry["timestamp"] <= time.time()
    assert json.loads(json.dumps(entry)) == entry


def test_confidence_levels_are_validated():
    assert persistence.CONFIDENCE_LABELS == {
        1: "Guessing", 2: "Unsure", 3: "Fairly sure", 4: "Certain"}
    for level in (1, 2, 3, 4):
        assert persistence.coerce_confidence(level) == level
    for bad in (0, 5, -1, "3", 3.0, None, True):
        with pytest.raises(ValueError):
            persistence.coerce_confidence(bad)


def test_log_confidence_pairs_the_rating_with_the_grade():
    q = _question()
    row = persistence.log_confidence(q, 4, False)
    assert row["id"] == persistence.mistake_id_for(q)     # same item id as the journal
    assert row["category"] == "Linear Algebra"
    on_disk = json.loads(persistence._CONFIDENCE_FILE.read_text(encoding="utf-8"))
    assert on_disk == [row]
    persistence.log_confidence(q, 4, True)
    persistence.log_confidence(_question(subject="Number Theory", text="Q2"), 1, False)
    assert len(persistence.load_confidence()) == 3
    assert persistence.confidence_accuracy() == {
        4: {"total": 2, "correct": 1}, 1: {"total": 1, "correct": 0}}
    # Confidently wrong = rated >= 3 and graded wrong.
    assert persistence.confidently_wrong_counts() == {"Linear Algebra": 1}
    assert persistence.confidently_wrong_counts(min_confidence=1) == {
        "Linear Algebra": 1, "Number Theory": 1}


def test_confidence_file_tolerates_corruption_and_foreign_rows(data_dir):
    data_dir.mkdir(parents=True)
    persistence._CONFIDENCE_FILE.write_text("]]not json", encoding="utf-8")
    assert persistence.load_confidence() == []
    persistence.save_confidence([
        {"id": "a", "app": "quantum-quiz", "category": "X", "confidence": 4, "correct": False},
        {"id": "b", "app": "math-quiz", "category": "Y", "confidence": 99, "correct": False},
        {"nope": 1},
        {"id": "c", "app": "math-quiz", "category": "Y", "confidence": 2, "correct": True},
    ])
    assert [e["id"] for e in persistence.load_confidence()] == ["a", "b", "c"]
    assert persistence.confidence_accuracy() == {2: {"total": 1, "correct": 1}}
    assert persistence.confidently_wrong_counts() == {}


# ── Persistence: settings ─────────────────────────────────────────────────────

def test_confidence_opt_out_is_remembered_and_survives_corruption(data_dir):
    assert persistence.confidence_prompt_enabled() is True
    persistence.set_confidence_prompt_enabled(False)
    assert json.loads(persistence._SETTINGS_FILE.read_text(encoding="utf-8")) == {
        "confidence_prompt": False}
    assert persistence.confidence_prompt_enabled() is False
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.confidence_prompt_enabled() is True
    # Unknown keys are preserved; a corrupt file falls back to the defaults.
    persistence.save_settings({"confidence_prompt": False, "future_key": 7})
    assert persistence.load_settings()["future_key"] == 7
    persistence.set_confidence_prompt_enabled(True)
    assert persistence.load_settings() == {"confidence_prompt": True, "future_key": 7}
    persistence._SETTINGS_FILE.write_text("nonsense", encoding="utf-8")
    assert persistence.load_settings() == {"confidence_prompt": True}
    assert persistence.confidence_prompt_enabled() is True


# ── UI: confidence strip on the question screen ───────────────────────────────

def test_confidence_strip_is_optional_single_select_and_resets(qapp):
    from ui.screens.question_screen import QuestionScreen

    qs = QuestionScreen()
    assert qs.confidence() is None
    assert qs.confidence_enabled() is True
    assert sorted(qs._confidence_buttons) == [1, 2, 3, 4]

    qs._confidence_buttons[3].click()
    assert qs.confidence() == 3
    qs._confidence_buttons[1].click()
    assert qs.confidence() == 1
    assert [lv for lv, c in qs._confidence_buttons.items() if c.isChecked()] == [1]
    qs._confidence_buttons[1].click()                 # clicking again unselects
    assert qs.confidence() is None

    qs._confidence_buttons[4].click()
    qs.load_question(_question(), 1, 5)               # a new question starts unrated
    assert qs.confidence() is None
    assert not any(c.isChecked() for c in qs._confidence_buttons.values())

    qs._confidence_buttons[2].click()
    qs.set_confidence_enabled(False)
    assert qs.confidence_enabled() is False and qs.confidence() is None
    qs.set_confidence_enabled(True)
    assert qs.confidence_enabled() is True

    fired = []
    qs.confidence_opt_out.connect(lambda: fired.append(True))
    qs._confidence_optout_btn.click()
    assert fired == [True]
    qs.deleteLater()


def test_confidence_chips_are_keyboard_reachable_and_labelled(qapp):
    from PyQt6.QtCore import Qt
    from ui.screens.question_screen import QuestionScreen
    from PyQt6.QtGui import QFont, QFontMetrics
    from ui.widgets.chip_button import CHECK_GLYPH, UNCHECK_GLYPH

    qs = QuestionScreen()
    for level, chip in qs._confidence_buttons.items():
        assert chip.focusPolicy() & Qt.FocusPolicy.TabFocus        # Tab reaches it
        assert chip.accessibleName() == (
            f"Confidence {level} of 4: {persistence.CONFIDENCE_LABELS[level]}")
        assert chip.toolTip()
        assert "focus" in chip.styleSheet()                        # visible focus ring
        assert chip.accessibleDescription() == "not selected"
        # Selection carries a glyph, never colour alone — and the unchecked
        # state carries one too, so the label cannot shift or elide on click.
        assert chip.text().startswith(UNCHECK_GLYPH)
        bold = QFont(chip.font())
        bold.setBold(True)
        checked_text_width = QFontMetrics(bold).horizontalAdvance(
            f"{CHECK_GLYPH} {chip.base_text()}")
        assert chip.minimumWidth() >= checked_text_width
        chip.click()
        assert chip.text().startswith(CHECK_GLYPH)
        assert chip.text().endswith(chip.base_text())
        assert chip.accessibleDescription() == "selected"
        chip.click()
    assert qs._confidence_optout_btn.accessibleName()
    assert qs._confidence_optout_btn.focusPolicy() & Qt.FocusPolicy.TabFocus
    qs.deleteLater()


# ── UI: "what went wrong?" row on the feedback screen ─────────────────────────

def test_mistake_row_appears_only_for_a_wrong_answer(qapp):
    from ui.screens.feedback_screen import FeedbackScreen

    fb = FeedbackScreen()
    assert fb.mistake_prompt_visible() is False
    fb.load_evaluation(_evaluation(9))
    assert fb.mistake_prompt_visible() is False
    fb.load_evaluation(_evaluation(4))                # partially correct: no prompt
    assert fb.mistake_prompt_visible() is False
    fb.load_evaluation(_evaluation(3))
    assert fb.mistake_prompt_visible() is True
    assert sorted(fb._cause_buttons) == sorted(persistence.MISTAKE_CAUSES)
    fb.deleteLater()


def test_mistake_row_is_single_select_skippable_and_resets(qapp):
    from ui.screens.feedback_screen import FeedbackScreen

    fb = FeedbackScreen()
    causes, notes = [], []
    fb.mistake_cause_chosen.connect(causes.append)
    fb.mistake_note_committed.connect(notes.append)

    fb.load_evaluation(_evaluation(1))
    fb._cause_buttons["misread"].click()
    assert fb.mistake_cause() == "misread" and causes == ["misread"]
    fb._cause_buttons["out_of_time"].click()
    assert fb.mistake_cause() == "out_of_time" and causes[-1] == "out_of_time"
    assert [c for c, b in fb._cause_buttons.items() if b.isChecked()] == ["out_of_time"]
    fb._cause_buttons["out_of_time"].click()          # unselect
    assert fb.mistake_cause() is None and causes[-1] == ""

    fb._note_edit.setText("  little-endian again  ")
    fb._note_edit.editingFinished.emit()
    assert notes == ["little-endian again"]
    fb._note_edit.editingFinished.emit()              # focus-out with no change: silent
    assert notes == ["little-endian again"]

    # Next wrong answer starts clean, and nothing is emitted by the reset.
    fb.load_evaluation(_evaluation(0))
    assert fb.mistake_cause() is None and fb.mistake_note() == ""
    assert not any(b.isChecked() for b in fb._cause_buttons.values())
    assert causes == ["misread", "out_of_time", ""] and notes == ["little-endian again"]

    # Skipping is always possible: nothing here disables "Next Question".
    advanced = []
    fb.next_question_requested.connect(lambda: advanced.append(True))
    fb.load_evaluation(_evaluation(1))
    fb.next_question_requested.emit()
    assert advanced == [True]
    fb.deleteLater()


def test_mistake_controls_are_keyboard_reachable_and_labelled(qapp):
    from PyQt6.QtCore import Qt
    from ui.screens.feedback_screen import FeedbackScreen, CAUSE_LABELS

    fb = FeedbackScreen()
    for code, chip in fb._cause_buttons.items():
        assert chip.focusPolicy() & Qt.FocusPolicy.TabFocus
        assert chip.accessibleName() == f"Cause of mistake: {CAUSE_LABELS[code]}"
        assert "focus" in chip.styleSheet()
    assert fb._note_edit.accessibleName()
    assert fb._note_edit.maxLength() == persistence.TEXT_FIELD_MAX == 200
    assert "focus" in fb._note_edit.styleSheet()
    fb.deleteLater()


def test_new_widget_text_clears_45_to_1_against_the_dark_palette():
    """Contrast guard for the chip states (text is never colour-only anyway)."""
    from ui import theme
    from ui.widgets.chip_button import CHIP_QSS

    def _rel_luminance(rgb):
        chan = []
        for v in rgb:
            v /= 255.0
            chan.append(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4)
        return 0.2126 * chan[0] + 0.7152 * chan[1] + 0.0722 * chan[2]

    def _rgb(hex_color):
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

    def _ratio(fg, bg):
        l1, l2 = sorted((_rel_luminance(fg), _rel_luminance(bg)), reverse=True)
        return (l1 + 0.05) / (l2 + 0.05)

    text, surface2, accent = _rgb(theme.TEXT), _rgb(theme.SURFACE2), _rgb(theme.ACCENT)
    blended = tuple(0.18 * a + 0.82 * s for a, s in zip(accent, surface2))
    assert _ratio(text, surface2) >= 4.5          # unchecked chip
    assert _ratio(text, blended) >= 4.5           # checked chip (accent tint)
    assert _ratio(_rgb(theme.TEXT_MUTED), _rgb(theme.BG)) >= 4.5       # the "optional" hints
    assert _ratio(_rgb(theme.TEXT_MUTED), _rgb(theme.SURFACE)) >= 4.5
    assert f"rgba({accent[0]}, {accent[1]}, {accent[2]}, 0.18)" in CHIP_QSS


# ── Headless drive of the whole loop ──────────────────────────────────────────

@pytest.fixture
def driven_window(qapp, monkeypatch):
    """MainWindow with the two Claude workers replaced by synchronous fakes."""
    from PyQt6.QtCore import QObject, pyqtSignal
    import ui.main_window as mw

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    queued_questions: list[Question] = []
    queued_evaluations: list[Evaluation] = []

    class FakeQuestionWorker(QObject):
        question_ready = pyqtSignal(object)
        error = pyqtSignal(str)

        def __init__(self, session, parent=None):
            super().__init__(parent)
            self._session = session

        def start(self):
            question = queued_questions.pop(0)
            self._session.record_generated(question)
            self.question_ready.emit(question)

    class FakeEvaluationWorker(QObject):
        evaluation_ready = pyqtSignal(object)
        error = pyqtSignal(str)

        def __init__(self, question, answer, parent=None):
            super().__init__(parent)

        def start(self):
            self.evaluation_ready.emit(queued_evaluations.pop(0))

    monkeypatch.setattr(mw, "QuestionWorker", FakeQuestionWorker)
    monkeypatch.setattr(mw, "EvaluationWorker", FakeEvaluationWorker)

    win = mw.MainWindow()
    win.queued_questions = queued_questions
    win.queued_evaluations = queued_evaluations
    try:
        yield win
    finally:
        win.close()
        win.deleteLater()


def _answer(win, qapp, text: str, confidence: int | None = None) -> None:
    if confidence is not None:
        win._question._confidence_buttons[confidence].click()
    win._question._answer_edit.setPlainText(text)
    win._question._submit_btn.click()
    qapp.processEvents()


def test_drive_wrong_answer_journals_categorises_and_resolves(driven_window, qapp):
    import ui.main_window as mw

    win = driven_window
    q = _question()
    win.queued_questions.extend([q, q])
    win.queued_evaluations.extend([_evaluation(2), _evaluation(9)])

    win._on_quiz_started(QuizConfig(subjects=["Linear Algebra"], difficulty="beginner",
                                    question_types=["conceptual"], question_count=2))
    qapp.processEvents()
    assert win._stack.currentIndex() == mw.PAGE_QUESTION
    assert win._question.confidence_enabled() is True

    # (1) answer it wrongly, rated "certain" beforehand
    before = time.time()
    _answer(win, qapp, "Every Hermitian operator is unitary.", confidence=4)
    assert win._stack.currentIndex() == mw.PAGE_FEEDBACK
    assert win._feedback.mistake_prompt_visible() is True

    # (2) the journal entry matches the contract field for field
    rows = json.loads(persistence._MISTAKES_FILE.read_text(encoding="utf-8"))
    assert len(rows) == 1
    entry = rows[0]
    assert set(entry) == MISTAKE_FIELDS
    assert entry["id"] == persistence.mistake_id_for(q)
    assert entry["app"] == "math-quiz"
    assert entry["category"] == "Linear Algebra"       # category == subject
    assert entry["question"] == q.text
    assert entry["your_answer"] == "Every Hermitian operator is unitary."
    assert entry["correct_answer"] == "the model answer"
    assert entry["cause"] is None                      # skippable: logged uncategorised
    assert entry["note"] == ""
    assert isinstance(entry["timestamp"], float) and before <= entry["timestamp"] <= time.time()
    assert entry["resolved"] is False

    # (3) choosing a cause (with a note) updates that same entry
    win._feedback._note_edit.setText("mixed up Hermitian and unitary")
    win._feedback._cause_buttons["confused"].click()
    qapp.processEvents()
    rows = json.loads(persistence._MISTAKES_FILE.read_text(encoding="utf-8"))
    assert len(rows) == 1
    assert rows[0]["cause"] == "confused"
    assert rows[0]["note"] == "mixed up Hermitian and unitary"
    assert persistence.mistake_cause_counts() == {"confused": 1}

    # (4) the confidence rating is paired with the grade
    conf = json.loads(persistence._CONFIDENCE_FILE.read_text(encoding="utf-8"))
    assert len(conf) == 1
    assert set(conf[0]) == CONFIDENCE_FIELDS
    assert conf[0]["id"] == persistence.mistake_id_for(q)
    assert conf[0]["app"] == "math-quiz"
    assert conf[0]["category"] == "Linear Algebra"
    assert conf[0]["confidence"] == 4
    assert conf[0]["correct"] is False                 # confidently wrong
    assert persistence.confidently_wrong_counts() == {"Linear Algebra": 1}

    # (5) re-answering the same item correctly resolves it
    win._feedback.next_question_requested.emit()
    qapp.processEvents()
    assert win._stack.currentIndex() == mw.PAGE_QUESTION
    assert win._question.confidence() is None          # rating reset for the new question
    _answer(win, qapp, "A Hermitian operator has real eigenvalues.", confidence=3)
    assert win._feedback.mistake_prompt_visible() is False
    rows = json.loads(persistence._MISTAKES_FILE.read_text(encoding="utf-8"))
    assert len(rows) == 1 and rows[0]["resolved"] is True
    assert rows[0]["cause"] == "confused"              # the diagnosis is kept
    assert persistence.mistake_cause_counts() == {}
    assert persistence.confidence_accuracy() == {
        4: {"total": 1, "correct": 0}, 3: {"total": 1, "correct": 1}}

    # Existing behaviour is untouched: the session still recorded both answers.
    assert win._session.stats.answered == 2
    assert persistence.has_draft() is True


def test_drive_skipping_both_prompts_still_logs_the_mistake(driven_window, qapp):
    win = driven_window
    q = _question(text="Compute the determinant of a 2x2 rotation matrix.")
    win.queued_questions.append(q)
    win.queued_evaluations.append(_evaluation(0))
    win._on_quiz_started(QuizConfig(subjects=["Linear Algebra"], difficulty="beginner",
                                    question_types=["conceptual"], question_count=1))
    qapp.processEvents()

    _answer(win, qapp, "no idea")                      # no confidence, no cause
    rows = persistence.load_mistakes()
    assert len(rows) == 1 and rows[0]["cause"] is None and rows[0]["resolved"] is False
    assert persistence.load_confidence() == []         # nothing invented
    assert persistence.mistake_cause_counts() == {"uncategorised": 1}


def test_drive_confidence_opt_out_is_remembered_across_windows(driven_window, qapp, monkeypatch):
    import ui.main_window as mw

    win = driven_window
    assert win._question.confidence_enabled() is True
    assert win._setup.confidence_pref() is True

    win._question._confidence_optout_btn.click()
    qapp.processEvents()
    assert win._question.confidence_enabled() is False
    assert win._setup.confidence_pref() is False
    assert persistence.confidence_prompt_enabled() is False
    assert win.statusBar().currentMessage()

    # A fresh window never asks again…
    second = mw.MainWindow()
    try:
        assert second._question.confidence_enabled() is False
        assert second._setup.confidence_pref() is False
        # …until it is switched back on from the setup screen.
        second._setup._confidence_cb.setChecked(True)
        qapp.processEvents()
        assert second._question.confidence_enabled() is True
        assert persistence.confidence_prompt_enabled() is True
    finally:
        second.close()
        second.deleteLater()


def test_drive_persistence_failures_are_surfaced_not_crashed(driven_window, qapp, monkeypatch):
    win = driven_window
    win.queued_questions.append(_question())
    win.queued_evaluations.append(_evaluation(1))
    win._on_quiz_started(QuizConfig(subjects=["Linear Algebra"], difficulty="beginner",
                                    question_types=["conceptual"], question_count=1))
    qapp.processEvents()

    def boom(*_a, **_k):
        raise OSError("read-only data dir")
    monkeypatch.setattr(persistence, "log_mistake", boom)

    _answer(win, qapp, "wrong", confidence=2)
    assert "Could not update the mistake journal" in win.statusBar().currentMessage()
    assert win._pending_mistake_id is None
    # The flow continues: feedback still rendered, confidence still recorded.
    assert win._feedback.mistake_prompt_visible() is True
    assert len(persistence.load_confidence()) == 1
    # Clicking a cause with no journal entry to update is a silent no-op.
    win._feedback._cause_buttons["other"].click()
    qapp.processEvents()
    assert persistence.load_mistakes() == []


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

    q = _question()
    persistence.log_mistake(q, "wrong", "right")
    persistence.update_mistake(persistence.mistake_id_for(q), cause="misread")
    persistence.resolve_mistake(q)
    persistence.log_confidence(q, 3, False)

    mistakes = json.loads((data_dir / "mistakes.json").read_text())
    assert mistakes[0] == FOREIGN_MISTAKE_ROW      # unchanged, unknown keys intact
    assert len(mistakes) > 1                       # and our own row was written
    assert {r["app"] for r in mistakes[1:]} == {"math-quiz"}
    confidence = json.loads((data_dir / "confidence.json").read_text())
    assert confidence[0] == FOREIGN_CONFIDENCE_ROW
    assert len(confidence) > 1
    assert {r["app"] for r in confidence[1:]} == {"math-quiz"}
