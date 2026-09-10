"""Single offscreen smoke test: the main window constructs with no API key/data."""
from __future__ import annotations


def test_main_window_constructs(qapp, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    from ui.main_window import MainWindow

    win = MainWindow()
    try:
        assert win.windowTitle()
        assert win.centralWidget() is not None
    finally:
        win.close()
        win.deleteLater()
