"""Question: sa_measure_all_second_creg"""
from core.models import Question

QUESTION = Question(
    id='sa_measure_all_second_creg',
    section='Sampler',
    question='What does this print?\n\n```python\nfrom qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister\nfrom qiskit.primitives import StatevectorSampler\n\nqc = QuantumCircuit(QuantumRegister(1, "q"), ClassicalRegister(1, "c"))\nqc.x(0)\nqc.measure(0, 0)\nqc.measure_all()\n\nprint(list(StatevectorSampler().run([qc], shots=8).result()[0].data.keys()))\n```',
    options=[
        "['c', 'meas'] — measure_all() appended a second classical register called 'meas'",
        "['c'] — measure_all() reuses the existing classical register",
        "['meas'] — measure_all() replaces the existing register",
        "['c0', 'c1'] — registers are renamed positionally in the DataBin",
    ],
    correct_index=0,
    explanation='measure_all() always adds a *new* register named "meas" sized to the qubit count (unless add_bits=False) — it never reuses an existing one. The circuit therefore has two classical registers, the DataBin has two fields, and the same qubit is recorded twice. Use measure_all(add_bits=False) or explicit measure() calls to avoid the duplicate.',
    difficulty='hard',
)
