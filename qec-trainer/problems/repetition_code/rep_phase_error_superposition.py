"""Problem: rep_phase_error_superposition"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_phase_error_superposition',
    category='Repetition Code',
    difficulty='intermediate',
    question='Consider the state α|000⟩ + β|111⟩. If a Z error acts on qubit 1, what is the resulting state, and why does the 3-qubit bit-flip code fail to detect it?',
    choices=[
        'α|000⟩ − β|111⟩; both stabilizers Z₁Z₂ and Z₂Z₃ still give +1, so syndrome is (0,0)',
        '−α|000⟩ + β|111⟩; syndrome is (1,0) so it is detected',
        'α|100⟩ + β|011⟩; syndrome is (1,1) indicating qubit 2 errored',
        'α|000⟩ + β|111⟩ unchanged; Z commutes with X stabilizers',
    ],
    correct_index=0,
    explanation='Z₁ on α|000⟩+β|111⟩ gives α Z₁|000⟩+β Z₁|111⟩ = α|000⟩−β|111⟩. The stabilizers Z₁Z₂ and Z₂Z₃ both measure the parity of Z eigenvalues, and Z₁Z₂(α|000⟩−β|111⟩) = +(α|000⟩−β|111⟩) since Z₁=+1, Z₂=+1 for |00⟩ and Z₁=−1, Z₂=−1 for |11⟩ in both terms. The phase flip is completely invisible to these stabilizers — it only changes the relative phase between |000⟩ and |111⟩.',
    hints=[
        'Apply Z to qubit 1 of each term and check all stabilizer eigenvalues.',
    ],
    grade_mode=GradeMode.AUTO,
)
