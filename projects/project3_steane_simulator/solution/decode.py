"""decode.py -- milestone 4: lookup decoding and the logical-failure test.

Decoder
-------
CSS structure means the two sectors decode independently:

    Z-checks  ->  3-bit syndrome  ->  which qubit carries an X error
    X-checks  ->  3-bit syndrome  ->  which qubit carries a Z error

and because column j of H *is* the binary number j, the lookup table is
"syndrome value s means flip qubit s-1".  A Y error is an X and a Z at the
same site, so it lights up both sectors and is corrected by both -- no special
case is needed, which is the whole point of the CSS construction.

Failure test
------------
After correction the residual is ``r = e + c`` in each sector.  Three cases:

    r in C_perp            the correction succeeded (r is a stabiliser)
    r in C \\ C_perp        a LOGICAL error: r acts as X_bar or Z_bar
    r not in C = ker(H)    the state is not in the code space at all

With a perfect syndrome the third case cannot happen (H r = H e + H c = 0 by
construction), so "logical error" and "not restored" agree.  With *noisy*
syndromes (milestone 6) they do not, and keeping them apart is the difference
between a plot that means something and one that does not.
"""

from __future__ import annotations

import numpy as np

from steane_code import (H_HAMMING, LOOKUP, N_QUBITS, SUPPORTS, is_logical,
                  is_stabilizer, syndrome, syndrome_to_int)


def decode_sector(syndrome_bits: np.ndarray) -> np.ndarray:
    """3-bit syndromes -> weight<=1 correction patterns (vectorised)."""
    return LOOKUP[syndrome_to_int(np.asarray(syndrome_bits, dtype=np.uint8))]


def correct(errors: np.ndarray) -> np.ndarray:
    """One sector, perfect syndrome: return the residual e + c."""
    errors = np.asarray(errors, dtype=np.uint8)
    return errors ^ decode_sector(syndrome(errors))


def classify(residual: np.ndarray) -> np.ndarray:
    """0 = corrected, 1 = logical error, 2 = left the code space."""
    residual = np.asarray(residual, dtype=np.uint8)
    out = np.full(residual.shape[:-1], 2, dtype=np.uint8)
    out[is_logical(residual)] = 1
    out[is_stabilizer(residual)] = 0
    return out


def single_qubit_error(qubit: int, pauli: str) -> tuple[np.ndarray, np.ndarray]:
    """(x-part, z-part) of a weight-1 Pauli error."""
    ex = np.zeros(N_QUBITS, dtype=np.uint8)
    ez = np.zeros(N_QUBITS, dtype=np.uint8)
    if pauli in ("X", "Y"):
        ex[qubit] = 1
    if pauli in ("Z", "Y"):
        ez[qubit] = 1
    return ex, ez


def corrects_perfectly(ex: np.ndarray, ez: np.ndarray) -> bool:
    """True when both sectors come back to a stabiliser element."""
    return bool(classify(correct(ex)) == 0 and classify(correct(ez)) == 0)
