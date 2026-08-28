"""Question: oq_loads_vs_load"""
from core.models import Question

QUESTION = Question(
    id='oq_loads_vs_load',
    section='OpenQASM',
    question='You hold an OpenQASM 3 program in a Python STRING named `src`. Which call turns it into a QuantumCircuit?',
    options=[
        'qc = qasm3.loads(src)',
        'qc = qasm3.load(src)',
        'qc = QuantumCircuit.from_qasm_str(src)',
        'qc = qasm3.parse(src)',
    ],
    correct_index=0,
    explanation='Following the json module convention, loads() parses a string while load() takes a filename/file. QuantumCircuit.from_qasm_str() only understands OpenQASM 2, and qasm3.parse() does not exist.',
    difficulty='easy',
)
