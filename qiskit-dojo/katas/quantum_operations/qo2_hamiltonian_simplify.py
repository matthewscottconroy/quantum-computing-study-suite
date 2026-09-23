"""Kata: qo2_hamiltonian_simplify"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo2_hamiltonian_simplify",
    section="Quantum operations",
    title="Build and simplify a SparsePauliOp Hamiltonian",
    difficulty="intermediate",
    prompt="""\
Hamiltonians assembled term by term usually arrive with duplicates and
zero coefficients. `SparsePauliOp.simplify()` sums duplicate Pauli labels
and drops (near-)zero terms — fewer terms means fewer Estimator
measurement bases.

The starter gives `raw_terms`, a redundant 2-qubit term list. Build:
1. `H_raw` — SparsePauliOp.from_list(raw_terms)   (5 terms, as given)
2. `H` — the simplified operator
3. `n_terms` — len(H)

After simplification: "ZZ" collects 1.0 + (-0.25) = 0.75, "XI" collects
0.5 + 0.5 = 1.0, and the 0.0 "IY" term disappears — 2 terms left.
The matrix must be unchanged.
""",
    starter_code="""\
import numpy as np
from qiskit.quantum_info import SparsePauliOp

raw_terms = [
    ("ZZ", 1.0),
    ("XI", 0.5),
    ("IY", 0.0),
    ("ZZ", -0.25),
    ("XI", 0.5),
]

# TODO: H_raw = ..., H = ..., n_terms = ...
""",
    test_code="""\
import numpy as np
from qiskit.quantum_info import SparsePauliOp

assert isinstance(H_raw, SparsePauliOp), "H_raw must be a SparsePauliOp"
assert len(H_raw) == 5, f"H_raw keeps all 5 raw terms, got {len(H_raw)}"
assert isinstance(H, SparsePauliOp), "H must be a SparsePauliOp"

assert n_terms == 2, (
    f"simplify() should leave 2 terms (ZZ and XI), got {n_terms}. "
    "Duplicates add up and the zero-coefficient term is dropped."
)
assert len(H) == n_terms, "n_terms must be len(H)"

_got = {str(p): complex(c) for p, c in H.to_list()}
assert set(_got) == {"ZZ", "XI"}, f"Expected labels ZZ and XI, got {sorted(_got)}"
assert abs(_got["ZZ"] - 0.75) < 1e-12, f"ZZ coefficient should be 0.75, got {_got['ZZ']}"
assert abs(_got["XI"] - 1.0) < 1e-12, f"XI coefficient should be 1.0, got {_got['XI']}"
assert np.allclose(H.to_matrix(), H_raw.to_matrix()), (
    "simplify() must not change the operator — only its representation"
)
print(f"Simplified {len(H_raw)} -> {n_terms} terms: {H.to_list()}")
""",
    solution_code="""\
import numpy as np
from qiskit.quantum_info import SparsePauliOp

raw_terms = [
    ("ZZ", 1.0),
    ("XI", 0.5),
    ("IY", 0.0),
    ("ZZ", -0.25),
    ("XI", 0.5),
]

H_raw = SparsePauliOp.from_list(raw_terms)
H = H_raw.simplify()
n_terms = len(H)
""",
    hints=[
        "SparsePauliOp.from_list(raw_terms) keeps duplicate labels as separate terms.",
        "simplify() returns a NEW operator with duplicates summed and zero terms removed.",
        "len(op) is the number of Pauli terms; op.to_list() shows (label, coeff) pairs.",
    ],
)
