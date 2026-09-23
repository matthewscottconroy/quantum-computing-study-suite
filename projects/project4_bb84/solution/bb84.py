"""bb84.py -- milestones 1-3: the protocol, the eavesdropper, the decision.

Design rule that prevents every accounting bug in this project
--------------------------------------------------------------
Two namespaces, never mixed:

* ``Run``          -- **ground truth**.  What actually happened, including
                      everything Eve did.  Only the simulator and the
                      analysis may read it.
* ``ProtocolView`` -- **what Alice and Bob can see**: their own bits and
                      bases, and whatever they announce publicly.  Every
                      decision the protocol makes is a function of this
                      object alone.

If a key-rate calculation reaches into ``Run`` for something Alice and Bob
could not know, the result is not a key rate.  Keeping them in separate
dataclasses makes that mistake visible instead of subtle.

Bases and states
----------------
basis 0 = Z = {|0>, |1>}, basis 1 = X = {|+>, |->}.  Measuring a Z state in
the X basis (or vice versa) is a fair coin -- that single fact drives
everything, including the 25% figure.

Everything is vectorised numpy: 10^6 qubits take about 40 ms.  The explicit
``Statevector`` version lives in ``quantum.py`` and exists to show that the
numpy bookkeeping really is quantum mechanics.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

Z_BASIS, X_BASIS = 0, 1


@dataclass
class Run:
    """Ground truth for one protocol run -- includes what only Eve knows."""
    alice_bit: np.ndarray
    alice_basis: np.ndarray
    eve_intercepted: np.ndarray
    eve_basis: np.ndarray
    eve_bit: np.ndarray
    bob_basis: np.ndarray
    bob_bit: np.ndarray

    def __len__(self) -> int:
        return self.alice_bit.size


@dataclass
class ProtocolView:
    """Everything Alice and Bob legitimately share or hold."""
    sifted_index: np.ndarray      # positions where the bases matched
    alice_sifted: np.ndarray
    bob_sifted: np.ndarray
    sample_mask: np.ndarray       # which sifted bits were publicly compared
    qber: float                   # estimated from the public sample
    n_sample: int
    alice_key: np.ndarray         # sifted minus the sacrificed sample
    bob_key: np.ndarray

    @property
    def n_sifted(self) -> int:
        return self.alice_sifted.size

    @property
    def n_key(self) -> int:
        return self.alice_key.size


def simulate(n: int, eta: float = 0.0, p_channel: float = 0.0,
             seed: int | None = None) -> Run:
    """Transmit ``n`` qubits with an intercept-resend Eve of strength ``eta``.

    ``p_channel`` is an optional depolarising channel applied after Eve: with
    probability ``p_channel`` the qubit is randomised, which flips Bob's bit
    half the time.  It is off by default; milestone 3 uses it to make the
    false-alarm rate non-trivial.
    """
    rng = np.random.default_rng(seed)
    alice_bit = rng.integers(0, 2, n, dtype=np.int8)
    alice_basis = rng.integers(0, 2, n, dtype=np.int8)
    bob_basis = rng.integers(0, 2, n, dtype=np.int8)

    eve_intercepted = rng.random(n) < eta
    eve_basis = rng.integers(0, 2, n, dtype=np.int8)
    # Eve measures: right basis -> Alice's bit; wrong basis -> a fair coin.
    eve_correct_basis = eve_basis == alice_basis
    eve_bit = np.where(eve_correct_basis, alice_bit,
                       rng.integers(0, 2, n)).astype(np.int8)
    eve_bit = np.where(eve_intercepted, eve_bit, -1).astype(np.int8)

    # What reaches Bob: Eve's re-prepared state where she intercepted,
    # Alice's original otherwise.
    carried_bit = np.where(eve_intercepted, eve_bit, alice_bit)
    carried_basis = np.where(eve_intercepted, eve_basis, alice_basis)

    # Bob measures: matching basis -> the carried bit; else a fair coin.
    bob_bit = np.where(bob_basis == carried_basis, carried_bit,
                       rng.integers(0, 2, n)).astype(np.int8)
    if p_channel > 0:
        randomised = rng.random(n) < p_channel
        bob_bit = np.where(randomised & (rng.random(n) < 0.5),
                           1 - bob_bit, bob_bit).astype(np.int8)
    return Run(alice_bit, alice_basis, eve_intercepted, eve_basis, eve_bit,
               bob_basis, bob_bit)


def sift(run: Run, sample_fraction: float = 0.10,
         seed: int | None = None) -> ProtocolView:
    """Keep matching-basis positions, publicly compare a random sample.

    The sampled bits are announced, so they are burnt: they are removed from
    the key, not merely "used".  Forgetting that is the single most common
    accounting error in a BB84 implementation.
    """
    rng = np.random.default_rng(seed)
    keep = np.flatnonzero(run.alice_basis == run.bob_basis)
    a = run.alice_bit[keep]
    b = run.bob_bit[keep]
    n_sample = int(round(sample_fraction * keep.size))
    sample_mask = np.zeros(keep.size, dtype=bool)
    if n_sample:
        sample_mask[rng.choice(keep.size, size=n_sample, replace=False)] = True
    qber = float(np.mean(a[sample_mask] != b[sample_mask])) if n_sample else 0.0
    return ProtocolView(keep, a, b, sample_mask, qber, n_sample,
                        a[~sample_mask], b[~sample_mask])


def true_qber(run: Run) -> float:
    """The QBER Alice and Bob would measure with an infinite sample.

    Ground truth -- for validating the estimator, never for the protocol.
    """
    keep = run.alice_basis == run.bob_basis
    if not keep.any():
        return 0.0
    return float(np.mean(run.alice_bit[keep] != run.bob_bit[keep]))


def eve_agreement_on_sifted(run: Run) -> float:
    """P(Eve's bit == Alice's bit) on sifted positions she intercepted.

    Theory: on a sifted position Eve guessed the basis right half the time
    (and then knows the bit), and wrong half the time (and then her resent
    bit matches Alice's by chance half the time), so
    1/2 * 1 + 1/2 * 1/2 = 3/4.
    """
    mask = (run.alice_basis == run.bob_basis) & run.eve_intercepted
    if not mask.any():
        return float("nan")
    return float(np.mean(run.eve_bit[mask] == run.alice_bit[mask]))


def should_abort(view: ProtocolView, threshold: float) -> bool:
    """The only security decision, and it reads the protocol view only."""
    return view.qber > threshold
