"""Question: cc_copy_empty_like"""
from core.models import Question

QUESTION = Question(
    id='cc_copy_empty_like',
    section='Create circuits',
    question='A developer wants a new circuit with the same quantum and classical registers as `qc` but with no instructions. Which call does this?',
    options=[
        'qc.copy_empty_like()',
        'qc.copy(deep=False)',
        'qc.clear_gates()',
        'QuantumCircuit.from_registers(qc)',
    ],
    correct_index=0,
    explanation='copy_empty_like() clones the register structure (and metadata) while dropping all instructions. copy() duplicates the instructions too, and the other two methods do not exist.',
    difficulty='medium',
)
