"""encoder.py -- milestone 2: the encoding circuit.

Construction (derived, not copied)
----------------------------------
``|0_L> = sum over c in C_perp of |c>`` where ``C_perp`` is the row space of H.
A superposition over a linear code is built the standard way:

1. Put one "seed" qubit per generator into |+>.  Column 4 (1-indexed) of H is
   non-zero only in row 1, column 2 only in row 2, column 1 only in row 3 --
   so qubits 3, 1 and 0 (0-indexed) each belong to exactly one generator and
   can carry its free coefficient.  That is ``code.SEEDS``.
2. CNOT from each seed to the rest of its generator's support.  Qubit j then
   holds the XOR of the coefficients of every generator containing it, i.e.
   the state is ``sum over a,b,c of |a h1 + b h2 + c h3>`` = |0_L>.

To encode an arbitrary ``|psi> = alpha|0> + beta|1>`` rather than |0_L>, note
that ``|1_L> = X_bar |0_L>`` for any representative of X_bar.  Pick a weight-3
Hamming codeword **disjoint from the seeds** -- qubits (2, 4, 5), from columns
3, 5, 6 -- and spread the input across it *before* the seed network:

    CX 2->4, CX 2->5        (alpha|0000000> + beta|0010110>)
    then the |0_L> network  (alpha|0_L> + beta X_bar|0_L>)

Because everything is linear over F2 the two steps compose exactly.  The
disjointness matters: if the injection touched a seed qubit, the H gate would
destroy the amplitude it carries.

TRAP: the seed CNOTs all have seeds as controls and non-seeds as targets, so
they commute with each other and the order inside the network is free -- but
the *injection* must come first, and the H gates must come before the network.
Getting that order wrong produces a state that is still stabilised by the six
generators (so a naive check passes!) but encodes the wrong logical state.
``test_steane.py`` therefore checks the logical content, not just the
stabilisers.
"""

from __future__ import annotations

from qiskit import QuantumCircuit

from steane_code import INJECT, N_QUBITS, SEEDS, SUPPORTS


def encoder_circuit(inject_input: bool = True) -> QuantumCircuit:
    """The Steane encoder as a 7-qubit unitary.

    With ``inject_input=True`` the logical state is taken from qubit
    ``INJECT[0]`` (qubit 2); the other six qubits must start in |0>.
    With ``inject_input=False`` the circuit prepares |0_L> from |0>^7.
    """
    qc = QuantumCircuit(N_QUBITS, name="steane_encode")
    if inject_input:
        src, *rest = INJECT
        for q in rest:
            qc.cx(src, q)
    qc.barrier(label="inject")
    for seed in SEEDS:
        qc.h(seed)
    for seed, support in zip(SEEDS, SUPPORTS):
        for q in support:
            if q != seed:
                qc.cx(seed, q)
    return qc


def encode_state(prep: QuantumCircuit | None = None) -> QuantumCircuit:
    """A 7-qubit circuit preparing the encoding of the state ``prep`` makes.

    ``prep`` is a 1-qubit circuit applied to the injection qubit first, so
    ``encode_state(None)`` gives |0_L>, ``encode_state(x_gate)`` gives |1_L>
    and ``encode_state(h_gate)`` gives |+_L>.
    """
    qc = QuantumCircuit(N_QUBITS, name="steane_state")
    if prep is not None:
        qc.compose(prep, qubits=[INJECT[0]], inplace=True)
    qc.compose(encoder_circuit(inject_input=True), inplace=True)
    return qc


def logical_zero() -> QuantumCircuit:
    return encode_state(None)


def logical_one() -> QuantumCircuit:
    p = QuantumCircuit(1)
    p.x(0)
    return encode_state(p)


def logical_plus() -> QuantumCircuit:
    p = QuantumCircuit(1)
    p.h(0)
    return encode_state(p)
