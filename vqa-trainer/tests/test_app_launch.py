"""The app must construct headless with no API key."""
from __future__ import annotations


def test_main_window_constructs_offscreen(qapp, monkeypatch):
    from PyQt6.QtWidgets import QMainWindow

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    win = MainWindow()
    try:
        assert isinstance(win, QMainWindow)
        assert win.windowTitle()
        assert win.centralWidget() is not None
    finally:
        win.close()
