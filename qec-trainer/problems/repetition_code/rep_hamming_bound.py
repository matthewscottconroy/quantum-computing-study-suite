"""Problem: rep_hamming_bound"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_hamming_bound',
    category='Repetition Code',
    difficulty='advanced',
    question='Why does the quantum Hamming bound require at least n=5 physical qubits to encode 1 qubit and correct 1 error?',
    choices=[
        'With n=5, k=1, there are 2^4=16 syndromes for 1+3·5=16 error possibilities (I plus X,Y,Z on each of 5 qubits)',
        'n=5 is required to have 5 stabilizer generators',
        'The bound n ≥ k+2+log₂(3n+1) gives n≥5 for k=1',
        'Both A and C are correct derivations of the same requirement',
    ],
    correct_index=3,
    explanation='There are two equivalent ways to see this. Counting: 4 independent stabilizers give 2⁴=16 distinguishable syndromes. The errors on 5 qubits are {I} ∪ {X,Y,Z on each qubit} = 1 + 3×5 = 16 distinct patterns — exactly fitting the 16 syndromes. Alternatively, the Hamming bound n ≥ k + 2 + log₂(3n+1) with k=1 gives n ≥ 3 + log₂(3n+1); for n=5: 3 + log₂(16) = 3+4 = 7 ≥ 5? Checking n=4: 1+3×4+1=14 errors, but 2^3=8 syndromes — insufficient. n=5: 16 errors, 16 syndromes — exactly saturated.',
    hints=[
        'Count error possibilities: I + 3 Paulis × n qubits, and compare to available syndrome space 2^(n-k).',
    ],
    grade_mode=GradeMode.AUTO,
)
