"""History screen: flagged list (newest first, Unflag works) and stat cards."""
from __future__ import annotations

from PyQt6.QtWidgets import QPushButton

import persistence
from core.models import AnswerFormat, Attempt, Problem, ProblemCategory, SessionStats


def _problem(text: str, cat: ProblemCategory = ProblemCategory.GATE_SEQUENCE) -> Problem:
    return Problem(
        category=cat, difficulty="beginner", question_text=text,
        answer_format=AnswerFormat.MULTIPLE_CHOICE, correct_answer="0",
        choices=["a", "b", "c", "d"], circuit_png=None, aux_circuit_png=None,
        matrix_str=None, state_str=None, solution_steps=["s"], key_concepts=["k"],
    )


def test_flagged_rows_is_safe_before_refresh(qapp):
    from ui.screens.history_screen import HistoryScreen

    assert HistoryScreen().flagged_rows() == 0


def test_flagged_list_newest_first_and_unflag_button_removes_entry(qapp, isolated_data_dir):
    from ui.screens.history_screen import HistoryScreen

    first, second = _problem("first question"), _problem("second question", ProblemCategory.NOISE_CHANNEL)
    persistence.toggle_flag(first)
    persistence.toggle_flag(second)

    screen = HistoryScreen()
    screen.refresh()
    assert screen.flagged_rows() == 2
    ids = [fid for fid, _ in screen._flag_rows]
    assert ids == [persistence.flag_id_for(second), persistence.flag_id_for(first)]

    _, newest_row = screen._flag_rows[0]
    unflag = [b for b in newest_row.findChildren(QPushButton) if b.text() == "Unflag"]
    assert len(unflag) == 1
    unflag[0].click()

    assert screen.flagged_rows() == 1
    assert [fid for fid, _ in screen._flag_rows] == [persistence.flag_id_for(first)]
    assert [e["id"] for e in persistence.load_flagged()] == [persistence.flag_id_for(first)]

    screen._flag_rows[0][1].findChildren(QPushButton)[0].click()
    assert screen.flagged_rows() == 0
    assert persistence.load_flagged() == []
    screen.refresh()
    assert screen.flagged_rows() == 0


def test_stat_cards_reflect_saved_sessions(qapp, isolated_data_dir):
    from ui.screens.history_screen import HistoryScreen

    def stats(rows):
        s = SessionStats()
        for score in rows:
            ok = score >= 7
            s.attempts.append(Attempt(_problem("q"), "0", ok, score, "fb", elapsed_secs=3))
            s.total += 1
            s.correct += int(ok)
        return s

    screen = HistoryScreen()
    screen.refresh()
    assert screen._sessions_card._val.text() == "0"
    assert screen._accuracy_card._val.text() == "—"
    assert not screen._empty_lbl.isHidden()

    persistence.save_session(stats([10, 0]))
    persistence.save_session(stats([10, 10]), sprint=True)
    screen.refresh()
    assert screen._sessions_card._val.text() == "2"
    assert screen._problems_card._val.text() == "4"
    assert screen._accuracy_card._val.text() == "75%"
    assert screen._empty_lbl.isHidden()
