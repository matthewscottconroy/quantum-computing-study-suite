"""Problem: steane_hadamard_css_duality"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='steane_hadamard_css_duality',
    category='Steane Code',
    difficulty='intermediate',
    question='In a CSS code, applying H to every physical qubit swaps the X and Z stabilizer groups. For the Steane code, what does this mean for the logical state?',
    choices=[
        'The logical |0̄⟩ and |+̄⟩ states are swapped, implementing logical H̄ — this works because the Steane code is self-dual (H_X = H_Z)',
        'The code is mapped to a different code and logical information is lost',
        'Only the Z-stabilizers are affected; X-stabilizers are unchanged by H',
        'H⊗7 implements logical S̄ by rotating the stabilizer structure',
    ],
    correct_index=0,
    explanation='H⊗7 maps each X-stabilizer generator g_X to the corresponding Z-stabilizer generator g_Z and vice versa (since HXH=Z and HZH=X). For a general CSS code, this changes H_X to H_Z and H_Z to H_X — which is only a valid code transformation if H_X = H_Z (self-dual). The Steane code satisfies this: its X and Z check matrices are identical. The net logical effect maps |0̄⟩ to |+̄⟩ = H̄|0̄⟩, implementing logical H̄.',
    hints=[
        'Self-duality (H_X = H_Z) ensures H⊗7 maps the codespace to itself.',
    ],
    grade_mode=GradeMode.AUTO,
)
