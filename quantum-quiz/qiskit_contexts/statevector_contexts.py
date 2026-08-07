"""
Statevector-based Qiskit contexts for: Quantum Mechanics, Foundations of QM.

build_context(topic) → QiskitContext with statevector_table.
"""

from __future__ import annotations
import random
import math
import cmath

from qiskit.quantum_info import Statevector, partial_trace, entropy
from qiskit_contexts import QiskitContext


def build_context(topic: str) -> QiskitContext:
    builder = _choose_builder(topic)
    sv, description = builder()
    table = _format_amplitude_table(sv)
    return QiskitContext(
        statevector_table=table,
        prose_description=description,
    )


# ── Builder router ────────────────────────────────────────────────────────────

def _choose_builder(topic: str):
    t = topic.lower()
    if "bell" in t or "entangl" in t:
        return _bell_state
    if "ghz" in t or "w state" in t:
        return _ghz_state
    if "bloch" in t or "single-qubit" in t or "postulate" in t:
        return _single_qubit_state
    if "teleport" in t:
        return _bell_state
    if "measurement" in t or "born rule" in t or "povm" in t:
        return _superposition_state
    if "schmidt" in t or "bipartite" in t:
        return _schmidt_state
    if "decoher" in t or "density" in t or "mixed" in t:
        return _cluster_state
    if "no-clon" in t or "holevo" in t:
        return _nonorthogonal_pair
    return _random_state


# ── State builders ────────────────────────────────────────────────────────────

def _bell_state():
    choice = random.randint(0, 3)
    bells = [
        (Statevector([1, 0, 0, 1]) / math.sqrt(2), "|Φ⁺⟩ = (|00⟩+|11⟩)/√2"),
        (Statevector([1, 0, 0, -1]) / math.sqrt(2), "|Φ⁻⟩ = (|00⟩−|11⟩)/√2"),
        (Statevector([0, 1, 1, 0]) / math.sqrt(2), "|Ψ⁺⟩ = (|01⟩+|10⟩)/√2"),
        (Statevector([0, 1, -1, 0]) / math.sqrt(2), "|Ψ⁻⟩ = (|01⟩−|10⟩)/√2"),
    ]
    sv, desc = bells[choice]
    ent = _entanglement_entropy(sv, 2)
    return sv, f"Bell state {desc} — entanglement entropy S = {ent:.4f} bits"


def _ghz_state():
    n = random.choice([3, 4])
    dim = 2 ** n
    data = [0.0] * dim
    data[0] = 1.0 / math.sqrt(2)
    data[-1] = 1.0 / math.sqrt(2)
    sv = Statevector(data)
    ent = _entanglement_entropy(sv, n)
    return sv, f"{n}-qubit GHZ state (|0…0⟩+|1…1⟩)/√2 — S₁ = {ent:.4f} bits"


def _single_qubit_state():
    theta = random.choice([math.pi / 6, math.pi / 4, math.pi / 3, math.pi / 2])
    phi = random.choice([0, math.pi / 4, math.pi / 2, math.pi])
    a = math.cos(theta / 2)
    b = cmath.exp(1j * phi) * math.sin(theta / 2)
    sv = Statevector([a, b])
    return sv, (
        f"Single-qubit state |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ)sin(θ/2)|1⟩ "
        f"with θ={theta:.3f}, φ={phi:.3f}"
    )


def _superposition_state():
    # Random 2-qubit state
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2)
    qc.h(0)
    theta = random.choice([math.pi / 6, math.pi / 4, math.pi / 3])
    qc.ry(theta, 1)
    qc.cx(0, 1)
    sv = Statevector(qc)
    return sv, "2-qubit state for measurement analysis"


def _schmidt_state():
    """A 2-qubit state with known Schmidt rank 2."""
    alpha = round(random.uniform(0.3, 0.7), 2)
    beta = math.sqrt(1 - alpha ** 2)
    sv = Statevector([alpha, 0, 0, beta])
    ent = -alpha**2 * math.log2(alpha**2) - beta**2 * math.log2(beta**2)
    return sv, (
        f"2-qubit state {alpha:.2f}|00⟩ + {beta:.2f}|11⟩ "
        f"(Schmidt rank 2, S = {ent:.4f} bits)"
    )


def _cluster_state():
    """4-qubit linear cluster state."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(4)
    qc.h([0, 1, 2, 3])
    qc.cz(0, 1)
    qc.cz(1, 2)
    qc.cz(2, 3)
    sv = Statevector(qc)
    return sv, "4-qubit linear cluster state (resource state for measurement-based QC)"


def _nonorthogonal_pair():
    """Two non-orthogonal states — for no-cloning / Holevo bound questions."""
    sv = Statevector([math.cos(math.pi / 8), math.sin(math.pi / 8)])
    return sv, (
        "Single-qubit state |ψ⟩ = cos(π/8)|0⟩ + sin(π/8)|1⟩ "
        "(non-orthogonal to |0⟩; relevant to no-cloning, state discrimination)"
    )


def _random_state():
    from qiskit import QuantumCircuit
    n = random.randint(2, 3)
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for q in range(n - 1):
        angle = random.choice([math.pi / 4, math.pi / 3, math.pi / 6])
        qc.cp(angle, q, q + 1)
    sv = Statevector(qc)
    return sv, f"{n}-qubit state for quantum mechanics analysis"


# ── Formatting ────────────────────────────────────────────────────────────────

def _format_amplitude_table(sv: Statevector) -> str:
    n = int(math.log2(len(sv)))
    lines = [f"  Basis state │ Amplitude              │ Probability"]
    lines.append("  " + "─" * 52)
    for idx, amp in enumerate(sv):
        if abs(amp) < 1e-9:
            continue
        label = f"|{format(idx, f'0{n}b')}⟩"
        prob = abs(amp) ** 2
        re, im = amp.real, amp.imag
        if abs(im) < 1e-9:
            amp_str = f"{re:+.4f}      "
        elif abs(re) < 1e-9:
            amp_str = f"{im:+.4f}i     "
        else:
            amp_str = f"{re:+.4f}{im:+.4f}i"
        lines.append(f"  {label:>11} │ {amp_str:<22} │ {prob:.4f}")
    # Append entanglement info for multi-qubit states
    if n >= 2:
        try:
            ent = _entanglement_entropy(sv, n)
            lines.append(f"\n  Von Neumann entropy (qubit 0 ↔ rest): S = {ent:.4f} bits")
        except Exception:
            pass
    return "\n".join(lines)


def _entanglement_entropy(sv: Statevector, n: int) -> float:
    """Entanglement entropy of qubit 0 with the rest."""
    try:
        rho = sv.to_operator()  # density matrix
        from qiskit.quantum_info import DensityMatrix
        dm = DensityMatrix(sv)
        rho_0 = partial_trace(dm, list(range(1, n)))
        return float(entropy(rho_0, base=2))
    except Exception:
        return 0.0
