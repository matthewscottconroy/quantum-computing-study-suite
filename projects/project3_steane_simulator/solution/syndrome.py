"""syndrome.py -- milestone 3: 6-ancilla syndrome extraction.

CSS codes make this easy: the X and Z sectors are measured by two different
ancilla patterns, and each sector's 3 bits are a classical Hamming syndrome.

    Z-type generator  Z on supp   ->  ancilla in |0>, CX data->ancilla,
                                      measure Z.  Detects **X** errors.
    X-type generator  X on supp   ->  ancilla in |+>, CX ancilla->data,
                                      H, measure Z.  Detects **Z** errors.

Bit layout (fixed once, here, and never re-derived anywhere else):

    bits 0,1,2  X-checks, in the row order of H  -> locate a Z error
    bits 3,4,5  Z-checks, in the row order of H  -> locate an X error

so ``syndrome_bits[3:6]`` read as a 3-bit number (MSB first) is the 1-based
index of a single X error, and ``syndrome_bits[0:3]`` likewise for Z.

TRAP: Qiskit counts strings are little-endian -- the right-most character is
clbit 0.  ``bits_from_key`` is the single place that is dealt with, and
``test_steane.py`` checks it against all 21 weight-1 errors.
"""

from __future__ import annotations

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister
from qiskit_aer import AerSimulator

from steane_code import N_QUBITS, SUPPORTS

N_ANCILLA = 6
_SIM = AerSimulator(method="stabilizer")


def syndrome_circuit() -> QuantumCircuit:
    """Measure all six generators onto six ancillas (ancillas start in |0>)."""
    data = QuantumRegister(N_QUBITS, "d")
    anc = QuantumRegister(N_ANCILLA, "a")
    cr = ClassicalRegister(N_ANCILLA, "s")
    qc = QuantumCircuit(data, anc, cr)

    # X-checks (bits 0..2): ancilla in |+>, CX ancilla -> data
    for i, support in enumerate(SUPPORTS):
        qc.h(anc[i])
        for q in support:
            qc.cx(anc[i], data[q])
        qc.h(anc[i])
    # Z-checks (bits 3..5): ancilla in |0>, CX data -> ancilla
    for i, support in enumerate(SUPPORTS):
        for q in support:
            qc.cx(data[q], anc[3 + i])
    for i in range(N_ANCILLA):
        qc.measure(anc[i], cr[i])
    return qc


def inject_error(qc: QuantumCircuit, qubit: int, pauli: str) -> None:
    """Apply a single-qubit Pauli error to a data qubit in place."""
    if pauli == "X":
        qc.x(qubit)
    elif pauli == "Z":
        qc.z(qubit)
    elif pauli == "Y":
        qc.y(qubit)
    elif pauli != "I":
        raise ValueError(f"unknown Pauli {pauli!r}")


def bits_from_key(key: str) -> np.ndarray:
    """Counts key -> 6 syndrome bits indexed by ancilla number.

    Qiskit prints clbit 0 last, so the string must be reversed.
    """
    clean = key.replace(" ", "")
    return np.array([int(c) for c in reversed(clean)], dtype=np.uint8)


def extract(state_circuit: QuantumCircuit, errors=(), shots: int = 64,
            rounds: int = 1, seed: int = 1234) -> list[np.ndarray]:
    """Run encoding -> errors -> ``rounds`` syndrome extractions.

    Returns one (rounds, 6) array of syndrome bits per shot.
    """
    data = QuantumRegister(N_QUBITS, "d")
    anc = QuantumRegister(N_ANCILLA, "a")
    regs = [ClassicalRegister(N_ANCILLA, f"s{r}") for r in range(rounds)]
    qc = QuantumCircuit(data, anc, *regs)
    qc.compose(state_circuit, qubits=data, inplace=True)
    for qubit, pauli in errors:
        inject_error(qc, data[qubit], pauli)
    base = syndrome_circuit()
    for r in range(rounds):
        # fresh ancillas each round
        qc.reset(anc)
        qc.compose(base, qubits=list(data) + list(anc), clbits=list(regs[r]),
                   inplace=True)
    result = _SIM.run(qc, shots=shots, seed_simulator=seed).result()
    out = []
    for key, count in result.get_counts().items():
        # multi-register keys come back space-separated, LAST register first
        parts = key.split()[::-1]
        rows = np.stack([bits_from_key(p) for p in parts])
        out.extend([rows] * count)
    return out


def predicted_syndrome(qubit: int, pauli: str) -> np.ndarray:
    """What the six bits *should* be for a weight-1 error (the oracle)."""
    bits = np.zeros(6, dtype=np.uint8)
    col = [(qubit + 1) >> 2 & 1, (qubit + 1) >> 1 & 1, (qubit + 1) & 1]
    if pauli in ("Z", "Y"):          # X-checks see Z errors
        bits[0:3] = col
    if pauli in ("X", "Y"):          # Z-checks see X errors
        bits[3:6] = col
    return bits
