"""Kata: ra2_marginal_counts"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="ra2_marginal_counts",
    section="Results analysis",
    title="marginal_counts: keep only the qubits you care about",
    difficulty="intermediate",
    prompt="""\
`qiskit.result.marginal_counts` sums a counts dict over the qubits you
did NOT list, leaving a smaller dict keyed by the ones you kept. That is
how you read a sub-register out of a big measurement without re-running
anything.

`indices` are QUBIT indices (little-endian), and the surviving key keeps
little-endian order: for indices=[0, 2] the key is 'q2 q0'.

Using the fixed counts in the starter, build:

1. `m_q0`  — marginal over qubit 0 alone
2. `m_q02` — marginal over qubits 0 and 2

Work the first one out by hand: the keys ending in '1' are '011' and
'101', so m_q0 == {'0': 550, '1': 450}.
""",
    starter_code="""\
from qiskit.result import marginal_counts

counts = {"000": 300, "011": 250, "101": 200, "110": 250}

# TODO: m_q0 = ..., m_q02 = ...
""",
    test_code="""\
assert isinstance(m_q0, dict), f"m_q0 must be a counts dict, got {type(m_q0).__name__}"
assert m_q0 == {"0": 550, "1": 450}, (
    f"Marginalising onto qubit 0 gives {{'0': 550, '1': 450}}, got {m_q0}. "
    "Qubit 0 is the RIGHTMOST character of each key."
)
assert sum(m_q0.values()) == sum(counts.values()), (
    "Marginalising never loses shots — the totals must still match"
)
assert m_q02 == {"00": 300, "01": 250, "10": 250, "11": 200}, (
    f"Marginalising onto qubits 0 and 2 gives "
    f"{{'00': 300, '01': 250, '10': 250, '11': 200}}, got {m_q02}. "
    "The surviving key is 'q2 q0' — qubit 1 is summed away."
)
print(f"m_q0 = {m_q0}\\nm_q02 = {m_q02}")
""",
    solution_code="""\
from qiskit.result import marginal_counts

counts = {"000": 300, "011": 250, "101": 200, "110": 250}

m_q0 = marginal_counts(counts, indices=[0])
m_q02 = marginal_counts(counts, indices=[0, 2])
""",
    hints=[
        "from qiskit.result import marginal_counts — it takes (counts, indices=[...]).",
        "indices lists the qubits to KEEP; everything else is summed over.",
        "marginal_distribution is the same idea for probability dicts.",
    ],
)
