"""QiskitContext datatype shared across all context-builder modules."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class QiskitContext:
    """All the Qiskit-generated artefacts that may accompany a question."""
    circuit_png: bytes | None = None          # rendered circuit image
    qasm_snippet: str | None = None           # QASM text of the circuit
    hamiltonian_str: str | None = None        # formatted Pauli-term table
    statevector_table: str | None = None      # amplitude table as plain text
    prose_description: str = ""               # short human-readable description

    def has_content(self) -> bool:
        return any([
            self.circuit_png,
            self.qasm_snippet,
            self.hamiltonian_str,
            self.statevector_table,
        ])


# Singleton for the "no context" case so callers can do `ctx is EMPTY_CONTEXT`
EMPTY_CONTEXT = QiskitContext()
