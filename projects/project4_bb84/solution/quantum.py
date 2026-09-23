"""quantum.py -- milestone 1's explicit quantum-mechanics check.

The vectorised simulator in ``bb84.py`` never builds a state vector: it
encodes "measuring in the conjugate basis is a fair coin" as an ``np.where``.
This module does the same four preparations with real ``Statevector`` objects
so that assumption is *verified* rather than asserted.
"""

from __future__ import annotations

import numpy as np
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector

#: (bit, basis) -> the BB84 state, as a 1-qubit circuit
STATES = {
    (0, 0): "|0>", (1, 0): "|1>", (0, 1): "|+>", (1, 1): "|->",
}


def prepare(bit: int, basis: int) -> QuantumCircuit:
    qc = QuantumCircuit(1)
    if bit:
        qc.x(0)
    if basis:
        qc.h(0)
    return qc


def measurement_distribution(bit: int, basis: int, measure_basis: int) -> np.ndarray:
    """P(outcome 0), P(outcome 1) for measuring the state in ``measure_basis``."""
    qc = prepare(bit, basis)
    if measure_basis:
        qc.h(0)                     # rotate X basis onto the computational one
    probs = Statevector(qc).probabilities()
    return np.asarray(probs, dtype=float)


def sample_outcomes(bit: int, basis: int, measure_basis: int,
                    shots: int, seed: int) -> np.ndarray:
    """``shots`` measurement outcomes as 0/1 integers."""
    qc = prepare(bit, basis)
    if measure_basis:
        qc.h(0)
    memory = Statevector(qc).sample_memory(shots, qargs=[0], seed=seed)
    return np.array([int(m) for m in memory], dtype=np.int8)
