"""Kata: ra2_parity_subset"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="ra2_parity_subset",
    section="Results analysis",
    title="<Z2 Z0> from three-qubit counts",
    difficulty="advanced",
    prompt="""\
A Pauli-Z observable that touches only SOME qubits is still a parity
calculation — but the parity runs over the qubits in the observable's
support only. Qubits sitting under an identity must be IGNORED, not
folded into the sign.

Given the fixed 3-qubit counts (keys are 'q2 q1 q0'), compute `exp` — the
estimate of <Z on qubit 2 * Z on qubit 0>, i.e. the observable "ZIZ":

    eigenvalue of a key = (-1) ** (b2 + b0)      <- qubit 1 not involved

By hand: +300 - 100 + 150 + 250 - 200 = 400, over 1000 shots -> 0.4.
(Counting the middle bit too would give 0.5 — that is the trap.)
""",
    starter_code="""\
counts = {"000": 300, "001": 100, "010": 150, "101": 250, "110": 200}
shots = sum(counts.values())

# TODO: exp = ...   (parity of qubits 2 and 0 only; remember bits[-1] is qubit 0)
""",
    test_code="""\
assert abs(exp - 0.5) > 1e-9, (
    f"You got {exp} — that is the parity of ALL THREE bits. "
    "The observable is ZIZ: qubit 1 carries an identity and must not change the sign."
)
assert abs(exp - 0.4) < 1e-9, (
    f"Expected <Z2 Z0> = 0.4, got {exp}. Key 'b2 b1 b0': qubit 0 is bits[-1] and "
    "qubit 2 is bits[-3] (== bits[0] for 3-bit keys). Sign is +1 when those two agree."
)
print(f"<Z2 Z0> = {exp}")
""",
    solution_code="""\
counts = {"000": 300, "001": 100, "010": 150, "101": 250, "110": 200}
shots = sum(counts.values())

exp = sum(
    (1 if bits[-1] == bits[-3] else -1) * n
    for bits, n in counts.items()
) / shots
""",
    hints=[
        "For a key 'b2 b1 b0', qubit k is bits[-(k + 1)] — so qubit 2 is bits[-3].",
        "The eigenvalue is (-1) ** (int(bits[-3]) + int(bits[-1])): +1 when the two bits agree.",
        "Equivalently: marginal_counts(counts, indices=[0, 2]) first, then the usual 2-bit parity.",
    ],
)
