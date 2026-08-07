"""Problem: bos_rep_cat"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_rep_cat',
    category='Bosonic Codes',
    difficulty='advanced',
    question='The repetition-cat code combines an inner cat qubit with an outer repetition code. What is the key insight that makes this efficient?',
    choices=[
        'Cat qubits have exponentially suppressed Z errors, so the outer repetition code only needs to correct the remaining X errors — achieving low logical error rates with far fewer qubits than a surface code',
        'The cat qubit eliminates all errors, and the repetition code is only needed for classical fault tolerance',
        'The repetition code corrects Z errors while the cat qubit corrects X errors — orthogonal protection',
        'Concatenating cat qubits with a repetition code always outperforms the surface code at all error rates',
    ],
    correct_index=0,
    explanation='The repetition-cat architecture exploits noise bias: each physical qubit is a cat qubit with Z-error probability p_Z ~ e^{-2|α|²} (exponentially small) and X-error probability p_X ~ κt|α|² (polynomial). The outer repetition code is designed to only correct X errors — it needs minimal distance because p_X is the only relevant error. Since the repetition code is simple (few qubits), the total overhead is potentially far below that of a surface code at the same logical error rate. This has been the basis of experiments at Alice & Bob and theoretical proposals for near-term fault-tolerant qubits.',
    hints=[
        'Use the cat qubit to make one error type rare; then a simple code handles the other.',
    ],
    grade_mode=GradeMode.AUTO,
)
