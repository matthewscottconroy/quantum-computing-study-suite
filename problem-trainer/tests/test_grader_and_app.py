"""ai.grader retry wrapper (stubbed client), key discovery, offscreen MainWindow."""
import json
from types import SimpleNamespace

import pytest

from ai.response_parser import ParseError
from config import MODEL, WINDOW_TITLE
from core.models import GradeResult

GOOD = json.dumps({"score": 6, "feedback": "ok", "missed_points": []})


def test_call_retries_once_on_unparseable_output(fake_claude):
    from ai.grader import _call
    from ai.response_parser import parse_grade_response

    messages = fake_claude("total garbage", GOOD)
    result = _call("SYS", "USER", parse_grade_response)
    assert isinstance(result, GradeResult) and result.score == 6
    assert len(messages.calls) == 2
    for call in messages.calls:
        assert call["model"] == MODEL
        assert call["system"] == "SYS"
        assert call["messages"] == [{"role": "user", "content": "USER"}]


def test_call_gives_up_after_two_bad_responses(fake_claude):
    from ai.grader import _call
    from ai.response_parser import parse_grade_response

    messages = fake_claude("garbage one", "garbage two", GOOD)
    with pytest.raises(ParseError):
        _call("s", "u", parse_grade_response)
    assert len(messages.calls) == 2


def test_call_ignores_non_text_blocks(fake_claude):
    from ai.grader import _call
    from ai.response_parser import parse_grade_response

    fake_claude([SimpleNamespace(type="tool_use", name="x"),
                 SimpleNamespace(type="text", text=GOOD)])
    assert _call("s", "u", parse_grade_response).score == 6


def test_no_key_is_reported_cleanly(no_api_key):
    from ai.client import has_api_key, make_client

    assert has_api_key() is False
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
