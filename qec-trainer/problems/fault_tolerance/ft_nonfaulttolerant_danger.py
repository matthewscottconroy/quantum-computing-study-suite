"""Problem: ft_nonfaulttolerant_danger"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_nonfaulttolerant_danger',
    category='Fault Tolerance',
    difficulty='intermediate',
    question='What can go wrong if a non-fault-tolerant operation (e.g., a direct cross-block CNOT) is applied within a fault-tolerant code?',
    choices=[
        'A single gate fault can create a high-weight error in one code block, exceeding the correction capacity and causing a logical error',
        'Non-FT operations always cause immediate logical errors regardless of the fault rate',
        'Non-FT operations are harmless as long as the error rate is below threshold',
        'Only measurements need to be fault-tolerant; gate operations do not',
    ],
    correct_index=0,
    explanation='Fault tolerance requires that one fault creates at most one error per code block. A non-FT operation — e.g., coupling multiple qubits within one block — can spread a single fault to multiple qubits. For example, a CNOT between qubit 1 and qubit 2 of the same block: an error on the CNOT creates errors on both qubits 1 and 2 (weight 2). A distance-3 code can only correct weight-1 errors; this weight-2 error from one fault is uncorrectable, breaking fault tolerance. The entire point of transversality is to prevent intra-block error propagation.',
    hints=[
        "One fault → weight-2 error → uncorrectable by a distance-3 code. That's the danger.",
    ],
    grade_mode=GradeMode.AUTO,
)
