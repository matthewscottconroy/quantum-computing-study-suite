"""Problem: bos_cat_name"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='bos_cat_name',
    category='Bosonic Codes',
    difficulty='beginner',
    question="Why are cat qubits called 'cat' qubits?",
    choices=[
        "The codewords |C±_α⟩ = |α⟩ ± |−α⟩ are macroscopic superpositions analogous to Schrödinger's cat (alive + dead)",
        "The acronym CAT stands for 'Coherent Amplitude Transfer'",
        'The coherent state amplitude traces a cat-ear shape in phase space',
        'They were first demonstrated using an optical lattice shaped like a cat',
    ],
    correct_index=0,
    explanation="The cat qubit codewords are quantum superpositions of two macroscopically distinct coherent states |α⟩ and |−α⟩ in phase space. For large |α|, these states have very different mean photon number and are nearly orthogonal — analogous to Schrödinger's thought experiment of a cat in a superposition of alive (|α⟩) and dead (|−α⟩). The 'cat' name reflects this direct analogy to Schrödinger cat states, which were initially considered paradoxical precisely because they are superpositions of macroscopically distinguishable states.",
    hints=[
        "Schrödinger's cat is the famous thought experiment involving a quantum superposition of two classical outcomes.",
    ],
    grade_mode=GradeMode.AUTO,
)
