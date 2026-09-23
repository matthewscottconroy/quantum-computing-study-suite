"""montecarlo.py -- milestones 5 and 6: logical error rate vs physical error rate.

Everything here is pure F2 arithmetic on numpy arrays; no circuits are built.
That is a ~1000x speed-up over the circuit path and it is *also* an
independent implementation of the same physics, so agreeing with the
stabiliser-circuit results (``test_steane.py::test_montecarlo_matches_circuits``)
is a real check on both.

Two shortcuts make the inner loop one pass over an (n, 7) array:

1. **Sampling.**  Depolarising with probability p gives X, Y or Z with p/3
   each.  Draw one uniform u per qubit and read off both sectors:

       x-part present  <=>  u < 2p/3      (X or Y)
       z-part present  <=>  p/3 <= u < p  (Y or Z)

   One RNG draw, two comparisons, and the X/Z correlation through Y is exact.

2. **Scoring (perfect extraction only).**  The correction flips exactly one
   qubit when the syndrome is non-zero and none when it is zero, so the
   residual's parity is ``(weight(e) + [syndrome != 0]) mod 2`` -- no residual
   vector has to be materialised.  And since ``H r = 0`` automatically, odd
   parity *is* a logical error (see code.py).

   The noisy-syndrome path in ``run_noisy`` cannot use this shortcut: the
   correction is derived from a corrupted syndrome, so the residual can leave
   the code space and must be built and classified explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from steane_code import H_HAMMING, LOOKUP, N_QUBITS, SUPPORTS, syndrome_to_int

CHUNK = 2_000_000


@dataclass
class Point:
    p: float
    shots: int
    failures: int

    @property
    def rate(self) -> float:
        return self.failures / self.shots if self.shots else 0.0

    @property
    def stderr(self) -> float:
        """Binomial standard error, with a floor so a zero-count point still
        gets a visible bar (Wilson-style 1/shots rather than exactly 0)."""
        r = self.rate
        return max(np.sqrt(max(r * (1 - r), 1e-30) / self.shots), 1.0 / self.shots)


def _sample(rng: np.random.Generator, n: int, p: float):
    u = rng.random((n, N_QUBITS), dtype=np.float32)
    ex = u < np.float32(2 * p / 3)
    ez = (u >= np.float32(p / 3)) & (u < np.float32(p))
    return ex, ez


def _syndrome_int(bits: np.ndarray) -> np.ndarray:
    """Pack the 3 Hamming checks of a (n, 7) boolean sector into ints 0..7."""
    out = np.zeros(bits.shape[0], dtype=np.uint8)
    for i, support in enumerate(SUPPORTS):
        out |= ((bits[:, support].sum(1) % 2).astype(np.uint8) << (2 - i))
    return out


def run_perfect(p: float, shots: int, seed: int = 0) -> Point:
    """Milestone 5: i.i.d. depolarising, perfect syndrome extraction."""
    rng = np.random.default_rng(seed)
    failures = 0
    done = 0
    while done < shots:
        n = min(CHUNK, shots - done)
        ex, ez = _sample(rng, n, p)
        sz = _syndrome_int(ex)          # Z-checks locate X errors
        sx = _syndrome_int(ez)          # X-checks locate Z errors
        fx = (ex.sum(1) + (sz > 0)) % 2
        fz = (ez.sum(1) + (sx > 0)) % 2
        failures += int(np.count_nonzero((fx | fz).astype(bool)))
        done += n
    return Point(p, shots, failures)


def run_noisy(p: float, shots: int, p_meas: float, rounds: int = 1,
              seed: int = 0) -> tuple[Point, Point]:
    """Milestone 6: the same, but each syndrome bit flips with ``p_meas``.

    A static data error is measured ``rounds`` times; each round's 6 bits are
    flipped independently, then majority-voted (``rounds`` must be odd for a
    vote with no ties).  The correction is applied and the residual is
    classified explicitly.

    Returns ``(not_restored, logical_only)``:

    ``not_restored``  residual is not a stabiliser -- the memory failed, which
                      includes "the state was pushed out of the code space by
                      a wrong correction".  This is the generalisation of
                      milestone 4's criterion and the curve to plot.
    ``logical_only``  residual is in ker(H) *and* has odd parity -- a genuine
                      X_bar / Z_bar.  Reported alongside so the two failure
                      mechanisms can be told apart.
    """
    if rounds % 2 == 0:
        raise ValueError("use an odd number of rounds so the majority vote has no tie")
    rng = np.random.default_rng(seed)
    not_restored = logical_only = 0
    done = 0
    while done < shots:
        n = min(CHUNK, shots - done)
        ex, ez = _sample(rng, n, p)
        residual_bad = np.zeros(n, dtype=bool)
        residual_log = np.zeros(n, dtype=bool)
        for sector in (ex, ez):
            true_bits = np.stack(
                [(sector[:, s].sum(1) % 2).astype(np.uint8) for s in SUPPORTS], axis=1)
            votes = np.zeros((n, 3), dtype=np.int16)
            for _ in range(rounds):
                flips = rng.random((n, 3)) < p_meas
                votes += (true_bits ^ flips).astype(np.int16)
            measured = (votes * 2 > rounds).astype(np.uint8)
            packed = syndrome_to_int(measured)
            residual = sector.astype(np.uint8) ^ LOOKUP[packed]
            in_kernel = np.all((residual @ H_HAMMING.T) % 2 == 0, axis=1)
            odd = residual.sum(1) % 2 == 1
            residual_bad |= ~(in_kernel & ~odd)
            residual_log |= in_kernel & odd
        not_restored += int(np.count_nonzero(residual_bad))
        logical_only += int(np.count_nonzero(residual_log))
        done += n
    return (Point(p, shots, not_restored), Point(p, shots, logical_only))


def adaptive_shots(p: float, c_guess: float = 19.7, target_events: int = 30,
                   lo: int = 10_000, hi: int = 200_000_000) -> int:
    """Enough shots that the expected number of failures clears ``target_events``.

    ``target_events`` is 30, not the 10 the milestone asks for, because 10 is
    the *expected* count: a point budgeted for exactly 10 comes back with 6 or
    7 about a fifth of the time (Poisson).  Budgeting 30 makes "at least 10
    observed at every point" hold in practice.  ``c_guess`` is the measured
    constant from a previous run -- bootstrapping the budget off the answer is
    fine here because the budget only has to be roughly right.
    """
    estimate = max(c_guess * p * p, 1e-12)
    return int(np.clip(target_events / estimate, lo, hi))


def fit_slope(points: list[Point], p_max: float = 0.01):
    """log-log least squares on the low-p points: p_L ~ c p^slope."""
    usable = [pt for pt in points if pt.p <= p_max and pt.failures > 0]
    if len(usable) < 2:
        return float("nan"), float("nan"), 0
    x = np.log10([pt.p for pt in usable])
    y = np.log10([pt.rate for pt in usable])
    slope, intercept = np.polyfit(x, y, 1)
    return float(slope), float(10 ** intercept), len(usable)


def pseudo_threshold(points: list[Point]) -> float:
    """Where the p_L = p line is crossed, by linear interpolation in log-log."""
    xs = [pt for pt in points if pt.failures > 0]
    for a, b in zip(xs, xs[1:]):
        if a.rate < a.p and b.rate >= b.p:
            la, lb = np.log10(a.p), np.log10(b.p)
            da, db = np.log10(a.rate) - la, np.log10(b.rate) - lb
            t = da / (da - db)
            return float(10 ** (la + t * (lb - la)))
    return float("nan")
