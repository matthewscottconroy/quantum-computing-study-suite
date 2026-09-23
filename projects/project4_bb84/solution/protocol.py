"""protocol.py -- the end-to-end run: raw qubits in, secret key out.

Ties bb84.py (milestones 1-3) to infotheory.py (milestones 4-5) and produces
the ledger the spec asks for.
"""

from __future__ import annotations

import numpy as np

import bb84
import infotheory as it


def run_protocol(n: int, eta: float, *, accounting: str = "conservative",
                 threshold: float = 0.11, sample_fraction: float = 0.10,
                 f: float = it.CASCADE_EFFICIENCY, safety_bits: int = 64,
                 p_channel: float = 0.0, seed: int = 0):
    """One complete BB84 run.  Returns ``(ledger, key, run, view)``.

    ``key`` is the amplified secret key (empty when the protocol aborts or the
    accounting leaves nothing).
    """
    run = bb84.simulate(n, eta=eta, p_channel=p_channel, seed=seed)
    view = bb84.sift(run, sample_fraction=sample_fraction, seed=seed + 1)

    if bb84.should_abort(view, threshold):
        ledger = it.Ledger(n, view.n_sifted, view.n_sample, 0, view.qber,
                           accounting + " (ABORTED)", float("nan"), float("nan"),
                           0.0, safety_bits, 0)
        return ledger, np.zeros(0, dtype=np.uint8), run, view

    # --- milestone 4: reconciliation.  Bob adopts Alice's bits (the errors are
    # located with ground truth) but the information price is charged below.
    corrected = view.alice_key.astype(np.uint8)
    assert np.array_equal(corrected, view.alice_key.astype(np.uint8))
    bob_corrected = corrected.copy()
    assert np.array_equal(corrected, bob_corrected), "post-EC keys must match"

    leak = it.leak_ec_per_bit(view.qber, f)
    if accounting == "individual":
        eve = it.eve_info_individual(eta)
    elif accounting == "conservative":
        eve = it.eve_info_conservative(view.qber)
    else:
        raise ValueError(f"unknown accounting {accounting!r}")

    fraction = it.secret_fraction(view.qber, eve, f)
    length = max(0, int(np.floor(view.n_key * fraction)) - safety_bits)
    key = it.toeplitz_hash(corrected, length, seed=seed + 2)
    bob_key = it.toeplitz_hash(bob_corrected, length, seed=seed + 2)
    assert np.array_equal(key, bob_key), "privacy amplification must be shared"

    ledger = it.Ledger(n, view.n_sifted, view.n_sample, view.n_key, view.qber,
                       accounting, leak, eve, fraction, safety_bits, length)
    return ledger, key, run, view


def detection_probability(n_sample: int, eta: float, threshold: float = 0.11,
                          trials: int = 4000, p_channel: float = 0.0,
                          seed: int = 0) -> float:
    """P(estimated QBER > threshold) from ``n_sample`` publicly compared bits.

    Milestone 3's finite-size point: the QBER estimate is a binomial mean over
    ``n_sample`` bits, so at eta = 0.25 (true QBER 6.25%) a 50-bit sample
    exceeds an 11% threshold surprisingly often -- and, worse, falls below it
    almost always, which is a *missed* eavesdropper.
    """
    rng = np.random.default_rng(seed)
    q = eta / 4.0 + p_channel / 2.0 * (1 - eta / 2.0)
    errors = rng.binomial(n_sample, min(q, 1.0), size=trials)
    return float(np.mean(errors / n_sample > threshold))
