"""
Hamiltonian-based Qiskit contexts for: Linear Algebra, Abstract Algebra,
Representation Theory topics.

build_context(topic) → QiskitContext with hamiltonian_str.
"""

from __future__ import annotations
import random

from qiskit.quantum_info import SparsePauliOp
from qiskit_contexts import QiskitContext


def build_context(topic: str) -> QiskitContext:
    builder = _choose_builder(topic)
    op, description = builder()
    table = _format_pauli_table(op)
    return QiskitContext(
        hamiltonian_str=table,
        prose_description=description,
    )


# ── Builder router ────────────────────────────────────────────────────────────

def _choose_builder(topic: str):
    t = topic.lower()
    if "eigen" in t or "spectral" in t or "diagonali" in t:
        return _diagonal_hamiltonian
    if "hermitian" in t or "unitary" in t or "matrix" in t:
        return _pauli_hamiltonian
    if "tensor" in t or "composite" in t:
        return _tensor_product_hamiltonian
    if "lie" in t or "su(2)" in t or "commut" in t:
        return _su2_hamiltonian
    if "ising" in t or "heisenberg" in t or "spin" in t:
        return _heisenberg_hamiltonian
    if "symmetr" in t or "representation" in t or "group" in t:
        return _symmetric_hamiltonian
    if "density" in t or "mixed" in t or "partial trace" in t:
        return _entangled_state_hamiltonian
    return _random_local_hamiltonian


# ── Hamiltonian builders ──────────────────────────────────────────────────────

def _diagonal_hamiltonian():
    """A 2-qubit Hamiltonian diagonal in the Z basis — easy to diagonalise by inspection."""
    op = SparsePauliOp.from_list([
        ("ZI", 0.5),
        ("IZ", -0.5),
        ("ZZ", 0.25),
    ])
    return op, "2-qubit diagonal Hamiltonian (Z-basis eigenstates)"


def _pauli_hamiltonian():
    """A general 1-qubit Hamiltonian as a Pauli sum."""
    hx = round(random.uniform(0.1, 0.9), 2)
    hz = round(random.uniform(0.1, 0.9), 2)
    op = SparsePauliOp.from_list([("X", hx), ("Z", hz)])
    return op, f"Single-qubit Hamiltonian H = {hx}X + {hz}Z"


def _tensor_product_hamiltonian():
    """Tensor product structure: local terms on each qubit."""
    op = SparsePauliOp.from_list([
        ("XI", 1.0),
        ("IX", 1.0),
        ("ZI", 0.5),
        ("IZ", 0.5),
    ])
    return op, "2-qubit Hamiltonian with tensor-product structure (H = X⊗I + I⊗X + Z⊗I + I⊗Z)"


def _su2_hamiltonian():
    """SU(2) generators as a Hamiltonian: H = Jx + Jy + Jz (spin-1/2)."""
    op = SparsePauliOp.from_list([
        ("X", 0.5),
        ("Y", 0.5),
        ("Z", 0.5),
    ])
    return op, "SU(2) Hamiltonian: H = ½(X + Y + Z) — equal-weight Pauli sum"


def _heisenberg_hamiltonian():
    """3-site Heisenberg XXX chain."""
    op = SparsePauliOp.from_list([
        ("IXX", 1.0),
        ("IYY", 1.0),
        ("IZZ", 1.0),
        ("XXI", 1.0),
        ("YYI", 1.0),
        ("ZZI", 1.0),
    ])
    return op, "3-site Heisenberg XXX chain: H = Σᵢ (XᵢXᵢ₊₁ + YᵢYᵢ₊₁ + ZᵢZᵢ₊₁)"


def _symmetric_hamiltonian():
    """Transverse-field Ising model with Z₂ symmetry."""
    J = round(random.uniform(0.5, 1.5), 2)
    h = round(random.uniform(0.3, 0.8), 2)
    op = SparsePauliOp.from_list([
        ("ZZI", -J),
        ("IZZ", -J),
        ("XII", -h),
        ("IXI", -h),
        ("IIX", -h),
    ])
    return op, (
        f"Transverse-field Ising model (J={J}, h={h}): "
        f"H = −{J}(ZZI + IZZ) − {h}(XII + IXI + IIX)"
    )


def _entangled_state_hamiltonian():
    """A Hamiltonian whose ground state is a Bell state."""
    op = SparsePauliOp.from_list([
        ("XX", -1.0),
        ("ZZ", -1.0),
    ])
    return op, "Bell-state Hamiltonian: H = −XX − ZZ (ground state = |Φ⁺⟩)"


def _random_local_hamiltonian():
    """Random 2-local Hamiltonian on 3 qubits."""
    terms = []
    paulis = ["X", "Y", "Z", "I"]
    for _ in range(6):
        p = "".join(random.choice(paulis) for _ in range(3))
        if p == "III":
            continue
        coeff = round(random.uniform(-1.0, 1.0), 2)
        terms.append((p, coeff))
    if not terms:
        terms = [("ZZI", 1.0), ("IZZ", 1.0)]
    op = SparsePauliOp.from_list(terms)
    return op, "Random 2-local Hamiltonian on 3 qubits"


# ── Formatting ────────────────────────────────────────────────────────────────

def _format_pauli_table(op: SparsePauliOp) -> str:
    simplified = op.simplify()
    lines = ["  Pauli term │ Coefficient"]
    lines.append("  " + "─" * 28)
    for pauli, coeff in zip(simplified.paulis, simplified.coeffs):
        c = coeff.real if abs(coeff.imag) < 1e-9 else coeff
        lines.append(f"  {str(pauli):>10} │  {c:+.4f}")
    return "\n".join(lines)
