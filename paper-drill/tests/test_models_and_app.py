"""Domain-model helpers, key discovery, and a single offscreen MainWindow build."""
import pytest

from config import DEFAULT_Q_COUNT, WINDOW_TITLE
from core.models import DrillConfig, SessionStats, Verdict


def test_session_stats_average():
    assert SessionStats().average == 0.0
    assert SessionStats(total=3, scores=[10, 5, 0]).average == pytest.approx(5.0)


def test_verdict_labels():
    assert {v.value for v in Verdict} == {"Correct", "Partially correct", "Incorrect"}


def test_drill_config_default_question_count():
    assert DrillConfig(paper_text="x", paper_title="t").question_count == DEFAULT_Q_COUNT


def test_get_api_key_none_without_env_or_file(no_api_key):
    from ai.client import get_api_key
    assert get_api_key() is None


def test_make_client_raises_without_key(no_api_key):
    from ai.client import make_client
    with pytest.raises(RuntimeError):
        make_client()


def test_main_window_constructs_offscreen_without_api_key(qapp, data_dir, no_api_key):
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
