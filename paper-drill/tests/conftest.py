"""Shared fixtures for paper-drill tests.

* Puts the app root on sys.path so bare imports (``from ai.generator import
  generate_questions``) work exactly as they do inside the app.
* ``data_dir`` redirects every persistence path constant into a temp dir so no
  test can ever touch the real ~/.local/share/quantum-study/.
* ``fake_claude`` swaps the Anthropic client for an in-memory stub so prompt
  building and response parsing can be exercised with zero network access.
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
    "HISTORY_FILE": "paper_history.json",
    "LIBRARY_FILE": "paper_library.json",
    "FLAGGED_FILE": "paper_flagged.json",
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
    # Also redirect any other Path-valued *_FILE constant on the module (a
    # store added later that the table above does not know about yet) so no
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


_QAPP = None


@pytest.fixture(scope="session")
def qapp():
    """One offscreen QApplication for the whole test process."""
    global _QAPP
    from PyQt6.QtWidgets import QApplication

    _QAPP = QApplication.instance() or QApplication([])
    return _QAPP


class FakeMessages:
    """Stand-in for ``anthropic.Anthropic().messages`` that records each call."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls: list[dict] = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        text = self._responses.pop(0) if len(self._responses) > 1 else self._responses[0]
        return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])


@pytest.fixture
def fake_claude(monkeypatch):
    """``fake_claude(*responses)`` installs a stub client in generator + grader.

    Returns the FakeMessages so tests can inspect the recorded request kwargs.
    """

    def install(*responses: str) -> FakeMessages:
        import ai.generator
        import ai.grader
        from config import MODEL

        messages = FakeMessages(responses)
        client = SimpleNamespace(messages=messages)
        monkeypatch.setattr(ai.generator, "make_client", lambda: (client, MODEL))
        monkeypatch.setattr(ai.grader, "make_client", lambda: (client, MODEL))
        return messages

    return install
