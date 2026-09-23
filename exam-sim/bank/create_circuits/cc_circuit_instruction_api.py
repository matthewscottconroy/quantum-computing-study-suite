"""Question: cc_circuit_instruction_api"""
from core.models import Question

QUESTION = Question(
    id='cc_circuit_instruction_api',
    section='Create circuits',
    question='A circuit is built and one entry inspected:\n\n```python\nfrom qiskit import QuantumCircuit\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\ninstr = qc.data[1]\n```\n\nWhich access pattern is deprecated legacy behaviour in Qiskit 2.x?',
    options=[
        'instr[0] — treating the CircuitInstruction as an (operation, qubits, clbits) tuple',
        'instr.operation — the operation stored in the instruction',
        'instr.qubits — the qubits the instruction acts on',
        'instr.clbits — the classical bits the instruction acts on',
    ],
    correct_index=0,
    explanation='qc.data yields CircuitInstruction objects. Tuple-style unpacking/indexing (op, qargs, cargs = instr, or instr[0]) is deprecated legacy behaviour since Qiskit 1.2 and is slated for removal in 3.0; the supported accessors are the named attributes .operation, .qubits and .clbits.',
    difficulty='medium',
)
