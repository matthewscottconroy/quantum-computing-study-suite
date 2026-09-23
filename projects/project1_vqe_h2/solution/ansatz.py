"""ansatz.py -- milestone 2: an ansatz zoo behind one interface.

Four ansaetze, all built from standard single-parameter Pauli rotations so
that the two-term parameter-shift rule in ``vqe.py`` applies unchanged:

    hardware_efficient  efficient_su2(2, reps=1)   8 parameters
    real_pair           hand-built, real amplitudes 2 parameters
    ucc_single          one excitation parameter    1 parameter
    product             deliberately under-expressive control, 2 parameters

``product`` is not asked for by the spec.  It is here because without it the
milestone-5 error budget has a zero expressibility column: ansaetze (a)-(c)
all contain the exact ground state of this Hamiltonian, so their
expressibility error is numerically zero.  ``product`` has no entangling gate,
so it *cannot* represent the ground state once the molecule is stretched --
which is the cleanest possible demonstration of the milestone-5 question
"why is the stretched geometry harder?".
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter
from qiskit.circuit.library import efficient_su2


@dataclass(frozen=True)
class Ansatz:
    """A named parameterised circuit plus a sensible starting point."""

    name: str
    circuit: QuantumCircuit
    x0: np.ndarray
    note: str

    @property
    def num_parameters(self) -> int:
        return self.circuit.num_parameters


def _hardware_efficient() -> Ansatz:
    """(a) The generic hardware-efficient ansatz.

    ``efficient_su2`` is a lowercase *function* in Qiskit 2.x -- the old
    ``EfficientSU2`` class is gone.  reps=1 already gives 8 parameters for two
    qubits, which is four times more than the problem needs; that redundancy
    is exactly what makes it slow to optimise (see NOTES / SOLUTION.md).
    """
    qc = efficient_su2(2, reps=1, entanglement="linear")
    # TRAP (cost me an afternoon): starting from all-zeros puts the state at
    # |00>, which lies in the *other* parity block of this Hamiltonian.  The
    # gradient there points nowhere useful and L-BFGS converges happily to
    # -1.244585 Ha -- the minimum of the {|00>,|11>} block, 613 mHa above the
    # true ground state, with no warning.  Start from Hartree-Fock (|01>,
    # i.e. the first RY on q0 at pi) plus a small seeded jitter to break the
    # symmetry that keeps the ansatz inside a single block.
    x0 = np.zeros(qc.num_parameters)
    x0[0] = np.pi
    x0 += np.random.default_rng(7).normal(0.0, 0.1, qc.num_parameters)
    return Ansatz("hardware_efficient", qc, x0,
                  "generic; 8 parameters, heavily over-parameterised for H2")


def _real_pair() -> Ansatz:
    """(b) Hand-built 2-parameter real-amplitude ansatz.

    H has only real matrix elements (II, IZ, ZI, ZZ, XX -- no Y), so its
    ground state can always be chosen real.  RY rotations and a CX generate
    every real 2-qubit state reachable this way:

        RY(a) on q0, RY(b) on q1, then CX(q0 -> q1)

    At b = pi the state collapses to sin(a/2)|01> + cos(a/2)|10>, which is the
    full subspace the ground state lives in -- so this ansatz is exact.
    """
    a, b = Parameter("a"), Parameter("b")
    qc = QuantumCircuit(2, name="real_pair")
    qc.ry(a, 0)
    qc.ry(b, 1)
    qc.cx(0, 1)
    return Ansatz("real_pair", qc, np.array([np.pi / 2, np.pi]),
                  "2 real parameters; exact for this H at b = pi")


def _ucc_single() -> Ansatz:
    """(c) UCC-inspired single-excitation ansatz, one parameter.

    In the 2-qubit reduced picture |01> is Hartree-Fock (sigma_g doubly
    occupied) and |10> is the double excitation.  The excitation generator is
    Y (x) X, and exp(-i theta/2 * Y0 X1) is compiled the standard way: rotate
    both qubits into the Pauli basis, a CX ladder, RZ(theta) on the last wire,
    then undo.  theta = 0 leaves |01> untouched, as the milestone requires.
    """
    t = Parameter("t")
    qc = QuantumCircuit(2, name="ucc_single")
    qc.x(0)                 # Hartree-Fock reference |01>
    qc.rx(np.pi / 2, 0)     # Y-basis on q0
    qc.h(1)                 # X-basis on q1
    qc.cx(0, 1)
    qc.rz(t, 1)
    qc.cx(0, 1)
    qc.h(1)
    qc.rx(-np.pi / 2, 0)
    return Ansatz("ucc_single", qc, np.array([0.0]),
                  "1 parameter; chemically motivated, exact for this H")


def _product() -> Ansatz:
    """Control ansatz with no entangling gate -- cannot express a correlated
    ground state.  Its error *is* the correlation energy the ansatz misses."""
    a, b = Parameter("a"), Parameter("b")
    qc = QuantumCircuit(2, name="product")
    qc.ry(a, 0)
    qc.ry(b, 1)
    return Ansatz("product", qc, np.array([np.pi, 0.0]),
                  "no entangler; under-expressive by construction")


BUILDERS: dict[str, Callable[[], Ansatz]] = {
    "hardware_efficient": _hardware_efficient,
    "real_pair": _real_pair,
    "ucc_single": _ucc_single,
    "product": _product,
}

#: the three the spec asks for, in spec order
SPEC_ANSATZE = ("hardware_efficient", "real_pair", "ucc_single")


def get(name: str) -> Ansatz:
    try:
        return BUILDERS[name]()
    except KeyError:
        raise KeyError(f"unknown ansatz {name!r}; have {sorted(BUILDERS)}") from None


def all_ansatze(include_control: bool = False) -> list[Ansatz]:
    names = list(SPEC_ANSATZE) + (["product"] if include_control else [])
    return [get(n) for n in names]
