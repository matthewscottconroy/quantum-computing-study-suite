"""infotheory.py -- milestones 4 and 5: the information accounting.

This is where a BB84 *simulation* becomes a BB84 *protocol*.  Sifting gives
Alice and Bob a shared string with errors, about which Eve knows something.
Two prices must be paid out of that string:

    leak_EC  bits revealed while reconciling the errors
    I_E      bits Eve knows, which privacy amplification must destroy

and what survives is the secret key:

    ell = n_sift * (1 - leak_EC_per_bit - I_E_per_bit) - safety

Error correction (milestone 4)
------------------------------
Cascade is not implemented.  Instead the errors are located using ground
truth -- but the *information-theoretic price is still charged*:

    leak_EC = f * h(Q)  bits per sifted bit,  f = 1.1

f = 1 is the Shannon limit; f ~ 1.1 is what a good Cascade implementation
actually achieves.  Simulating the reconciliation while paying the real price
is the standard way to separate "does my key agree" from "how many bits did
it cost", and it is honest as long as the price is not quietly set to zero.

Eve's information (milestone 5)
-------------------------------
Two accountings, deliberately both reported:

``individual``   For intercept-resend specifically, Eve intercepts a fraction
                 eta of the qubits.  On a sifted position she intercepted,
                 she chose the right basis half the time and then holds
                 Alice's bit exactly; the other half she holds nothing
                 useful.  So I_E = eta * 1/2 * 1 = eta/2 bits per sifted bit.
                 This is tight *for this attack* and known-eta -- which Alice
                 and Bob are not entitled to assume.

``conservative`` The one-way bound I_E = h(Q): assume every error is Eve and
                 that she is bounded only by the observed disturbance.  This
                 is what you use if you do not get to name the attack.  With
                 f = 1 it gives the textbook r = 1 - 2h(Q), which hits zero at
                 Q = 11.0%.

The two curves crossing is the whole point of milestone 5: assuming a
specific attack buys you key rate, and that assumption is exactly the thing a
real adversary is not obliged to respect.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np
from scipy.optimize import brentq

CASCADE_EFFICIENCY = 1.1


def binary_entropy(q):
    """h(q) = -q log2 q - (1-q) log2(1-q), with h(0) = h(1) = 0.

    Written once, tested once, used everywhere.  The endpoints are the whole
    reason this is a function: ``0 * log2(0)`` is a nan in numpy and the
    limit is 0, so a naive one-liner poisons the Q = 0 row of every table.
    """
    q = np.asarray(q, dtype=float)
    mid = (q > 0.0) & (q < 1.0)
    safe = np.where(mid, q, 0.5)                  # keep the log finite
    out = np.where(mid, -safe * np.log2(safe) - (1 - safe) * np.log2(1 - safe), 0.0)
    return float(out) if out.ndim == 0 else out


def leak_ec_per_bit(qber: float, f: float = CASCADE_EFFICIENCY) -> float:
    """Bits revealed per sifted bit by an error-correction round of efficiency f."""
    return float(f * binary_entropy(qber))


def eve_info_individual(eta: float) -> float:
    """I_E = eta/2, the intercept-resend individual-attack value."""
    return float(eta) / 2.0


def eve_info_conservative(qber: float) -> float:
    """I_E = h(Q), the attack-agnostic one-way bound."""
    return float(binary_entropy(qber))


def secret_fraction(qber: float, eve_info: float, f: float = CASCADE_EFFICIENCY,
                    safety_bits_per_bit: float = 0.0) -> float:
    """Secret bits per sifted bit, floored at zero."""
    return max(0.0, 1.0 - leak_ec_per_bit(qber, f) - eve_info - safety_bits_per_bit)


def zero_rate_qber(f: float = CASCADE_EFFICIENCY) -> float:
    """The QBER at which the conservative rate 1 - f h(Q) - h(Q) reaches zero."""
    def r(q):
        return 1.0 - leak_ec_per_bit(q, f) - eve_info_conservative(q)
    return float(brentq(r, 1e-9, 0.5 - 1e-9))


# --------------------------------------------------------- privacy amplification
def toeplitz_matrix(n_in: int, n_out: int, seed: int) -> np.ndarray:
    """A random binary Toeplitz matrix, the 2-universal hash family.

    A Toeplitz matrix is constant along diagonals, so it is fully described by
    its first column and first row -- ``n_out + n_in - 1`` random bits instead
    of ``n_out * n_in``.  That is what makes it cheap enough to agree on over
    the public channel, and the family is 2-universal, which is the property
    the leftover-hash lemma needs.
    """
    rng = np.random.default_rng(seed)
    seedbits = rng.integers(0, 2, n_out + n_in - 1, dtype=np.uint8)
    idx = np.arange(n_out)[:, None] - np.arange(n_in)[None, :] + (n_in - 1)
    return seedbits[idx]


def toeplitz_hash(key: np.ndarray, n_out: int, seed: int) -> np.ndarray:
    """(T @ key) mod 2 -- linear over F2, so it commutes with XOR."""
    key = np.asarray(key, dtype=np.uint8)
    if n_out <= 0:
        return np.zeros(0, dtype=np.uint8)
    return (toeplitz_matrix(key.size, n_out, seed) @ key) % 2


@dataclass
class Ledger:
    """Every number in the raw -> secret pipeline, in one place."""
    n_raw: int
    n_sifted: int
    n_sampled: int
    n_corrected: int
    qber: float
    accounting: str
    leak_ec_per_bit: float
    eve_info_per_bit: float
    secret_fraction: float
    safety_bits: int
    n_secret: int

    def as_rows(self):
        return list(asdict(self).items())

    def render(self) -> str:
        lines = [
            f"  raw transmitted          {self.n_raw:>10,}",
            f"  sifted (bases matched)   {self.n_sifted:>10,}"
            f"   ({self.n_sifted / max(self.n_raw, 1):.3f} of raw)",
            f"  sacrificed to QBER test  {self.n_sampled:>10,}",
            f"  after reconciliation     {self.n_corrected:>10,}",
            f"  measured QBER            {self.qber:>10.4f}",
            f"  accounting               {self.accounting:>10}",
            f"  leak_EC per bit          {self.leak_ec_per_bit:>10.4f}",
            f"  Eve's info per bit       {self.eve_info_per_bit:>10.4f}",
            f"  secret fraction          {self.secret_fraction:>10.4f}",
            f"  safety margin (bits)     {self.safety_bits:>10,}",
            f"  SECRET KEY               {self.n_secret:>10,}",
        ]
        return "\n".join(lines)
