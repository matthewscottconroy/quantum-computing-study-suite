"""Question: oq_global_phase_lost"""
from core.models import Question

QUESTION = Question(
    id='oq_global_phase_lost',
    section='OpenQASM',
    question='What does this print?\n\n```python\nimport numpy as np\nfrom qiskit import QuantumCircuit, qasm3\n\nqc = QuantumCircuit(1, name="myname", global_phase=np.pi / 2)\nqc.x(0)\n\nrt = qasm3.loads(qasm3.dumps(qc))\nprint(rt.global_phase, rt.name == "myname")\n```',
    options=[
        '1.5707963267948966 True',
        '0.0 False',
        '1.5707963267948966 False',
        'It raises QASM3ExporterError because of the global phase',
    ],
    correct_index=1,
    explanation='Neither OpenQASM dialect records a circuit-level global phase or the Python-side circuit name, so both are dropped on a round trip and the rebuilt circuit gets an auto-generated name such as circuit-42. Gates, barriers and register NAMES do survive. The result is therefore equivalent only up to global phase: Operator(qc).equiv(Operator(rt)) is True while plain equality is not.',
    difficulty='hard',
)
