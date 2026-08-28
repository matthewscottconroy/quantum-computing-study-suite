"""Question: cc_count_ops"""
from core.models import Question

QUESTION = Question(
    id='cc_count_ops',
    section='Create circuits',
    question="Which method returns a dictionary-like mapping of gate names to how many times each appears in a circuit, e.g. {'cx': 2, 'h': 1}?",
    options=[
        'qc.count_ops()',
        'qc.size()',
        'qc.num_instructions()',
        'qc.operations()',
    ],
    correct_index=0,
    explanation='count_ops() returns an OrderedDict of operation name -> count. size() returns the total number of instructions as a single int, and the other two methods do not exist on QuantumCircuit.',
    difficulty='easy',
)
