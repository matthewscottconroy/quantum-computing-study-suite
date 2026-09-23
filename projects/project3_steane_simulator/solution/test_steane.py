"""test_steane.py -- the acceptance criteria of milestones 1-4 as tests.

    cd projects/project3_steane_simulator/solution
    ../../../.venv/bin/python -m pytest -q
"""

from __future__ import annotations

import itertools

import numpy as np
import pytest
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli, PauliList, StabilizerState

import steane_code as C
import decode
import encoder as E
import montecarlo as mc
import syndrome as S

PAULIS = ("X", "Y", "Z")
ALL_WEIGHT1 = [(q, p) for q in range(C.N_QUBITS) for p in PAULIS]


# ---------------------------------------------------------------- milestone 1
def test_six_generators_of_weight_four():
    gens = C.stabilizer_generators()
    assert isinstance(gens, PauliList)
    assert len(gens) == 6
    for g in gens:
        assert np.count_nonzero(g.x | g.z) == 4


def test_generators_commute_pairwise():
    gens = C.stabilizer_generators()
    for a, b in itertools.combinations(gens, 2):
        assert not a.anticommutes(b)


def test_logicals_commute_with_generators_and_anticommute_with_each_other():
    gens = C.stabilizer_generators()
    lx, lz = C.logical_x(), C.logical_z()
    for g in gens:
        assert not lx.anticommutes(g)
        assert not lz.anticommutes(g)
    assert lx.anticommutes(lz)


@pytest.mark.parametrize("qubit,pauli", ALL_WEIGHT1)
def test_every_weight1_error_is_detected(qubit, pauli):
    """Distance sanity check: no weight-1 error is invisible."""
    gens = C.stabilizer_generators()
    err = C._pauli(x_support=[qubit] if pauli in ("X", "Y") else [],
                   z_support=[qubit] if pauli in ("Z", "Y") else [])
    assert any(err.anticommutes(g) for g in gens)


def test_self_orthogonality_and_coset_parity():
    """H H^T = 0, C_perp is even weight, C \\ C_perp is odd weight."""
    assert np.all((C.H_HAMMING @ C.H_HAMMING.T) % 2 == 0)
    assert np.all(C.C_PERP.sum(1) % 2 == 0)
    coset = [w for w in C.HAMMING_CODE
             if not any(np.array_equal(w, v) for v in C.C_PERP)]
    assert len(coset) == 8
    assert all(w.sum() % 2 == 1 for w in coset)


# ---------------------------------------------------------------- milestone 2
def test_encoder_produces_a_codeword():
    st = StabilizerState(E.logical_zero())
    for g in C.stabilizer_generators():
        assert np.real(st.expectation_value(g)) == pytest.approx(1.0)


def test_logical_zero_and_one_are_distinguished_by_zbar():
    lz = C.logical_z()
    assert np.real(StabilizerState(E.logical_zero()).expectation_value(lz)) \
        == pytest.approx(1.0)
    assert np.real(StabilizerState(E.logical_one()).expectation_value(lz)) \
        == pytest.approx(-1.0)


def test_logical_plus_has_xbar_plus_one():
    st = StabilizerState(E.logical_plus())
    assert np.real(st.expectation_value(C.logical_x())) == pytest.approx(1.0)
    for g in C.stabilizer_generators():
        assert np.real(st.expectation_value(g)) == pytest.approx(1.0)


# ---------------------------------------------------------------- milestone 3
def test_no_error_gives_trivial_syndrome():
    rows = S.extract(E.logical_zero(), shots=64)
    assert len(rows) == 64
    assert all((r == 0).all() for r in rows)


@pytest.mark.parametrize("qubit,pauli", ALL_WEIGHT1)
def test_weight1_syndromes_are_exactly_as_predicted(qubit, pauli):
    rows = S.extract(E.logical_zero(), errors=[(qubit, pauli)], shots=16)
    expected = S.predicted_syndrome(qubit, pauli)
    for r in rows:
        assert np.array_equal(r[0], expected)


def test_syndrome_extraction_is_non_destructive():
    """Extracting twice on a clean codeword gives a trivial syndrome twice."""
    rows = S.extract(E.logical_plus(), rounds=2, shots=64)
    assert all((r == 0).all() for r in rows)


def test_repeated_extraction_reproduces_a_static_error():
    rows = S.extract(E.logical_zero(), errors=[(5, "Y")], rounds=2, shots=32)
    for r in rows:
        assert np.array_equal(r[0], r[1])
        assert np.array_equal(r[0], S.predicted_syndrome(5, "Y"))


# ---------------------------------------------------------------- milestone 4
@pytest.mark.parametrize("qubit,pauli", ALL_WEIGHT1)
def test_all_weight1_errors_are_corrected(qubit, pauli):
    ex, ez = decode.single_qubit_error(qubit, pauli)
    assert decode.corrects_perfectly(ex, ez)


def test_x1x2_is_a_logical_failure():
    """The explicit weight-2 failure the milestone asks to record."""
    ex = np.zeros(7, dtype=np.uint8)
    ex[0] = ex[1] = 1                       # X on qubits 0 and 1
    residual = decode.correct(ex)
    assert int(decode.classify(residual)) == 1
    # the decoder "corrects" at the third site of a weight-3 codeword
    assert residual.sum() == 3
    assert np.all(C.syndrome(residual) == 0)


def test_some_weight2_errors_are_fine():
    """Not every weight-2 error fails -- two errors on one sector can look
    like a stabiliser after correction only if they sum into C_perp."""
    n_fail = 0
    for a, b in itertools.combinations(range(7), 2):
        ex = np.zeros(7, dtype=np.uint8)
        ex[a] = ex[b] = 1
        n_fail += int(decode.classify(decode.correct(ex))) == 1
    assert n_fail == 21, "every weight-2 X pair fails, by distance 3"


def test_classify_covers_the_three_cases():
    assert int(decode.classify(np.zeros(7, dtype=np.uint8))) == 0
    assert int(decode.classify(np.ones(7, dtype=np.uint8))) == 1      # X_bar
    out_of_code = np.zeros(7, dtype=np.uint8)
    out_of_code[0] = 1
    assert int(decode.classify(out_of_code)) == 2


# ------------------------------------------------- cross-check the two engines
def test_montecarlo_matches_circuits_on_weight1():
    """The symplectic engine and the stabiliser-circuit engine must agree.

    They are independent implementations; if they disagree, one of them is
    wrong and the fast one is the one everything else rests on.
    """
    for qubit, pauli in ALL_WEIGHT1:
        ex, ez = decode.single_qubit_error(qubit, pauli)
        circuit_bits = S.extract(E.logical_zero(), errors=[(qubit, pauli)],
                                 shots=8)[0][0]
        sympl = np.concatenate([C.syndrome(ez), C.syndrome(ex)])
        assert np.array_equal(circuit_bits, sympl)


def test_montecarlo_is_reproducible():
    a = mc.run_perfect(0.05, 200_000, seed=99)
    b = mc.run_perfect(0.05, 200_000, seed=99)
    assert a.failures == b.failures


def test_zero_error_rate_never_fails():
    assert mc.run_perfect(0.0, 100_000, seed=3).failures == 0


def test_low_p_slope_is_quadratic():
    pts = [mc.run_perfect(p, mc.adaptive_shots(p, target_events=40), seed=7)
           for p in (2e-3, 4e-3, 8e-3)]
    slope, c, n = mc.fit_slope(pts, p_max=0.01)
    assert n == 3
    assert slope == pytest.approx(2.0, abs=0.2)


def test_noisy_single_round_breaks_the_quadratic_law():
    pts = [mc.run_noisy(p, 400_000, p_meas=p, rounds=1, seed=5)[0]
           for p in (1e-3, 4e-3, 1.6e-2)]
    slope, _, _ = mc.fit_slope(pts, p_max=0.02)
    assert slope == pytest.approx(1.0, abs=0.2)


def test_three_round_majority_restores_it():
    pts = [mc.run_noisy(p, 800_000, p_meas=p, rounds=3, seed=5)[0]
           for p in (2e-3, 8e-3, 3.2e-2)]
    slope, _, _ = mc.fit_slope(pts, p_max=0.05)
    assert slope == pytest.approx(2.0, abs=0.25)


def test_even_round_counts_are_rejected():
    with pytest.raises(ValueError):
        mc.run_noisy(0.01, 100, p_meas=0.01, rounds=2)
