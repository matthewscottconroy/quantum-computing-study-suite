"""
Shared helpers used by all problem generators.
All Qiskit imports live here or in the generator files — nowhere else.
"""

from __future__ import annotations
import io
import cmath
import math
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector, Operator
from config import CIRCUIT_DPI


# ── Gate catalogue ────────────────────────────────────────────────────────────

# name → (label for display, builder fn that takes QuantumCircuit + qubit index)
SINGLE_QUBIT_GATES: dict[str, tuple[str, object]] = {
    "X":      ("X (Pauli-X / NOT)",   lambda qc, q: qc.x(q)),
    "Y":      ("Y (Pauli-Y)",         lambda qc, q: qc.y(q)),
    "Z":      ("Z (Pauli-Z)",         lambda qc, q: qc.z(q)),
    "H":      ("H (Hadamard)",        lambda qc, q: qc.h(q)),
    "S":      ("S (Phase √Z)",        lambda qc, q: qc.s(q)),
    "T":      ("T (π/8 gate)",        lambda qc, q: qc.t(q)),
    "Sdg":    ("S† (S-dagger)",       lambda qc, q: qc.sdg(q)),
    "Tdg":    ("T† (T-dagger)",       lambda qc, q: qc.tdg(q)),
    "Rx(π/4)": ("Rx(π/4)",           lambda qc, q: qc.rx(math.pi / 4, q)),
    "Rx(π/2)": ("Rx(π/2)",           lambda qc, q: qc.rx(math.pi / 2, q)),
    "Ry(π/4)": ("Ry(π/4)",           lambda qc, q: qc.ry(math.pi / 4, q)),
    "Ry(π/2)": ("Ry(π/2)",           lambda qc, q: qc.ry(math.pi / 2, q)),
    "Rz(π/4)": ("Rz(π/4)",           lambda qc, q: qc.rz(math.pi / 4, q)),
    "Rz(π/2)": ("Rz(π/2) = S",       lambda qc, q: qc.rz(math.pi / 2, q)),
}

TWO_QUBIT_GATES: dict[str, tuple[str, object]] = {
    "CNOT":  ("CNOT",   lambda qc, c, t: qc.cx(c, t)),
    "CZ":    ("CZ",     lambda qc, c, t: qc.cz(c, t)),
    "SWAP":  ("SWAP",   lambda qc, c, t: qc.swap(c, t)),
}

# Exact matrix representations
GATE_MATRICES: dict[str, np.ndarray] = {
    "X":      np.array([[0,1],[1,0]], dtype=complex),
    "Y":      np.array([[0,-1j],[1j,0]], dtype=complex),
    "Z":      np.array([[1,0],[0,-1]], dtype=complex),
    "H":      np.array([[1,1],[1,-1]], dtype=complex) / math.sqrt(2),
    "S":      np.array([[1,0],[0,1j]], dtype=complex),
    "T":      np.array([[1,0],[0,cmath.exp(1j*math.pi/4)]], dtype=complex),
    "Sdg":    np.array([[1,0],[0,-1j]], dtype=complex),
    "Tdg":    np.array([[1,0],[0,cmath.exp(-1j*math.pi/4)]], dtype=complex),
    "Rx(π/4)": np.array([[math.cos(math.pi/8), -1j*math.sin(math.pi/8)],
                          [-1j*math.sin(math.pi/8), math.cos(math.pi/8)]], dtype=complex),
    "Rx(π/2)": np.array([[1/math.sqrt(2), -1j/math.sqrt(2)],
                          [-1j/math.sqrt(2), 1/math.sqrt(2)]], dtype=complex),
    "Ry(π/4)": np.array([[math.cos(math.pi/8), -math.sin(math.pi/8)],
                          [math.sin(math.pi/8),  math.cos(math.pi/8)]], dtype=complex),
    "Ry(π/2)": np.array([[1/math.sqrt(2), -1/math.sqrt(2)],
                          [1/math.sqrt(2),  1/math.sqrt(2)]], dtype=complex),
    "Rz(π/4)": np.array([[cmath.exp(-1j*math.pi/8), 0],
                          [0, cmath.exp(1j*math.pi/8)]], dtype=complex),
    "Rz(π/2)": np.array([[cmath.exp(-1j*math.pi/4), 0],
                          [0, cmath.exp(1j*math.pi/4)]], dtype=complex),
}

# Standard input states
INPUT_STATES: dict[str, Statevector] = {
    "|0⟩": Statevector([1, 0]),
    "|1⟩": Statevector([0, 1]),
    "|+⟩": Statevector([1, 1]) / math.sqrt(2),
    "|−⟩": Statevector([1, -1]) / math.sqrt(2),
    "|i⟩": Statevector([1, 1j]) / math.sqrt(2),
    "|−i⟩": Statevector([1, -1j]) / math.sqrt(2),
}

TWO_QUBIT_INPUT_STATES: dict[str, Statevector] = {
    "|00⟩": Statevector([1,0,0,0]),
    "|01⟩": Statevector([0,1,0,0]),
    "|10⟩": Statevector([0,0,1,0]),
    "|11⟩": Statevector([0,0,0,1]),
    "|+0⟩": Statevector([1,0,1,0]) / math.sqrt(2),
    "|+1⟩": Statevector([0,1,0,1]) / math.sqrt(2),
}


# ── Rendering ─────────────────────────────────────────────────────────────────

def render_circuit(qc: QuantumCircuit) -> bytes:
    """Render a QuantumCircuit to PNG bytes. Returns empty bytes on failure."""
    try:
        fig = qc.draw(output="mpl", style="bw", fold=-1)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=CIRCUIT_DPI, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()
    except Exception:
        return b""


def render_matrix(matrix: np.ndarray, label: str = "") -> str:
    """Format a complex matrix as a Unicode box string."""
    n = matrix.shape[0]
    rows = []
    for i in range(n):
        cells = []
        for j in range(n):
            v = matrix[i, j]
            cells.append(_fmt_complex(v))
        rows.append("  ".join(f"{c:>14}" for c in cells))
    width = len(rows[0]) + 4
    top    = "┌" + " " * width + "┐"
    bottom = "└" + " " * width + "┘"
    lines = [top] + [f"│  {r}  │" for r in rows] + [bottom]
    if label:
        lines.insert(0, label)
    return "\n".join(lines)


def _fmt_complex(v: complex) -> str:
    re, im = v.real, v.imag
    # Round near-zero parts
    if abs(re) < 1e-9: re = 0.0
    if abs(im) < 1e-9: im = 0.0
    # Recognise common exact values
    exact = _recognise(v)
    if exact:
        return exact
    if im == 0:
        return f"{re:+.4f}"
    if re == 0:
        return f"{im:+.4f}i"
    return f"{re:+.4f}{im:+.4f}i"


def _recognise(v: complex) -> str | None:
    """Map common quantum values to their symbolic form."""
    s2 = math.sqrt(2)
    table: list[tuple[complex, str]] = [
        (0, "0"), (1, "1"), (-1, "−1"),
        (1j, "i"), (-1j, "−i"),
        (1/s2, "1/√2"), (-1/s2, "−1/√2"),
        (1j/s2, "i/√2"), (-1j/s2, "−i/√2"),
        (cmath.exp(1j*math.pi/4), "e^(iπ/4)"),
        (cmath.exp(-1j*math.pi/4), "e^(−iπ/4)"),
        (cmath.exp(1j*math.pi/2), "i"),
        (cmath.exp(-1j*math.pi/2), "−i"),
    ]
    for val, sym in table:
        if abs(v - val) < 1e-9:
            return sym
    return None


# ── State formatting ──────────────────────────────────────────────────────────

def format_statevector(sv: Statevector, n_qubits: int | None = None) -> str:
    """Return a human-readable Dirac expansion of a Statevector."""
    n = n_qubits or int(round(math.log2(len(sv))))
    terms = []
    for idx, amp in enumerate(sv):
        if abs(amp) < 1e-9:
            continue
        basis = f"|{format(idx, f'0{n}b')}⟩"
        sym = _recognise(amp)
        coeff = sym if sym else _fmt_complex(amp)
        if coeff == "1":
            terms.append(basis)
        elif coeff == "−1":
            terms.append(f"−{basis}")
        else:
            terms.append(f"({coeff}){basis}")
    return " + ".join(terms).replace("+ (−", "− (").replace("+ −", "− ") or "0"


def statevector_for_circuit(qc: QuantumCircuit, initial: Statevector | None = None) -> Statevector:
    """Evolve a statevector through a circuit (no measurements)."""
    qc_no_meas = qc.remove_final_measurements(inplace=False)
    if initial is None:
        return Statevector(qc_no_meas)
    return initial.evolve(qc_no_meas)


# ── Distractors ───────────────────────────────────────────────────────────────

def make_distractors(correct_str: str, n: int = 3) -> list[str]:
    """Generate n plausible wrong state-vector strings different from correct_str."""
    pool = [
        "|0⟩", "|1⟩", "|+⟩", "|−⟩", "|i⟩", "|−i⟩",
        "(1/√2)|00⟩ + (1/√2)|11⟩", "(1/√2)|00⟩ − (1/√2)|11⟩",
        "(1/√2)|01⟩ + (1/√2)|10⟩", "(1/√2)|01⟩ − (1/√2)|10⟩",
        "|00⟩", "|01⟩", "|10⟩", "|11⟩",
        "(1/√2)|0⟩ + (i/√2)|1⟩",
        "(1/√2)|0⟩ − (i/√2)|1⟩",
        "(1/√2)|0⟩ + (e^(iπ/4)/√2)|1⟩",
    ]
    distractors = [s for s in pool if s != correct_str]
    random.shuffle(distractors)
    return distractors[:n]


def make_prob_distractors(correct: float, n: int = 3) -> list[float]:
    """Generate n wrong probability values."""
    candidates = [0.0, 0.25, 0.5, 0.75, 1.0,
                  round(correct + 0.25, 4), round(correct - 0.25, 4),
                  round(1.0 - correct, 4), round(correct / 2, 4)]
    candidates = [max(0.0, min(1.0, c)) for c in candidates]
    candidates = [c for c in candidates if abs(c - correct) > 1e-3]
    candidates = list(dict.fromkeys(candidates))  # dedupe
    random.shuffle(candidates)
    return candidates[:n]
