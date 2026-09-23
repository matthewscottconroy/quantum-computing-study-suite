"""Kata: ra2_shot_noise"""
from __future__ import annotations
from core.models import Kata

KATA = Kata(
    id="ra2_shot_noise",
    section="Results analysis",
    title="Error bar on an expectation value",
    difficulty="intermediate",
    prompt="""\
An expectation value read off counts is an ESTIMATE, and quoting it
without an error bar is the classic beginner mistake. For a Pauli
observable with eigenvalues +-1:

    ev  = (n_plus - n_minus) / shots
    err = sqrt((1 - ev**2) / shots)        <- standard error of the mean

and, because err shrinks like 1/sqrt(shots), reaching a target error
takes  shots = ceil((1 - ev**2) / target**2)  of them.

From the fixed single-qubit Z counts, compute:

1. `ev`           — the expectation value              (expect 0.28)
2. `err`          — its standard error                 (expect ~0.0304)
3. `shots_needed` — an int: shots required for err <= 0.005

Note how expensive that last one is compared with the 1000 you have.
""",
    starter_code="""\
import math

counts = {"0": 640, "1": 360}
shots = sum(counts.values())
target = 0.005

# TODO: ev = ..., err = ..., shots_needed = ...
""",
    test_code="""\
import math

assert abs(ev - 0.28) < 1e-9, (
    f"ev = (n0 - n1) / shots = (640 - 360) / 1000 = 0.28, got {ev}. "
    "Outcome '0' is the +1 eigenvalue, '1' is -1."
)
_err = math.sqrt((1 - 0.28 ** 2) / 1000)
assert abs(err - _err) < 1e-12, (
    f"err = sqrt((1 - ev**2) / shots) = {_err:.6f}, got {err}. "
    "Divide by shots inside the square root, not after it."
)
assert isinstance(shots_needed, int), (
    f"shots_needed must be a whole number of shots (use math.ceil), "
    f"got {type(shots_needed).__name__}"
)
assert shots_needed == 36864, (
    f"ceil((1 - ev**2) / 0.005**2) = 36864, got {shots_needed}. "
    "Six times smaller error costs about thirty-seven times the shots."
)
print(f"ev = {ev} +/- {err:.4f}; {shots_needed} shots needed for +/-{0.005}")
""",
    solution_code="""\
import math

counts = {"0": 640, "1": 360}
shots = sum(counts.values())
target = 0.005

ev = (counts["0"] - counts["1"]) / shots
err = math.sqrt((1 - ev ** 2) / shots)
shots_needed = math.ceil((1 - ev ** 2) / target ** 2)
""",
    hints=[
        "For +-1 eigenvalues the variance is 1 - ev**2, so the standard error is sqrt of that over shots.",
        "Solve err = sqrt((1 - ev**2) / N) for N, then round UP with math.ceil.",
        "Shot noise scales as 1/sqrt(N): ten times the precision costs a hundred times the shots.",
    ],
)
