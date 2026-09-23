"""Kata: qo2_group_commuting"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="qo2_group_commuting",
    section="Quantum operations",
    title="Grouping commuting Pauli terms",
    difficulty="advanced",
    prompt="""\
An Estimator needs one measurement basis per group of simultaneously
measurable terms. `SparsePauliOp.group_commuting()` does that grouping
for you, and `qubit_wise=True` restricts it to the stricter
same-Pauli-per-qubit grouping that a plain basis rotation can realise.

For the given `H`:
1. `H` — SparsePauliOp.from_list(terms)  (5 terms)
2. `groups` — H.group_commuting()                  (general commutation)
3. `qw_groups` — H.group_commuting(qubit_wise=True)
4. `n_groups`, `n_qw` — the number of groups in each

Qubit-wise grouping is strictly finer, so n_qw >= n_groups. Every term
must survive: the groups partition H's terms.
""",
    starter_code="""\
from qiskit.quantum_info import SparsePauliOp

terms = [("XX", 1.0), ("YY", 2.0), ("ZZ", 3.0), ("IZ", 0.5), ("ZI", 0.25)]

# TODO: H, groups, qw_groups, n_groups, n_qw
""",
    test_code="""\
from qiskit.quantum_info import SparsePauliOp

assert isinstance(H, SparsePauliOp) and len(H) == 5, "H must be the 5-term SparsePauliOp"
assert all(isinstance(g, SparsePauliOp) for g in groups), (
    "group_commuting returns a list of SparsePauliOp"
)
assert n_groups == len(groups) and n_qw == len(qw_groups), (
    "n_groups and n_qw must be the lengths of the two group lists"
)
assert n_groups == 2, (
    f"XX, YY and ZZ mutually commute and IZ, ZI commute, so there are 2 general groups, "
    f"got {n_groups}"
)
assert n_qw == 3, (
    f"Qubit-wise, XX / YY / (ZZ, IZ, ZI) need 3 distinct measurement bases, got {n_qw}"
)
assert n_qw >= n_groups, "Qubit-wise grouping can never be coarser than general grouping"

for _name, _gs in (("groups", groups), ("qw_groups", qw_groups)):
    _labels = sorted(str(p) for g in _gs for p in g.paulis)
    assert _labels == sorted(str(p) for p in H.paulis), (
        f"{_name} must partition every term of H exactly once, got {_labels}"
    )
print(f"general groups = {n_groups}, qubit-wise groups = {n_qw}")
""",
    solution_code="""\
from qiskit.quantum_info import SparsePauliOp

terms = [("XX", 1.0), ("YY", 2.0), ("ZZ", 3.0), ("IZ", 0.5), ("ZI", 0.25)]

H = SparsePauliOp.from_list(terms)
groups = H.group_commuting()
qw_groups = H.group_commuting(qubit_wise=True)
n_groups = len(groups)
n_qw = len(qw_groups)
""",
    hints=[
        "SparsePauliOp.from_list(terms) then op.group_commuting().",
        "Pass qubit_wise=True for the stricter grouping — each qubit must carry the same "
        "Pauli letter (or I) across the whole group.",
        "XX, YY and ZZ commute as full operators even though they differ on every qubit, "
        "which is exactly why the two groupings disagree.",
    ],
)
