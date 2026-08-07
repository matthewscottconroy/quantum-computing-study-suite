"""Problem: ft_prepare_zero_bar"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='ft_prepare_zero_bar',
    category='Fault Tolerance',
    difficulty='advanced',
    question='How is the logical |0̄⟩ state prepared fault-tolerantly for a stabilizer code?',
    choices=[
        'Prepare many non-fault-tolerant |0̄⟩ copies, verify using stabilizer measurements with ancilla, and repeat if errors are detected',
        'Apply the encoding circuit directly to |0⟩ — this is inherently fault-tolerant',
        'Prepare |+̄⟩ and measure Z̄ to project to |0̄⟩',
        'Use a cat state and CNOT fan-out to create |0̄⟩ fault-tolerantly',
    ],
    correct_index=0,
    explanation='Fault-tolerant |0̄⟩ preparation: (1) prepare a candidate codeword using a non-fault-tolerant encoding circuit; (2) measure all stabilizers to detect errors — any error from the non-FT encoding step will produce a detectable syndrome; (3) if syndrome is non-trivial, correct it and re-verify; (4) repeat until the state passes verification with high confidence. The key insight is that verification can be fault-tolerant (using the stabilizer measurements themselves) even if preparation was not.',
    hints=[
        'Prepare, then verify using stabilizer measurements — errors during encoding are detectable.',
    ],
    grade_mode=GradeMode.AUTO,
)
