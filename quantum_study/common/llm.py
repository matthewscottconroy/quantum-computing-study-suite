"""The one place the Claude model is named.

Eight of the ten apps call the Claude API (question generation, free-form
grading, code review).  Each used to hard-code the model id in its own
``config.py``; they all read it from here now.

Changing ``MODEL`` is not only a rename.  The calls are written for a model
that answers with a single text block and does not think unless asked: they
read ``response.content[0].text`` and set a small ``max_tokens``.  Newer
models think by default, so the first content block may not be text and the
thinking counts against ``max_tokens``.  Move the id together with those call
sites (``grep -rn "messages.create" quantum_study``), not on its own.
"""
from __future__ import annotations

__all__ = ["MODEL"]

#: Model id used by every app that calls the Claude API.
MODEL = "claude-sonnet-4-6"
