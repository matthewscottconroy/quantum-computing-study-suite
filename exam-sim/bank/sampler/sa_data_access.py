"""Question: sa_data_access"""
from core.models import Question

QUESTION = Question(
    id='sa_data_access',
    section='Sampler',
    question='Which line extracts the counts dictionary?\n\n```python\nfrom qiskit import QuantumCircuit\nfrom qiskit.primitives import StatevectorSampler\n\nqc = QuantumCircuit(2)\nqc.h(0)\nqc.cx(0, 1)\nqc.measure_all()\nresult = StatevectorSampler().run([qc], shots=1024).result()\n```',
    options=[
        'counts = result[0].data.meas.get_counts()',
        'counts = result.get_counts(0)',
        'counts = result[0].quasi_dists[0]',
        'counts = result[0].data.get_counts()',
    ],
    correct_index=0,
    explanation="V2 sampler results are indexed per pub; each pub result's data has one field per classical register. measure_all() created a register named 'meas', hence result[0].data.meas.get_counts(). get_counts() on the result itself and quasi_dists are V1 idioms that no longer exist.",
    difficulty='medium',
)
