"""Kata: ra_zz_from_counts"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="ra_zz_from_counts",
    section="Results analysis",
    title="<ZZ> from raw counts",
    difficulty="intermediate",
    prompt="""\
When you only have counts (a Sampler, or real hardware), expectation
values must be reconstructed by hand. For Z-basis observables that is a
parity calculation:

    ZZ eigenvalue of |b1 b0>  =  +1 if b1 == b0 (even parity)
                                 -1 if b1 != b0 (odd parity)

Given the fixed counts in the starter, compute `exp_zz` — the estimate of
<ZZ> — as   sum(eigenvalue * count) / shots.

By hand: (400 + 500 - 60 - 40) / 1000 = 0.8.
""",
    starter_code="""\
counts = {"00": 400, "01": 60, "10": 40, "11": 500}
shots = sum(counts.values())

# TODO: exp_zz = ...  (+1 for 00/11, -1 for 01/10)
""",
    test_code="""\
assert abs(exp_zz - 0.8) < 1e-9, (
    f"Expected <ZZ> = 0.8, got {exp_zz}. "
    "Even-parity strings (00, 11) contribute +1, odd-parity (01, 10) contribute -1."
)
print(f"<ZZ> = {exp_zz}")
""",
    solution_code="""\
counts = {"00": 400, "01": 60, "10": 40, "11": 500}
shots = sum(counts.values())

exp_zz = sum(
    (1 if bits.count("1") % 2 == 0 else -1) * n
    for bits, n in counts.items()
) / shots
""",
    hints=[
        "The eigenvalue is (-1) ** (number of 1s in the bitstring).",
        "Weight each eigenvalue by its count, then divide by total shots.",
    ],
)
