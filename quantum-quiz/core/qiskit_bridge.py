"""
Route topic → context mode and delegate to the appropriate qiskit_contexts module.
All Qiskit imports are isolated here and in qiskit_contexts/; nothing else imports Qiskit.

The context modules are imported EAGERLY, at import time of this module, which
happens on the main thread (ui.main_window → workers.question_worker → here).
That is deliberate: build_context() is called from QuestionWorker QThreads, and
with Python 3.14 + qiskit 2.x the Rust extension (`qiskit._accelerate`) must be
initialised on the main thread — first-initialising it inside a worker thread
makes every *subsequent* fresh thread's Qiskit call segfault (the app used to
die at question 2 of every session).  Do not turn these back into lazy imports
inside build_context(); tests/test_qiskit_thread_safety.py guards this.
"""

from __future__ import annotations

import importlib
from typing import Callable

from core.topics import SUBJECT_CONTEXT_MODE
from qiskit_contexts import QiskitContext, EMPTY_CONTEXT

_CONTEXT_MODULES = {
    "circuit":     "qiskit_contexts.circuit_contexts",
    "hamiltonian": "qiskit_contexts.hamiltonian_contexts",
    "statevector": "qiskit_contexts.statevector_contexts",
}


def _import_builders() -> dict[str, Callable[[str], QiskitContext]]:
    """Import every context module now (main thread); a module that fails to
    import (e.g. Qiskit not installed) simply has no builder, and its subjects
    run contextless instead of crashing the quiz."""
    builders: dict[str, Callable[[str], QiskitContext]] = {}
    for mode, module_name in _CONTEXT_MODULES.items():
        try:
            builders[mode] = importlib.import_module(module_name).build_context
        except Exception:
            continue
    return builders


_BUILDERS = _import_builders()


def build_context(subject: str, topic: str) -> QiskitContext:
    """Return a QiskitContext (may be EMPTY_CONTEXT if no Qiskit scaffolding applies)."""
    builder = _BUILDERS.get(SUBJECT_CONTEXT_MODE.get(subject) or "")
    if builder is None:
        return EMPTY_CONTEXT
    try:
        return builder(topic)
    except Exception:
        # Never crash the quiz over a failed Qiskit context — just go contextless
        return EMPTY_CONTEXT
