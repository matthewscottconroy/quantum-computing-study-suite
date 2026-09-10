"""Shared fixtures for problem-trainer tests.

* Puts the app root on sys.path so bare imports (``from problems import
  all_problems``) work exactly as they do inside the app.
* ``data_dir`` redirects the persistence path constants into a temp dir so no
  test can ever touch the real ~/.local/share/quantum-study/.
* ``problems`` / ``derivations`` load each bank once per process.
* ``fake_claude`` swaps the Anthropic client for an in-memory stub.
* ``main_window`` builds an offscreen MainWindow on the Setup page with
  persistence redirected and no API key; ``find_button`` locates a child
  QPushButton by its visible text so tests click what the user clicks.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_PERSISTENCE_PATHS = {
    "DATA_DIR": "",
    "HISTORY_FILE": "problems_history.json",
    "FLAGGED_FILE": "problems_flagged.json",   # suite flagging contract: <prefix>_flagged.json
}


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point persistence at a temp dir. Fails closed if a constant vanished."""
    import persistence

    root = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(root))
    for name, filename in _PERSISTENCE_PATHS.items():
        if not hasattr(persistence, name):
            pytest.fail(f"persistence.{name} no longer exists - update tests/conftest.py")
        monkeypatch.setattr(persistence, name, root / filename if filename else root)
    # Also redirect any other Path-valued *_FILE constant on the module so no
    # code path reached from a test can write outside the temp dir.
    for name, value in list(vars(persistence).items()):
        if name.endswith("_FILE") and isinstance(value, Path) and name not in _PERSISTENCE_PATHS:
            monkeypatch.setattr(persistence, name, root / value.name)
    return root


@pytest.fixture
def no_api_key(monkeypatch, tmp_path):
    """Guarantee no Anthropic key is discoverable from env or key file."""
    import ai.client as client_mod

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(client_mod, "API_KEY_FILE", tmp_path / "missing_key.txt")


@pytest.fixture(scope="session")
def problems():
    from problems import all_problems
    return all_problems()


@pytest.fixture(scope="session")
def derivations():
    from derivations import all_derivations
    return all_derivations()


@pytest.fixture
def main_window(qapp, data_dir, no_api_key):
    """Offscreen MainWindow on the Setup page; closed and deleted afterwards."""
    from ui.main_window import MainWindow

    win = MainWindow()
    try:
        yield win
    finally:
        win.close()
        win.deleteLater()
        qapp.processEvents()


@pytest.fixture
def find_button():
    """``find_button(widget, text)`` -> the one child QPushButton with that text."""
    from PyQt6.QtWidgets import QPushButton

    def _find(widget, text: str):
        matches = [b for b in widget.findChildren(QPushButton) if b.text() == text]
        assert len(matches) == 1, f"expected one {text!r} button, found {len(matches)}"
        return matches[0]

    return _find


_QAPP = None


@pytest.fixture(scope="session")
def qapp():
    """One offscreen QApplication for the whole test process."""
    global _QAPP
    from PyQt6.QtWidgets import QApplication

    _QAPP = QApplication.instance() or QApplication([])
    return _QAPP


class FakeMessages:
    """Stand-in for ``anthropic.Anthropic().messages`` that records each call.

    Each entry in ``responses`` is either a string (one text block) or a list of
    pre-built content blocks; responses are consumed in order, repeating the last.
    """

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        item = self._responses.pop(0) if len(self._responses) > 1 else self._responses[0]
        blocks = item if isinstance(item, list) else [SimpleNamespace(type="text", text=item)]
        return SimpleNamespace(content=blocks)


@pytest.fixture
def fake_claude(monkeypatch):
    """``fake_claude(*responses)`` installs a stub client in ai.grader."""

    def install(*responses) -> FakeMessages:
        import ai.grader
        from config import MODEL

        messages = FakeMessages(responses)
        client = SimpleNamespace(messages=messages)
        monkeypatch.setattr(ai.grader, "make_client", lambda: (client, MODEL))
        return messages

    return install
