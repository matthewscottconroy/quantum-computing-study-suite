"""Question: oq_custom_gate_export"""
from core.models import Question

QUESTION = Question(
    id='oq_custom_gate_export',
    section='OpenQASM',
    question='What appears in the output?\n\n```python\nsub = QuantumCircuit(2, name="bell")\nsub.h(0)\nsub.cx(0, 1)\n\nqc = QuantumCircuit(2)\nqc.append(sub.to_gate(), [0, 1])\nprint(qasm2.dumps(qc))\n```',
    options=[
        'A gate bell q0,q1 { h q0; cx q0,q1; } definition, followed by bell q[0],q[1];',
        'The custom gate inlined as h q[0]; cx q[0],q[1];',
        'QASM2ExportError — only qelib1.inc gates can be exported',
        'opaque bell q0,q1; with no body',
    ],
    correct_index=0,
    explanation='Both exporters walk the definition of any non-standard instruction and emit a matching `gate` declaration ahead of the program body, so the structure of the circuit survives instead of being flattened. Only an instruction with no unitary definition at all — a genuine opaque, or something non-unitary like initialize in OpenQASM 3 — causes an export error.',
    difficulty='medium',
)
