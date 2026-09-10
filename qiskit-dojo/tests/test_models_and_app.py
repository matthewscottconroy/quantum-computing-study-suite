"""Domain-model helpers and a single offscreen MainWindow build."""
import pytest

from config import WINDOW_TITLE
from core.models import Kata, KataAttempt, RunResult, SessionStats


def _kata(kid: str) -> Kata:
    return Kata(id=kid, section="Sampler", title="t", difficulty="beginner",
                prompt="p", starter_code="", test_code="", solution_code="")


def test_session_stats_counts_and_accuracy():
    empty = SessionStats()
    assert (empty.total, empty.passed, empty.accuracy) == (0, 0, 0.0)
    stats = SessionStats(attempts=[
        KataAttempt(_kata("a"), passed=True),
        KataAttempt(_kata("b"), passed=False),
        KataAttempt(_kata("c"), passed=True),
    ])
    assert (stats.total, stats.passed) == (3, 2)
    assert stats.accuracy == pytest.approx(2 / 3)


def test_run_result_defaults():
    result = RunResult(passed=False, output="")
    assert result.phase == ""
    assert result.duration_secs == 0.0


def test_main_window_constructs_offscreen(qapp, data_dir, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from PyQt6.QtWidgets import QMainWindow
    from ui.main_window import MainWindow

    win = MainWindow()
    try:
        assert isinstance(win, QMainWindow)
        assert win.windowTitle() == WINDOW_TITLE
        assert win.centralWidget() is not None
    finally:
        win.close()
        win.deleteLater()
        qapp.processEvents()
