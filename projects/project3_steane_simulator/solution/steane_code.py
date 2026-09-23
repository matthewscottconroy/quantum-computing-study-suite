"""steane_code.py -- milestone 1: the Steane [[7,1,3]] code as data.

NAMING TRAP: the spec's suggested layout calls this file ``p3/code.py``.  Do
not.  ``code`` is a standard-library module, and Python's stdlib ``pdb``
imports it -- so a local ``code.py`` on ``sys.path`` makes **pytest itself**
die with ``INTERNALERROR: module 'code' has no attribute
'InteractiveConsole'`` before a single test runs.  The same applies to
``types.py``, ``random.py``, ``json.py`` and friends.

Two representations are kept side by side and cross-checked against each other
throughout the project:

* **Pauli objects** (``qiskit.quantum_info.PauliList``) -- readable, and what
  the circuit-level milestones need.
* **Binary symplectic vectors** over F2 (numpy ``uint8``) -- what the Monte
  Carlo needs.  Commutation is a dot product mod 2, decoding is a matrix
  multiply, and 10^6 shots take milliseconds instead of hours.

Everything below follows from one classical object, the [7,4,3] Hamming
parity-check matrix whose columns are the binary numbers 1..7:

    H = [[0,0,0,1,1,1,1],
         [0,1,1,0,0,1,1],
         [1,0,1,0,1,0,1]]

Column j (1-indexed) is the binary representation of j, most significant bit
first.  That is what makes the classical decoder trivial: the syndrome of a
single bit flip at position j *is* the binary number j.

Steane's construction uses H twice: the X-type stabilisers are X on the
support of each row, the Z-type stabilisers are Z on the support of each row.
That works because H H^T = 0 over F2 (the code is self-orthogonal,
C_perp subset C), which is exactly the condition for the X and Z generators
to commute.

Two facts used constantly later:

* ``C = ker(H)`` is the Hamming [7,4,3] code (16 words).
* ``C_perp = rowspace(H)`` is the [7,3,4] simplex code (8 words), and every
  one of its words has **even** weight, while every word of ``C \\ C_perp`` has
  **odd** weight (they are the coset of the all-ones vector).

So a residual X-pattern ``r`` with ``H r = 0`` is a logical X operator exactly
when ``r`` has odd parity.  That single line replaces a whole stabiliser-group
membership test in the inner Monte Carlo loop.
"""

from __future__ import annotations

import itertools

import numpy as np
from qiskit.quantum_info import Pauli, PauliList

N_QUBITS = 7

H_HAMMING = np.array([[0, 0, 0, 1, 1, 1, 1],
                      [0, 1, 1, 0, 0, 1, 1],
                      [1, 0, 1, 0, 1, 0, 1]], dtype=np.uint8)

#: qubit indices (0-based) in the support of each parity check
SUPPORTS = [tuple(int(j) for j in np.flatnonzero(row)) for row in H_HAMMING]

#: each generator has exactly one qubit that no other generator touches;
#: those are the qubits the encoder seeds with |+>.
SEEDS = (3, 1, 0)          # row 0 -> qubit 3, row 1 -> qubit 1, row 2 -> qubit 0

#: a weight-3 Hamming codeword disjoint from SEEDS, used to inject the logical
#: state in the encoder (columns 3, 5, 6 one-indexed sum to zero mod 2)
INJECT = (2, 4, 5)


def _pauli(x_support=(), z_support=()) -> Pauli:
    """Build a Pauli from qubit-index supports, avoiding label endianness.

    TRAP: ``Pauli("XIIIIII")`` puts the X on qubit **6**, not qubit 0 --
    Qiskit labels are little-endian.  Constructing from (z, x) boolean arrays
    indexed by qubit number sidesteps the whole question.
    """
    z = np.zeros(N_QUBITS, dtype=bool)
    x = np.zeros(N_QUBITS, dtype=bool)
    for q in x_support:
        x[q] = True
    for q in z_support:
        z[q] = True
    return Pauli((z, x))


def stabilizer_generators() -> PauliList:
    """The 6 generators: 3 X-type then 3 Z-type, each of weight 4."""
    return PauliList([_pauli(x_support=s) for s in SUPPORTS]
                     + [_pauli(z_support=s) for s in SUPPORTS])


def logical_x() -> Pauli:
    return _pauli(x_support=range(N_QUBITS))


def logical_z() -> Pauli:
    return _pauli(z_support=range(N_QUBITS))


# --------------------------------------------------------------- F2 linear algebra
def _row_space(mat: np.ndarray) -> np.ndarray:
    """All 2^k combinations of the rows of ``mat`` over F2."""
    k = mat.shape[0]
    combos = np.array(list(itertools.product([0, 1], repeat=k)), dtype=np.uint8)
    return (combos @ mat) % 2


def _null_space(mat: np.ndarray) -> np.ndarray:
    """Every vector v with mat @ v = 0 (brute force -- n = 7)."""
    n = mat.shape[1]
    allv = np.array(list(itertools.product([0, 1], repeat=n)), dtype=np.uint8)
    return allv[np.all((allv @ mat.T) % 2 == 0, axis=1)]


C_PERP = _row_space(H_HAMMING)      # 8 words, the stabiliser sector
HAMMING_CODE = _null_space(H_HAMMING)  # 16 words


def syndrome(errors: np.ndarray) -> np.ndarray:
    """H @ e mod 2, vectorised over a stack of error patterns.

    ``errors`` is (..., 7) uint8; the result is (..., 3) uint8.
    """
    return (np.asarray(errors, dtype=np.uint8) @ H_HAMMING.T) % 2


#: syndrome (as an integer 0..7) -> the single-qubit correction to apply.
#: Because column j of H is the binary number j, syndrome value s means
#: "flip qubit s-1"; s = 0 means "do nothing".  That is the entire decoder.
LOOKUP = np.zeros((8, N_QUBITS), dtype=np.uint8)
for _s in range(1, 8):
    LOOKUP[_s, _s - 1] = 1


def syndrome_to_int(syn: np.ndarray) -> np.ndarray:
    """Pack a 3-bit syndrome (MSB first) into an integer 0..7."""
    syn = np.asarray(syn, dtype=np.uint8)
    return (syn[..., 0].astype(int) << 2) | (syn[..., 1].astype(int) << 1) | syn[..., 2]


def is_stabilizer(pattern: np.ndarray) -> np.ndarray:
    """True where the F2 pattern lies in C_perp (i.e. acts trivially).

    A pattern in ``ker(H)`` is a stabiliser element iff it has even weight;
    outside ``ker(H)`` it is not even in the code space.
    """
    pattern = np.asarray(pattern, dtype=np.uint8)
    in_kernel = np.all(syndrome(pattern) == 0, axis=-1)
    even = pattern.sum(axis=-1) % 2 == 0
    return in_kernel & even


def is_logical(pattern: np.ndarray) -> np.ndarray:
    """True where the residual acts as a logical operator (in C, odd weight)."""
    pattern = np.asarray(pattern, dtype=np.uint8)
    in_kernel = np.all(syndrome(pattern) == 0, axis=-1)
    odd = pattern.sum(axis=-1) % 2 == 1
    return in_kernel & odd
