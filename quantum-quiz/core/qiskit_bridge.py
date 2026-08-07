"""
Route topic → context mode and delegate to the appropriate qiskit_contexts module.
All Qiskit imports are isolated here and in qiskit_contexts/; nothing else imports Qiskit.
"""

from __future__ import annotations
from core.topics import SUBJECT_CONTEXT_MODE
from qiskit_contexts import QiskitContext, EMPTY_CONTEXT


def build_context(subject: str, topic: str) -> QiskitContext:
    """Return a QiskitContext (may be EMPTY_CONTEXT if no Qiskit scaffolding applies)."""
    mode = SUBJECT_CONTEXT_MODE.get(subject)
    try:
        if mode == "circuit":
            from qiskit_contexts.circuit_contexts import build_context as _build
            return _build(topic)
        elif mode == "hamiltonian":
            from qiskit_contexts.hamiltonian_contexts import build_context as _build
            return _build(topic)
        elif mode == "statevector":
            from qiskit_contexts.statevector_contexts import build_context as _build
            return _build(topic)
    except Exception:
        # Never crash the quiz over a failed Qiskit context — just go contextless
        pass
    return EMPTY_CONTEXT
