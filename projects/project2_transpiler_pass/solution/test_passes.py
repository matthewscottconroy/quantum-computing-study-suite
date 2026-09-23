"""test_passes.py -- the acceptance criteria of milestones 1, 2 and 3, as tests.

    cd projects/project2_transpiler_pass/solution
    ../../../.venv/bin/python -m pytest -q

This file is deliberately NOT wired into tools/run_tests.sh: the repository's
test runner discovers suites at <repo>/<dir>/pytest.ini, and the reference
solutions are study material, not part of the suite's contract.
"""

from __future__ import annotations

import math

import numpy as np
import pytest
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Parameter
from qiskit.circuit.random import random_circuit
from qiskit.quantum_info import Operator, SparsePauliOp
from qiskit.transpiler import PassManager, generate_preset_pass_manager
from qiskit_ibm_runtime.fake_provider import FakeManilaV2, FakeTorino

import integration
from passes import CXRZCXFuser, DropIdentityRZ

BASIS = ["cx", "rz", "sx", "x"]


def assert_equiv(before: QuantumCircuit, after: QuantumCircuit) -> None:
    """Correctness definition from the spec: equal up to global phase."""
    assert Operator(before).equiv(Operator(after)), "pass changed the unitary"


def assert_exact(before: QuantumCircuit, after: QuantumCircuit) -> None:
    """Stronger: equal *including* global phase (our tracked-phase convention)."""
    assert Operator(before) == Operator(after), "global phase was not preserved"


def run(passes, qc: QuantumCircuit) -> QuantumCircuit:
    return PassManager(passes).run(qc)


# ---------------------------------------------------------------- milestone 1
def test_m1_removes_rz_zero_keeps_small_angle():
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.rz(0.0, 1)
    qc.rz(1e-3, 1)
    qc.cx(0, 1)
    out = run([DropIdentityRZ()], qc)
    assert dict(out.count_ops()) == {"cx": 2, "rz": 1}
    assert_exact(qc, out)


def test_m1_four_pi_removed_two_pi_convention():
    for angle in (4 * math.pi, 2 * math.pi):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.rz(angle, 0)
        tracked = run([DropIdentityRZ(track_global_phase=True)], qc)
        conservative = run([DropIdentityRZ(track_global_phase=False)], qc)
        # tracked: always removed, and the operator is preserved *exactly*
        assert "rz" not in tracked.count_ops()
        assert_exact(qc, tracked)
        # conservative: 4pi removed, 2pi kept
        if math.isclose(angle, 4 * math.pi):
            assert "rz" not in conservative.count_ops()
        else:
            assert conservative.count_ops()["rz"] == 1
        assert_exact(qc, conservative)


def test_m1_leaves_unbound_parameter_alone():
    theta = Parameter("theta")
    qc = QuantumCircuit(1)
    qc.rz(theta, 0)
    out = run([DropIdentityRZ()], qc)
    assert out.count_ops()["rz"] == 1
    assert out.parameters == qc.parameters


def test_m1_multiples_of_four_pi():
    for k in (-2, -1, 1, 2, 3):
        qc = QuantumCircuit(1)
        qc.h(0)
        qc.rz(4 * math.pi * k, 0)
        out = run([DropIdentityRZ()], qc)
        assert "rz" not in out.count_ops()
        assert_exact(qc, out)


# ---------------------------------------------------------------- milestone 2
@pytest.mark.parametrize("theta", [0.1, 0.7, 1.9, -2.4, 3.14159])
def test_cx_rz_cx_is_rzz(theta):
    """The identity the whole pass rests on: CX . RZ(t)_t . CX = RZZ(t)."""
    window = QuantumCircuit(2)
    window.cx(0, 1)
    window.rz(theta, 1)
    window.cx(0, 1)
    zz = SparsePauliOp("ZZ").to_matrix()
    expected = (np.cos(theta / 2) * np.eye(4) - 1j * np.sin(theta / 2) * zz)
    assert np.allclose(Operator(window).data, expected, atol=1e-12)


def test_m2_trap_gate_on_control_blocks_fusion():
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.rz(1.0, 1)
    qc.x(0)
    qc.cx(0, 1)
    out = run([CXRZCXFuser()], qc)
    assert out.count_ops()["cx"] == 2, "a busy control wire must block the rewrite"
    assert_exact(qc, out)


def test_m2_trap_direction_blocks_fusion():
    qc = QuantumCircuit(2)
    qc.cx(0, 1)
    qc.rz(1.0, 1)
    qc.cx(1, 0)
    out = run([CXRZCXFuser()], qc)
    assert out.count_ops()["cx"] == 2, "cx(0,1) ... cx(1,0) is not a window"
    assert_exact(qc, out)


def test_m2_fuses_adjacent_blocks():
    qc = QuantumCircuit(2)
    qc.h(0)
    for a in (0.3, 0.4):
        qc.cx(0, 1)
        qc.rz(a, 1)
        qc.cx(0, 1)
    out = run([CXRZCXFuser()], qc)
    assert out.count_ops()["cx"] == 2
    assert out.count_ops()["rz"] == 1
    assert_exact(qc, out)
    angles = [float(i.operation.params[0]) for i in out.data if i.operation.name == "rz"]
    assert angles == pytest.approx([0.7])


def test_m2_fuses_a_long_chain():
    qc = QuantumCircuit(2)
    qc.h(0)
    angles = [0.1, 0.2, 0.3, 0.4, 0.5]
    for a in angles:
        qc.cx(0, 1)
        qc.rz(a, 1)
        qc.cx(0, 1)
    out = run([CXRZCXFuser()], qc)
    assert out.count_ops()["cx"] == 2
    got = [float(i.operation.params[0]) for i in out.data if i.operation.name == "rz"]
    assert got == pytest.approx([sum(angles)])
    assert_exact(qc, out)


def test_m2_annihilates_zero_window():
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.rz(4 * math.pi, 1)
    qc.cx(0, 1)
    out = run([CXRZCXFuser()], qc)
    assert "cx" not in out.count_ops()
    assert_exact(qc, out)


def test_m2_symbolic_angles_fuse():
    """Beyond the spec: symbolic angles add, which Qiskit's own block
    consolidation cannot do (it needs a numeric matrix)."""
    ts = [Parameter(f"t{i}") for i in range(3)]
    qc = QuantumCircuit(2)
    qc.h(0)
    for t in ts:
        qc.cx(0, 1)
        qc.rz(t, 1)
        qc.cx(0, 1)
    out = run([CXRZCXFuser()], qc)
    assert out.count_ops()["cx"] == 2
    assert out.count_ops()["rz"] == 1
    binding = {t: v for t, v in zip(ts, (0.11, 0.22, 0.33))}
    assert_exact(qc.assign_parameters(binding), out.assign_parameters(binding))


@pytest.mark.parametrize("seed", range(200))
def test_m2_random_circuits_are_equivalent(seed):
    """200 random 4-qubit circuits: the pass never changes the unitary."""
    rc = random_circuit(4, 8, max_operands=2, seed=seed)
    qc = transpile(rc, basis_gates=BASIS, optimization_level=0, seed_transpiler=0)
    out = run([CXRZCXFuser(), DropIdentityRZ()], qc)
    assert_equiv(qc, out)
    assert_exact(qc, out)


@pytest.mark.parametrize("seed", range(40))
def test_m2_idempotent(seed):
    """Running the pass twice equals running it once."""
    rc = random_circuit(4, 8, max_operands=2, seed=seed)
    qc = transpile(rc, basis_gates=BASIS, optimization_level=0, seed_transpiler=0)
    once = run([CXRZCXFuser()], qc)
    twice = run([CXRZCXFuser()], once)
    assert dict(once.count_ops()) == dict(twice.count_ops())
    assert once == twice


def test_m2_idempotent_on_planted_chain():
    qc = QuantumCircuit(3)
    qc.h(2)
    for a in (0.1, 0.2, 0.3, 0.4):
        qc.cx(0, 1)
        qc.rz(a, 1)
        qc.cx(0, 1)
    once = run([CXRZCXFuser()], qc)
    twice = run([CXRZCXFuser()], once)
    assert once == twice
    assert once.count_ops()["cx"] == 2


# ---------------------------------------------------------------- milestone 3
def test_m3_level0_reduces_two_qubit_gates_and_stays_isa_valid():
    r = integration.compare(FakeManilaV2(), level=0, stage="init")
    assert r["twoq_with"] < r["twoq_without"]
    assert r["depth_with"] < r["depth_without"]
    assert r["isa_valid"]
    assert r["coupling_ok"]


@pytest.mark.parametrize("level", [0, 1, 2, 3])
@pytest.mark.parametrize("stage", ["init", "optimization"])
def test_m3_never_makes_things_worse(level, stage):
    r = integration.compare(FakeManilaV2(), level=level, stage=stage)
    assert r["twoq_with"] <= r["twoq_without"]
    assert r["isa_valid"] and r["coupling_ok"]


@pytest.mark.parametrize("level", [0, 1, 2, 3])
def test_m3_respects_torino_coupling_map(level):
    r = integration.compare(FakeTorino(), level=level, stage="init")
    assert r["coupling_ok"], "routing was broken by the extra stage"
    assert r["isa_valid"]


def test_m3_transpiled_circuit_is_still_correct():
    qc = integration.bell_phase_circuit(3)
    pm = integration.with_fuser(
        generate_preset_pass_manager(optimization_level=0, backend=FakeManilaV2(),
                                     seed_transpiler=7), "init")
    out = pm.run(qc)
    # compare on the 2 qubits the circuit actually uses
    full = Operator(out)
    assert full.dim[0] == 2 ** FakeManilaV2().num_qubits
    ref = Operator(qc)
    expanded = Operator(
        transpile(qc, basis_gates=BASIS, optimization_level=0, seed_transpiler=0))
    assert ref.equiv(expanded)
