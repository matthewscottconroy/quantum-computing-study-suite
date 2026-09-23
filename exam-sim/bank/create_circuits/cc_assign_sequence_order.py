"""Question: cc_assign_sequence_order"""
from core.models import Question

QUESTION = Question(
    id='cc_assign_sequence_order',
    section='Create circuits',
    question='What angle does the `rz` gate end up with?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.circuit import ParameterVector\n\nv = ParameterVector("v", 3)\nqc = QuantumCircuit(1)\nqc.rz(v[2], 0)\nqc.rx(v[0], 0)\nqc.ry(v[1], 0)\nbound = qc.assign_parameters([0.1, 0.2, 0.3])\n```',
    options=[
        '0.3 — a positional sequence is matched against qc.parameters, so v[2] gets the third value',
        '0.1 — a positional sequence is matched against the order the gates were added',
        '0.2 — the sequence is matched against the order the ParameterVector elements were created, offset by one',
        'A CircuitError — a plain list can only be used when the circuit has exactly one parameter',
    ],
    correct_index=0,
    explanation='assign_parameters accepts either a dict or a sequence. A sequence is zipped against qc.parameters, which is sorted by name: v[0], v[1], v[2]. So v[0]=0.1, v[1]=0.2, v[2]=0.3 and the rz gate (which uses v[2]) becomes rz(0.3), regardless of it being the first gate added.',
    difficulty='hard',
)
