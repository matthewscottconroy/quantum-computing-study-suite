"""Question: cc_prepare_state"""
from core.models import Question

QUESTION = Question(
    id='cc_prepare_state',
    section='Create circuits',
    question='Which method prepares an arbitrary normalized state on chosen qubits WITHOUT first resetting them (unlike initialize)?',
    options=[
        'qc.prepare_state(...)',
        'qc.set_statevector(...)',
        'qc.load_state(...)',
        'qc.statevector(...)',
    ],
    correct_index=0,
    explanation='prepare_state() applies the state-preparation unitary directly, assuming the qubits start in |0⟩; initialize() additionally inserts reset instructions first. set_statevector is an Aer simulator instruction, not a state-preparation method, and the other two do not exist.',
    difficulty='medium',
)
