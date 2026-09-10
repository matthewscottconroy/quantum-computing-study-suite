"""History screen: pure helpers (verdict scaling, aggregates, trend) + offscreen render.

The verdict boundaries pin ``pass_mark_for`` scaling as the History table
shows it: 46/47 of 68, 6/7 of 10 (sprint), 4/5 of 7 (OpenQASM sprint — only
7 questions in the bank).
"""
from __future__ import annotations

import json
import time

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QPushButton

from config import PASS_MARK, EXAM_QUESTION_COUNT

T0 = 1_750_000_000.0          # fixed base timestamp (2025-06); rows are ordered relative to it


def _entry(mode: str, total: int, correct: int, ts: float, sections: dict | None = None,
           duration: float = 60.0) -> dict:
    if sections is None:
        sections = ({"Create circuits": {"total": total, "correct": correct}}
                    if mode == "full" else {"Sampler": {"total": total, "correct": correct}})
    return {"timestamp": ts, "mode": mode, "total": total, "correct": correct,
            "duration_secs": duration, "sections": sections}


# The seven-row synthetic history used throughout (oldest first).
SAMPLE = [
    _entry("full", 68, 46, T0 + 100, duration=3661,
           sections={"Create circuits": {"total": 12, "correct": 10},
                     "OpenQASM": {"total": 4, "correct": 2}}),
    _entry("full", 68, 47, T0 + 200, duration=5000,
           sections={"Create circuits": {"total": 12, "correct": 10},
                     "OpenQASM": {"total": 4, "correct": 2}}),
    _entry("sprint", 10, 6, T0 + 300, sections={"Sampler": {"total": 10, "correct": 6}}),
    _entry("sprint", 10, 7, T0 + 400, sections={"Sampler": {"total": 10, "correct": 7}}),
    _entry("sprint", 7, 4, T0 + 500, sections={"OpenQASM": {"total": 7, "correct": 4}}),
    _entry("sprint", 7, 5, T0 + 600, sections={"OpenQASM": {"total": 7, "correct": 5}}),
    _entry("sprint", 0, 0, T0 + 700, sections={}),          # degenerate: never written by the app
]


@pytest.fixture
def hs():
    from ui.screens import history_screen
    return history_screen


# ── pure helpers ─────────────────────────────────────────────────────────────

def test_fmt_duration(hs):
    assert hs._fmt_duration(3661) == "1h 01m"
    assert hs._fmt_duration(5000) == "1h 23m"
    assert hs._fmt_duration(754) == "12m 34s"
    assert hs._fmt_duration(0) == "0m 00s"
    assert hs._fmt_duration(None) == "0m 00s"
    assert hs._fmt_duration(-5) == "0m 00s"


def test_mode_label(hs):
    assert hs._mode_label({"mode": "full", "sections": {"Sampler": {}}}) == "Full exam"
    assert hs._mode_label({"mode": "sprint", "sections": {"Sampler": {}}}) == "Sprint · Sampler"
    assert hs._mode_label({"mode": "sprint", "sections": {}}) == "Sprint"
    assert hs._mode_label({"mode": "sprint", "sections": {"A": {}, "B": {}}}) == "Sprint"


def test_attempt_rows_verdicts_at_every_boundary(hs):
    rows = hs.attempt_rows(SAMPLE)
    assert [r["score"] for r in rows] == ["0/0", "5/7", "4/7", "7/10", "6/10", "47/68", "46/68"]
    by_score = {r["score"]: r for r in rows}
    for score, passed, need in (("46/68", False, 47), ("47/68", True, 47),
                                ("6/10", False, 7), ("7/10", True, 7),
                                ("4/7", False, 5), ("5/7", True, 5)):
        assert by_score[score]["passed"] is passed, score
        assert by_score[score]["need"] == need, score
    assert by_score["0/0"]["passed"] is False and by_score["0/0"]["need"] == 0
    assert by_score["0/0"]["pct"] == 0.0
    assert by_score["46/68"]["duration"] == "1h 01m"
    assert by_score["47/68"]["duration"] == "1h 23m"
    assert by_score["46/68"]["is_full"] and not by_score["6/10"]["is_full"]
    assert by_score["5/7"]["mode"] == "Sprint · OpenQASM"
    assert by_score["47/68"]["pct"] == pytest.approx(100 * 47 / 68)


def test_attempt_rows_tolerates_missing_fields(hs):
    rows = hs.attempt_rows([{"mode": "full"}, {}])
    assert len(rows) == 2
    assert all(r["score"] == "0/0" and r["passed"] is False for r in rows)


def test_section_totals_only_counts_full_exams_in_exam_order(hs):
    totals = hs.section_totals(SAMPLE)
    assert list(totals) == ["Create circuits", "OpenQASM"]          # exam order, sprints excluded
    assert totals["Create circuits"] == {"total": 24, "correct": 20}
    assert totals["OpenQASM"] == {"total": 8, "correct": 4}


def test_section_totals_empty_for_sprint_only_history(hs):
    assert hs.section_totals([e for e in SAMPLE if e["mode"] != "full"]) == {}
    assert hs.section_totals([]) == {}


def test_section_totals_appends_unknown_sections_last(hs):
    hist = [_entry("full", 5, 5, T0, sections={"Zeta": {"total": 1, "correct": 1},
                                               "Sampler": {"total": 4, "correct": 4}})]
    assert list(hs.section_totals(hist)) == ["Sampler", "Zeta"]


def test_trend_series_numbers_only_plotted_attempts(hs):
    series = hs.trend_series(SAMPLE)
    assert series["full"][0] == [1, 2]
    assert series["sprint"][0] == [3, 4, 5, 6]                 # total==0 entry skipped, not counted
    assert series["full"][1] == pytest.approx([100 * 46 / 68, 100 * 47 / 68])
    assert series["sprint"][1] == pytest.approx([60.0, 70.0, 100 * 4 / 7, 100 * 5 / 7])
    n_points = sum(len(xs) for xs, _ in series.values())
    assert max(series["full"][0] + series["sprint"][0]) == n_points   # last point inside xlim


def test_trend_series_is_chronological_regardless_of_file_order(hs):
    shuffled = [SAMPLE[3], SAMPLE[0], SAMPLE[2], SAMPLE[1]]
    series = hs.trend_series(shuffled)
    assert series["full"][0] == [1, 2] and series["sprint"][0] == [3, 4]
    assert hs.trend_series([]) == {"full": ([], []), "sprint": ([], [])}


# ── offscreen rendering ──────────────────────────────────────────────────────

@pytest.fixture
def screen(qapp, hs):
    s = hs.HistoryScreen()
    s.resize(1100, 760)
    s.show()
    yield s
    s.close()
    s.deleteLater()
    qapp.processEvents()


def _col(table, col: int) -> list[str]:
    return [table.item(r, col).text() for r in range(table.rowCount())]


def test_render_history_populates_cards_tables_and_chart(screen, qapp, hs):
    screen.render_history(SAMPLE)
    qapp.processEvents()

    assert screen._sessions_card.value() == "7"
    assert screen._full_card.value() == "2"
    assert screen._best_card.value() == "47/68"
    assert screen._pass_card.value() == "1/2 passed"
    assert screen._empty_lbl.isHidden()
    assert not screen._attempts_table.isHidden()

    t = screen._attempts_table
    assert t.rowCount() == 7
    assert _col(t, 3) == ["FAIL", "PASS", "FAIL", "PASS", "FAIL", "PASS", "FAIL"]
    assert _col(t, 2)[1] == "5/7  (71%)"
    assert _col(t, 2)[5] == "47/68  (69%)"
    assert _col(t, 1)[:3] == ["Sprint", "Sprint · OpenQASM", "Sprint · OpenQASM"]
    assert _col(t, 4)[5:] == ["1h 23m", "1h 01m"]
    assert t.item(6, 3).toolTip() == "pass mark 47/68"
    assert t.item(2, 3).toolTip() == "pass mark 5/7"
    assert t.item(4, 3).toolTip() == "pass mark 7/10"
    assert t.item(1, 3).foreground().color().name() == hs.theme.SUCCESS
    assert t.item(0, 3).foreground().color().name() == hs.theme.ERROR

    s = screen._section_table
    assert not s.isHidden() and screen._section_note.isHidden()
    assert _col(s, 0) == ["Create circuits", "OpenQASM"]
    assert _col(s, 1) == ["20/24", "4/8"]
    assert _col(s, 2) == ["83%", "50%"]
    assert _col(s, 3) == ["18%", "6%"]

    sub = screen._sub_lbl.text()
    assert sub.startswith("7 sessions on file — most recent: sprint 0/0 on ")
    assert f"Pass mark is {PASS_MARK}/{EXAM_QUESTION_COUNT} (69%)" in sub

    if hs.HAVE_MPL:
        assert screen._canvas is not None
        assert screen._trend_slot.count() == 1


def test_subheading_keeps_section_casing(screen, hs):
    screen.render_history([SAMPLE[5]])                        # Sprint · OpenQASM 5/7
    assert "most recent: sprint · OpenQASM 5/7 on " in screen._sub_lbl.text()
    screen.render_history([SAMPLE[1]])
    assert "most recent: full exam 47/68 on " in screen._sub_lbl.text()


def test_sprint_only_history_hides_section_table_and_shows_note(screen, qapp):
    screen.render_history([e for e in SAMPLE if e["mode"] != "full"])
    qapp.processEvents()
    assert screen._full_card.value() == "0"
    assert screen._best_card.value() == "—" and screen._pass_card.value() == "—"
    assert screen._section_table.isHidden()
    assert not screen._section_note.isHidden()
    assert not screen._attempts_table.isHidden()


def test_empty_history_shows_only_the_empty_label(screen, qapp):
    screen.render_history([])
    qapp.processEvents()
    assert not screen._empty_lbl.isHidden()
    for w in (screen._trend_lbl, screen._trend_frame, screen._attempts_lbl,
              screen._attempts_table, screen._section_lbl, screen._section_note,
              screen._section_table):
        assert w.isHidden(), w
    assert screen._sessions_card.value() == "0"
    assert screen._sub_lbl.text().startswith(f"Pass mark is {PASS_MARK}/{EXAM_QUESTION_COUNT}")


def test_attempts_table_caps_visible_rows(screen, qapp, hs):
    many = [_entry("sprint", 10, 7, T0 + i) for i in range(20)]
    screen.render_history(many)
    qapp.processEvents()
    t = screen._attempts_table
    assert t.rowCount() == 20
    row_h = t.verticalHeader().defaultSectionSize()
    header_h = t.horizontalHeader().sizeHint().height()
    assert t.height() == header_h + hs._MAX_VISIBLE_ROWS * row_h + 4
    # all 12 capped rows are fully visible; the rest scroll
    assert t.rowViewportPosition(hs._MAX_VISIBLE_ROWS - 1) + row_h <= t.viewport().height()
    assert t.rowViewportPosition(hs._MAX_VISIBLE_ROWS) + row_h > t.viewport().height()


def test_refresh_reads_history_file_from_data_dir(screen, qapp, data_dir):
    import persistence
    data_dir.mkdir(parents=True, exist_ok=True)
    persistence.HISTORY_FILE.write_text(json.dumps(SAMPLE[:2]))
    screen.refresh()
    qapp.processEvents()
    assert screen._sessions_card.value() == "2"
    assert screen._attempts_table.rowCount() == 2
    # a corrupt file renders as "no sessions" rather than crashing
    persistence.HISTORY_FILE.write_text("{not json")
    screen.refresh()
    assert screen._sessions_card.value() == "0"
    assert not screen._empty_lbl.isHidden()


def test_back_button_emits_back_requested(screen, qapp):
    fired: list[int] = []
    screen.back_requested.connect(lambda: fired.append(1))
    btn = next(b for b in screen.findChildren(QPushButton) if b.text() == "← Back to Home")
    QTest.mouseClick(btn, Qt.MouseButton.LeftButton)
    assert fired == [1]


def test_render_is_idempotent_across_repeated_calls(screen, qapp):
    """Re-rendering (as every History visit does) must not accumulate widgets."""
    for _ in range(3):
        screen.render_history(SAMPLE)
        qapp.processEvents()
    assert screen._trend_slot.count() <= 1
    assert screen._attempts_table.rowCount() == 7
    screen.render_history([])
    assert screen._attempts_table.isHidden()
