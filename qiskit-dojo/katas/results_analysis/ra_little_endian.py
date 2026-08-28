"""Kata: ra_little_endian"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="ra_little_endian",
    section="Results analysis",
    title="Per-qubit probabilities from counts (little-endian!)",
    difficulty="intermediate",
    prompt="""\
Counts keys are little-endian bitstrings: the RIGHTMOST character is
qubit 0. Misreading this is the single most common results bug.

Given the fixed counts dict in the starter:

    counts = {"01": 480, "10": 520}

compute:
1. `p1_q0` — probability that QUBIT 0 measured 1
2. `p1_q1` — probability that QUBIT 1 measured 1

Work it out by hand first: in "01", qubit 0 is the '1' (rightmost) and
qubit 1 is the '0'. So p1_q0 = 0.48 and p1_q1 = 0.52.
""",
    starter_code="""\
counts = {"01": 480, "10": 520}
shots = sum(counts.values())

# TODO: p1_q0 = ..., p1_q1 = ...   (remember: qubit 0 is the RIGHTMOST char)
""",
    test_code="""\
assert abs(p1_q0 - 0.48) < 1e-9, (
    f"p1_q0 should be 0.48, got {p1_q0}. Qubit 0 is bitstring[-1], not bitstring[0]!"
)
assert abs(p1_q1 - 0.52) < 1e-9, (
    f"p1_q1 should be 0.52, got {p1_q1}. Qubit 1 is bitstring[-2]."
)
print(f"p1_q0 = {p1_q0}, p1_q1 = {p1_q1}")
""",
    solution_code="""\
counts = {"01": 480, "10": 520}
shots = sum(counts.values())

p1_q0 = sum(n for bits, n in counts.items() if bits[-1] == "1") / shots
p1_q1 = sum(n for bits, n in counts.items() if bits[-2] == "1") / shots
""",
    hints=[
        "For an n-bit key, qubit k is bits[-(k + 1)] — count from the right.",
        "Sum the counts of every key whose relevant bit is '1', divide by total shots.",
    ],
)
