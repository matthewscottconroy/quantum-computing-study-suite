"""
Circuit-based Qiskit contexts for: Quantum Computing, Qiskit, QASM,
Algorithm Design, and Transpiling topics.

build_context(topic) → QiskitContext with circuit_png + qasm_snippet.
"""

from __future__ import annotations
import io
import random
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Operator
from qiskit_contexts import QiskitContext
from config import CIRCUIT_RENDER_DPI, CIRCUIT_MAX_QUBITS


# ── Public entry point ────────────────────────────────────────────────────────

def build_context(topic: str) -> QiskitContext:
    builder = _choose_builder(topic)
    qc = builder()
    return _render(qc, topic)


# ── Builder router ────────────────────────────────────────────────────────────

def _choose_builder(topic: str):
    t = topic.lower()
    if "bell" in t or "entangl" in t:
        return _bell_circuit
    if "grover" in t or "amplitude amplif" in t:
        return _grover_circuit
    if "qft" in t or "fourier" in t:
        return _qft_circuit
    if "phase estim" in t or "qpe" in t:
        return _qpe_circuit
    if "toffoli" in t or "ccx" in t or "three-qubit" in t:
        return _toffoli_decomposition
    if "swap" in t and "rout" in t:
        return _routing_example
    if "parameteriz" in t or "vqe" in t or "ansatz" in t:
        return _parameterized_ansatz
    if "teleport" in t:
        return _teleportation_circuit
    if "trotter" in t or "hamiltonian simul" in t:
        return _trotter_circuit
    if "error correct" in t or "stabilizer" in t or "syndrome" in t:
        return _steane_syndrome_circuit
    if "transpil" in t or "routing" in t or "sabre" in t or "basis translat" in t:
        return _transpilation_example
    if "qaoa" in t:
        return _qaoa_circuit
    if "deutsch" in t:
        return _deutsch_jozsa_circuit
    if "single-qubit" in t or "bloch" in t:
        return _single_qubit_rotations
    # Default: a random 3-qubit entangling circuit
    return _random_entangling_circuit


# ── Circuit builders ──────────────────────────────────────────────────────────

def _bell_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(2, 2, name="Bell State |Φ⁺⟩")
    qc.h(0)
    qc.cx(0, 1)
    qc.barrier()
    qc.measure([0, 1], [0, 1])
    return qc


def _grover_circuit() -> QuantumCircuit:
    """2-qubit Grover for |11⟩."""
    qc = QuantumCircuit(2, name="Grover (n=2, target=|11⟩)")
    qc.h([0, 1])
    qc.barrier(label="init")
    # Oracle: flip phase of |11⟩
    qc.cz(0, 1)
    qc.barrier(label="oracle")
    # Diffusion
    qc.h([0, 1])
    qc.x([0, 1])
    qc.h(1)
    qc.cx(0, 1)
    qc.h(1)
    qc.x([0, 1])
    qc.h([0, 1])
    qc.barrier(label="diffusion")
    return qc


def _qft_circuit() -> QuantumCircuit:
    n = 3
    qc = QuantumCircuit(n, name=f"QFT (n={n})")
    for j in range(n):
        qc.h(j)
        for k in range(j + 1, n):
            qc.cp(math.pi / (2 ** (k - j)), j, k)
        qc.barrier()
    # Swap qubits for correct bit ordering
    for i in range(n // 2):
        qc.swap(i, n - 1 - i)
    return qc


def _qpe_circuit() -> QuantumCircuit:
    """3-ancilla QPE estimating phase of T gate (φ=1/8)."""
    ancilla = 3
    qc = QuantumCircuit(ancilla + 1, ancilla, name="QPE (T gate, φ=1/8)")
    # Prepare eigenstate |1⟩ of T
    qc.x(ancilla)
    qc.barrier(label="eigenstate")
    # Hadamard on ancilla
    qc.h(range(ancilla))
    qc.barrier(label="H⊗t")
    # Controlled-T^(2^k)
    for k in range(ancilla):
        for _ in range(2 ** k):
            qc.cp(math.pi / 4, k, ancilla)
    qc.barrier(label="ctrl-U")
    # Inverse QFT on ancilla (simplified: just IQFT)
    for j in range(ancilla // 2):
        qc.swap(j, ancilla - 1 - j)
    for j in range(ancilla):
        for k in range(j):
            qc.cp(-math.pi / (2 ** (j - k)), k, j)
        qc.h(j)
    qc.barrier(label="IQFT")
    qc.measure(range(ancilla), range(ancilla))
    return qc


def _toffoli_decomposition() -> QuantumCircuit:
    """Toffoli gate and its explicit T-gate decomposition side by side."""
    qc = QuantumCircuit(3, name="Toffoli (CCNOT) — T-gate decomposition")
    qc.h(2)
    qc.cx(1, 2)
    qc.tdg(2)
    qc.cx(0, 2)
    qc.t(2)
    qc.cx(1, 2)
    qc.tdg(2)
    qc.cx(0, 2)
    qc.t(1)
    qc.t(2)
    qc.h(2)
    qc.cx(0, 1)
    qc.t(0)
    qc.tdg(1)
    qc.cx(0, 1)
    return qc


def _routing_example() -> QuantumCircuit:
    """Dense 4-qubit circuit that requires SWAP insertion on a line topology."""
    qc = QuantumCircuit(4, name="Routing example (line topology)")
    qc.h([0, 1, 2, 3])
    qc.cx(0, 3)   # non-adjacent — needs routing
    qc.cx(1, 3)
    qc.cx(0, 2)
    qc.barrier(label="pre-routing")
    # Manual SWAP insertion for line 0-1-2-3
    qc.swap(1, 2)
    qc.cx(0, 1)
    qc.swap(1, 2)
    qc.barrier(label="post-routing")
    return qc


def _parameterized_ansatz() -> QuantumCircuit:
    """Hardware-efficient ansatz with 2 layers."""
    n = 3
    depth = 2
    params = ParameterVector("θ", n * depth * 2)
    qc = QuantumCircuit(n, name=f"HEA ansatz (n={n}, d={depth})")
    idx = 0
    for d in range(depth):
        for q in range(n):
            qc.ry(params[idx], q)
            idx += 1
        for q in range(n):
            qc.rz(params[idx], q)
            idx += 1
        for q in range(n - 1):
            qc.cx(q, q + 1)
        qc.barrier(label=f"layer {d+1}")
    return qc


def _teleportation_circuit() -> QuantumCircuit:
    qc = QuantumCircuit(3, 3, name="Quantum Teleportation")
    # Prepare arbitrary state on qubit 0
    qc.rx(0.9, 0)
    qc.ry(0.4, 0)
    qc.barrier(label="state prep")
    # Create Bell pair between qubits 1 and 2
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier(label="Bell pair")
    # Bell measurement on qubits 0 and 1
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier(label="Bell meas")
    qc.measure([0, 1], [0, 1])
    # Classical feed-forward
    with qc.if_test((1, 1)):
        qc.x(2)
    with qc.if_test((0, 1)):
        qc.z(2)
    qc.barrier(label="correction")
    qc.measure(2, 2)
    return qc


def _trotter_circuit() -> QuantumCircuit:
    """First-order Trotter step for 3-site Ising model H = ZZ + ZZ + X."""
    dt = 0.2
    qc = QuantumCircuit(3, name=f"Trotter step (Ising, dt={dt})")
    # ZZ terms
    for q in range(2):
        qc.cx(q, q + 1)
        qc.rz(2 * dt, q + 1)
        qc.cx(q, q + 1)
    qc.barrier(label="ZZ")
    # X terms
    for q in range(3):
        qc.rx(2 * dt, q)
    qc.barrier(label="X")
    return qc


def _steane_syndrome_circuit() -> QuantumCircuit:
    """3-qubit bit-flip code: encoding + syndrome measurement."""
    qc = QuantumCircuit(5, 2, name="3-qubit bit-flip: encode + syndrome")
    # Encode logical |ψ⟩ = α|0⟩+β|1⟩ using qubits 0,1,2; ancilla 3,4
    qc.cx(0, 1)
    qc.cx(0, 2)
    qc.barrier(label="encode")
    # Syndrome: ancilla 3 measures qubit 0 XOR qubit 1
    qc.cx(0, 3)
    qc.cx(1, 3)
    # Ancilla 4 measures qubit 1 XOR qubit 2
    qc.cx(1, 4)
    qc.cx(2, 4)
    qc.barrier(label="syndrome")
    qc.measure([3, 4], [0, 1])
    return qc


def _transpilation_example() -> QuantumCircuit:
    """Abstract circuit that will be transpiled to native gates."""
    qc = QuantumCircuit(3, name="Pre-transpilation circuit")
    qc.h(0)
    qc.cx(0, 1)
    qc.t(1)
    qc.s(2)
    qc.swap(0, 2)
    qc.cz(1, 2)
    return qc


def _qaoa_circuit() -> QuantumCircuit:
    """1-layer QAOA for MaxCut on a triangle graph."""
    gamma = ParameterVector("γ", 1)
    beta = ParameterVector("β", 1)
    qc = QuantumCircuit(3, name="QAOA p=1 (MaxCut, triangle)")
    qc.h([0, 1, 2])
    qc.barrier(label="init")
    # Problem unitary U_C(γ)
    for edge in [(0, 1), (1, 2), (0, 2)]:
        qc.rzz(gamma[0], edge[0], edge[1])
    qc.barrier(label="U_C(γ)")
    # Mixing unitary U_B(β)
    for q in range(3):
        qc.rx(2 * beta[0], q)
    qc.barrier(label="U_B(β)")
    return qc


def _deutsch_jozsa_circuit() -> QuantumCircuit:
    """2-qubit Deutsch-Jozsa for a balanced oracle."""
    qc = QuantumCircuit(3, 2, name="Deutsch-Jozsa (n=2, balanced oracle)")
    # Ancilla in |−⟩
    qc.x(2)
    qc.h([0, 1, 2])
    qc.barrier(label="init")
    # Balanced oracle: flip ancilla on |01⟩ and |10⟩
    qc.cx(0, 2)
    qc.cx(1, 2)
    qc.barrier(label="oracle")
    qc.h([0, 1])
    qc.barrier(label="H⊗n")
    qc.measure([0, 1], [0, 1])
    return qc


def _single_qubit_rotations() -> QuantumCircuit:
    """Showcase of single-qubit rotation gates on the Bloch sphere."""
    qc = QuantumCircuit(3, name="Single-qubit rotations")
    qc.rx(math.pi / 3, 0)
    qc.ry(math.pi / 4, 1)
    qc.rz(math.pi / 6, 2)
    qc.barrier()
    qc.h(0)
    qc.s(1)
    qc.t(2)
    qc.barrier()
    qc.u(math.pi / 2, math.pi / 4, math.pi / 8, 0)
    return qc


def _random_entangling_circuit() -> QuantumCircuit:
    n = random.randint(2, min(4, CIRCUIT_MAX_QUBITS))
    qc = QuantumCircuit(n, name=f"Random entangling circuit (n={n})")
    qc.h(range(n))
    for q in range(n - 1):
        qc.cx(q, q + 1)
    qc.rz(math.pi / random.choice([2, 4, 6, 8]), random.randrange(n))
    return qc


# ── Rendering ─────────────────────────────────────────────────────────────────

def _render(qc: QuantumCircuit, topic: str) -> QiskitContext:
    try:
        from qiskit.qasm2 import dumps as qasm2_dumps
        qasm = qasm2_dumps(qc)
    except Exception:
        qasm = f"# Circuit: {qc.name}\n# (QASM export unavailable for this circuit)"

    try:
        fig = qc.draw(output="mpl", style="bw", fold=-1)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=CIRCUIT_RENDER_DPI, bbox_inches="tight")
        plt.close(fig)
        png_bytes = buf.getvalue()
    except Exception:
        png_bytes = None

    return QiskitContext(
        circuit_png=png_bytes,
        qasm_snippet=qasm,
        prose_description=f"Circuit: {qc.name}",
    )
