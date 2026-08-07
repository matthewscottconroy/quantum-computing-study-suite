"""Problem: surf_circuit_level_threshold"""
from __future__ import annotations
from core.models import Problem, GradeMode

PROBLEM = Problem(
    id='surf_circuit_level_threshold',
    category='Surface Code',
    difficulty='intermediate',
    question='The fault-tolerant threshold for the surface code under circuit-level depolarizing noise (all gates, measurements, and idles noisy) is approximately:',
    choices=[
        '~0.5–1% per gate, depending on the noise model and decoder',
        '~10% — same as the code capacity threshold',
        '~0.01% — much lower due to ancilla errors',
        '~5% — limited by CNOT gate errors during syndrome extraction',
    ],
    correct_index=0,
    explanation="Under circuit-level noise (where each two-qubit gate, single-qubit gate, measurement, state preparation, and idle step is subject to depolarizing noise), the surface code threshold drops to approximately 0.5–1%. The exact value depends on the syndrome extraction circuit, the decoder, and the specific noise model. Google's experiments with superconducting qubits (Arute et al. 2019 and later) and Fowler et al.'s theoretical analyses place this around 1% for standard MWPM decoding. This is still higher than typical trapped-ion or superconducting error rates.",
    hints=[
        'Circuit-level noise includes errors during syndrome extraction — much more pessimistic than code capacity.',
    ],
    grade_mode=GradeMode.AUTO,
)
