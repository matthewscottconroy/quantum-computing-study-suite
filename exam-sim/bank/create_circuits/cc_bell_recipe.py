"""Question: cc_bell_recipe"""
from core.models import Question

QUESTION = Question(
    id='cc_bell_recipe',
    section='Create circuits',
    question='Which snippet prepares the Bell state (|00⟩ + |11⟩)/√2 from |00⟩?',
    options=[
        'qc.h(0); qc.cx(0, 1)',
        'qc.cx(0, 1); qc.h(0)',
        'qc.h(0); qc.h(1)',
        'qc.x(0); qc.cx(0, 1)',
    ],
    correct_index=0,
    explanation='H on qubit 0 creates (|0⟩+|1⟩)/√2, then CX with qubit 0 as control copies that superposition into correlation: (|00⟩+|11⟩)/√2. Applying CX first does nothing (control is |0⟩); H on both qubits gives a product state |++⟩; X then CX gives |11⟩ with no superposition.',
    difficulty='easy',
)
