"""Problem: rep_no_direct_measure"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='rep_no_direct_measure',
    category='Repetition Code',
    difficulty='intermediate',
    question="Why can't we measure the data qubits directly to detect errors in a quantum repetition code?",
    choices=[
        'Direct measurement collapses the logical superposition, destroying the encoded quantum state',
        'Direct measurement is too slow to be practical',
        'The ancilla qubits would need to be re-initialized after every measurement',
        'Data qubits are not accessible in a physical quantum device',
    ],
    correct_index=0,
    explanation='If we measured the data qubits directly in the Z basis, we would project α|000⟩ + β|111⟩ onto either |000⟩ or |111⟩, destroying the superposition and learning nothing useful about which error occurred. Instead, syndrome measurements using ancilla qubits extract parity information (e.g., Z₁Z₂) without collapsing the logical state.',
    hints=[
        'What happens to α|000⟩ + β|111⟩ if we measure qubit 1 in the {|0⟩,|1⟩} basis?',
    ],
    grade_mode=GradeMode.AUTO,
)
