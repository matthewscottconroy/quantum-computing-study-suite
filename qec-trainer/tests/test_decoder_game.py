"""GF(2)/symplectic decoder game: codes are what they claim, rounds are fair."""
from __future__ import annotations

import itertools
import random

import pytest

from core.decoder_game import (
    IDENTITY, LEVEL_DIFFICULTY, LEVEL_TITLES, LEVELS, REP3, REP5, SURFACE,
    SURFACE_LOGICAL_X_SUPPORT, SURFACE_LOGICAL_Z_SUPPORT, SURFACE_X_CHECKS,
    SURFACE_Z_CHECKS, Round, generate_round, make_repetition_code, pauli_label,
    pauli_weight, pauli_xor, symplectic_product,
)

CODES = {"rep3": REP3, "rep5": REP5, "surface": SURFACE}


def _bits(mask: int, n: int) -> set[int]:
    return {q for q in range(n) if mask >> q & 1}


def _gf2_rank(vectors: list[int], nbits: int) -> int:
    rows = list(vectors)
    rank = 0
    for bit in range(nbits):
        pivot = next((i for i in range(rank, len(rows)) if rows[i] >> bit & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(len(rows)):
            if i != rank and rows[i] >> bit & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def _all_paulis_up_to_weight(n: int, max_w: int):
    for w in range(1, max_w + 1):
        for qubits in itertools.combinations(range(n), w):
            for kinds in itertools.product("XZY", repeat=w):
                x = z = 0
                for q, k in zip(qubits, kinds):
                    if k in "XY":
                        x |= 1 << q
                    if k in "ZY":
                        z |= 1 << q
                yield (x, z)


# ── Primitives ────────────────────────────────────────────────────────────────

def test_symplectic_primitives():
    X0, Z0, Y0, X1 = (1, 0), (0, 1), (1, 1), (2, 0)
    assert symplectic_product(X0, Z0) == 1
    assert symplectic_product(X0, X0) == 0
    assert symplectic_product(X0, X1) == 0
    assert symplectic_product(Y0, X0) == 1 and symplectic_product(Y0, Z0) == 1
    assert pauli_xor(X0, Z0) == Y0 and pauli_xor(Y0, Y0) == IDENTITY
    assert pauli_weight(IDENTITY) == 0 and pauli_weight(Y0) == 1
    assert pauli_weight((5, 4)) == 2          # X0, Y2 -> support {0, 2}
    assert pauli_weight((5, 2)) == 3          # X0, Z1, X2
    assert pauli_label(IDENTITY, 3) == "no error"
    assert pauli_label((1 | 4, 4), 3) == "X1 · Y3"
    assert pauli_label((0, 2), 3) == "Z2"


# ── Repetition codes ──────────────────────────────────────────────────────────

@pytest.mark.parametrize("n", [3, 5])
def test_repetition_syndrome_matches_independent_parity_computation(n):
    code = make_repetition_code(n)
    assert code.n == n and len(code.stabilizers) == n - 1
    for flipped in itertools.chain.from_iterable(
            itertools.combinations(range(n), w) for w in range(0, n + 1)):
        err = (sum(1 << q for q in flipped), 0)
        expected = tuple(int((i in flipped) != (i + 1 in flipped)) for i in range(n - 1))
        assert code.syndrome(err) == expected


def test_repetition_codes_decode_up_to_their_distance_uniquely():
    # rep-3 corrects weight <= 1; rep-5 corrects weight <= 2: syndromes must be injective.
    for code, t in ((REP3, 1), (REP5, 2)):
        table = {}
        for w in range(0, t + 1):
            for qs in itertools.combinations(range(code.n), w):
                err = (sum(1 << q for q in qs), 0)
                syn = code.syndrome(err)
                assert syn not in table, (code.name, err, table[syn])
                table[syn] = err
                assert code.is_success(err, err)
        # every X-string other than the true error is a failed correction
        for err in table.values():
            for other in table.values():
                assert code.is_success(err, other) == (other == err)


# ── Surface code [[9,1,3]] ────────────────────────────────────────────────────

def test_all_codes_have_pairwise_commuting_stabilizers():
    for code in CODES.values():
        for a, b in itertools.combinations(code.stabilizers, 2):
            assert symplectic_product(a, b) == 0, code.name
        for s in code.stabilizers:
            assert symplectic_product(s, code.logical_x) == 0
            assert symplectic_product(s, code.logical_z) == 0
        assert symplectic_product(code.logical_x, code.logical_z) == 1, code.name


def test_surface_code_is_9_1_3():
    assert SURFACE.n == 9 and len(SURFACE.stabilizers) == 8
    vectors = [x | (z << 9) for x, z in SURFACE.stabilizers]
    assert _gf2_rank(vectors, 18) == 8                       # independent -> k = 9 - 8 = 1
    assert pauli_weight(SURFACE.logical_x) == 3 and pauli_weight(SURFACE.logical_z) == 3
    for logical in (SURFACE.logical_x, SURFACE.logical_z):
        assert not SURFACE.acts_trivially(logical)          # logicals are not stabilizers
        assert not any(SURFACE.syndrome(logical))            # ...yet invisible to checks

    # Distance 3: every Pauli of weight <= 2 is either detected or is itself a
    # stabilizer (the four weight-2 boundary checks). None is an undetected logical.
    silent = []
    for p in _all_paulis_up_to_weight(9, 2):
        if any(SURFACE.syndrome(p)):
            continue
        assert SURFACE.acts_trivially(p), pauli_label(p, 9)
        silent.append(p)
    assert set(silent) == {s for s in SURFACE.stabilizers if pauli_weight(s) == 2}
    assert len(silent) == 4


def test_surface_syndrome_matches_independent_support_computation():
    rng = random.Random(99)
    for _ in range(200):
        x = rng.getrandbits(9)
        z = rng.getrandbits(9)
        xs, zs = _bits(x, 9), _bits(z, 9)
        expected = tuple(len(set(c) & zs) % 2 for c in SURFACE_X_CHECKS) + \
                   tuple(len(set(c) & xs) % 2 for c in SURFACE_Z_CHECKS)
        assert SURFACE.syndrome((x, z)) == expected
    assert _bits(SURFACE.logical_x[0], 9) == set(SURFACE_LOGICAL_X_SUPPORT)
    assert _bits(SURFACE.logical_z[1], 9) == set(SURFACE_LOGICAL_Z_SUPPORT)


# ── Rounds ────────────────────────────────────────────────────────────────────

def test_level_tables_are_consistent():
    assert set(LEVELS) == set(LEVEL_TITLES) == set(LEVEL_DIFFICULTY)
    assert set(LEVEL_DIFFICULTY.values()) <= {"beginner", "intermediate", "advanced"}
    with pytest.raises(ValueError):
        generate_round("no-such-level", random.Random(0))


def test_randomized_rounds_are_fair(monkeypatch):
    """A few hundred seeded rounds: syndromes match, the intended correction wins,
    stabilizer-equivalent corrections also win, and wrong ones lose."""
    rng = random.Random(1234)
    seen_levels = set()
    for _ in range(400):
        level = rng.choice(LEVELS)
        r = generate_round(level, rng)
        seen_levels.add(level)
        assert isinstance(r, Round) and r.level == level
        code = r.code
        assert r.syndrome == code.syndrome(r.error)
        assert code.is_success(r.error, r.error)

        if level.startswith("rep"):
            assert not r.is_grid_round
            assert len(r.choices) == 4 and len({c for _, c in r.choices}) == 4
            assert r.choices[r.correct_index][1] == r.error
            assert pauli_weight(r.error) <= (1 if level == "rep3" else 2)
            for i, (label, c) in enumerate(r.choices):
                assert label == pauli_label(c, code.n)
                assert code.is_success(r.error, c) == (i == r.correct_index)
        else:
            assert r.is_grid_round and r.correct_index == -1
            assert pauli_weight(r.error) == (1 if level == "surface1" else 2)
            # wrong: off by a logical operator
            assert not code.is_success(r.error, pauli_xor(r.error, code.logical_x))
            assert not code.is_success(r.error, pauli_xor(r.error, code.logical_z))
            # wrong: residual is a single-qubit Pauli (never a stabilizer at d=3)
            q = rng.randrange(9)
            single = rng.choice([(1 << q, 0), (0, 1 << q), (1 << q, 1 << q)])
            assert not code.is_success(r.error, pauli_xor(r.error, single))
            # right: off by a random product of stabilizers
            prod = IDENTITY
            for s in code.stabilizers:
                if rng.random() < 0.5:
                    prod = pauli_xor(prod, s)
            assert code.is_success(r.error, pauli_xor(r.error, prod))
    assert seen_levels == set(LEVELS)


def test_generate_round_is_reproducible_with_a_seed():
    a = [generate_round(l, random.Random(7)) for l in LEVELS]
    b = [generate_round(l, random.Random(7)) for l in LEVELS]
    assert [(r.error, r.syndrome, r.choices, r.correct_index) for r in a] == \
           [(r.error, r.syndrome, r.choices, r.correct_index) for r in b]
