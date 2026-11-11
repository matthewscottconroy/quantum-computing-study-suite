"""Fixtures for the problem-trainer tests.

The repository's root ``conftest.py`` provides ``qapp``, headless Qt and a
process-wide throwaway data directory.  This file narrows the data directory
to a fresh ``tmp_path`` per test and adds what only this app needs.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

APP_ROOT = Path(__file__).resolve().parent.parent

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


_PERSISTENCE_PATHS = {
    "DATA_DIR": "",
    "HISTORY_FILE": "problems_history.json",
    "FLAGGED_FILE": "problems_flagged.json",   # suite flagging contract: <prefix>_flagged.json
    "MISTAKES_FILE": "mistakes.json",          # suite-wide mistake journal
    "CONFIDENCE_FILE": "confidence.json",      # suite-wide confidence calibration
    "SETTINGS_FILE": "problems_settings.json", # this app's own UI preferences
}


#: persistence path *helper* -> the file it must resolve to inside the temp dir.
#: These are the call-time resolvers the app actually writes through.
_PERSISTENCE_RESOLVERS = {
    "history_path":    "problems_history.json",
    "flagged_path":    "problems_flagged.json",
    "mistakes_path":   "mistakes.json",
    "confidence_path": "confidence.json",
    "settings_path":   "problems_settings.json",
}


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point the suite data directory at a temp dir. Fails closed."""
    from quantum_study.problem_trainer import persistence
    from quantum_study.common import schema

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
    # The constants above are the published surface; these resolvers are what
    # the writes actually use.  If the two ever disagree a test would silently
    # assert against a file nothing wrote, so check them here instead.
    for helper, filename in _PERSISTENCE_RESOLVERS.items():
        if not hasattr(persistence, helper):
            pytest.fail(f"persistence.{helper}() no longer exists - update tests/conftest.py")
        resolved = getattr(persistence, helper)()
        assert resolved == root / filename, (
            f"persistence.{helper}() resolves to {resolved}, not inside the temp dir")

    # Per-process state in common/ that would otherwise leak between tests.
    schema.reset_session()            # so the next write backs up again
    persistence.clear_write_error()
    yield root
    schema.reset_session()
    persistence.clear_write_error()


@pytest.fixture
def no_api_key(monkeypatch, tmp_path):
    """Guarantee no Anthropic key is discoverable from env or key file."""
    import quantum_study.problem_trainer.ai.client as client_mod

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(client_mod, "API_KEY_FILE", tmp_path / "missing_key.txt")


@pytest.fixture(scope="session")
def problems():
    from quantum_study.problem_trainer.problems import all_problems
    return all_problems()


@pytest.fixture(scope="session")
def derivations():
    from quantum_study.problem_trainer.derivations import all_derivations
    return all_derivations()


@pytest.fixture
def main_window(qapp, data_dir, no_api_key):
    """Offscreen MainWindow on the Setup page; closed and deleted afterwards."""
    from quantum_study.problem_trainer.ui.main_window import MainWindow

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
        import quantum_study.problem_trainer.ai.grader  # noqa: F401
        from quantum_study.problem_trainer import ai
        from quantum_study.problem_trainer.config import MODEL

        messages = FakeMessages(responses)
        client = SimpleNamespace(messages=messages)
        monkeypatch.setattr(ai.grader, "make_client", lambda: (client, MODEL))
        return messages

    return install
