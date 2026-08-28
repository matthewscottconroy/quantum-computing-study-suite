"""Decoder Game — pure GF(2)/symplectic logic for syndrome-decoding rounds.

Pauli operators (mod phase) are represented as bitmask pairs ``(x, z)`` where
bit ``i`` of ``x`` means an X on qubit ``i`` and bit ``i`` of ``z`` means a Z
on qubit ``i`` (a Y sets both).  Two Paulis P=(x1,z1), Q=(x2,z2) commute iff
the symplectic product  parity(x1&z2) XOR parity(z1&x2)  is 0.

Codes provided:
  * 3- and 5-qubit bit-flip repetition codes (Z-type stabilizers Z_i Z_{i+1})
  * distance-3 rotated surface code, [[9,1,3]], 9 data qubits laid out

        0 1 2
        3 4 5
        6 7 8

    with X-checks {1,2}, {0,1,3,4}, {4,5,7,8}, {6,7} and
    Z-checks {0,3}, {1,2,4,5}, {3,4,6,7}, {5,8}.
    Logical X = X0 X3 X6 (left column), logical Z = Z0 Z1 Z2 (top row).
    These supports were verified by an exhaustive GF(2)/symplectic script:
    all 8 stabilizers commute pairwise, they are independent (rank 8 over
    GF(2), so k = 9 - 8 = 1), every weight-1 and weight-2 Pauli anticommutes
    with at least one stabilizer, and the weight-3 logicals above commute
    with all stabilizers while anticommuting with each other — i.e. the code
    is [[9,1,3]].

Success criterion for a proposed correction ``c`` against actual error ``e``:
the residual r = c XOR e (GF(2) sum) must lie in the stabilizer group — it
must commute with every stabilizer generator AND act trivially on the logical
operators (zero symplectic product with logical X and logical Z).  For these
codes {stabilizers, logicals, pure errors} span the Pauli group mod phase, so
this check is exactly membership of r in the stabilizer group.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

Pauli = tuple[int, int]          # (x_mask, z_mask)

IDENTITY: Pauli = (0, 0)

# ── Symplectic / GF(2) primitives ─────────────────────────────────────────────


def _parity(v: int) -> int:
    return bin(v).count("1") & 1


def symplectic_product(p: Pauli, q: Pauli) -> int:
    """0 if p and q commute, 1 if they anticommute."""
    return _parity(p[0] & q[1]) ^ _parity(p[1] & q[0])


def pauli_xor(p: Pauli, q: Pauli) -> Pauli:
    """GF(2) sum (composition mod phase) of two Paulis."""
    return (p[0] ^ q[0], p[1] ^ q[1])


def pauli_weight(p: Pauli) -> int:
    return bin(p[0] | p[1]).count("1")


def pauli_label(p: Pauli, n: int) -> str:
    """Human-readable label, 1-indexed qubits: e.g. 'X2 · Z5' or 'no error'."""
    if p == IDENTITY:
        return "no error"
    parts = []
    for i in range(n):
        x = (p[0] >> i) & 1
        z = (p[1] >> i) & 1
        if x and z:
            parts.append(f"Y{i + 1}")
        elif x:
            parts.append(f"X{i + 1}")
        elif z:
            parts.append(f"Z{i + 1}")
    return " · ".join(parts)


# ── Code definition ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Code:
    name: str
    n: int
    stabilizers: tuple[Pauli, ...]
    stabilizer_labels: tuple[str, ...]
    logical_x: Pauli
    logical_z: Pauli

    def syndrome(self, error: Pauli) -> tuple[int, ...]:
        """One bit per stabilizer generator: 1 = check fired (anticommutes)."""
        return tuple(symplectic_product(s, error) for s in self.stabilizers)

    def acts_trivially(self, p: Pauli) -> bool:
        """True iff p is in the stabilizer group: commutes with every
        stabilizer generator and has trivial action on both logicals."""
        if any(symplectic_product(s, p) for s in self.stabilizers):
            return False
        return (symplectic_product(self.logical_x, p) == 0
                and symplectic_product(self.logical_z, p) == 0)

    def is_success(self, error: Pauli, correction: Pauli) -> bool:
        """Correction succeeds iff correction XOR error is in the stabilizer
        group (equal to the error up to stabilizer)."""
        return self.acts_trivially(pauli_xor(error, correction))


def _mask(bits: list[int]) -> int:
    m = 0
    for b in bits:
        m |= 1 << b
    return m


def make_repetition_code(n: int) -> Code:
    """n-qubit bit-flip repetition code: stabilizers Z_i Z_{i+1}."""
    stabs = tuple((0, _mask([i, i + 1])) for i in range(n - 1))
    labels = tuple(f"Z{i + 1}Z{i + 2}" for i in range(n - 1))
    return Code(
        name=f"{n}-qubit repetition code",
        n=n,
        stabilizers=stabs,
        stabilizer_labels=labels,
        logical_x=(_mask(list(range(n))), 0),   # X on every qubit
        logical_z=(0, _mask([0])),              # Z on qubit 1
    )


# d=3 rotated surface code stabilizer supports (row-major 3x3 grid, see module
# docstring). Verified [[9,1,3]] by exhaustive script before hardcoding.
SURFACE_X_CHECKS: tuple[tuple[int, ...], ...] = ((1, 2), (0, 1, 3, 4), (4, 5, 7, 8), (6, 7))
SURFACE_Z_CHECKS: tuple[tuple[int, ...], ...] = ((0, 3), (1, 2, 4, 5), (3, 4, 6, 7), (5, 8))
SURFACE_LOGICAL_X_SUPPORT: tuple[int, ...] = (0, 3, 6)
SURFACE_LOGICAL_Z_SUPPORT: tuple[int, ...] = (0, 1, 2)


def make_surface_code() -> Code:
    stabs: list[Pauli] = []
    labels: list[str] = []
    # Labels are 1-indexed for display (matching pauli_label);
    # the support tuples themselves are 0-indexed.
    for sup in SURFACE_X_CHECKS:
        stabs.append((_mask(list(sup)), 0))
        labels.append("X" + "".join(str(q + 1) for q in sup))
    for sup in SURFACE_Z_CHECKS:
        stabs.append((0, _mask(list(sup))))
        labels.append("Z" + "".join(str(q + 1) for q in sup))
    return Code(
        name="distance-3 rotated surface code",
        n=9,
        stabilizers=tuple(stabs),
        stabilizer_labels=tuple(labels),
        logical_x=(_mask(list(SURFACE_LOGICAL_X_SUPPORT)), 0),
        logical_z=(0, _mask(list(SURFACE_LOGICAL_Z_SUPPORT))),
    )


REP3 = make_repetition_code(3)
REP5 = make_repetition_code(5)
SURFACE = make_surface_code()


# ── Rounds ────────────────────────────────────────────────────────────────────

LEVELS = ("rep3", "rep5", "surface1", "surface2")

LEVEL_TITLES = {
    "rep3":     "3-qubit repetition code",
    "rep5":     "5-qubit repetition code",
    "surface1": "Surface code d=3 · weight-1 errors",
    "surface2": "Surface code d=3 · weight-2 errors",
}

LEVEL_DIFFICULTY = {
    "rep3":     "beginner",
    "rep5":     "intermediate",
    "surface1": "intermediate",
    "surface2": "advanced",
}


@dataclass
class Round:
    level: str
    code: Code
    error: Pauli
    syndrome: tuple[int, ...]
    # Multiple-choice rounds (repetition codes): (label, correction) pairs.
    # Surface rounds have no choices — the correction is placed on the grid.
    choices: list[tuple[str, Pauli]] = field(default_factory=list)
    correct_index: int = -1

    @property
    def is_grid_round(self) -> bool:
        return not self.choices


def _random_x_error(n: int, weight: int, rng: random.Random) -> Pauli:
    qubits = rng.sample(range(n), weight)
    return (_mask(qubits), 0)


def _rep_choices(code: Code, error: Pauli, max_weight: int,
                 rng: random.Random) -> tuple[list[tuple[str, Pauli]], int]:
    """Four corrections including the true error; distractors are other
    X-strings of weight <= max_weight (plus 'no error' when applicable)."""
    pool: list[Pauli] = [IDENTITY]
    single = [(_mask([q]), 0) for q in range(code.n)]
    pool.extend(single)
    if max_weight >= 2:
        for a in range(code.n):
            for b in range(a + 1, code.n):
                pool.append((_mask([a, b]), 0))
    distractors = [p for p in pool if p != error]
    rng.shuffle(distractors)
    options = [error] + distractors[:3]
    rng.shuffle(options)
    idx = options.index(error)
    return [(pauli_label(p, code.n), p) for p in options], idx


def generate_round(level: str, rng: random.Random | None = None) -> Round:
    rng = rng or random.Random()
    if level == "rep3":
        # weight 0 or 1 — always unambiguously decodable from the syndrome
        weight = 0 if rng.random() < 0.2 else 1
        error = _random_x_error(3, weight, rng)
        choices, idx = _rep_choices(REP3, error, max_weight=1, rng=rng)
        return Round("rep3", REP3, error, REP3.syndrome(error), choices, idx)
    if level == "rep5":
        # weight 1 or 2 — distance 5 corrects both unambiguously
        weight = 1 if rng.random() < 0.5 else 2
        error = _random_x_error(5, weight, rng)
        choices, idx = _rep_choices(REP5, error, max_weight=2, rng=rng)
        return Round("rep5", REP5, error, REP5.syndrome(error), choices, idx)
    if level in ("surface1", "surface2"):
        weight = 1 if level == "surface1" else 2
        qubits = rng.sample(range(9), weight)
        x_mask = z_mask = 0
        for q in qubits:
            kind = rng.choice(("X", "Z", "Y"))
            if kind in ("X", "Y"):
                x_mask |= 1 << q
            if kind in ("Z", "Y"):
                z_mask |= 1 << q
        error = (x_mask, z_mask)
        return Round(level, SURFACE, error, SURFACE.syndrome(error))
    raise ValueError(f"Unknown level: {level}")
