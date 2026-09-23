"""Question: vz_circuit_layout_needs_transpile"""
from core.models import Question

QUESTION = Question(
    id='vz_circuit_layout_needs_transpile',
    section='Visualization',
    question='What happens?\n\n```python\nfrom qiskit.visualization import plot_circuit_layout\n\nqc = QuantumCircuit(3)\nqc.h(0)\nqc.cx(0, 1)\nplot_circuit_layout(qc, backend)\n```',
    options=[
        'It shows the trivial layout 0 → 0, 1 → 1, 2 → 2',
        "QiskitError: 'Circuit has no layout. Perhaps it has not been transpiled.'",
        'It transpiles the circuit for you, then plots the result',
        'It plots every backend qubit in the same colour',
    ],
    correct_index=1,
    explanation='plot_circuit_layout reads circuit.layout, which only exists after a transpiler run — transpile(...) or pass_manager.run(...). Hand it the ISA circuit, not the abstract one; the function never transpiles on your behalf.',
    difficulty='medium',
)
