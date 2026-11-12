"""Fixtures for the paper-drill tests.

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


#: Every path helper the app writes through.  ``data_dir`` asserts each one
#: lands inside the temp directory, so a store added later that forgets to go
#: through common.datadir fails the whole suite instead of quietly writing to
#: the real study history.
_PATH_HELPERS = ("history_path", "library_path", "flagged_path",
                 "settings_path", "mistakes_path", "confidence_path")


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    """Point the suite at a temp dir. Fails closed if a path escapes it."""
    from quantum_study.paper_drill import persistence
    from quantum_study.common import schema

    root = tmp_path / "quantum-study"
    monkeypatch.setenv("QUANTUM_STUDY_DATA_DIR", str(root))

    # One backup per file per *process*, so without this a later test in the
    # same process would silently skip the backup its predecessor already made.
    schema.reset_session()

    for name in _PATH_HELPERS:
        helper = getattr(persistence, name, None)
        if helper is None:
            pytest.fail(f"persistence.{name}() no longer exists - update tests/conftest.py")
        resolved = helper()
        assert resolved.parent == root, f"{name}() escaped the temp dir: {resolved}"
    return root


@pytest.fixture
def no_api_key(monkeypatch, tmp_path):
    """Guarantee no Anthropic key is discoverable from env or key file."""
    import quantum_study.paper_drill.ai.client as client_mod

    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setattr(client_mod, "API_KEY_FILE", tmp_path / "missing_key.txt")


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
        import quantum_study.paper_drill.ai.generator  # noqa: F401
        from quantum_study.paper_drill import ai
        import quantum_study.paper_drill.ai.grader  # noqa: F401
        from quantum_study.paper_drill import ai
        from quantum_study.paper_drill.config import MODEL

        messages = FakeMessages(responses)
        client = SimpleNamespace(messages=messages)
        monkeypatch.setattr(ai.generator, "make_client", lambda: (client, MODEL))
        monkeypatch.setattr(ai.grader, "make_client", lambda: (client, MODEL))
        return messages

    return install
