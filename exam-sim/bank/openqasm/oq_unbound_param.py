"""Question: oq_unbound_param"""
from core.models import Question

QUESTION = Question(
    id='oq_unbound_param',
    section='OpenQASM',
    question='What happens?\n\n```python\nfrom qiskit import QuantumCircuit, qasm2, qasm3\nfrom qiskit.circuit import Parameter\n\ntheta = Parameter("theta")\nqc = QuantumCircuit(1)\nqc.rx(theta, 0)\n\nprint(qasm3.dumps(qc))\nprint(qasm2.dumps(qc))\n```',
    options=[
        'Both exporters emit rx(theta) q[0]; with a matching parameter declaration',
        'The OpenQASM 3 export declares input float[64] theta; while qasm2.dumps raises QASM2ExportError',
        'Both raise — parameters must be bound before any export',
        'Both silently substitute theta = 0',
    ],
    correct_index=1,
    explanation='OpenQASM 3 has a real notion of a free parameter, so Qiskit emits `input float[64] theta;` and uses the name in the gate call. OpenQASM 2 has nothing equivalent, so the second call fails with QASM2ExportError("Cannot represent circuits with unbound parameters in OpenQASM 2."). Bind first with qc.assign_parameters({theta: 0.5}) if you need OpenQASM 2.',
    difficulty='hard',
)
