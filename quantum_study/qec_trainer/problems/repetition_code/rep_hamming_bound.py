"""Problem: rep_hamming_bound"""
from __future__ import annotations
from quantum_study.qec_trainer.core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_hamming_bound',
    category='Repetition Code',
    difficulty='advanced',
    question='Why does the quantum Hamming bound require at least n=5 physical qubits to encode 1 qubit and correct 1 error?',
    choices=[
        'Every one of the 1+3n single-qubit errors needs its own syndrome, so 2^(n−1) ≥ 1+3n, first true at n=5',
        'A code on n qubits needs n stabilizer generators, and five generators are needed to locate an error',
        'The bound is 2^n ≥ 1+3n, and n=5 is the smallest n that satisfies it',
        'Only the n bit-flip errors need distinct syndromes, so 2^(n−1) ≥ 1+n, which first holds at n=5',
    ],
    correct_index=0,
    explanation='A non-degenerate [[n,k]] code that corrects one error must give every correctable error its own syndrome. There are 2^(n−k) syndromes and 1+3n errors to tell apart (no error, plus X, Y or Z on each of the n qubits), so 2^(n−k) ≥ 1+3n. For k=1: n=4 gives 2³=8 syndromes for 13 errors — too few; n=5 gives 2⁴=16 syndromes for 16 errors — exactly saturated, which is why the [[5,1,3]] code is called perfect. The distractors fail on the counting: an [[n,1]] code has n−1 generators, not n; 2^n ≥ 1+3n already holds at n=4; and counting only X errors gives 2^(n−1) ≥ 1+n, which holds at n=3 (the classical repetition code).',
    hints=[
        'Count error possibilities: I + 3 Paulis × n qubits, and compare to available syndrome space 2^(n-k).',
    ],
    grade_mode=GradeMode.AUTO,
)
