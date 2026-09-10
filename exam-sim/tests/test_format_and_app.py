"""Fenced-code rendering helper and a single offscreen MainWindow build."""
import re

from config import WINDOW_TITLE


def test_question_html_renders_fence_as_pre_and_strips_language_tag():
    from ui.format import question_html

    html_out = question_html("Before\n```python\nqc.h(0)\n```\nAfter")
    pre_blocks = re.findall(r"<pre[^>]*>(.*?)</pre>", html_out, re.S)
    assert pre_blocks == ["qc.h(0)"]      # language tag stripped, code kept verbatim
    assert "Before<br>" in html_out
    assert "After" in html_out


def test_question_html_escapes_markup():
    from ui.format import question_html

    assert "&lt;b&gt;" in question_html("a <b> tag")
    assert "&lt;qc&gt;" in question_html("```\n<qc>\n```")


def test_main_window_constructs_offscreen(qapp, data_dir):
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
