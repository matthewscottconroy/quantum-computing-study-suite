"""Question: oq_loads_optional_dep"""
from core.models import Question

QUESTION = Question(
    id='oq_loads_optional_dep',
    section='OpenQASM',
    question='On a machine with only `qiskit` and `qiskit-aer` installed, qasm3.dumps(qc) works but qasm3.loads(src) raises MissingOptionalLibraryError. Why?',
    options=[
        'loads() needs qiskit-ibm-runtime',
        'The OpenQASM 3 importer was removed in Qiskit 2.0',
        'The OpenQASM 3 PARSER ships separately: qasm3.loads/load require the optional qiskit-qasm3-import package',
        'loads() needs a backend to validate the program against',
    ],
    correct_index=2,
    explanation='Qiskit bundles the OpenQASM 3 exporter but leaves parsing to the optional qiskit-qasm3-import package, which qasm3.loads and qasm3.load require at call time (pip install qiskit-qasm3-import). OpenQASM 2 is different — qasm2.dumps and qasm2.loads are both built in.',
    difficulty='medium',
)
