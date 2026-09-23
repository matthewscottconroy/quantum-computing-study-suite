"""Question: cc_switch_case"""
from core.models import Question

QUESTION = Question(
    id='cc_switch_case',
    section='Create circuits',
    question='What does count_ops() report for this circuit?\n\n```python\nfrom qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\n\ncr = ClassicalRegister(2, "c")\nqc = QuantumCircuit(QuantumRegister(2, "q"), cr)\nqc.h(0)\nqc.measure(0, 0)\nwith qc.switch(cr) as case:\n    with case(0):\n        qc.x(1)\n    with case(1):\n        qc.z(1)\n    with case(case.DEFAULT):\n        qc.y(1)\nprint(dict(qc.count_ops()))\n```',
    options=[
        "{'h': 1, 'measure': 1, 'switch_case': 1}",
        "{'h': 1, 'measure': 1, 'x': 1, 'z': 1, 'y': 1}",
        "{'h': 1, 'measure': 1, 'if_else': 3}",
        'It raises a CircuitError — switch() takes a single clbit, never a whole register',
    ],
    correct_index=0,
    explanation='The switch context manager builds ONE SwitchCaseOp (operation name "switch_case") whose bodies are nested circuits; the branch gates are not instructions of the outer circuit. switch() accepts a clbit, a ClassicalRegister, or a classical expression as the target, and case.DEFAULT supplies the fallback branch.',
    difficulty='hard',
)
